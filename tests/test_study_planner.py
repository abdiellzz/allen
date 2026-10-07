from datetime import date, timedelta
from backend.study_planner import build_plan, cornell_guide, study_guide

def future(days=4):
    return (date.today()+timedelta(days=days)).isoformat()

def test_plan_distributes_content_and_reserves_exam_review():
    plan=build_plan("Redes",["IPv4","Subnetting","DNS"],future(3),40,"Universidad / Técnico","Examen")
    assert len(plan["days"])==4
    assert all(sum(a["minutes"] for a in day["activities"])==40 for day in plan["days"])
    assert plan["days"][-1]["activities"][0]["type"]=="simulation"

def test_plan_prioritizes_weak_topic():
    quiz=[{"result":{"review":["Subnetting"]}}]
    plan=build_plan("Redes",["IPv4","Subnetting"],future(2),30,"Premedia","Repaso",quiz_rows=quiz)
    first=plan["days"][0]["activities"][0]
    assert first["topic"]=="Subnetting"
    assert "Subnetting" in plan["weak_topics"]

def test_plan_considers_due_flashcards():
    cards=[{"question":"¿Qué es DNS?","answer":"Resolución de nombres","due":date.today().isoformat()}]
    plan=build_plan("Redes",["IPv4","DNS"],future(2),30,"Premedia","Examen",cards=cards)
    assert "DNS" in plan["due_card_topics"]

def test_cornell_and_study_guides_are_deterministic_offline():
    text="DNS traduce nombres de dominio a direcciones IP. DHCP asigna parámetros de red. Un router conecta redes distintas."
    cornell=cornell_guide(text,"Redes")
    guide=study_guide(text,"Redes")
    assert cornell["cues"] and cornell["notes"] and cornell["summary"]
    assert guide["questions"] and guide["flashcards"] and guide["mini_quiz"]
