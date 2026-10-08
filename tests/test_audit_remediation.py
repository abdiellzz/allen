import json
import time
from datetime import date, timedelta

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.backup import export_backup, restore_backup
from backend.backup_crypto import encrypt_backup, decrypt_backup
from backend.database import Database
from backend.schemas import StudyPlanCreate
from backend.time_utils import local_day_from_timestamp


def client_for(tmp_path, *, teacher=False):
    app=create_app(
        tmp_path / "allen.sqlite3",
        require_license=False,
        require_local_access=False,
        require_teacher_auth=teacher,
    )
    client=TestClient(app)
    token=client.get("/api/bootstrap").json()["token"]
    client.headers["X-Allen-Token"]=token
    return app,client


def test_study_plan_deadline_is_limited_to_one_year(tmp_path):
    _,client=client_for(tmp_path)
    payload={
        "profile_id":1,
        "subject":"Redes",
        "topics":["IPv4"],
        "deadline":(date.today()+timedelta(days=366)).isoformat(),
        "minutes_per_day":30,
        "level":"Premedia",
        "goal":"Practicar redes",
    }
    response=client.post("/api/study-plans",json=payload)
    assert response.status_code==422
    client.close()


def test_student_course_route_never_contains_assessment_secrets(tmp_path):
    app,client=client_for(tmp_path)
    structure={
        "units":[{"title":"U1","topics":[{"title":"DNS","route":[{"type":"practice","prompt":"Pregunta","correct":"SECRETO","answer_hint":"PISTA"}]}]}],
        "final_exam":[{"topic":"DNS","prompt":"Final","options":["A","B"],"correct":"A","answer_hint":"A"}],
    }
    cid=app.state.db.execute(
        "INSERT INTO courses(owner_profile_id,title,subject,level,status,version,structure_json,created_at,updated_at) VALUES(1,'Curso','Redes','Premedia','published',1,?,?,?)",
        (json.dumps(structure), "2026-10-08T00:00:00+00:00","2026-10-08T00:00:00+00:00"),
    )
    app.state.db.execute(
        "INSERT INTO course_enrollments(course_id,user_id,status,unit_index,topic_index,step_index,started_at,updated_at) VALUES(?,1,'active',0,0,0,?,?)",
        (cid,"2026-10-08T00:00:00+00:00","2026-10-08T00:00:00+00:00"),
    )
    response=client.get(f"/api/courses/{cid}/route?profile_id=1")
    assert response.status_code==200
    encoded=json.dumps(response.json())
    assert "final_exam" not in encoded
    assert '"correct"' not in encoded
    assert "answer_hint" not in encoded
    client.close()


def test_backup_roundtrip_replaces_conversations_instead_of_mixing_profiles(tmp_path):
    path=tmp_path/"allen.sqlite3"
    db=Database(path)
    cid=db.execute("INSERT INTO conversations(user_id,title,messages,updated) VALUES(1,'Original','[]','2026-10-08T00:00:00+00:00')")
    db.execute("INSERT INTO conversation_states(conversation_id,value) VALUES(?,?)",(cid,'{"mode":"learn"}'))
    backup=export_backup(db)
    assert backup["tables"]["conversations"]
    assert backup["tables"]["conversation_states"]

    db.execute("DELETE FROM conversation_states")
    db.execute("DELETE FROM conversations")
    db.execute("INSERT INTO conversations(user_id,title,messages,updated) VALUES(1,'STale','[]','2026-10-08T01:00:00+00:00')")
    restore_backup(db,backup)

    rows=db.all("SELECT title FROM conversations ORDER BY id")
    assert rows==[{"title":"Original"}]
    assert db.one("SELECT value FROM conversation_states WHERE conversation_id=?",(cid,))["value"]=='{"mode":"learn"}'


def test_teacher_routes_require_server_side_pin_session(tmp_path):
    _,client=client_for(tmp_path,teacher=True)
    blocked=client.get("/api/teacher/analytics?profile_id=1")
    assert blocked.status_code==403
    assert blocked.json()["teacher_auth_required"] is True

    setup=client.post("/api/teacher/security/setup",json={"pin":"123456"})
    assert setup.status_code==200
    allowed=client.get("/api/teacher/analytics?profile_id=1")
    assert allowed.status_code==200

    client.post("/api/teacher/security/lock",json={})
    assert client.get("/api/teacher/analytics?profile_id=1").status_code==403
    unlock=client.post("/api/teacher/security/unlock",json={"pin":"123456"})
    assert unlock.status_code==200
    assert client.get("/api/teacher/analytics?profile_id=1").status_code==200
    client.close()


def test_course_progress_cannot_jump_or_self_complete(tmp_path):
    app,client=client_for(tmp_path)
    structure={"units":[{"title":"U","topics":[{"title":"T","route":[{"type":"discover"},{"type":"practice"},{"type":"check"}]}]}],"final_exam":[{"topic":"T","prompt":"Q","options":["A","B"],"correct":"A"}]}
    cid=app.state.db.execute(
        "INSERT INTO courses(owner_profile_id,title,subject,level,status,version,structure_json,created_at,updated_at) VALUES(1,'Curso','Redes','Premedia','published',1,?,?,?)",
        (json.dumps(structure),"2026-10-08T00:00:00+00:00","2026-10-08T00:00:00+00:00"),
    )
    app.state.db.execute(
        "INSERT INTO course_enrollments(course_id,user_id,status,unit_index,topic_index,step_index,started_at,updated_at) VALUES(?,1,'active',0,0,0,?,?)",
        (cid,"2026-10-08T00:00:00+00:00","2026-10-08T00:00:00+00:00"),
    )
    jump=client.post(f"/api/courses/{cid}/progress",json={"profile_id":1,"unit_index":0,"topic_index":0,"step_index":2,"status":"active"})
    assert jump.status_code==409
    fake_complete=client.post(f"/api/courses/{cid}/progress",json={"profile_id":1,"unit_index":0,"topic_index":0,"step_index":0,"status":"completed"})
    assert fake_complete.status_code==409
    client.close()


def test_study_heartbeat_is_rate_limited(tmp_path):
    app,client=client_for(tmp_path)
    body={"profile_id":1,"subject":"Redes","seconds":30}
    assert client.post("/api/study",json=body).json()["deduplicated"] is False
    assert client.post("/api/study",json=body).json()["deduplicated"] is True
    count=app.state.db.one("SELECT count(*) n FROM learning_sessions WHERE user_id=1")["n"]
    assert count==1
    client.close()


def test_local_day_conversion_respects_machine_timezone(monkeypatch):
    if not hasattr(time,"tzset"):
        return
    monkeypatch.setenv("TZ","America/Panama")
    time.tzset()
    assert local_day_from_timestamp("2026-10-08T01:30:00+00:00")=="2026-10-07"


def test_encrypted_backup_rejects_wrong_password_and_tampering(tmp_path):
    db=Database(tmp_path/"allen.sqlite3")
    payload=export_backup(db)
    encrypted=encrypt_backup(payload,"correct horse battery")
    restored=decrypt_backup(encrypted,"correct horse battery")
    assert restored["format"]=="allen-backup"

    try:
        decrypt_backup(encrypted,"wrong password")
    except ValueError as exc:
        assert "incorrecta" in str(exc) or "modificado" in str(exc)
    else:
        raise AssertionError("Wrong backup password must fail")

    tampered=dict(encrypted)
    tampered["ciphertext"]=encrypted["ciphertext"][:-4]+"AAAA"
    try:
        decrypt_backup(tampered,"correct horse battery")
    except ValueError:
        pass
    else:
        raise AssertionError("Tampered encrypted backup must fail")


def test_system_routes_are_teacher_protected(tmp_path):
    _,client=client_for(tmp_path,teacher=True)
    assert client.get("/api/system/integrity").status_code==403
    client.post("/api/teacher/security/setup",json={"pin":"123456"})
    assert client.get("/api/system/integrity").status_code==200
    client.close()


def test_plaintext_backup_export_is_disabled_in_distributed_mode(tmp_path):
    app=create_app(
        tmp_path/"allen.sqlite3",
        require_license=False,
        require_local_access=False,
        require_teacher_auth=True,
    )
    client=TestClient(app)
    token=client.get("/api/bootstrap").json()["token"]
    client.headers["X-Allen-Token"]=token
    client.post("/api/teacher/security/setup",json={"pin":"123456"})
    response=client.get("/api/backup/export?profile_id=1")
    assert response.status_code==409
    assert "cifrados" in response.json()["detail"]
    client.close()
