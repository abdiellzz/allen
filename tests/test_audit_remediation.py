import json
import os
import time
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.database import Database, now
from backend.time_utils import local_day_from_iso


def client_for(path: Path, *, teacher_auth=False):
    app = create_app(path, require_license=False, require_local_access=False, require_teacher_auth=teacher_auth)
    client = TestClient(app)
    token = client.get("/api/bootstrap").json()["token"]
    client.headers["X-Allen-Token"] = token
    return app, client, token


def sample_course():
    return {
        "title": "Curso seguro",
        "subject": "Redes",
        "level": "Premedia",
        "units": [
            {
                "title": "Unidad 1",
                "topics": [
                    {
                        "title": "CIDR",
                        "objective": "Explicar y aplicar CIDR",
                        "source": {"page": 1},
                        "source_excerpt": "CIDR usa prefijos.",
                        "route": [
                            {"type": "discover", "title": "Descubre"},
                            {"type": "practice", "title": "Practica"},
                            {"type": "review", "title": "Revisa"},
                        ],
                        "questions": [
                            {
                                "prompt": "¿Qué es CIDR?",
                                "options": ["A", "B", "C"],
                                "correct": "A",
                                "answer_hint": "Mira el prefijo.",
                            }
                        ],
                    }
                ],
            }
        ],
        "final_exam": [
            {
                "topic": "CIDR",
                "prompt": "¿Qué describe CIDR?",
                "options": ["A", "B", "C"],
                "correct": "A",
                "answer_hint": "No debe viajar al estudiante.",
                "source": {"page": 1},
            }
        ],
    }


def seed_published_course(app):
    db = app.state.db
    structure = sample_course()
    cid = db.execute(
        """INSERT INTO courses(owner_profile_id,source_document_id,title,subject,level,status,version,structure_json,created_at,updated_at,published_at)
           VALUES(1,NULL,?,?,?,?,1,?,?,?,?)""",
        (
            structure["title"],
            structure["subject"],
            structure["level"],
            "published",
            json.dumps(structure, ensure_ascii=False),
            now(),
            now(),
            now(),
        ),
    )
    eid = db.execute(
        """INSERT INTO course_enrollments(course_id,user_id,status,unit_index,topic_index,step_index,started_at,updated_at)
           VALUES(?,1,'active',0,0,0,?,?)""",
        (cid, now(), now()),
    )
    return cid, eid, structure


def assert_no_answer_keys(value):
    forbidden = {"correct", "answer", "answer_hint", "explanation"}
    if isinstance(value, dict):
        assert not (forbidden & set(value))
        for child in value.values():
            assert_no_answer_keys(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_answer_keys(child)


def test_student_route_never_exposes_exam_or_answer_keys(tmp_path):
    app, client, _ = client_for(tmp_path / "allen.sqlite3")
    cid, _, _ = seed_published_course(app)

    response = client.get(f"/api/courses/{cid}/route?profile_id=1")

    assert response.status_code == 200
    structure = response.json()["course"]["structure"]
    assert "final_exam" not in structure
    assert_no_answer_keys(structure)
    client.close()


def test_simulations_hide_answers_and_validate_every_requested_topic(tmp_path):
    app, client, _ = client_for(tmp_path / "allen.sqlite3")
    created = client.post(
        "/api/simulations",
        json={
            "profile_id": 1,
            "subject": "Redes",
            "topics": ["IPv4 y CIDR", "DNS y DHCP"],
            "question_count": 4,
            "minutes": 20,
            "timed": True,
            "level": "Premedia",
        },
    )
    assert created.status_code == 200, created.text
    assert_no_answer_keys(created.json()["questions"])

    active = client.get("/api/simulations/active?profile_id=1")
    assert active.status_code == 200
    assert_no_answer_keys(active.json()["questions"])

    invalid = client.post(
        "/api/simulations",
        json={
            "profile_id": 1,
            "subject": "Redes",
            "topics": ["IPv4 y CIDR", "TEMA QUE NO EXISTE"],
            "question_count": 3,
            "minutes": 20,
            "timed": True,
            "level": "Premedia",
        },
    )
    assert invalid.status_code == 422
    client.close()


def test_backup_roundtrip_preserves_conversations_and_rejects_broken_foreign_keys(tmp_path):
    app, client, _ = client_for(tmp_path / "allen.sqlite3")
    db = app.state.db
    cid = db.execute(
        "INSERT INTO conversations(user_id,title,messages,updated) VALUES(1,?,?,?)",
        ("Privada", json.dumps([{"role": "user", "content": "dato privado"}]), now()),
    )
    db.execute(
        "INSERT INTO conversation_states(conversation_id,value) VALUES(?,?)",
        (cid, json.dumps({"mode": "Tutor"})),
    )

    backup = client.get("/api/backup/export?profile_id=1").json()
    assert backup["tables"]["conversations"]
    assert backup["tables"]["conversation_states"]

    db.execute("DELETE FROM conversations WHERE id=?", (cid,))
    restored = client.post("/api/backup/restore", json=backup)
    assert restored.status_code == 200, restored.text
    assert db.one("SELECT title FROM conversations WHERE id=?", (cid,))["title"] == "Privada"

    broken = json.loads(json.dumps(backup))
    broken["tables"]["conversations"][0]["user_id"] = 999999
    rejected = client.post("/api/backup/restore", json=broken)
    assert rejected.status_code == 422
    assert db.one("SELECT title FROM conversations WHERE id=?", (cid,))["title"] == "Privada"
    client.close()


def test_study_plan_deadline_is_bounded_to_one_year(tmp_path):
    _, client, _ = client_for(tmp_path / "allen.sqlite3")
    payload = {
        "profile_id": 1,
        "subject": "Redes",
        "topics": ["CIDR"],
        "deadline": (date.today() + timedelta(days=366)).isoformat(),
        "minutes_per_day": 30,
        "level": "Premedia",
        "goal": "Examen",
    }
    response = client.post("/api/study-plans", json=payload)
    assert response.status_code == 422
    client.close()


def test_course_progress_cannot_jump_or_self_complete(tmp_path):
    app, client, _ = client_for(tmp_path / "allen.sqlite3")
    cid, _, _ = seed_published_course(app)

    jump = client.post(
        f"/api/courses/{cid}/progress",
        json={"profile_id": 1, "unit_index": 0, "topic_index": 0, "step_index": 2, "status": "active"},
    )
    assert jump.status_code == 409

    next_step = client.post(
        f"/api/courses/{cid}/progress",
        json={"profile_id": 1, "unit_index": 0, "topic_index": 0, "step_index": 1, "status": "active"},
    )
    assert next_step.status_code == 200

    forged_complete = client.post(
        f"/api/courses/{cid}/progress",
        json={"profile_id": 1, "unit_index": 0, "topic_index": 0, "step_index": 1, "status": "completed"},
    )
    assert forged_complete.status_code == 409
    client.close()


def test_failed_final_exam_does_not_complete_course(tmp_path):
    app, client, _ = client_for(tmp_path / "allen.sqlite3")
    cid, _, _ = seed_published_course(app)

    response = client.post(
        f"/api/courses/{cid}/exam/submit",
        json={"profile_id": 1, "answers": ["B"]},
    )

    assert response.status_code == 200
    assert response.json()["passed"] is False
    enrollment = app.state.db.one(
        "SELECT status,completed_at FROM course_enrollments WHERE course_id=? AND user_id=1",
        (cid,),
    )
    assert enrollment["status"] == "active"
    assert enrollment["completed_at"] is None
    client.close()


def test_teacher_endpoints_require_server_side_pin_session(tmp_path):
    _, client, token = client_for(tmp_path / "allen.sqlite3", teacher_auth=True)

    blocked = client.get("/api/teacher/analytics?profile_id=1")
    assert blocked.status_code == 403
    assert blocked.json()["teacher_required"] is True

    created = client.post("/api/teacher/auth/setup", json={"pin": "4826"})
    assert created.status_code == 200, created.text
    assert "HttpOnly" in created.headers.get("set-cookie", "")

    allowed = client.get("/api/teacher/analytics?profile_id=1")
    assert allowed.status_code == 200

    client.post("/api/teacher/auth/logout", json={})
    blocked_again = client.get("/api/backup/export?profile_id=1")
    assert blocked_again.status_code == 403
    client.close()


def test_fair_mode_isolated_and_exit_requires_teacher_pin(tmp_path):
    _, client, normal_token = client_for(tmp_path / "allen.sqlite3", teacher_auth=True)
    assert client.post("/api/teacher/auth/setup", json={"pin": "4826"}).status_code == 200

    fair_page = client.get("/fair")
    assert fair_page.status_code == 200

    assert client.get("/api/bootstrap").status_code == 403

    fair_token = client.get("/api/fair/token").json()["token"]
    client.headers["X-Allen-Token"] = fair_token
    wrong = client.post("/api/fair/exit", json={"pin": "1111"})
    assert wrong.status_code == 403

    exited = client.post("/api/fair/exit", json={"pin": "4826"})
    assert exited.status_code == 200

    client.headers["X-Allen-Token"] = normal_token
    assert client.get("/api/bootstrap").status_code == 200
    client.close()


def test_study_time_ping_is_rate_limited(tmp_path):
    app, client, _ = client_for(tmp_path / "allen.sqlite3")
    first = client.post("/api/study", json={"profile_id": 1, "subject": "Redes", "seconds": 30})
    second = client.post("/api/study", json={"profile_id": 1, "subject": "Redes", "seconds": 30})
    assert first.json()["ignored"] is False
    assert second.json()["ignored"] is True
    assert app.state.db.one("SELECT count(*) n FROM learning_sessions WHERE user_id=1")["n"] == 1
    client.close()


@pytest.mark.skipif(not hasattr(time, "tzset"), reason="tzset is unavailable on this platform")
def test_utc_timestamp_maps_to_panama_student_day(monkeypatch):
    previous = os.environ.get("TZ")
    monkeypatch.setenv("TZ", "America/Panama")
    time.tzset()
    try:
        assert local_day_from_iso("2026-10-08T00:30:00+00:00").isoformat() == "2026-10-07"
    finally:
        if previous is None:
            monkeypatch.delenv("TZ", raising=False)
        else:
            monkeypatch.setenv("TZ", previous)
        time.tzset()


def test_database_transaction_rolls_back_and_wal_is_enabled(tmp_path):
    db = Database(tmp_path / "allen.sqlite3")
    with db.connect() as con:
        assert con.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"

    with pytest.raises(RuntimeError):
        with db.transaction():
            db.execute("INSERT INTO users(name,level,avatar) VALUES('Temporal','Premedia','X')")
            raise RuntimeError("rollback")

    assert db.one("SELECT id FROM users WHERE name='Temporal'") is None
