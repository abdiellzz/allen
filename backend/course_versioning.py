from __future__ import annotations
import json
import re
from datetime import date

def _key(text):
    return re.sub(r"[^a-z0-9áéíóúüñ]+"," ",(text or "").lower()).strip()

def _topics(structure):
    rows=[]
    for ui,unit in enumerate(structure.get("units",[])):
        for ti,topic in enumerate(unit.get("topics",[])):
            rows.append({"key":_key(topic.get("title")),"title":topic.get("title",""),"unit_index":ui,"topic_index":ti,
                         "objective":topic.get("objective",""),"source_excerpt":topic.get("source_excerpt","")})
    return rows

def compare_versions(old_structure,new_structure):
    old={x["key"]:x for x in _topics(old_structure) if x["key"]}
    new={x["key"]:x for x in _topics(new_structure) if x["key"]}
    unchanged=[];modified=[];added=[];removed=[]
    for key,item in new.items():
        before=old.get(key)
        if not before:
            added.append(item)
        elif _key(before["objective"])==_key(item["objective"]) and _key(before["source_excerpt"])==_key(item["source_excerpt"]):
            unchanged.append({"before":before,"after":item})
        else:
            modified.append({"before":before,"after":item})
    for key,item in old.items():
        if key not in new: removed.append(item)
    total=max(1,len(new))
    return {
        "unchanged":unchanged,"modified":modified,"added":added,"removed":removed,
        "summary":{"unchanged":len(unchanged),"modified":len(modified),"added":len(added),"removed":len(removed),
                   "progress_preservable_percent":round(len(unchanged)/total*100)}
    }

def seed_initial_version(db,course_id,source_document_id,structure,status="draft"):
    course=db.one("SELECT version FROM courses WHERE id=?",(course_id,))
    version=int(course["version"] if course else 1)
    exists=db.one("SELECT id FROM course_versions WHERE course_id=? AND version_number=?",(course_id,version))
    if not exists:
        db.execute("""INSERT INTO course_versions(course_id,version_number,source_document_id,structure_json,diff_json,status,created_at)
            VALUES(?,?,?,?,?,?,datetime('now'))""",(course_id,version,source_document_id,json.dumps(structure,ensure_ascii=False),json.dumps({"summary":{"initial":True}},ensure_ascii=False),status))

def apply_version(db,course,source_document_id,new_structure,diff):
    next_version=int(course["version"])+1
    db.execute("""INSERT INTO course_versions(course_id,version_number,source_document_id,structure_json,diff_json,status,created_at)
        VALUES(?,?,?,?,?,'draft',datetime('now'))""",(course["id"],next_version,source_document_id,json.dumps(new_structure,ensure_ascii=False),json.dumps(diff,ensure_ascii=False)))
    db.execute("""UPDATE courses SET source_document_id=?,version=?,structure_json=?,status='draft',updated_at=?,published_at=NULL WHERE id=?""",
               (source_document_id,next_version,json.dumps(new_structure,ensure_ascii=False),date.today().isoformat(),course["id"]))
    modified_titles={x["after"]["title"] for x in diff["modified"]}
    for title in modified_titles:
        db.execute("""UPDATE topic_mastery SET status='reviewing',next_review=date('now')
            WHERE subject=? AND topic=?""",(course["subject"],title))
    # Keep enrollment progress when the exact topic survives; otherwise move to the nearest valid location.
    new_by_key={x["key"]:x for x in _topics(new_structure)}
    old_topics=_topics(json.loads(course["structure_json"]))
    old_by_pos={(x["unit_index"],x["topic_index"]):x for x in old_topics}
    for enrollment in db.all("SELECT * FROM course_enrollments WHERE course_id=?",(course["id"],)):
        old=old_by_pos.get((enrollment["unit_index"],enrollment["topic_index"]))
        mapped=new_by_key.get(old["key"]) if old else None
        if mapped:
            db.execute("UPDATE course_enrollments SET unit_index=?,topic_index=?,step_index=0,status='active',updated_at=datetime('now'),completed_at=NULL WHERE id=?",
                       (mapped["unit_index"],mapped["topic_index"],enrollment["id"]))
        else:
            db.execute("UPDATE course_enrollments SET unit_index=0,topic_index=0,step_index=0,status='active',updated_at=datetime('now'),completed_at=NULL WHERE id=?",(enrollment["id"],))
    return next_version

def history(db,course_id):
    rows=db.all("SELECT id,version_number,source_document_id,diff_json,status,created_at,published_at FROM course_versions WHERE course_id=? ORDER BY version_number DESC",(course_id,))
    for row in rows: row["diff"]=json.loads(row.pop("diff_json") or "{}")
    return rows
