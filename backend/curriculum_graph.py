from __future__ import annotations
import re

STOPWORDS={"para","como","este","esta","estos","estas","sobre","desde","entre","tambien","también","tema","curso","unidad","explica","aplica","identifica","describe"}

def _tokens(text):
    return {w.lower() for w in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{4,}", text or "") if w.lower() not in STOPWORDS}

def _mentions(previous,current):
    prev=_tokens(previous.get("title",""))
    current_text=_tokens(current.get("title","")+" "+current.get("objective",""))
    return bool(prev and prev & current_text)

def build_graph(structure):
    nodes=[]; edges=[]; previous=None
    for ui,unit in enumerate(structure.get("units",[])):
        for ti,topic in enumerate(unit.get("topics",[])):
            node_id=f"u{ui}:t{ti}"
            node={"id":node_id,"unit_index":ui,"topic_index":ti,"title":topic.get("title",""),"objective":topic.get("objective",""),"source":topic.get("source",{})}
            nodes.append(node)
            if previous:
                # Sequence implies progression, but not automatically a hard prerequisite.
                edges.append({"from":node_id,"to":previous["id"],"relation":"builds_on","reason":"Progresión definida por el orden del curso"})
                if _mentions(previous,node):
                    edges.append({"from":previous["id"],"to":node_id,"relation":"prerequisite","reason":"El tema actual reutiliza explícitamente conceptos del tema anterior"})
            previous=node
    for i,a in enumerate(nodes):
        ta=_tokens(a["title"]+" "+a["objective"])
        for b in nodes[i+1:]:
            tb=_tokens(b["title"]+" "+b["objective"])
            overlap=ta & tb
            if len(overlap)>=2:
                edges.append({"from":a["id"],"to":b["id"],"relation":"related_to","reason":"Conceptos compartidos: "+", ".join(sorted(overlap)[:4])})
    # Stable de-duplication keeps the graph deterministic.
    unique=[]; seen=set()
    for edge in edges:
        key=(edge["from"],edge["to"],edge["relation"])
        if key not in seen:
            seen.add(key); unique.append(edge)
    return {"nodes":nodes,"edges":unique}

def persist_graph(db,course_id,structure):
    graph=build_graph(structure)
    db.execute("DELETE FROM curriculum_edges WHERE course_id=?",(course_id,))
    for edge in graph["edges"]:
        db.execute("INSERT INTO curriculum_edges(course_id,from_node,to_node,relation,reason) VALUES(?,?,?,?,?)",
                   (course_id,edge["from"],edge["to"],edge["relation"],edge["reason"]))
    return graph

def prerequisite_chain(db,course_id,node_id):
    return db.all("SELECT from_node,to_node,relation,reason FROM curriculum_edges WHERE course_id=? AND to_node=? AND relation='prerequisite'",(course_id,node_id))
