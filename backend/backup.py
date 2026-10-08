from __future__ import annotations
import json
FORMAT="allen-backup"; VERSION=1
TABLES=("users","progress","quiz_results","flashcards","learning_sessions","library_packs","student_memory","saved_answers","conversations","conversation_states","study_plans","study_sessions","study_session_events","adventure_sessions","adventure_events","simulation_results","topic_mastery","learning_events","profile_current_activity","teacher_documents","courses","course_enrollments","course_exam_results","course_exam_sessions","curriculum_edges","question_bank","course_quality_reviews","diagnostic_results","course_versions")
TABLE_SET=frozenset(TABLES)

def _safe_table(table):
    if table not in TABLE_SET:
        raise ValueError('Tabla de respaldo no permitida.')
    return table


def export_backup(db):
    data={"format":FORMAT,"version":VERSION,"tables":{}}
    for table in TABLES:
        table=_safe_table(table)
        try:data["tables"][table]=db.all(f"SELECT * FROM {table}")  # nosec B608: table is a closed allowlist
        except Exception:data["tables"][table]=[]
    try:data["settings"]=db.settings().model_dump()
    except Exception:data["settings"]={}
    return data

def validate_backup(payload):
    if not isinstance(payload,dict) or payload.get("format")!=FORMAT: raise ValueError("Este archivo no es un respaldo de ALLEN.")
    if payload.get("version")!=VERSION: raise ValueError("Versión de respaldo no compatible.")
    tables=payload.get("tables")
    if not isinstance(tables,dict): raise ValueError("Respaldo incompleto.")
    size=len(json.dumps(payload,ensure_ascii=False))
    if size>5_000_000: raise ValueError("El respaldo es demasiado grande.")
    return {"profiles":len(tables.get("users",[])),"flashcards":len(tables.get("flashcards",[])),"plans":len(tables.get("study_plans",[])),"adventures":len(tables.get("adventure_sessions",[])),"simulations":len(tables.get("simulation_results",[])),"courses":len(tables.get("courses",[])),"questions":len(tables.get("question_bank",[])),"diagnostics":len(tables.get("diagnostic_results",[]))}

def restore_backup(db,payload):
    validate_backup(payload)
    tables=payload["tables"]
    # Restore is all-or-nothing. Table names are fixed and columns must match
    # the actual schema; malformed backups fail instead of leaking across users.
    with db.connect() as con:
        con.execute("PRAGMA foreign_keys=OFF")
        schema_columns={}
        for table in TABLES:
            table=_safe_table(table)
            schema_columns[table]={row["name"] for row in con.execute(f"PRAGMA table_info({table})").fetchall()}  # nosec B608: allowlisted table
        for table in reversed(TABLES):
            table=_safe_table(table)
            con.execute(f"DELETE FROM {table}")  # nosec B608: allowlisted table
        for table in TABLES:
            rows=tables.get(table,[])
            if not isinstance(rows,list):
                raise ValueError(f"Tabla inválida en el respaldo: {table}.")
            allowed=schema_columns.get(table,set())
            for row in rows:
                if not isinstance(row,dict) or not row:
                    continue
                unknown=set(row)-allowed
                if unknown:
                    raise ValueError(f"El respaldo contiene columnas no válidas en {table}.")
                cols=[c for c in row.keys() if c in allowed]
                if not cols:
                    continue
                if any(col not in allowed for col in cols):
                    raise ValueError(f"El respaldo contiene columnas no válidas en {table}.")
                values=[row[c] for c in cols]
                q=",".join("?" for _ in cols)
                con.execute(f"INSERT INTO {table}({','.join(cols)}) VALUES({q})",values)  # nosec B608: table allowlisted, columns verified against PRAGMA
        settings=payload.get("settings")
        if isinstance(settings,dict):
            from .schemas import Settings
            safe=Settings.model_validate(settings)
            con.execute("INSERT OR REPLACE INTO settings(id,value) VALUES(1,?)",(safe.model_dump_json(),))
        violations=con.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ValueError("El respaldo tiene relaciones inválidas y no se restauró.")

    # Backup v1 is intentionally backward compatible. Older v1 files did not
    # contain derived learning-intelligence tables, so reconstruct only those
    # derived structures without inventing diagnostic history.
    if "question_bank" not in tables or "curriculum_edges" not in tables:
        from .course_quality import evaluate_course
        from .curriculum_graph import persist_graph
        from .question_bank import sync_course_questions
        for course in db.all("SELECT id,status,structure_json FROM courses"):
            try:
                structure=json.loads(course["structure_json"])
                persist_graph(db,course["id"],structure)
                sync_course_questions(db,course["id"],structure)
                if course["status"] in ("reviewed","published"):
                    db.execute("UPDATE question_bank SET status='approved' WHERE course_id=?",(course["id"],))
                report=evaluate_course(structure)
                db.execute("INSERT INTO course_quality_reviews(course_id,score,blocking_issues,report_json,created_at) VALUES(?,?,?,?,datetime('now'))",
                           (course["id"],report["score"],report["blocking_issues"],json.dumps(report,ensure_ascii=False)))
            except Exception:
                continue
    if "course_versions" not in tables:
        from .course_versioning import seed_initial_version
        for course in db.all("SELECT id,source_document_id,structure_json,status FROM courses"):
            try:
                seed_initial_version(db,course["id"],course["source_document_id"],json.loads(course["structure_json"]),course["status"])
            except Exception:
                continue
    return validate_backup(payload)
