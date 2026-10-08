import base64
import tempfile
from datetime import date, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import create_app


def client_for(path):
    c=TestClient(create_app(path))
    c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
    return c


def published_course(c):
    text="# Redes\nIPv4 identifica interfaces de red. DNS permite resolver nombres. DHCP asigna configuración de red.\n# Seguridad\nMFA añade otra comprobación de identidad. Los backups permiten recuperar información."
    cid=c.post("/api/teacher/import",json={"profile_id":1,"title":"Redes","subject":"Redes","level":"Premedia","filename":"curso.md","mime":"text/markdown","content_base64":base64.b64encode(text.encode()).decode()}).json()["course_id"]
    structure=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()["structure"]
    assert c.put(f"/api/teacher/courses/{cid}/review",json={"profile_id":1,"structure":structure}).status_code==200
    assert c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1}).status_code==200
    return cid


def test_student_course_route_does_not_expose_exam_answers():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        cid=published_course(c)
        c.post(f"/api/courses/{cid}/enroll",json={"profile_id":1})
        route=c.get(f"/api/courses/{cid}/route?profile_id=1")
        assert route.status_code==200
        structure=route.json()["course"]["structure"]
        assert "final_exam" not in structure
        assert structure["units"][0]["topics"][0]["questions"]
        assert all("answer_hint" not in q for u in structure["units"] for t in u["topics"] for q in t["questions"])
        assert "correct" not in route.text

        exam=c.get(f"/api/courses/{cid}/exam?profile_id=1").json()
        assert all("correct" not in q for q in exam["questions"])
        teacher=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()
        answers=[q["correct"] for q in teacher["structure"]["final_exam"]]
        result=c.post(f"/api/courses/{cid}/exam/submit",json={"profile_id":1,"answers":answers}).json()
        assert result["score"]==result["total"]


def test_simulation_questions_hide_answers_but_are_graded():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        sim=c.post('/api/simulations',json={'profile_id':1,'subject':'Redes','topics':['IPv4 y CIDR'],'question_count':3,'minutes':20,'timed':True,'level':'Premedia'}).json()
        assert sim["questions"] and all("answer" not in q and "explanation" not in q for q in sim["questions"])
        active=c.get('/api/simulations/active?profile_id=1').json()
        assert all("answer" not in q and "explanation" not in q for q in active["questions"])
        stored=c.app.state.db.one("SELECT questions FROM simulation_results WHERE id=?",(sim["id"],))
        assert '"answer"' in stored["questions"]
        result=c.post(f"/api/simulations/{sim['id']}/submit",json={'profile_id':1,'answers':['x']*len(sim["questions"])}).json()
        assert result["total"]==len(sim["questions"])


def test_simulation_with_unknown_topic_is_rejected_cleanly():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        response=c.post('/api/simulations',json={'profile_id':1,'subject':'Redes','topics':['Tema inventado'],'question_count':3,'minutes':20,'timed':True,'level':'Premedia'})
        assert response.status_code==422


def test_backup_restore_does_not_leave_other_profiles_conversations():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        backup=c.get("/api/backup/export?profile_id=1").json()
        second=c.post("/api/profiles",json={"name":"Ana","level":"Media","avatar":"🦊"}).json()
        db=c.app.state.db
        db.execute("INSERT INTO conversations(user_id,title,messages,updated) VALUES(?,?,?,?)",(second["id"],"Privado de Ana",'[{"role":"user","content":"secreto"}]',"2026-10-08T00:00:00+00:00"))
        backup["tables"]["users"].append({"id":second["id"],"name":"Luis","age":None,"level":"Premedia","avatar":"🐵"})
        assert c.post("/api/backup/restore",json=backup).status_code==200
        assert c.get(f"/api/conversations?profile_id={second['id']}").json()==[]
        assert db.one("SELECT count(*) n FROM conversations")["n"]==0


def test_backup_restore_rejects_unknown_columns_without_changing_data():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        c.post("/api/flashcards",json={"profile_id":1,"question":"¿Qué es DNS?","answer":"Resolución de nombres"})
        backup=c.get("/api/backup/export?profile_id=1").json()
        backup["tables"]["flashcards"]=[{"id":99,"user_id":1,"question":"x","answer":"y","due":"2026-01-01","bad column":"1"}]
        response=c.post("/api/backup/restore",json=backup)
        assert response.status_code==422
        cards=c.get("/api/flashcards?profile_id=1").json()
        assert [x["question"] for x in cards]==["¿Qué es DNS?"]


def test_backup_restore_rejects_broken_references():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        backup=c.get("/api/backup/export?profile_id=1").json()
        backup["tables"]["flashcards"]=[{"id":1,"user_id":777,"question":"x","answer":"y","due":"2026-01-01","interval":0,"reviews":0}]
        assert c.post("/api/backup/restore",json=backup).status_code==422
        assert c.get("/api/bootstrap").json()["profiles"]


def test_study_plan_deadline_is_bounded():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        base={"profile_id":1,"subject":"Matemáticas","topics":["Fracciones"],"minutes_per_day":30,"level":"Premedia","goal":"Examen"}
        far=c.post("/api/study-plans",json={**base,"deadline":"9999-12-31"})
        assert far.status_code==422
        ok=c.post("/api/study-plans",json={**base,"deadline":(date.today()+timedelta(days=365)).isoformat()})
        assert ok.status_code==200
        assert len(ok.json()["days"])==366
