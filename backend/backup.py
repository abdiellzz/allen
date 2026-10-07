from __future__ import annotations
import json
FORMAT="allen-backup"; VERSION=1
TABLES=("users","progress","quiz_results","flashcards","learning_sessions","library_packs","student_memory","saved_answers","study_plans","study_sessions","study_session_events","adventure_sessions","adventure_events","simulation_results","topic_mastery","learning_events","profile_current_activity","teacher_documents","courses","course_enrollments","course_exam_results","course_exam_sessions","curriculum_edges","question_bank","course_quality_reviews","diagnostic_results")

def export_backup(db):
    data={"format":FORMAT,"version":VERSION,"tables":{}}
    for table in TABLES:
        try:data["tables"][table]=db.all(f"SELECT * FROM {table}")
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
    # Restore is intentionally all-or-nothing and uses trusted table/column names only.
    with db.connect() as con:
        con.execute("PRAGMA foreign_keys=OFF")
        for table in reversed(TABLES):
            try:con.execute(f"DELETE FROM {table}")
            except Exception:pass
        for table in TABLES:
            rows=tables.get(table,[])
            for row in rows:
                if not isinstance(row,dict) or not row: continue
                cols=[c for c in row.keys() if c.replace("_","").isalnum()]
                values=[row[c] for c in cols]
                q=",".join("?" for _ in cols)
                con.execute(f"INSERT INTO {table}({','.join(cols)}) VALUES({q})",values)
        settings=payload.get("settings")
        if isinstance(settings,dict):
            from .schemas import Settings
            safe=Settings.model_validate(settings)
            con.execute("INSERT OR REPLACE INTO settings(id,value) VALUES(1,?)",(safe.model_dump_json(),))
        con.execute("PRAGMA foreign_keys=ON")
    return validate_backup(payload)
