"""Regressions for the 2026-10-11 bug hunt: every case reproduced the bug before its fix."""
import base64
import json
import sqlite3
import tempfile
import time
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

import backend.licensing as licensing
from backend.app import create_app
from backend.backup import MAX_BACKUP_BYTES, backup_size, validate_backup
from backend.backup_crypto import encrypt_backup
from backend.course_builder import build_course
from backend.course_quality import evaluate_course
from backend.education import equivalent
from backend.learning_intelligence import diagnostic_questions
from backend.licensing import LicenseError, LicenseManager
from backend.prompts import declared_name
from backend.security import safe_reply
from backend.time_utils import local_day_iso
from tools.license_manager import renew_payload

MATERIAL = ("# Unidad 1: Fundamentos\nCIDR describe prefijos de red y ayuda a interpretar máscaras. IPv4 identifica interfaces de red. "
            "DNS traduce nombres a direcciones IP.\n# Unidad 2: Servicios\nDHCP asigna parámetros de red automáticamente. Un gateway conecta redes diferentes.")
TEMPLATES = ("Según el material,", "El texto indica que", "La fuente no atribuye")


def client(tmp):
    c = TestClient(create_app(Path(tmp) / "allen.sqlite3"), raise_server_exceptions=False)
    c.headers["X-Allen-Token"] = c.get("/api/bootstrap").json()["token"]
    return c


def published_course(c):
    payload = {"profile_id": 1, "title": "Redes", "subject": "Redes", "level": "Premedia", "filename": "redes.md",
               "mime": "text/markdown", "content_base64": base64.b64encode(MATERIAL.encode()).decode()}
    cid = c.post("/api/teacher/import", json=payload).json()["course_id"]
    structure = c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()["structure"]
    assert c.put(f"/api/teacher/courses/{cid}/review", json={"profile_id": 1, "structure": structure}).status_code == 200
    assert c.post(f"/api/teacher/courses/{cid}/publish", json={"profile_id": 1}).status_code == 200
    return cid, c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()["structure"]


def pass_exam(c, cid, structure):
    c.post(f"/api/courses/{cid}/enroll", json={"profile_id": 1})
    result = c.post(f"/api/courses/{cid}/exam/submit", json={"profile_id": 1, "answers": [q["correct"] for q in structure["final_exam"]]})
    assert result.json()["passed"]


def enrollment(c):
    return c.get("/api/courses?profile_id=1").json()[0]["enrollment"]


# --- Child safety and privacy -------------------------------------------------------------------

def test_self_harm_phrases_children_write_are_detected():
    for phrase in ("me quiero morir", "quiero morirme", "me voy a matar", "me quiero matar", "pienso en suicidarme",
                   "ya no quiero estar viva", "Quiero hacerme daño", "no quiero vivir así", "I want to die"):
        assert safe_reply(phrase), phrase
    for phrase in ("¿Qué es el suicidio?", "no quiero vivir lejos de mi escuela", "quiero aprender a cortar fracciones"):
        assert safe_reply(phrase) is None, phrase


def test_deleted_profile_is_purged_from_recovery_snapshots():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        uid = c.post("/api/profiles", json={"name": "NinaPrivada"}).json()["id"]
        c.post("/api/saved", json={"profile_id": uid, "title": "privado", "content": "dato privado"})
        c.app.state.db.create_snapshot("manual")
        assert c.delete(f"/api/profiles/{uid}").status_code == 200
        for snapshot in (Path(tmp) / "recovery").glob("*.sqlite3"):
            con = sqlite3.connect(snapshot)
            try:
                assert con.execute("SELECT count(*) FROM users WHERE id=?", (uid,)).fetchone()[0] == 0
                assert con.execute("SELECT count(*) FROM saved_answers WHERE user_id=?", (uid,)).fetchone()[0] == 0
            finally:
                con.close()


def test_ordinary_sentence_does_not_rename_the_profile():
    assert declared_name("Me llamo Juan y quiero aprender inglés") is None
    assert declared_name("me llamo María de la Cruz") == "María de la Cruz"
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        before = c.get("/api/bootstrap").json()["profiles"][0]["name"]
        c.post("/api/chat", json={"profile_id": 1, "message": "Me llamo Juan y quiero aprender inglés"})
        assert c.get("/api/bootstrap").json()["profiles"][0]["name"] == before


# --- Assessment integrity -----------------------------------------------------------------------

def test_checked_quiz_answers_are_locked_for_submission():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        quiz = c.post("/api/quiz", json={"profile_id": 1, "subject": "Ciencias", "topic": "Sistema Solar", "count": 3, "kind": "multiple"}).json()
        keys = [c.post(f"/api/quiz/{quiz['id']}/answer", json={"profile_id": 1, "index": i, "answer": "x"}).json()["answer"] for i in range(3)]
        result = c.post(f"/api/quiz/{quiz['id']}/submit", json={"profile_id": 1, "answers": keys}).json()
        assert result["score"] == 0


def test_diagnostic_differs_from_final_exam_and_is_taken_once():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        cid, structure = published_course(c)
        c.post(f"/api/courses/{cid}/enroll", json={"profile_id": 1})
        diagnostic = c.get(f"/api/courses/{cid}/diagnostic?profile_id=1").json()["questions"]
        exam = c.get(f"/api/courses/{cid}/exam?profile_id=1").json()["questions"]
        assert not {q["prompt"] for q in diagnostic} & {q["prompt"] for q in exam}
        answers = [q["correct"] for q in diagnostic_questions(structure, 7)]
        assert c.post(f"/api/courses/{cid}/diagnostic/submit", json={"profile_id": 1, "answers": answers}).status_code == 200
        assert c.post(f"/api/courses/{cid}/diagnostic/submit", json={"profile_id": 1, "answers": answers}).status_code == 409
        assert c.get(f"/api/courses/{cid}/diagnostic?profile_id=1").status_code == 409


def test_exam_key_is_not_given_away_by_template_distractors():
    structure = build_course("Redes", "Redes", "Premedia", [{"page": 1, "text": MATERIAL}], MATERIAL)
    for question in structure["final_exam"]:
        assert not any(option.startswith(TEMPLATES) for option in question["options"]), question["options"]
        assert len(set(question["options"])) == len(question["options"]) >= 3
    report = evaluate_course(structure)
    assert report["blocking_issues"] == 0 and report["score"] >= 80


# --- Progress -----------------------------------------------------------------------------------

def test_reviewing_a_passed_course_keeps_it_completed():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        cid, structure = published_course(c)
        pass_exam(c, cid, structure)
        completed_at = enrollment(c)["completed_at"]
        r = c.post(f"/api/courses/{cid}/progress", json={"profile_id": 1, "unit_index": 0, "topic_index": 0, "step_index": 1, "status": "active"})
        assert r.status_code == 200
        assert enrollment(c)["status"] == "completed" and enrollment(c)["completed_at"] == completed_at


def test_course_exam_with_more_than_ten_questions_can_be_submitted():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        _, structure = published_course(c)
        big = json.loads(json.dumps(structure))
        big["final_exam"] = [dict(q, prompt=f"Pregunta {i}: {q['prompt']}") for i, q in enumerate((structure["final_exam"] * 3)[:12])]
        pid = c.post("/api/teacher/packs/import", json={"profile_id": 1, "pack": {"format": "allen-course-pack", "version": 1, "course": big}}).json()["course_id"]
        full = c.get(f"/api/teacher/courses/{pid}?profile_id=1").json()["structure"]
        c.put(f"/api/teacher/courses/{pid}/review", json={"profile_id": 1, "structure": full})
        assert c.post(f"/api/teacher/courses/{pid}/publish", json={"profile_id": 1}).status_code == 200
        c.post(f"/api/courses/{pid}/enroll", json={"profile_id": 1})
        result = c.post(f"/api/courses/{pid}/exam/submit", json={"profile_id": 1, "answers": [q["correct"] for q in full["final_exam"]]})
        assert result.status_code == 200 and result.json()["total"] == 12 and result.json()["passed"]


def test_new_course_version_keeps_students_who_already_passed():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        cid, structure = published_course(c)
        pass_exam(c, cid, structure)
        changed = MATERIAL.replace("Un gateway conecta redes diferentes.", "Un gateway conecta redes diferentes y aplica rutas.")
        r = c.post(f"/api/teacher/courses/{cid}/versions", json={"profile_id": 1, "filename": "redes.md", "mime": "text/markdown",
                                                                 "content_base64": base64.b64encode(changed.encode()).decode()})
        assert r.status_code == 200
        row = c.app.state.db.one("SELECT status,completed_at FROM course_enrollments WHERE course_id=?", (cid,))
        assert row["status"] == "completed" and row["completed_at"]


def test_editing_a_published_course_publishes_a_new_version_without_hiding_it():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        cid, structure = published_course(c)
        c.post(f"/api/courses/{cid}/enroll", json={"profile_id": 1})
        edited = json.loads(json.dumps(structure))
        edited["units"][0]["topics"][0]["objective"] = "Explica cómo CIDR describe prefijos de red con un ejemplo."
        r = c.put(f"/api/teacher/courses/{cid}/review", json={"profile_id": 1, "structure": edited})
        assert r.status_code == 200 and r.json()["published"] and r.json()["version"] == 2
        assert c.get(f"/api/courses/{cid}/route?profile_id=1").status_code == 200
        history = {v["version_number"]: v["status"] for v in c.get(f"/api/teacher/courses/{cid}/versions?profile_id=1").json()}
        assert history == {1: "published", 2: "published"}
        v1 = c.app.state.db.one("SELECT structure_json FROM course_versions WHERE course_id=? AND version_number=1", (cid,))
        assert json.loads(v1["structure_json"])["units"][0]["topics"][0]["objective"] == structure["units"][0]["topics"][0]["objective"]
        weak = json.loads(json.dumps(edited)); weak["final_exam"] = []
        for topic in weak["units"][0]["topics"]:
            topic["questions"] = []
        assert c.put(f"/api/teacher/courses/{cid}/review", json={"profile_id": 1, "structure": weak}).status_code == 409
        assert c.app.state.db.one("SELECT status,version FROM courses WHERE id=?", (cid,)) == {"status": "published", "version": 2}


def test_completed_study_session_is_not_reopened_by_a_pause():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        plan = c.post("/api/study-plans", json={"profile_id": 1, "subject": "Matemáticas", "topics": ["Fracciones"], "deadline": local_day_iso(),
                                                "minutes_per_day": 20, "goal": "Repasar"}).json()
        session = c.post(f"/api/study-plans/{plan['id']}/start?profile_id=1").json()
        url = f"/api/study-sessions/{session['id']}/event"
        c.post(url, json={"profile_id": 1, "kind": "completed", "activity_index": 0})
        assert c.post(url, json={"profile_id": 1, "kind": "paused", "activity_index": 0}).json()["status"] == "completed"
        assert c.get("/api/continuity?profile_id=1").json()["current_activity"] is None


# --- Backups ------------------------------------------------------------------------------------

def test_every_exportable_backup_is_restorable():
    def payload(size):
        rows = []
        data = {"format": "allen-backup", "version": 1, "tables": {"saved_answers": rows}}
        while backup_size(data) < size:
            rows.extend({"id": len(rows) + i, "user_id": 1, "title": "t", "content": "x" * 990, "created": "2026-01-01"} for i in range(500))
        return data
    for size in (5_200_000, MAX_BACKUP_BYTES - 600_000):
        data = payload(size)
        assert backup_size(data) <= MAX_BACKUP_BYTES
        encrypt_backup(data, "contraseña-segura")
        validate_backup(data)
    too_big = payload(MAX_BACKUP_BYTES + 200_000)
    assert backup_size(too_big) > MAX_BACKUP_BYTES
    for action in (lambda: encrypt_backup(too_big, "contraseña-segura"), lambda: validate_backup(too_big)):
        try:
            action()
        except ValueError:
            continue
        raise AssertionError("se aceptó un respaldo por encima del límite")


def test_encrypted_backup_export_rejects_invalid_profile_cleanly():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        r = c.post("/api/backup/export-encrypted", json={"profile_id": "uno", "password": "contraseña-segura"})
        assert r.status_code == 422


# --- Robustness and dates -----------------------------------------------------------------------

def test_scientific_notation_answer_is_graded_instantly():
    started = time.monotonic()
    assert equivalent("1e10000000", "5") is False
    assert time.monotonic() - started < 0.5
    assert equivalent("0,5", "1/2") and equivalent(" 7 ", "7") and not equivalent("1/0", "5")


def test_malformed_course_pack_is_rejected_and_analytics_survive_legacy_data():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        _, structure = published_course(c)
        bad = json.loads(json.dumps(structure)); bad["final_exam"] = ["texto suelto"]
        r = c.post("/api/teacher/packs/import", json={"profile_id": 1, "pack": {"format": "allen-course-pack", "version": 1, "course": bad}})
        assert r.status_code == 422
        # A course stored before the stricter validation must not take Teacher Analytics down.
        c.app.state.db.execute("UPDATE courses SET structure_json=? WHERE id=1", (json.dumps(bad),))
        assert c.get("/api/teacher/analytics?profile_id=1").status_code == 200


def test_reviews_marked_by_a_new_version_use_the_local_day():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        c = client(tmp)
        cid, structure = published_course(c)
        pass_exam(c, cid, structure)
        topic = structure["units"][0]["topics"][0]["title"]
        changed = MATERIAL.replace("CIDR describe prefijos de red y ayuda a interpretar máscaras.",
                                   "CIDR describe prefijos de red, ayuda a interpretar máscaras y resume rutas.")
        c.post(f"/api/teacher/courses/{cid}/versions", json={"profile_id": 1, "filename": "redes.md", "mime": "text/markdown",
                                                         "content_base64": base64.b64encode(changed.encode()).decode()})
        rows = c.app.state.db.all("SELECT next_review FROM topic_mastery WHERE topic=? AND status='reviewing'", (topic,))
        assert all(row["next_review"] == local_day_iso() for row in rows)
        stamps = [row["created_at"] for row in c.app.state.db.all("SELECT created_at FROM course_versions WHERE course_id=?", (cid,))]
        assert all("T" in stamp for stamp in stamps), stamps


# --- Licensing ----------------------------------------------------------------------------------

def license_manager(tmp_path, monkeypatch):
    key = Ed25519PrivateKey.generate()
    public = tmp_path / "public.pem"
    public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    monkeypatch.setattr(licensing, "machine_id", lambda: "ABCD-1234-EF56-7890-ABCD-1234")
    return LicenseManager(tmp_path / "data", public), key


def license_document(key, **changes):
    payload = {"schema": 1, "license_id": "ALLEN-TEST123456", "customer": "Cliente", "plan": "Institution",
               "machine_id": "ABCD-1234-EF56-7890-ABCD-1234", "valid_from": "2026-10-01", "valid_until": "2026-12-31",
               "issued_at": "2026-10-01", "renewal_number": 1, "unlimited_profiles": True, **changes}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return json.dumps({"payload": payload, "signature": base64.b64encode(key.sign(canonical)).decode()})


def test_reinstalling_a_license_does_not_reset_clock_rollback_protection(tmp_path, monkeypatch):
    manager, key = license_manager(tmp_path, monkeypatch)
    manager.install(license_document(key), today=date(2026, 11, 20))
    for document in (license_document(key), license_document(key, license_id="ALLEN-OTHER00001")):
        try:
            manager.install(document, today=date(2026, 10, 10))
        except LicenseError:
            pass
        else:
            raise AssertionError("se instaló con el reloj atrasado")
    assert manager.status(today=date(2026, 10, 10))["state"] == "clock_rollback"


def test_damaged_license_file_does_not_block_a_new_one(tmp_path, monkeypatch):
    manager, key = license_manager(tmp_path, monkeypatch)
    manager.license_dir.mkdir(parents=True)
    manager.license_path.write_text("{dañado", encoding="utf-8")
    assert manager.install(license_document(key), today=date(2026, 10, 10))["active"]


def test_license_manager_never_issues_a_renewal_allen_rejects():
    existing = {"license_id": "ALLEN-TEST123456", "customer": "Cliente", "plan": "Institution", "machine_id": "ABCD-1234-EF56-7890-ABCD-1234",
                "valid_from": "2020-01-01", "valid_until": "2027-01-01", "renewal_number": 3}
    renewed = renew_payload(existing, 365, today=date(2026, 10, 10))
    span = (date.fromisoformat(renewed["valid_until"]) - date.fromisoformat(renewed["valid_from"])).days
    assert span <= 3660 and renewed["valid_until"] == "2028-01-01"
    try:
        renew_payload(dict(existing, valid_until="2036-01-01"), 3660, today=date(2026, 10, 10))
    except ValueError:
        return
    raise AssertionError("emitió una licencia de más de 3660 días")
