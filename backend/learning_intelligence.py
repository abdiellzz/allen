from __future__ import annotations
import json
from .time_utils import local_day_iso

def mastery_evidence(db,user_id,subject,topic):
    row=db.one("SELECT * FROM topic_mastery WHERE user_id=? AND subject=? AND topic=?",(user_id,subject,topic))
    if not row:return None
    last_exam=None
    for item in db.all("SELECT result_json FROM course_exam_results WHERE user_id=? ORDER BY id DESC LIMIT 20",(user_id,)):
        try:
            result=json.loads(item["result_json"])
            matches=[x for x in result.get("feedback",[]) if x.get("topic")==topic]
            if matches:
                last_exam=round(sum(1 for x in matches if x.get("correct"))/len(matches)*100)
                break
        except Exception: pass
    return {
      **row,
      "evidence":{
        "correct":row["correct_answers"],"attempts":row["attempts"],"incorrect":row["incorrect_answers"],
        "hints":row["hints_used"],"practice_count":row["practice_count"],"quiz_count":row["quiz_count"],
        "last_exam_percentage":last_exam,
      }
    }

def due_reviews(db,user_id,limit=10):
    return db.all("""SELECT subject,topic,mastery_score,status,next_review,last_seen
      FROM topic_mastery WHERE user_id=? AND next_review IS NOT NULL AND next_review<=?
      ORDER BY next_review ASC,mastery_score ASC LIMIT ?""",(user_id,local_day_iso(),limit))

def diagnostic_questions(structure,count=7):
    pool=[]
    for q in structure.get("final_exam",[]) or []:
        pool.append({"topic":q.get("topic",""),"prompt":q.get("prompt",""),"options":q.get("options",[]),"correct":q.get("correct",""),"source":q.get("source",{})})
    return pool[:max(5,min(10,count))]

def score_diagnostic(questions,answers):
    by_topic={}
    for q,a in zip(questions,answers):
        item=by_topic.setdefault(q["topic"],{"correct":0,"total":0})
        item["total"]+=1
        item["correct"]+=int(a==q["correct"])
    for topic,data in by_topic.items():
        data["percentage"]=round(data["correct"]/max(1,data["total"])*100)
        data["status"]="strong" if data["percentage"]>=80 else "developing" if data["percentage"]>=50 else "weak"
    return by_topic

def recommended_start(structure,topic_scores):
    for ui,unit in enumerate(structure.get("units",[])):
        for ti,topic in enumerate(unit.get("topics",[])):
            score=topic_scores.get(topic.get("title",""),{}).get("percentage",0)
            if score<80:return {"unit_index":ui,"topic_index":ti}
    return {"unit_index":0,"topic_index":0}
