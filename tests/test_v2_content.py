from backend.education import catalog, generate
from backend.schemas import QuizRequest


def test_v2_catalog_includes_new_learning_areas():
    data = catalog()
    for subject in ("Redes", "Ciberseguridad", "IA", "Estudio", "Pensamiento crítico"):
        assert subject in data
        assert data[subject]


def test_v2_network_quiz_generates_locally():
    request = QuizRequest(
        profile_id=1,
        subject="Redes",
        topic="IPv4 y CIDR",
        difficulty="Normal",
        count=3,
        kind="multiple",
    )
    questions = generate(request)
    assert len(questions) == 3
    assert all(q["options"] for q in questions)
    assert all(q["answer"] in q["options"] for q in questions)


def test_v2_security_content_is_defensive_and_educational():
    request = QuizRequest(
        profile_id=1,
        subject="Ciberseguridad",
        topic="Contraseñas y MFA",
        difficulty="Fácil",
        count=3,
        kind="multiple",
    )
    questions = generate(request)
    text = " ".join(q["prompt"] + " " + q["explanation"] for q in questions).lower()
    assert "mfa" in text or "contraseña" in text
    assert "exploit" not in text
    assert "payload" not in text
