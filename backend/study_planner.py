from __future__ import annotations
from datetime import date, datetime, timedelta
from .time_utils import local_day, local_day_iso

TECHNIQUES=("Descubre","Recupera","Explica","Mezcla","Representa","Revisa")

def _parse_deadline(value:str):
    target=datetime.strptime(value,"%Y-%m-%d").date()
    if target < local_day():
        raise ValueError("La fecha objetivo no puede estar en el pasado.")
    return target

def _weak_topics(quiz_rows, topics):
    scores={t:0 for t in topics}
    for row in quiz_rows or []:
        result=row.get("result")
        if isinstance(result,str):
            import json
            try: result=json.loads(result)
            except Exception: result={}
        for topic in result.get("review",[]) if isinstance(result,dict) else []:
            for t in topics:
                if t.lower() in str(topic).lower() or str(topic).lower() in t.lower():
                    scores[t]+=3
    return scores

def _due_topics(cards, topics):
    today=local_day_iso()
    due={t:0 for t in topics}
    for card in cards or []:
        if card.get("due","9999-12-31")<=today:
            text=(str(card.get("question",""))+" "+str(card.get("answer",""))).lower()
            for t in topics:
                if t.lower() in text: due[t]+=1
    return due

def build_plan(subject,topics,deadline,minutes_per_day,level,goal,quiz_rows=None,cards=None,progress=None):
    topics=[t.strip() for t in topics if t and t.strip()]
    if not topics: topics=[subject]
    target=_parse_deadline(deadline)
    days=max(1,(target-local_day()).days+1)
    weak=_weak_topics(quiz_rows,topics); due=_due_topics(cards,topics)
    ranked=sorted(topics,key=lambda t:(weak.get(t,0)+due.get(t,0),-topics.index(t)),reverse=True)
    plan_days=[]
    for i in range(days):
        current=local_day()+timedelta(days=i)
        is_last=current==target
        budget=minutes_per_day
        activities=[]
        if is_last and days>1:
            sim=max(10,min(20,budget//2)); activities.append(dict(type="simulation",topic=subject,minutes=sim,label="Simulacro mixto")); budget-=sim
            if budget>0: activities.append(dict(type="review",topic=ranked[0],minutes=budget,label="Repasar errores y tarjetas difíciles"))
        else:
            topic=ranked[i%len(ranked)]
            chunks=[("explanation","Descubre",max(5,budget//4)),("retrieval","Recupera",max(5,budget//4)),("practice","Mezcla",max(5,budget//4))]
            used=0
            for kind,label,m in chunks:
                if used>=minutes_per_day: break
                m=min(m,minutes_per_day-used); activities.append(dict(type=kind,topic=topic,minutes=m,label=f"{label}: {topic}")); used+=m
            remaining=minutes_per_day-used
            if remaining>0:
                activities.append(dict(type="spaced_review",topic=ranked[(i+1)%len(ranked)],minutes=remaining,label="Revisión espaciada / flashcards"))
        plan_days.append(dict(date=current.isoformat(),activities=activities,status="planned"))
    return dict(subject=subject,goal=goal,deadline=deadline,minutes_per_day=minutes_per_day,level=level,topics=topics,days=plan_days,weak_topics=[t for t in ranked if weak.get(t,0)>0],due_card_topics=[t for t in ranked if due.get(t,0)>0])

def cornell_guide(text,title="Guía Cornell"):
    clean=" ".join(str(text).split())
    sentences=[s.strip() for s in clean.replace("!","." ).replace("?","." ).split(".") if s.strip()]
    main=sentences[:8]
    cues=[f"¿Qué significa o por qué importa: {s[:90]}?" for s in main[:5]]
    summary=" ".join(main[:3])[:500]
    return dict(title=title,cues=cues,notes=main,summary=summary,retrieval_questions=cues[:3])

def study_guide(text,title="Guía de estudio"):
    c=cornell_guide(text,title)
    return dict(title=title,concepts=c["notes"][:5],definitions=[],examples=[],questions=c["retrieval_questions"],common_errors=[],flashcards=[{"question":q,"answer":"Respóndela con tus propias palabras usando los apuntes."} for q in c["retrieval_questions"]],mini_quiz=c["retrieval_questions"][:3],summary=c["summary"])
