from __future__ import annotations
from datetime import datetime, timedelta, timezone
from .time_utils import local_day, local_day_iso

STATUSES=("new","learning","practicing","reviewing","mastered","needs_reinforcement")

def _clamp(v,lo=0,hi=100):
    return max(lo,min(hi,v))

def compute_mastery(attempts=0,correct=0,incorrect=0,hints=0,practice_count=0,quiz_count=0,last_seen=None,next_review=None,difficulty="Normal"):
    if attempts<=0 and practice_count<=0 and quiz_count<=0:
        return dict(score=0,confidence=0,status="new")
    accuracy=correct/max(1,attempts)
    evidence=min(1.0,(attempts+practice_count+quiz_count)/12)
    difficulty_bonus={"Fácil":0,"Normal":4,"Difícil":8}.get(difficulty,2)
    hint_penalty=min(18,hints*3)
    recent_bonus=0
    if last_seen:
        try:
            seen=datetime.fromisoformat(str(last_seen).replace("Z","+00:00")).date()
            age=(local_day()-seen).days
            recent_bonus=6 if age<=1 else 3 if age<=7 else 0
        except Exception:
            pass
    score=round(_clamp((accuracy*72)+(evidence*16)+difficulty_bonus+recent_bonus-hint_penalty))
    confidence=round(_clamp(evidence*100))
    if score>=85 and confidence>=55: status="mastered"
    elif incorrect>=3 and score<45: status="needs_reinforcement"
    elif next_review and str(next_review)<=local_day_iso(): status="reviewing"
    elif score>=55: status="practicing"
    else: status="learning"
    return dict(score=score,confidence=confidence,status=status)

def next_review_date(score:int):
    days=1 if score<40 else 2 if score<60 else 4 if score<80 else 7
    return (local_day()+timedelta(days=days)).isoformat()

def recommend_for_state(state):
    score=state.get("mastery_score",0)
    topic=state.get("topic","este tema")
    if state.get("status")=="needs_reinforcement" or score<30:
        return dict(action="explain",reason=f"Conviene reconstruir {topic} con una explicación corta y un ejemplo concreto.",priority=.95)
    if score<60:
        return dict(action="guided_practice",reason=f"Tu dominio de {topic} está creciendo; una práctica guiada es el siguiente paso.",priority=.82)
    if score<80:
        return dict(action="interleave",reason=f"Ya tienes base en {topic}; mezclar ejercicios comprobará si eliges bien la estrategia.",priority=.72)
    return dict(action="challenge",reason=f"Tu dominio de {topic} es alto; conviene un reto y dejar una revisión futura.",priority=.62)

def upsert_from_event(db,user_id,subject,topic,event_type,metadata=None):
    metadata=metadata or {}
    row=db.one("SELECT * FROM topic_mastery WHERE user_id=? AND subject=? AND topic=?",(user_id,subject,topic))
    if not row:
        row=dict(user_id=user_id,subject=subject,topic=topic,mastery_score=0,confidence=0,attempts=0,correct_answers=0,incorrect_answers=0,hints_used=0,explanations_requested=0,practice_count=0,quiz_count=0,last_seen=None,next_review=None,difficulty="Normal",status="new")
    if event_type=="question_answered":
        row["attempts"]+=1
        if metadata.get("correct") is True: row["correct_answers"]+=1
        elif metadata.get("correct") is False: row["incorrect_answers"]+=1
    elif event_type=="hint_used":
        row["hints_used"]+=1
    elif event_type in ("topic_practiced","study_session_completed","adventure_completed"):
        row["practice_count"]+=1
    elif event_type in ("quiz_completed","simulation_completed"):
        row["quiz_count"]+=1
    elif event_type=="explanation_requested":
        row["explanations_requested"]+=1
    row["difficulty"]=metadata.get("difficulty",row.get("difficulty") or "Normal")
    row["last_seen"]=datetime.now(timezone.utc).isoformat()
    calculated=compute_mastery(row["attempts"],row["correct_answers"],row["incorrect_answers"],row["hints_used"],row["practice_count"],row["quiz_count"],row["last_seen"],row.get("next_review"),row["difficulty"])
    row["mastery_score"]=calculated["score"];row["confidence"]=calculated["confidence"];row["status"]=calculated["status"];row["next_review"]=next_review_date(calculated["score"])
    db.execute("""INSERT INTO topic_mastery(user_id,subject,topic,mastery_score,confidence,attempts,correct_answers,incorrect_answers,hints_used,explanations_requested,practice_count,quiz_count,last_seen,next_review,difficulty,status)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
      ON CONFLICT(user_id,subject,topic) DO UPDATE SET mastery_score=excluded.mastery_score,confidence=excluded.confidence,attempts=excluded.attempts,correct_answers=excluded.correct_answers,incorrect_answers=excluded.incorrect_answers,hints_used=excluded.hints_used,explanations_requested=excluded.explanations_requested,practice_count=excluded.practice_count,quiz_count=excluded.quiz_count,last_seen=excluded.last_seen,next_review=excluded.next_review,difficulty=excluded.difficulty,status=excluded.status""",
      (user_id,subject,topic,row["mastery_score"],row["confidence"],row["attempts"],row["correct_answers"],row["incorrect_answers"],row["hints_used"],row["explanations_requested"],row["practice_count"],row["quiz_count"],row["last_seen"],row["next_review"],row["difficulty"],row["status"]))
    return db.one("SELECT * FROM topic_mastery WHERE user_id=? AND subject=? AND topic=?",(user_id,subject,topic))

def recommend_next_action(db,user_id):
    rows=db.all("SELECT * FROM topic_mastery WHERE user_id=? ORDER BY CASE status WHEN 'needs_reinforcement' THEN 0 WHEN 'reviewing' THEN 1 WHEN 'learning' THEN 2 WHEN 'practicing' THEN 3 ELSE 4 END, mastery_score ASC, COALESCE(last_seen,'') DESC LIMIT 20",(user_id,))
    if not rows:return None
    row=rows[0]; rec=recommend_for_state(row)
    return dict(subject=row["subject"],topic=row["topic"],mastery=row["mastery_score"],status=row["status"],**rec)
