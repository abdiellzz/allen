from __future__ import annotations
import json, re

def _tokens(text):
    return {w.lower() for w in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{4,}", text or "")}

def build_graph(structure):
    nodes=[]; edges=[]; seen=[]
    for ui,unit in enumerate(structure.get("units",[])):
        for ti,topic in enumerate(unit.get("topics",[])):
            node_id=f"u{ui}:t{ti}"
            node={"id":node_id,"unit_index":ui,"topic_index":ti,"title":topic.get("title",""),"objective":topic.get("objective",""),"source":topic.get("source",{})}
            nodes.append(node)
            if seen:
                prev=seen[-1]
                edges.append({"from":prev["id"],"to":node_id,"relation":"prerequisite","reason":"Orden curricular del material"})
                edges.append({"from":node_id,"to":prev["id"],"relation":"builds_on","reason":"Este tema se apoya en el tema anterior"})
            seen.append(node)
    for i,a in enumerate(nodes):
        ta=_tokens(a["title"]+" "+a["objective"])
        for b in nodes[i+1:]:
            tb=_tokens(b["title"]+" "+b["objective"])
            overlap=ta & tb
            if len(overlap)>=2:
                edges.append({"from":a["id"],"to":b["id"],"relation":"related_to","reason":"Conceptos compartidos: "+", ".join(sorted(overlap)[:4])})
    return {"nodes":nodes,"edges":edges}

def persist_graph(db,course_id,structure):
    graph=build_graph(structure)
    db.execute("DELETE FROM curriculum_edges WHERE course_id=?",(course_id,))
    for edge in graph["edges"]:
        db.execute("INSERT INTO curriculum_edges(course_id,from_node,to_node,relation,reason) VALUES(?,?,?,?,?)",
                   (course_id,edge["from"],edge["to"],edge["relation"],edge["reason"]))
    return graph

def prerequisite_chain(db,course_id,node_id):
    rows=db.all("SELECT from_node,to_node,relation,reason FROM curriculum_edges WHERE course_id=? AND to_node=? AND relation='prerequisite'",(course_id,node_id))
    return rows
