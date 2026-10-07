from __future__ import annotations
import json

def sync_course_questions(db,course_id,structure):
    db.execute("DELETE FROM question_bank WHERE course_id=? AND origin='generated'",(course_id,))
    count=0
    for ui,unit in enumerate(structure.get("units",[])):
        for ti,topic in enumerate(unit.get("topics",[])):
            for q in topic.get("questions",[]) or []:
                db.execute("""INSERT INTO question_bank(course_id,unit_index,topic_index,subject,topic,objective,prompt,answer,options_json,difficulty,kind,source_page,status,origin,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'generated',datetime('now'))""",
                    (course_id,ui,ti,structure.get("subject",""),topic.get("title",""),topic.get("objective",""),q.get("prompt",""),q.get("answer_hint",""),
                     json.dumps(q.get("options",[]),ensure_ascii=False),"Normal","open",int((q.get("source") or topic.get("source") or {}).get("page") or 1),"reviewed"))
                count+=1
    for q in structure.get("final_exam",[]) or []:
        node=next(((ui,ti,t) for ui,u in enumerate(structure.get("units",[])) for ti,t in enumerate(u.get("topics",[])) if t.get("title")==q.get("topic")),(0,0,{}))
        ui,ti,topic=node
        db.execute("""INSERT INTO question_bank(course_id,unit_index,topic_index,subject,topic,objective,prompt,answer,options_json,difficulty,kind,source_page,status,origin,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'generated',datetime('now'))""",
            (course_id,ui,ti,structure.get("subject",""),q.get("topic",""),topic.get("objective",""),q.get("prompt",""),q.get("correct",""),
             json.dumps(q.get("options",[]),ensure_ascii=False),"Normal","multiple",int((q.get("source") or {}).get("page") or 1),"reviewed"))
        count+=1
    return count

def stats_for_course(db,course_id):
    rows=db.all("SELECT id,attempts,correct_count,incorrect_count FROM question_bank WHERE course_id=?",(course_id,))
    ambiguous=[]
    for r in rows:
        attempts=r["attempts"]
        if attempts>=5:
            rate=r["correct_count"]/max(1,attempts)
            if rate<0.15 or rate>0.95: ambiguous.append({"id":r["id"],"correct_rate":round(rate,2),"attempts":attempts})
    return {"questions":len(rows),"flagged_by_stats":ambiguous}
