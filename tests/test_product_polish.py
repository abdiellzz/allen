from datetime import date, timedelta
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from backend.learning_engine import compute_mastery, recommend_for_state
from backend.app import create_app


def make_client(path):
    app=create_app(path)
    c=TestClient(app)
    c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
    return c


def test_mastery_grows_with_evidence_and_penalizes_hints():
    low=compute_mastery(attempts=4,correct=2,incorrect=2,hints=0,practice_count=1,quiz_count=1)
    high=compute_mastery(attempts=10,correct=9,incorrect=1,hints=0,practice_count=3,quiz_count=2)
    hinted=compute_mastery(attempts=10,correct=9,incorrect=1,hints=4,practice_count=3,quiz_count=2)
    assert high['score']>low['score']
    assert hinted['score']<high['score']
    assert high['confidence']>=low['confidence']


def test_mastery_recommendation_changes_by_level():
    assert recommend_for_state({'mastery_score':20,'topic':'Subnetting','status':'learning'})['action']=='explain'
    assert recommend_for_state({'mastery_score':50,'topic':'Subnetting','status':'practicing'})['action']=='guided_practice'
    assert recommend_for_state({'mastery_score':70,'topic':'Subnetting','status':'practicing'})['action']=='interleave'
    assert recommend_for_state({'mastery_score':90,'topic':'Subnetting','status':'mastered'})['action']=='challenge'


def test_quiz_creates_mastery_and_event_log():
    with tempfile.TemporaryDirectory() as tmp:
        c=make_client(Path(tmp)/'allen.sqlite3')
        q=c.post('/api/quiz',json={'profile_id':1,'subject':'Redes','topic':'IPv4 y CIDR','difficulty':'Fácil','count':1,'kind':'multiple'}).json()
        # Submit the first visible option; correctness is irrelevant for event creation.
        option=q['questions'][0]['options'][0]
        r=c.post(f"/api/quiz/{q['id']}/submit",json={'profile_id':1,'answers':[option]})
        assert r.status_code==200
        mastery=c.get('/api/mastery?profile_id=1').json()
        assert any(row['subject']=='Redes' for row in mastery)
        c.close()


def test_one_active_adventure_pauses_previous():
    with tempfile.TemporaryDirectory() as tmp:
        c=make_client(Path(tmp)/'allen.sqlite3')
        first=c.post('/api/adventures/start',json={'profile_id':1,'adventure_id':'recover-network'}).json()
        second=c.post('/api/adventures/start',json={'profile_id':1,'adventure_id':'ai-lab'}).json()
        db=c.app.state.db
        old=db.one('SELECT status FROM adventure_sessions WHERE id=?',(first['id'],))
        current=db.one('SELECT * FROM profile_current_activity WHERE user_id=1')
        assert old['status']=='paused'
        assert current['activity_type']=='adventure'
        assert current['reference_id']==second['id']
        c.close()


def test_backup_validate_restore_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'allen.sqlite3'
        c=make_client(path)
        c.post('/api/flashcards',json={'profile_id':1,'question':'¿Qué es DNS?','answer':'Resolución de nombres'})
        backup=c.get('/api/backup/export?profile_id=1').json()
        summary=c.post('/api/backup/validate',json=backup)
        assert summary.status_code==200
        assert summary.json()['flashcards']>=1
        restored=c.post('/api/backup/restore',json=backup)
        assert restored.status_code==200
        assert c.get('/api/flashcards?profile_id=1').json()
        c.close()
