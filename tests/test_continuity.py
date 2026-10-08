import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app import create_app

def client_for(path):
    app=create_app(path)
    client=TestClient(app)
    client.headers['X-Allen-Token']=client.get('/api/bootstrap').json()['token']
    return app,client

def test_adventure_persists_across_restart_and_manual_completion():
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'allen.sqlite3'
        app,c=client_for(db)
        started=c.post('/api/adventures/start',json={'profile_id':1,'adventure_id':'recover-network'}).json()
        sid=started['id']
        answer=c.post(f'/api/adventures/{sid}/event',json={'profile_id':1,'step':0,'event':'answer','answer':'192.168.10'})
        assert answer.json()['correct'] is True
        c.post(f'/api/adventures/{sid}/event',json={'profile_id':1,'step':1,'event':'advance','answer':''})
        c.close()
        app2,c2=client_for(db)
        active=c2.get('/api/adventures/active?profile_id=1').json()
        assert active['id']==sid
        assert active['status'] in ('active','paused')
        assert active['current_step']==1
        answers=['255.255.255.0','/26','192.168.10.65']
        for step,text in enumerate(answers,start=1):
            answered=c2.post(f'/api/adventures/{sid}/event',json={'profile_id':1,'step':step,'event':'answer','answer':text})
            assert answered.json()['correct'] is True
            if step<3:
                advanced=c2.post(f'/api/adventures/{sid}/event',json={'profile_id':1,'step':step+1,'event':'advance','answer':''})
                assert advanced.status_code==200
        done=c2.post(f'/api/adventures/{sid}/event',json={'profile_id':1,'step':4,'event':'complete','answer':''}).json()
        assert done['status']=='completed'
        assert c2.get('/api/adventures/active?profile_id=1').json() is None
        c2.close()

def test_continuity_returns_resumable_study_session():
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'allen.sqlite3'
        app,c=client_for(db)
        from datetime import date, timedelta
        plan=c.post('/api/study-plans',json={'profile_id':1,'subject':'Redes','topics':['IPv4','DNS'],'deadline':(date.today()+timedelta(days=2)).isoformat(),'minutes_per_day':30,'level':'Premedia','goal':'Examen'}).json()
        session=c.post(f"/api/study-plans/{plan['id']}/start?profile_id=1",json={}).json()
        c.post(f"/api/study-sessions/{session['id']}/event",json={'profile_id':1,'kind':'understood','activity_index':1,'note':''})
        c.post(f"/api/study-sessions/{session['id']}/event",json={'profile_id':1,'kind':'paused','activity_index':1,'note':''})
        c.close()
        _,c2=client_for(db)
        continuity=c2.get('/api/continuity?profile_id=1').json()
        assert continuity['study_session']['id']==session['id']
        assert continuity['study_session']['current_activity_index']==1
        assert continuity['study_session']['status']=='paused'
        c2.close()

def test_continuity_recommendation_prefers_active_adventure():
    with tempfile.TemporaryDirectory() as tmp:
        _,c=client_for(Path(tmp)/'allen.sqlite3')
        c.post('/api/adventures/start',json={'profile_id':1,'adventure_id':'ai-lab'})
        data=c.get('/api/continuity?profile_id=1').json()
        assert data['adventure']['adventure_id']=='ai-lab'
        assert data['recommendation']['kind']=='continue'
        assert data['recommendation']['activity']['activity_type']=='adventure'
        c.close()
