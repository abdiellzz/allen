from __future__ import annotations
import re

MEASURABLE=("explica","aplica","identifica","compara","distingue","resuelve","analiza","describe","demuestra","clasifica")

def evaluate_course(structure):
    issues=[]; checks=0; passed=0
    units=structure.get("units") or []
    topics=[(ui,ti,t) for ui,u in enumerate(units) for ti,t in enumerate(u.get("topics") or [])]
    checks+=1
    if units and topics: passed+=1
    else: issues.append({"severity":"error","code":"empty_course","message":"El curso no tiene suficientes unidades o temas."})
    sizes=[len(u.get("topics") or []) for u in units]
    if sizes:
        checks+=1
        if max(sizes)-min(sizes)<=4: passed+=1
        else: issues.append({"severity":"warning","code":"unbalanced_units","message":"Las unidades están desbalanceadas en cantidad de temas."})
    prompts=set()
    for ui,ti,t in topics:
        loc=f"Unidad {ui+1} · Tema {ti+1}"
        checks+=1
        if t.get("source") and t.get("source_excerpt"): passed+=1
        else: issues.append({"severity":"error","code":"missing_source","location":loc,"message":"Tema sin fuente verificable."})
        objective=(t.get("objective") or "").lower()
        checks+=1
        if any(v in objective for v in MEASURABLE): passed+=1
        else: issues.append({"severity":"warning","code":"weak_objective","location":loc,"message":"El objetivo no usa un verbo claramente medible."})
        questions=t.get("questions") or []
        checks+=1
        if questions: passed+=1
        else: issues.append({"severity":"error","code":"no_questions","location":loc,"message":"Tema sin preguntas de comprobación."})
        excerpt=t.get("source_excerpt") or ""
        checks+=1
        if len(excerpt)<=500: passed+=1
        else: issues.append({"severity":"warning","code":"long_excerpt","location":loc,"message":"El extracto fuente es demasiado largo."})
        for q in questions:
            prompt=(q.get("prompt") or "").strip().lower()
            if not prompt: continue
            checks+=1
            if prompt in prompts:
                issues.append({"severity":"warning","code":"duplicate_question","location":loc,"message":"Pregunta duplicada en el curso."})
            else:
                prompts.add(prompt); passed+=1
            checks+=1
            if len(prompt)>=18 and not re.search(r"\b(todo|algo|cosa)\b",prompt): passed+=1
            else: issues.append({"severity":"warning","code":"ambiguous_question","location":loc,"message":"Pregunta demasiado corta o ambigua."})
    exam=structure.get("final_exam") or []
    checks+=1
    if exam: passed+=1
    else: issues.append({"severity":"warning","code":"no_final_exam","message":"El curso no tiene examen final."})

    score=round((passed/max(1,checks))*100)
    blocking=sum(1 for i in issues if i["severity"]=="error")
    counts={}
    for issue in issues:
        counts[issue["code"]]=counts.get(issue["code"],0)+1
    breakdown={
        "source_grounding":{
            "ok":sum(1 for _,_,t in topics if t.get("source") and t.get("source_excerpt")),
            "total":len(topics),
        },
        "measurable_objectives":{
            "ok":sum(1 for _,_,t in topics if any(v in (t.get("objective") or "").lower() for v in MEASURABLE)),
            "total":len(topics),
        },
        "assessed_topics":{
            "ok":sum(1 for _,_,t in topics if t.get("questions")),
            "total":len(topics),
        },
        "final_exam":{"ok":1 if exam else 0,"total":1},
        "issue_counts":counts,
    }
    return {
        "score":score,
        "checks":checks,
        "passed":passed,
        "blocking_issues":blocking,
        "issues":issues,
        "breakdown":breakdown,
        "status":"ready" if blocking==0 and score>=80 else "review",
    }

def publication_allowed(report):
    return report["blocking_issues"]==0 and report["score"]>=80
