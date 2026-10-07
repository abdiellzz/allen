from __future__ import annotations
import json
from .database import now
from .learning_engine import upsert_from_event

ALLOWED={"lesson_started","lesson_completed","question_answered","quiz_completed","hint_used","topic_practiced","adventure_completed","simulation_completed","flashcard_reviewed","study_session_completed","explanation_requested"}

def record_event(db,user_id,event_type,subject="",topic="",reference_type="",reference_id=None,metadata=None):
    if event_type not in ALLOWED: raise ValueError("Evento educativo no válido.")
    clean=dict(metadata or {})
    # Never persist arbitrary long prompt/answer text in the central event log.
    for key in list(clean):
        if key in ("prompt","message","content","answer_text"): clean.pop(key,None)
    payload=json.dumps(clean,ensure_ascii=False)[:4000]
    eid=db.execute("INSERT INTO learning_events(user_id,event_type,subject,topic,reference_type,reference_id,metadata_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (user_id,event_type,subject[:80],topic[:120],reference_type[:40],reference_id,payload,now()))
    if subject and topic:
        mastery=upsert_from_event(db,user_id,subject,topic,event_type,clean)
    else: mastery=None
    return dict(id=eid,mastery=mastery)
