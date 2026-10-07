import base64
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.course_builder import build_course, decode_source


def client_for(path):
    app=create_app(path)
    c=TestClient(app)
    c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
    return c


def test_text_material_builds_source_grounded_course():
    text="# Unidad 1: Redes\nIPv4 permite identificar interfaces dentro de una red. DNS traduce nombres de dominio a direcciones IP.\n# Unidad 2: Servicios\nDHCP puede asignar parámetros de red automáticamente."
    extracted=decode_source("redes.md","text/markdown",base64.b64encode(text.encode()).decode())
    course=build_course("Fundamentos de Redes","Redes","Premedia",extracted["pages"],extracted["text"])
    assert course["units"]
    assert course["coverage"]["topics"] >= 1
    first=course["units"][0]["topics"][0]
    assert first["source"]["page"] == 1
    assert first["source_excerpt"]
    assert [x["type"] for x in first["route"]] == ["discover","example","retrieval","practice","quiz","review"]


def test_teacher_review_gate_publish_and_student_resume():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        text="# Redes\nIPv4 identifica interfaces de red. DNS permite resolver nombres. DHCP asigna configuración de red.\n# Seguridad\nMFA añade otra comprobación de identidad. Los backups permiten recuperar información."
        payload={
            "profile_id":1,
            "title":"Redes y Seguridad",
            "subject":"Redes",
            "level":"Premedia",
            "filename":"curso.md",
            "mime":"text/markdown",
            "content_base64":base64.b64encode(text.encode()).decode(),
        }
        imported=c.post("/api/teacher/import",json=payload)
        assert imported.status_code==200
        cid=imported.json()["course_id"]
        blocked=c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1})
        assert blocked.status_code==409

        row=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()
        reviewed=c.put(f"/api/teacher/courses/{cid}/review",json={"profile_id":1,"structure":row["structure"]})
        assert reviewed.status_code==200
        published=c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1})
        assert published.status_code==200

        courses=c.get("/api/courses?profile_id=1").json()
        assert any(x["id"]==cid for x in courses)
        enrolled=c.post(f"/api/courses/{cid}/enroll",json={"profile_id":1}).json()
        assert enrolled["status"]=="active"
        route=c.get(f"/api/courses/{cid}/route?profile_id=1").json()
        assert route["course"]["structure"]["units"]

        progressed=c.post(f"/api/courses/{cid}/progress",json={"profile_id":1,"unit_index":0,"topic_index":0,"step_index":1,"status":"active"})
        assert progressed.status_code==200
        resumed=c.get(f"/api/courses/{cid}/route?profile_id=1").json()
        assert resumed["enrollment"]["step_index"]==1
        c.close()


def test_teacher_content_is_profile_owned():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        p2=c.post("/api/profiles",json={"name":"Otro","level":"Premedia","age":None,"avatar":"🐵"}).json()
        text="Tema principal de redes. IPv4 y DNS se estudian con ejemplos y ejercicios para comprender conexiones."
        payload={"profile_id":1,"title":"Privado","subject":"Redes","level":"Premedia","filename":"a.txt","mime":"text/plain","content_base64":base64.b64encode(text.encode()).decode()}
        cid=c.post("/api/teacher/import",json=payload).json()["course_id"]
        assert c.get(f"/api/teacher/courses/{cid}?profile_id={p2['id']}").status_code==404
        c.close()


def test_course_pack_roundtrip_requires_review_again():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        text="# Redes\nIPv4 identifica interfaces. DNS traduce nombres a direcciones. DHCP asigna configuración automáticamente."
        payload={"profile_id":1,"title":"Pack Redes","subject":"Redes","level":"Premedia","filename":"pack.txt","mime":"text/plain","content_base64":base64.b64encode(text.encode()).decode()}
        cid=c.post("/api/teacher/import",json=payload).json()["course_id"]
        row=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()
        c.put(f"/api/teacher/courses/{cid}/review",json={"profile_id":1,"structure":row["structure"]})
        c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1})
        pack=c.get(f"/api/teacher/courses/{cid}/pack?profile_id=1").json()
        assert pack["format"]=="allen-course-pack"
        imported=c.post("/api/teacher/packs/import",json={"profile_id":1,"pack":pack})
        assert imported.status_code==200
        new_id=imported.json()["course_id"]
        new_row=c.get(f"/api/teacher/courses/{new_id}?profile_id=1").json()
        assert new_row["status"]=="draft"
        assert c.post(f"/api/teacher/courses/{new_id}/publish",json={"profile_id":1}).status_code==409
        c.close()
