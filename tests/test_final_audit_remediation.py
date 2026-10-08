from pathlib import Path

from backend.library import Library
from backend.course_builder import build_course
from backend.course_quality import evaluate_course


def test_library_documents_are_cached_until_files_change(tmp_path, monkeypatch):
    root=tmp_path/"library"
    root.mkdir()
    source=root/"one.md"
    source.write_text("# Redes\nDNS traduce nombres.",encoding="utf-8")
    lib=Library(root)
    first=lib.documents()
    assert len(first)==1

    original=Path.read_text
    calls={"n":0}
    def counted(self,*args,**kwargs):
        calls["n"]+=1
        return original(self,*args,**kwargs)
    monkeypatch.setattr(Path,"read_text",counted)
    second=lib.documents()
    assert second==first
    assert calls["n"]==0


def test_course_quality_flags_generic_objective_and_cross_topic_distractor():
    structure={
        "units":[{"title":"U1","topics":[
            {"title":"DNS","objective":"Explicar y aplicar dns usando el material del curso.","source":{"page":1},"source_excerpt":"DNS traduce nombres.","questions":[{"prompt":"Explica cómo funciona DNS en una red real."}]},
            {"title":"DHCP","objective":"Identificar DHCP y justificar la respuesta con evidencia del material del curso.","source":{"page":2},"source_excerpt":"DHCP asigna parámetros.","questions":[{"prompt":"Describe cómo DHCP asigna parámetros de red."}]},
        ]}],
        "final_exam":[
            {"topic":"DNS","prompt":"Q1","options":["DNS traduce nombres.","DHCP asigna parámetros.","No aplica"],"correct":"DNS traduce nombres."},
            {"topic":"DHCP","prompt":"Q2","options":["DHCP asigna parámetros.","Otra","Ninguna"],"correct":"DHCP asigna parámetros."},
        ],
    }
    report=evaluate_course(structure)
    codes={x["code"] for x in report["issues"]}
    assert "generic_objective" in codes
    assert "cross_topic_distractor" in codes


def test_generated_exam_does_not_reuse_other_correct_answers_as_distractors():
    pages=[{"page":1,"text":"# DNS\nDNS traduce nombres de dominio a direcciones IP.\n# DHCP\nDHCP asigna parámetros de red automáticamente."}]
    course=build_course("Redes","Redes","Universidad",pages,pages[0]["text"])
    exam=course["final_exam"]
    correct={q["correct"] for q in exam}
    for q in exam:
        wrong=[x for x in q["options"] if x!=q["correct"]]
        assert not (set(wrong)&correct)
