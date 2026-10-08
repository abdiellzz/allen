import base64
import io
import hashlib
import secrets
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

import backend.app as app_module
import backend.course_builder as course_builder
from backend.course_builder import validate_course_structure
from backend.app import create_app
from backend.backup import export_backup
from backend.backup_crypto import AAD, decrypt_backup, encrypt_backup


def _client(tmp_path, *, teacher=False):
    app=create_app(
        tmp_path/"allen.sqlite3",
        require_license=False,
        require_local_access=False,
        require_teacher_auth=teacher,
    )
    client=TestClient(app)
    client.headers["X-Allen-Token"]=client.get("/api/bootstrap").json()["token"]
    return app,client


def test_persistent_adventure_ignores_client_correct_flag(tmp_path):
    app,client=_client(tmp_path)
    started=client.post("/api/adventures/start",json={"profile_id":1,"adventure_id":"digital-defender"})
    assert started.status_code==200
    sid=started.json()["id"]

    wrong=client.post(
        f"/api/adventures/{sid}/event",
        json={"profile_id":1,"step":0,"event":"answer","answer":"Reutilizar una contraseña fácil"},
    )
    assert wrong.status_code==200
    assert wrong.json()["correct"] is False
    assert wrong.json()["mistakes"]==1

    jump=client.post(
        f"/api/adventures/{sid}/event",
        json={"profile_id":1,"step":1,"event":"advance","answer":""},
    )
    assert jump.status_code==409

    early=client.post(
        f"/api/adventures/{sid}/event",
        json={"profile_id":1,"step":4,"event":"complete","answer":""},
    )
    assert early.status_code==409
    client.close()


def test_unknown_adventure_is_rejected(tmp_path):
    _,client=_client(tmp_path)
    response=client.post("/api/adventures/start",json={"profile_id":1,"adventure_id":"invented-by-client"})
    assert response.status_code==422
    client.close()


def test_simulation_remaining_time_cannot_be_increased_by_client(tmp_path):
    app,client=_client(tmp_path)
    created=client.post(
        "/api/simulations",
        json={"profile_id":1,"subject":"Redes","topics":["IPv4"],"question_count":3,"minutes":5,"timed":True,"level":"Premedia"},
    )
    assert created.status_code==200, created.text
    sid=created.json()["id"]
    old=(datetime.now(timezone.utc)-timedelta(seconds=90)).isoformat()
    app.state.db.execute("UPDATE simulation_results SET remaining_seconds=300,updated_at=? WHERE id=?",(old,sid))

    response=client.post(
        f"/api/simulations/{sid}/progress",
        json={"profile_id":1,"answers":[],"status":"active","remaining_seconds":9999},
    )
    assert response.status_code==200
    assert 0 < response.json()["remaining_seconds"] <= 211
    client.close()


def test_expired_simulation_uses_stored_answers_not_late_answers(tmp_path):
    app,client=_client(tmp_path)
    created=client.post(
        "/api/simulations",
        json={"profile_id":1,"subject":"Redes","topics":["IPv4"],"question_count":3,"minutes":5,"timed":True,"level":"Premedia"},
    )
    assert created.status_code==200
    sid=created.json()["id"]
    questions=json.loads(app.state.db.one("SELECT questions FROM simulation_results WHERE id=?",(sid,))["questions"])
    stored=[""]*len(questions)
    expired=(datetime.now(timezone.utc)-timedelta(seconds=20)).isoformat()
    app.state.db.execute(
        "UPDATE simulation_results SET answers=?,remaining_seconds=1,updated_at=? WHERE id=?",
        (json.dumps(stored),expired,sid),
    )
    late=[q.get("correct","") for q in questions]
    response=client.post(f"/api/simulations/{sid}/submit",json={"profile_id":1,"answers":late})
    assert response.status_code==200
    assert response.json()["score"]==0
    client.close()


def test_teacher_session_expires_after_idle_timeout(tmp_path, monkeypatch):
    clock={"now":1000.0}
    monkeypatch.setattr(app_module.time,"monotonic",lambda:clock["now"])
    _,client=_client(tmp_path,teacher=True)
    assert client.post("/api/teacher/security/setup",json={"pin":"12345678"}).status_code==200
    assert client.get("/api/system/integrity").status_code==200

    clock["now"]+=901
    expired=client.get("/api/system/integrity")
    assert expired.status_code==403
    assert expired.json()["teacher_auth_required"] is True
    assert client.get("/api/teacher/security/status").json()["unlocked"] is False
    client.close()


def test_security_headers_exist_on_cross_site_and_license_errors(tmp_path):
    app=create_app(
        tmp_path/"allen.sqlite3",
        require_license=False,
        require_local_access=False,
        require_teacher_auth=False,
    )
    client=TestClient(app)
    response=client.get("/api/bootstrap",headers={"Sec-Fetch-Site":"cross-site"})
    assert response.status_code==403
    assert response.headers["X-Frame-Options"]=="DENY"
    assert response.headers["Cache-Control"]=="no-store"
    client.close()


def test_pdf_extraction_stops_when_text_budget_is_reached(monkeypatch):
    calls={"count":0}
    class FakePage:
        def extract_text(self):
            calls["count"]+=1
            return "A"*120_000
    class FakeReader:
        def __init__(self,_):
            self.pages=[FakePage(),FakePage(),FakePage(),FakePage()]
    monkeypatch.setattr(course_builder,"PdfReader",FakeReader)
    raw=base64.b64encode(b"%PDF-fake").decode("ascii")
    decoded=course_builder.decode_source("course.pdf","application/pdf",raw)
    assert len(decoded["text"])<=course_builder.MAX_TEXT
    assert calls["count"]==2


def test_new_backup_kdf_is_stronger_and_old_122_backup_still_decrypts(tmp_path):
    app,_=_client(tmp_path)
    payload=export_backup(app.state.db)
    current=encrypt_backup(payload,"twelve-chars-plus")
    assert current["kdf"]=="scrypt-n32768-r8-p1"
    assert decrypt_backup(current,"twelve-chars-plus")["format"]=="allen-backup"

    password="old-pass"
    salt=b"1"*16
    nonce=b"2"*12
    key=Scrypt(salt=salt,length=32,n=2**14,r=8,p=1).derive(password.encode())
    raw=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode()
    ciphertext=AESGCM(key).encrypt(nonce,raw,AAD)
    old={
        "format":"allen-backup-encrypted",
        "version":1,
        "kdf":"scrypt-n16384-r8-p1",
        "cipher":"AES-256-GCM",
        "salt":base64.b64encode(salt).decode(),
        "nonce":base64.b64encode(nonce).decode(),
        "ciphertext":base64.b64encode(ciphertext).decode(),
    }
    assert decrypt_backup(old,password)["format"]=="allen-backup"


def test_complete_remover_requires_recognized_allen_root():
    root=Path(__file__).resolve().parent.parent
    script=(root/"distribution/remove_allen.ps1").read_text(encoding="utf-8")
    assert 'Join-Path $env:USERPROFILE "Downloads"' in script
    assert "$resolved -eq $driveRoot" in script
    assert "Test-Path -LiteralPath $portableFlag" in script
    assert "Test-Path -LiteralPath $internalDir" in script
    assert "Test-Path -LiteralPath $removeScript" in script
    assert "or (Test-Path -LiteralPath $allenExe)" not in script


def test_windows_workflow_pins_inno_setup():
    root=Path(__file__).resolve().parent.parent
    workflow=(root/".github/workflows/windows-distribution.yml").read_text(encoding="utf-8")
    assert "innosetup --version=6.7.1" in workflow


def test_new_teacher_pin_requires_eight_digits(tmp_path):
    _,client=_client(tmp_path,teacher=True)
    response=client.post("/api/teacher/security/setup",json={"pin":"123456"})
    assert response.status_code==422
    client.close()


def test_legacy_six_digit_teacher_pin_is_upgraded(tmp_path):
    app,client=_client(tmp_path,teacher=True)
    salt=secrets.token_bytes(16).hex()
    legacy_pin="123456"
    legacy_hash=hashlib.scrypt(
        legacy_pin.encode(),
        salt=bytes.fromhex(salt),
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    ).hex()
    app.state.db.execute(
        "INSERT INTO teacher_security(id,salt,pin_hash,kdf_n,updated_at) VALUES(1,?,?,16384,?)",
        (salt,legacy_hash,"2026-10-08T00:00:00+00:00"),
    )

    unlocked=client.post("/api/teacher/security/unlock",json={"pin":legacy_pin})
    assert unlocked.status_code==200
    row=app.state.db.one("SELECT kdf_n,salt,pin_hash FROM teacher_security WHERE id=1")
    assert row["kdf_n"]==65536
    assert row["salt"]!=salt
    assert row["pin_hash"]!=legacy_hash
    client.close()


def test_adventure_api_rejects_client_correct_field(tmp_path):
    _,client=_client(tmp_path)
    started=client.post("/api/adventures/start",json={"profile_id":1,"adventure_id":"digital-defender"})
    sid=started.json()["id"]
    response=client.post(
        f"/api/adventures/{sid}/event",
        json={"profile_id":1,"step":0,"event":"answer","answer":"Reutilizar una contraseña fácil","correct":True},
    )
    assert response.status_code==422
    client.close()


def test_course_structure_rejects_excessive_complexity():
    too_many_topics={
        "title":"Malicious",
        "subject":"Test",
        "level":"Premedia",
        "units":[{
            "title":"Unidad",
            "topics":[
                {"title":f"T{i}","objective":"Objetivo","route":[],"questions":[],"flashcards":[]}
                for i in range(13)
            ],
        }],
        "final_exam":[],
    }
    try:
        validate_course_structure(too_many_topics)
    except ValueError as exc:
        assert "12 temas" in str(exc)
    else:
        raise AssertionError("Oversized Course Pack structure must be rejected")

    nested={"title":"Nested","subject":"Test","level":"Premedia","units":[{"title":"U","topics":[{"title":"T","objective":"O"}]}]}
    cursor=nested
    for i in range(12):
        cursor["extra"]={}
        cursor=cursor["extra"]
    try:
        validate_course_structure(nested)
    except ValueError as exc:
        assert "compleja" in str(exc)
    else:
        raise AssertionError("Deeply nested Course Pack structure must be rejected")


def test_snapshot_restore_reapplies_teacher_kdf_column(tmp_path):
    from backend.database import Database
    from backend.recovery import create_snapshot
    db=Database(tmp_path/"allen.sqlite3")
    # Simulate a v11-era teacher table inside a valid snapshot.
    with db.connect() as con:
        con.execute("ALTER TABLE teacher_security RENAME TO teacher_security_new")
        con.execute("""CREATE TABLE teacher_security(
            id INTEGER PRIMARY KEY CHECK(id=1),
            salt TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")
        con.execute("DROP TABLE teacher_security_new")
        con.execute("PRAGMA user_version=11")
    snap=create_snapshot(db.path,"legacy-v11")
    # Reopen migrates the live DB, then restore the old snapshot and ensure
    # restore_snapshot runs compatibility migrations too.
    migrated=Database(db.path)
    assert "kdf_n" in {r["name"] for r in migrated.all("PRAGMA table_info(teacher_security)")}
    result=migrated.restore_snapshot(snap)
    assert result["integrity"]["ok"] is True
    assert migrated.schema_version()==12
    assert "kdf_n" in {r["name"] for r in migrated.all("PRAGMA table_info(teacher_security)")}
