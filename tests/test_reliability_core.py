import base64
import sqlite3
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.database import Database
from backend.course_versioning import compare_versions


def make_client(path):
    app=create_app(path)
    client=TestClient(app)
    client.headers["X-Allen-Token"]=client.get("/api/bootstrap").json()["token"]
    return client


def course_payload(text,title="Curso versionado"):
    return {
        "profile_id":1,
        "title":title,
        "subject":"Redes",
        "level":"Premedia",
        "filename":"redes.md",
        "mime":"text/markdown",
        "content_base64":base64.b64encode(text.encode()).decode(),
    }


def test_numbered_migration_upgrades_v8_and_keeps_pre_migration_snapshot():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"allen.sqlite3"
        con=sqlite3.connect(path)
        con.execute("PRAGMA user_version=8")
        con.execute("CREATE TABLE legacy_marker(id INTEGER PRIMARY KEY,value TEXT)")
        con.execute("INSERT INTO legacy_marker(value) VALUES('keep me')")
        con.commit();con.close()

        db=Database(path)
        assert db.schema_version()==12
        assert db.one("SELECT value FROM legacy_marker")["value"]=="keep me"
        versions={row["version"] for row in db.all("SELECT version FROM schema_migrations")}
        assert {9,10,11}.issubset(versions)
        assert db.one("SELECT name FROM sqlite_master WHERE type='table' AND name='course_versions'")
        assert any("pre-migration-v8-to-v11" in row["name"] for row in db.snapshots())


def test_recovery_snapshot_roundtrip_and_integrity():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"allen.sqlite3"
        db=Database(path)
        db.execute("UPDATE users SET name='Antes' WHERE id=1")
        snap=db.create_snapshot("test")
        assert snap
        db.execute("UPDATE users SET name='Después' WHERE id=1")
        result=db.restore_snapshot(snap)
        assert result["integrity"]["ok"] is True
        assert db.one("SELECT name FROM users WHERE id=1")["name"]=="Antes"
        assert db.integrity()["ok"] is True
        assert len(db.snapshots())<=5


def test_course_diff_reports_progress_preservable_topics():
    old={"units":[{"title":"U1","topics":[
        {"title":"CIDR","objective":"Explica CIDR","source_excerpt":"Prefijos de red"},
        {"title":"DNS","objective":"Explica DNS","source_excerpt":"Resolución de nombres"},
    ]}]}
    new={"units":[{"title":"U1","topics":[
        {"title":"CIDR","objective":"Explica CIDR","source_excerpt":"Prefijos de red"},
        {"title":"DNS","objective":"Aplica DNS","source_excerpt":"Resolución de nombres y caché"},
        {"title":"DHCP","objective":"Describe DHCP","source_excerpt":"Asignación automática"},
    ]}]}
    diff=compare_versions(old,new)
    assert diff["summary"]=={"unchanged":1,"modified":1,"added":1,"removed":0,"progress_preservable_percent":33}


def test_teacher_can_upload_new_course_version_and_must_review_again():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"allen.sqlite3"
        c=make_client(path)
        first="# Unidad 1: Redes\nCIDR usa prefijos para describir redes. DNS traduce nombres a direcciones IP. DHCP asigna parámetros automáticamente."
        imported=c.post("/api/teacher/import",json=course_payload(first)).json()
        cid=imported["course_id"]
        row=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()
        assert c.put(f"/api/teacher/courses/{cid}/review",json={"profile_id":1,"structure":row["structure"]}).status_code==200
        assert c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1}).status_code==200

        second="# Unidad 1: Redes\nCIDR usa prefijos para describir redes. DNS traduce nombres a direcciones IP y puede usar caché. DHCP asigna parámetros automáticamente.\n# Unidad 2: Seguridad\nMFA añade una segunda comprobación de identidad."
        version_payload={
            "profile_id":1,
            "filename":"redes-v2.md",
            "mime":"text/markdown",
            "content_base64":base64.b64encode(second.encode()).decode(),
        }
        created=c.post(f"/api/teacher/courses/{cid}/versions",json=version_payload)
        assert created.status_code==200
        body=created.json()
        assert body["version"]==2
        assert "summary" in body["diff"]

        current=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()
        assert current["version"]==2
        assert current["status"]=="draft"
        assert c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1}).status_code==409

        history=c.get(f"/api/teacher/courses/{cid}/versions?profile_id=1").json()
        assert [v["version_number"] for v in history][:2]==[2,1]
        assert any("before-course-v2" in x["name"] for x in c.get("/api/system/recovery/snapshots").json())
        c.close()


def test_recovery_api_reports_integrity_and_restores_snapshot():
    with tempfile.TemporaryDirectory() as tmp:
        c=make_client(Path(tmp)/"allen.sqlite3")
        health=c.get("/api/system/integrity")
        assert health.status_code==200
        assert health.json()["ok"] is True
        snap=c.post("/api/system/recovery/snapshot",json={}).json()["snapshot"]
        assert snap
        c.app.state.db.execute("UPDATE users SET name='Temporal' WHERE id=1")
        restored=c.post("/api/system/recovery/restore",json={"snapshot":snap})
        assert restored.status_code==200
        assert restored.json()["integrity"]["ok"] is True
        c.close()


def test_backup_contains_course_version_history():
    with tempfile.TemporaryDirectory() as tmp:
        c=make_client(Path(tmp)/"allen.sqlite3")
        text="# Redes\nCIDR usa prefijos. DNS resuelve nombres. DHCP asigna configuración automáticamente."
        cid=c.post("/api/teacher/import",json=course_payload(text)).json()["course_id"]
        backup=c.get("/api/backup/export?profile_id=1").json()
        rows=backup["tables"]["course_versions"]
        assert any(row["course_id"]==cid and row["version_number"]==1 for row in rows)
        c.close()
