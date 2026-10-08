import json

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.course_builder import validate_course_structure
from distribution import allen_launcher


class FakeResponse:
    def __init__(self,payload,status=200):
        self.status=status
        self.payload=payload
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self): return json.dumps(self.payload).encode("utf-8")


def test_launcher_rejects_foreign_process_on_allen_port(monkeypatch):
    monkeypatch.setattr(allen_launcher.urllib.request,"urlopen",lambda *a,**k:FakeResponse({"ok":True,"instance":"attacker"}))
    assert allen_launcher.health_ready(expected_instance="real-instance") is False
    monkeypatch.setattr(allen_launcher.urllib.request,"urlopen",lambda *a,**k:FakeResponse({"ok":True,"instance":"real-instance"}))
    assert allen_launcher.health_ready(expected_instance="real-instance") is True


def test_first_run_blocks_product_until_teacher_pin_is_configured(tmp_path):
    app=create_app(tmp_path/"allen.sqlite3",require_license=False,require_local_access=False,require_teacher_auth=True)
    with TestClient(app) as client:
        bootstrap=client.get("/api/bootstrap")
        assert bootstrap.status_code==200
        data=bootstrap.json()
        assert data["teacher_security"]["configured"] is False
        client.headers["X-Allen-Token"]=data["token"]

        blocked=client.get("/api/model/status")
        assert blocked.status_code==428
        assert blocked.json()["teacher_setup_required"] is True

        setup=client.post("/api/teacher/security/setup",json={"pin":"246810"})
        assert setup.status_code==200
        assert client.get("/api/model/status").status_code==200


def test_destructive_profile_delete_requires_teacher_session(tmp_path):
    app=create_app(tmp_path/"allen.sqlite3",require_license=False,require_local_access=False,require_teacher_auth=True)
    with TestClient(app) as client:
        data=client.get("/api/bootstrap").json()
        client.headers["X-Allen-Token"]=data["token"]
        client.post("/api/teacher/security/setup",json={"pin":"246810"})
        client.post("/api/teacher/security/lock",json={})
        blocked=client.delete("/api/profiles/1")
        assert blocked.status_code==403
        client.post("/api/teacher/security/unlock",json={"pin":"246810"})
        assert client.delete("/api/profiles/1").status_code==200


def test_student_can_change_visual_settings_but_not_global_ai_or_privacy(tmp_path):
    app=create_app(tmp_path/"allen.sqlite3",require_license=False,require_local_access=False,require_teacher_auth=True)
    with TestClient(app) as client:
        data=client.get("/api/bootstrap").json()
        client.headers["X-Allen-Token"]=data["token"]
        client.post("/api/teacher/security/setup",json={"pin":"246810"})
        client.post("/api/teacher/security/lock",json={})
        settings=client.get("/api/settings").json()

        visual={**settings,"font_size":"grande"}
        assert client.put("/api/settings",json=visual).status_code==200

        sensitive={**visual,"retention_days":60}
        denied=client.put("/api/settings",json=sensitive)
        assert denied.status_code==403


def test_health_exposes_only_readiness_identity(tmp_path):
    app=create_app(tmp_path/"allen.sqlite3",require_license=False,require_local_access=True,require_teacher_auth=False)
    with TestClient(app) as client:
        data=client.get("/api/health").json()
        assert set(data)=={"ok","instance"}
        assert data["ok"] is True
        assert data["instance"]==app.state.instance_id


def test_course_structure_rejects_excessive_complexity():
    valid={
        "units":[{"title":"Unidad","topics":[{"title":"Tema","objective":"Comprender el tema","route":[]}]}],
        "final_exam":[],
    }
    assert validate_course_structure(valid) is True

    too_many={"units":[{"title":f"U{i}","topics":[{"title":"T","objective":"O"}]} for i in range(21)]}
    try:
        validate_course_structure(too_many)
    except ValueError as exc:
        assert "20 unidades" in str(exc)
    else:
        raise AssertionError("Oversized course should be rejected")

    deep={"units":[{"title":"U","topics":[{"title":"T","objective":"O"}]}]}
    cursor=deep
    for _ in range(12):
        cursor["nested"]={}
        cursor=cursor["nested"]
    try:
        validate_course_structure(deep)
    except ValueError as exc:
        assert "compleja" in str(exc)
    else:
        raise AssertionError("Deeply nested course should be rejected")
