from __future__ import annotations
import base64
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

MAX_BYTES=8_000_000
MAX_TEXT=220_000

def _clean(text:str)->str:
    text=text.replace("\x00"," ")
    text=re.sub(r"[ \t]+"," ",text)
    text=re.sub(r"\n{3,}","\n\n",text)
    return text.strip()

def decode_source(filename:str,mime:str,content_base64:str):
    try:
        raw=base64.b64decode(content_base64,validate=True)
    except Exception as exc:
        raise ValueError('El archivo no tiene un formato válido.') from exc
    if len(raw)>MAX_BYTES:
        raise ValueError("El archivo supera el límite local de 8 MB.")
    ext=Path(filename).suffix.lower()
    pages=[]
    if ext==".pdf" or mime=="application/pdf":
        try:
            reader=PdfReader(io.BytesIO(raw))
        except Exception as exc:
            raise ValueError('No pudimos abrir este PDF.') from exc
        if len(reader.pages)>250:
            raise ValueError("El PDF tiene demasiadas páginas para esta versión.")
        for idx,page in enumerate(reader.pages,1):
            text=_clean(page.extract_text() or "")
            if text:
                pages.append({"page":idx,"text":text})
    elif ext in (".txt",".md") or mime in ("text/plain","text/markdown"):
        text=_clean(raw.decode("utf-8","replace"))
        pages=[{"page":1,"text":text}]
    else:
        raise ValueError("Formato no compatible. Usa PDF, TXT o Markdown.")
    joined="\n\n".join(p["text"] for p in pages)
    if len(joined)>MAX_TEXT:
        joined=joined[:MAX_TEXT]
        pages=_truncate_pages(pages,MAX_TEXT)
    if len(joined)<80:
        raise ValueError("No pudimos extraer suficiente texto del archivo.")
    return {"pages":pages,"text":joined,"bytes":len(raw),"page_count":len(pages)}

def _truncate_pages(pages,limit):
    out=[]; used=0
    for page in pages:
        left=limit-used
        if left<=0: break
        text=page["text"][:left]
        out.append({"page":page["page"],"text":text})
        used+=len(text)
    return out

def _heading_candidates(text:str):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    heads=[]
    for line in lines:
        plain=re.sub(r"^[#\-*\d.() ]+","",line).strip()
        if 3<=len(plain)<=90 and (
            line.startswith("#") or
            re.match(r"^(unidad|tema|cap[ií]tulo|m[oó]dulo|lecci[oó]n|parte)\b",plain,re.I) or
            (plain.isupper() and len(plain.split())<=9)
        ):
            if plain.lower() not in {h.lower() for h in heads}: heads.append(plain.title())
        if len(heads)>=12: break
    return heads

def _sentences(text:str):
    parts=re.split(r"(?<=[.!?])\s+",re.sub(r"\s+"," ",text))
    return [p.strip() for p in parts if 25<=len(p.strip())<=320]

def _keywords(text:str,limit=12):
    words=re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{5,}",text.lower())
    stop={"sobre","entre","desde","hasta","donde","cuando","porque","para","como","este","esta","estos","estas","puede","pueden","tambien","también","tener","tiene","cada","según","segun","ser","son","una","unos","unas","del","las","los","por","con"}
    freq={}
    for w in words:
        if w in stop: continue
        freq[w]=freq.get(w,0)+1
    return [w for w,_ in sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:limit]]

def _source_ref(pages,needle):
    low=needle.lower()
    for p in pages:
        if low[:36] and low[:36] in p["text"].lower():
            return {"page":p["page"]}
    return {"page":pages[0]["page"] if pages else 1}

def build_course(title:str,subject:str,level:str,pages:list[dict],source_text:str):
    headings=_heading_candidates(source_text)
    sentences=_sentences(source_text)
    keywords=_keywords(source_text,16)
    if not headings:
        headings=[f"Unidad {i+1}: {kw.title()}" for i,kw in enumerate(keywords[:min(6,max(2,len(keywords)))])]
    unit_count=min(8,max(1,len(headings)))
    units=[]
    cursor=0
    for idx,heading in enumerate(headings[:unit_count]):
        sample=sentences[cursor:cursor+5] or sentences[:5]
        cursor+=5
        topic_names=[]
        for s in sample:
            terms=_keywords(s,2)
            if terms:
                name=" ".join(t.title() for t in terms[:2])
                if name not in topic_names: topic_names.append(name)
        if not topic_names:
            topic_names=[heading]
        topics=[]
        for topic in topic_names[:4]:
            evidence=next((x for x in sample if any(k in x.lower() for k in topic.lower().split())),sample[0] if sample else source_text[:300])
            ref=_source_ref(pages,evidence)
            objective=f"Explicar y aplicar {topic.lower()} usando el material del curso."
            topics.append({
                "title":topic,
                "objective":objective,
                "source":ref,
                "source_excerpt":evidence[:360],
                "route":[
                    {"type":"discover","label":"Descubre","minutes":8},
                    {"type":"example","label":"Mira un ejemplo","minutes":7},
                    {"type":"retrieval","label":"Recuerda sin mirar","minutes":6},
                    {"type":"practice","label":"Practica","minutes":10},
                    {"type":"quiz","label":"Comprueba","minutes":8},
                    {"type":"review","label":"Revisa después","minutes":5},
                ],
                "flashcards":[
                    {"question":f"¿Cómo explicarías {topic} con tus palabras?","answer":evidence[:240],"source":ref}
                ],
                "questions":[
                    {"prompt":f"Explica la idea principal de {topic}.","answer_hint":evidence[:220],"source":ref},
                    {"prompt":f"¿Qué ejemplo del material ayuda a entender {topic}?","answer_hint":"Busca un ejemplo en la fuente y justifica tu elección.","source":ref}
                ]
            })
        units.append({"title":heading,"topics":topics})
    flat_topics=[t for u in units for t in u["topics"]]
    final_exam=[]
    for idx,topic in enumerate(flat_topics[:10]):
        correct=topic.get("source_excerpt","")[:220]
        distractors=[]
        for other in flat_topics:
            candidate=other.get("source_excerpt","")[:220]
            if other is not topic and candidate and candidate!=correct and candidate not in distractors:
                distractors.append(candidate)
            if len(distractors)>=3: break
        fallbacks=[
            "El material no presenta esta idea como definición del tema.",
            "Esta afirmación pertenece a otro concepto y no describe este tema.",
            "No hay evidencia suficiente en la fuente para sostener esta afirmación.",
        ]
        for fallback in fallbacks:
            if len(distractors)>=3: break
            if fallback not in distractors and fallback!=correct: distractors.append(fallback)
        options=[correct]+distractors[:3]
        # Rotate deterministically so the correct answer is not always first.
        shift=idx%len(options)
        options=options[shift:]+options[:shift]
        final_exam.append({
            "topic":topic["title"],
            "prompt":f"¿Cuál afirmación describe mejor {topic['title']} según el material del curso?",
            "options":options,
            "correct":correct,
            "source":topic.get("source",{}),
        })
    coverage={
        "units":len(units),
        "topics":sum(len(u["topics"]) for u in units),
        "questions":sum(len(t["questions"]) for u in units for t in u["topics"]),
        "flashcards":sum(len(t["flashcards"]) for u in units for t in u["topics"]),
        "exam_questions":len(final_exam),
        "topics_without_questions":sum(1 for u in units for t in u["topics"] if not t["questions"]),
    }
    return {
        "title":title,
        "subject":subject,
        "level":level,
        "version":1,
        "status":"draft",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "keywords":keywords,
        "units":units,
        "final_exam":final_exam,
        "coverage":coverage,
        "method":"Allen: Descubre → Recupera → Explica → Mezcla → Representa → Revisa",
    }

def course_pack(course:dict,document:dict):
    return {
        "format":"allen-course-pack",
        "version":1,
        "course":course,
        "source":{
            "title":document.get("title"),
            "filename":document.get("filename"),
            "page_count":document.get("page_count"),
        }
    }

def validate_course_structure(structure:dict):
    if not isinstance(structure,dict): raise ValueError("Curso no válido.")
    units=structure.get("units")
    if not isinstance(units,list) or not units: raise ValueError("El curso debe tener al menos una unidad.")
    for unit in units:
        if not unit.get("title") or not isinstance(unit.get("topics"),list): raise ValueError("Unidad incompleta.")
        for topic in unit["topics"]:
            if not topic.get("title") or not topic.get("objective"): raise ValueError("Tema incompleto.")
    return True
