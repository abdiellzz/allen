import base64
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.course_quality import evaluate_course
from backend.curriculum_graph import build_graph
from backend.learning_intelligence import score_diagnostic


def client_for(path):
    app=create_app(path)
    c=TestClient(app)
    c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
    return c


def material():
    return "# Unidad 1: Fundamentos\nCIDR describe prefijos de red y ayuda a interpretar máscaras. IPv4 identifica interfaces de red. DNS traduce nombres a direcciones IP.\n# Unidad 2: Servicios\nDHCP asigna parámetros de red automáticamente. Un gateway conecta redes diferentes."


def create_course(c):
    payload={"profile_id":1,"title":"Inteligencia de Redes","subject":"Redes","level":"Premedia","filename":"redes.md","mime":"text/markdown","content_base64":base64.b64encode(material().encode()).decode()}
    cid=c.post("/api/teacher/import",json=payload).json()["course_id"]
    row=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()
    reviewed=c.put(f"/api/teacher/courses/{cid}/review",json={"profile_id":1,"structure":row["structure"]})
    assert reviewed.status_code==200
    assert reviewed.json()["quality"]["score"]>=70
    assert reviewed.json()["graph"]["nodes"]>=1
    published=c.post(f"/api/teacher/courses/{cid}/publish",json={"profile_id":1})
    assert published.status_code==200
    return cid,row["structure"]


def test_course_quality_reports_concrete_reasons():
    weak={"units":[{"title":"U1","topics":[{"title":"X","objective":"Saber X","source":{},"source_excerpt":"","questions":[]}]}],"final_exam":[]}
    report=evaluate_course(weak)
    codes={x["code"] for x in report["issues"]}
    assert report["score"]<80
    assert "missing_source" in codes
    assert "no_questions" in codes
    assert "weak_objective" in codes


def test_curriculum_graph_has_prerequisite_relationships():
    structure={"units":[{"title":"U1","topics":[{"title":"CIDR","objective":"Explica prefijos"},{"title":"Subnetting","objective":"Aplica prefijos CIDR"}]}]}
    graph=build_graph(structure)
    assert len(graph["nodes"])==2
    assert any(e["relation"]=="prerequisite" and e["from"]=="u0:t0" and e["to"]=="u0:t1" for e in graph["edges"])


def test_teacher_review_populates_question_bank_quality_and_graph():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        cid,_=create_course(c)
        quality=c.get(f"/api/teacher/courses/{cid}/quality?profile_id=1").json()
        graph=c.get(f"/api/teacher/courses/{cid}/graph?profile_id=1").json()
        analytics=c.get("/api/teacher/analytics?profile_id=1").json()
        assert quality["question_bank"]["questions"]>0
        assert graph["nodes"]
        assert graph["persisted_edges"]
        assert analytics["summary"]["courses"]>=1
        c.close()


def test_diagnostic_moves_student_to_first_weak_topic():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        cid,structure=create_course(c)
        c.post(f"/api/courses/{cid}/enroll",json={"profile_id":1})
        diagnostic=c.get(f"/api/courses/{cid}/diagnostic?profile_id=1").json()
        assert 5<=len(diagnostic["questions"])<=10
        # Deliberately choose non-correct options when possible.
        correct=[q["correct"] for q in structure["final_exam"]][:len(diagnostic["questions"])]
        answers=[]
        for q,answer in zip(diagnostic["questions"],correct):
            answers.append(next((o for o in q["options"] if o!=answer),q["options"][0]))
        result=c.post(f"/api/courses/{cid}/diagnostic/submit",json={"profile_id":1,"answers":answers})
        assert result.status_code==200
        assert result.json()["recommended_start"]["unit_index"]>=0
        route=c.get(f"/api/courses/{cid}/route?profile_id=1").json()
        assert route["enrollment"]["unit_index"]==result.json()["recommended_start"]["unit_index"]
        c.close()


def test_diagnostic_scoring_marks_strong_and_weak():
    qs=[{"topic":"CIDR","correct":"A"},{"topic":"DNS","correct":"B"}]
    result=score_diagnostic(qs,["A","X"])
    assert result["CIDR"]["status"]=="strong"
    assert result["DNS"]["status"]=="weak"


def test_mastery_evidence_and_due_reviews_are_explainable():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        q=c.post('/api/quiz',json={'profile_id':1,'subject':'Redes','topic':'IPv4 y CIDR','difficulty':'Fácil','count':1,'kind':'multiple'}).json()
        c.post(f"/api/quiz/{q['id']}/submit",json={'profile_id':1,'answers':[q['questions'][0]['options'][0]]})
        rows=c.get('/api/mastery?profile_id=1').json()
        row=rows[0]
        evidence=c.get('/api/mastery/evidence',params={'profile_id':1,'subject':row['subject'],'topic':row['topic']})
        assert evidence.status_code==200
        assert "evidence" in evidence.json()
        assert evidence.json()["evidence"]["attempts"]>=1
        c.app.state.db.execute("UPDATE topic_mastery SET next_review=date('now') WHERE user_id=1")
        due=c.get('/api/reviews/due?profile_id=1').json()
        assert due
        continuity=c.get('/api/continuity?profile_id=1').json()
        assert continuity["due_topic_reviews"]
        c.close()


def test_question_bank_is_approved_after_teacher_review():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        cid,_=create_course(c)
        rows=c.get(f"/api/teacher/courses/{cid}/questions?profile_id=1").json()
        assert rows
        assert all(row["status"]=="approved" for row in rows)
        assert all("difficulty" in row and "objective" in row and "source_page" in row for row in rows)
        c.close()


def test_strong_diagnostic_topic_is_exposed_for_route_skipping():
    with tempfile.TemporaryDirectory() as tmp:
        c=client_for(Path(tmp)/"allen.sqlite3")
        cid,structure=create_course(c)
        c.post(f"/api/courses/{cid}/enroll",json={"profile_id":1})
        diagnostic=c.get(f"/api/courses/{cid}/diagnostic?profile_id=1").json()
        correct=[q["correct"] for q in structure["final_exam"]][:len(diagnostic["questions"])]
        if len(correct)<len(diagnostic["questions"]):
            correct=(correct*10)[:len(diagnostic["questions"])]
        result=c.post(f"/api/courses/{cid}/diagnostic/submit",json={"profile_id":1,"answers":correct})
        assert result.status_code==200
        route=c.get(f"/api/courses/{cid}/route?profile_id=1").json()
        assert isinstance(route["diagnostic_skip_topics"],list)
        c.close()


def test_quality_breakdown_is_explainable_and_publish_threshold_matches_ready():
    strong={"units":[{"title":"U1","topics":[{"title":"CIDR","objective":"Explica y aplica CIDR","source":{"page":1},"source_excerpt":"CIDR usa prefijos de red.","questions":[{"prompt":"¿Cómo se interpreta un prefijo CIDR?","answer_hint":"Usa la longitud del prefijo."}]}]}],"final_exam":[{"topic":"CIDR","prompt":"¿Qué describe CIDR?","options":["A","B","C"],"correct":"A","source":{"page":1}}]}
    report=evaluate_course(strong)
    assert "breakdown" in report
    assert report["breakdown"]["source_grounding"]["ok"]==1
    assert report["breakdown"]["assessed_topics"]["ok"]==1
    assert report["status"]=="ready"


def test_curriculum_graph_does_not_call_every_previous_topic_a_prerequisite():
    structure={"units":[{"title":"U1","topics":[{"title":"DNS","objective":"Explica resolución de nombres"},{"title":"DHCP","objective":"Describe asignación automática de red"}]}]}
    graph=build_graph(structure)
    assert any(e["relation"]=="builds_on" for e in graph["edges"])
    assert not any(e["relation"]=="prerequisite" for e in graph["edges"])


def test_learning_intelligence_tables_survive_backup_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"allen.sqlite3"
        c=client_for(path)
        cid,_=create_course(c)
        c.post(f"/api/courses/{cid}/enroll",json={"profile_id":1})
        diagnostic=c.get(f"/api/courses/{cid}/diagnostic?profile_id=1").json()
        course=c.get(f"/api/teacher/courses/{cid}?profile_id=1").json()["structure"]
        correct=[q["correct"] for q in course["final_exam"]][:len(diagnostic["questions"])]
        c.post(f"/api/courses/{cid}/diagnostic/submit",json={"profile_id":1,"answers":correct})
        backup=c.get("/api/backup/export?profile_id=1").json()
        assert backup["tables"]["curriculum_edges"]
        assert backup["tables"]["question_bank"]
        assert backup["tables"]["course_quality_reviews"]
        assert backup["tables"]["diagnostic_results"]
        summary=c.post("/api/backup/validate",json=backup).json()
        assert summary["questions"]>0
        assert summary["diagnostics"]>0
        restored=c.post("/api/backup/restore",json=backup)
        assert restored.status_code==200
        assert c.get(f"/api/teacher/courses/{cid}/graph?profile_id=1").json()["persisted_edges"]
        c.close()
