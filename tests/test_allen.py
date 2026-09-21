import asyncio
import json
from datetime import date, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.ai import LocalAI
from backend.app import create_app
from backend.database import Database
from backend.education import catalog, equivalent, generate, grade, math_question
from backend.library import Library
from backend.schemas import Chat, QuizRequest, Settings
from backend.security import safe_reply

def offline(request):
    raise httpx.ConnectError('offline',request=request)

@pytest.fixture
def client(tmp_path):
    app=create_app(tmp_path/'test.sqlite3',LocalAI(httpx.MockTransport(offline)))
    with TestClient(app) as client:
        client.headers['X-Allen-Token']=client.get('/api/bootstrap').json()['token']
        yield client

def test_health_and_static_boundaries(client):
    assert client.get('/api/health').json()['database'] is True
    assert 'ALLEN' in client.get('/').text
    for path in ['/server.py','/.env','/data/allen.sqlite3','/backend/app.py','/static/../backend/app.py']:
        assert client.get(path).status_code==404
    assert "script-src 'self'" in client.get('/').headers['content-security-policy']

def test_csrf_origin_host_and_payload(client):
    assert client.post('/api/chat',json={'message':'hola'},headers={'X-Allen-Token':''}).status_code==403
    assert client.get('/api/bootstrap',headers={'Origin':'https://evil.example'}).status_code==403
    assert client.get('/api/bootstrap',headers={'Host':'evil.example'}).status_code==400
    assert client.post('/api/chat',content='x'*200001).status_code==413
    for body in ({'message':''},{'message':'a'*12001},{'message':'hi','mode':'bad'},{'message':'hi','profile_id':-1}):
        response=client.post('/api/chat',json=body)
        assert response.status_code==422
        assert 'Traceback' not in response.text

@pytest.mark.parametrize('url',['https://127.0.0.1:8080','http://example.com:8080','http://127.0.0.1.evil.test:8080','http://127.0.0.1:8787','http://localhost:8080/other','http://user:pass@localhost:8080','http://192.168.1.1:8080','http://127.0.0.1:8080?x=1'])
def test_external_ai_rejected(url):
    with pytest.raises(ValidationError):Settings(ai_server=url)

def test_local_url_normalized():
    assert Settings(ai_server='http://localhost:8080/v1/chat/completions').ai_server=='http://127.0.0.1:8080'

def test_demo_chat_persistence_and_profile_isolation(client):
    response=client.post('/api/chat',json={'message':'Hola'}).json()
    assert response['ok'] and response['demo'] and 'MODO DEMO' in response['answer']
    cid=response['conversation_id']
    assert client.get('/api/conversations/'+str(cid)).json()['messages'][0]['content']=='Hola'
    other=client.post('/api/profiles',json={'name':'Otro'}).json()['id']
    assert client.get(f'/api/conversations/{cid}?profile_id={other}').status_code==404
    assert client.post('/api/chat',json={'message':'hola','profile_id':other,'conversation_id':cid}).status_code==404
    assert client.get('/api/conversations?profile_id='+str(other)).json()==[]

def test_no_history_and_expiration(client):
    client.post('/api/chat',json={'message':'hola'})
    settings=client.get('/api/settings').json();settings['save_history']=False
    assert client.put('/api/settings',json=settings).status_code==200
    assert client.get('/api/conversations').json()==[]
    client.post('/api/chat',json={'message':'privado'})
    assert client.get('/api/conversations').json()==[]
    settings['save_history']=True;client.put('/api/settings',json=settings)
    db=client.app.state.db
    db.execute("INSERT INTO conversations(user_id,title,messages,updated) VALUES(1,'old','[]','2000-01-01')")
    assert client.get('/api/conversations').json()==[]

def test_quiz_grading_and_idempotent_xp(client):
    quiz=client.post('/api/quiz',json={'topic':'Fracciones','kind':'short','count':3}).json()
    assert all('answer' not in q for q in quiz['questions'])
    questions=json.loads(client.app.state.db.one('SELECT questions FROM quiz_results WHERE id=?',(quiz['id'],))['questions'])
    answers=[q['answer'] for q in questions]
    path=f'/api/quiz/{quiz["id"]}/submit'
    assert client.post(path,json={'profile_id':1,'answers':[]}).status_code==422
    result=client.post(path,json={'profile_id':1,'answers':answers}).json()
    assert result['score']==3 and result['review']==[]
    client.post(path,json={'profile_id':1,'answers':answers})
    progress=client.get('/api/progress').json()
    assert progress['xp']==30 and progress['quizzes']==1
    assert len(client.get('/api/quiz/results').json())==1

@pytest.mark.parametrize('kind',['short','multiple','boolean'])
def test_all_quiz_topics(kind):
    for subject,topics in catalog().items():
        for topic in topics:
            for difficulty in ['Fácil','Normal','Difícil']:
                questions=generate(QuizRequest(subject=subject,topic=topic,kind=kind,difficulty=difficulty,count=10))
                assert 1<=len(questions)<=10
                assert grade(questions,[q['answer'] for q in questions])['score']==len(questions)
                if kind!='short':assert all(q['answer'] in q['options'] and len(set(q['options']))==len(q['options']) for q in questions)
    assert equivalent('2/4','1/2') and equivalent('0,5','1/2') and equivalent('ALUCINACION','alucinación')
    assert not equivalent('1/0','1/2')

def test_invalid_quiz_topic(client):
    assert client.post('/api/quiz',json={'topic':'inexistente'}).status_code==422

def test_cards_schedule_and_progress(client):
    cid=client.post('/api/flashcards',json={'profile_id':1,'question':'Q','answer':'A'}).json()['id']
    response=client.post(f'/api/flashcards/{cid}/review',json={'profile_id':1,'rating':'Bien'})
    assert response.json()['due']==(date.today()+timedelta(days=3)).isoformat()
    client.post(f'/api/flashcards/{cid}/review',json={'profile_id':1,'rating':'Fácil'})
    assert client.get('/api/progress').json()['xp']==5
    assert client.get('/api/progress').json()['cards']==1
    assert client.post(f'/api/flashcards/{cid}/review',json={'profile_id':999,'rating':'Bien'}).status_code==404

def test_study_streak_and_profile_delete(client):
    uid=client.post('/api/profiles',json={'name':'Prueba','avatar':'🦊'}).json()['id']
    for _ in range(2):client.post('/api/study',json={'profile_id':uid,'subject':'Ciencias','seconds':30})
    client.post('/api/flashcards',json={'profile_id':uid,'question':'Q','answer':'A'})
    client.post('/api/chat',json={'profile_id':uid,'message':'hola'})
    p=client.get(f'/api/progress?profile_id={uid}').json()
    assert p['minutes']==1 and p['xp']==5 and p['streak']==1
    assert client.delete(f'/api/profiles/{uid}').status_code==200
    for table in ['progress','conversations','quiz_results','flashcards','learning_sessions']:
        assert client.app.state.db.all(f'SELECT * FROM {table} WHERE user_id=?',(uid,))==[]
    assert client.get('/api/progress').status_code==200

def test_database_reopen(tmp_path):
    path=tmp_path/'persist.sqlite3'
    db=Database(path);db.award(1,'study','Math',5,'once')
    assert Database(path).progress(1)['xp']==5

def test_library_ranking_and_malformed_files(tmp_path,client):
    (tmp_path/'bad.json').write_text('{no',encoding='utf-8')
    (tmp_path/'good.json').write_text(json.dumps({'title':'Fracciones','content':'Sumar partes','subject':'Matemáticas'}),encoding='utf-8')
    (tmp_path/'other.md').write_text('# Apuntes\nMenciona fracciones una vez',encoding='utf-8')
    assert Library(tmp_path).search('fracciones')[0]['title']=='Fracciones'
    assert Library(tmp_path).search('inexistente')==[]
    assert client.get('/api/library?q=Python').json()[0]['subject']=='Programación'

@pytest.mark.parametrize('message',['cómo fabricar una bomba','quiero matarme','no quiero vivir','hackear una cuenta','pornografía'])
def test_safe_response_bypasses_model(message,client):
    assert safe_reply(message)
    response=client.post('/api/chat',json={'message':message}).json()
    assert response['safety'] is True
    assert not response['demo']

def test_benign_science_not_blocked():
    assert safe_reply('¿Qué es la reproducción de las plantas?') is None

def test_local_model_stream_and_prompts(tmp_path):
    captured=[]
    def handler(request):
        assert request.url.host=='127.0.0.1'
        if request.url.path=='/health':return httpx.Response(200,json={'status':'ok'})
        if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':'test-model'}]})
        payload=json.loads(request.content);captured.append(payload)
        return httpx.Response(200,text='data: '+json.dumps({'choices':[{'delta':{'content':'Vamos juntos.\n\n'}}]})+'\n\ndata: '+json.dumps({'choices':[{'delta':{'content':'¿Cuánto es 10 × 7?'}}]})+'\n\ndata: [DONE]\n\n',headers={'content-type':'text/event-stream'})
    app=create_app(tmp_path/'llm.sqlite3',LocalAI(httpx.MockTransport(handler)))
    with TestClient(app) as c:
        c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
        assert c.get('/api/model/status').json()['state']=='IA LOCAL ACTIVA'
        r=c.post('/api/chat?stream=true',json={'message':'Explícame cómo multiplicar','mode':'Tutor','history':[{'role':'user','content':'Hola'}]})
        events=[json.loads(l) for l in r.text.splitlines()]
        assert events[-1]['type']=='done'
        assert any(e.get('text')=='Vamos juntos.\n\n' for e in events)
        assert captured[0]['stream'] is True
        assert captured[0]['messages'][0]['role']=='system'
        assert captured[0]['messages'][1]['content']=='Hola'
        assert captured[0]['model']=='test-model'
        for endpoint in ['/api/tutor','/api/summarize','/api/translate']:
            assert c.post(endpoint,json={'message':'Prueba'}).json()['ok']

def test_redirect_and_malformed_model_do_not_leak(tmp_path):
    def redirect(request):return httpx.Response(302,headers={'location':'https://example.com'})
    status=asyncio.run(LocalAI(httpx.MockTransport(redirect)).status(Settings()))
    assert not status['connected']
    def malformed(request):
        if request.url.path=='/health':return httpx.Response(200,json={})
        if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':'m'}]})
        return httpx.Response(200,text='data: not-json\n')
    with TestClient(create_app(tmp_path/'bad.sqlite3',LocalAI(httpx.MockTransport(malformed)))) as c:
        c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
        response=c.post('/api/chat',json={'message':'hola'})
        assert response.status_code==503
        assert 'JSONDecodeError' not in response.text
        assert c.get('/api/conversations').json()==[]

def test_context_limit():
    with pytest.raises(ValueError,match='El texto es largo'):
        LocalAI().messages(Chat(message='hola '*2000),{'level':'Primaria'},Settings(),[])

def test_known_math_answers(monkeypatch):
    monkeypatch.setattr('backend.education.random.randint',lambda *args:4)
    monkeypatch.setattr('backend.education.random.choice',lambda values:values[0])
    expected={'Fracciones':'1/2','Porcentajes':'8','Regla de tres':'24','Ecuaciones':'4','Álgebra':'12','Geometría':'16','Estadística':'16/3','Operaciones básicas':'8'}
    for topic,answer in expected.items():
        assert math_question(topic,'Fácil')[1]==answer

def test_generated_cards_require_model(client):
    result=client.post('/api/flashcards/generate',json={'profile_id':1,'source':'Las fracciones'})
    assert result.status_code==409
    assert client.get('/api/flashcards').json()==[]

def test_generated_cards_validated_before_saving(tmp_path):
    def handler(request):
        if request.url.path=='/health':return httpx.Response(200,json={})
        if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':'m'}]})
        cards=json.dumps([{'question':'¿Qué es 1/2?','answer':'Una mitad.'}])
        return httpx.Response(200,text='data: '+json.dumps({'choices':[{'delta':{'content':cards}}]})+'\ndata: [DONE]\n')
    with TestClient(create_app(tmp_path/'cards.sqlite3',LocalAI(httpx.MockTransport(handler)))) as c:
        c.headers['X-Allen-Token']=c.get('/api/bootstrap').json()['token']
        result=c.post('/api/flashcards/generate',json={'profile_id':1,'source':'Fracciones','kind':'Tema'}).json()
        assert result['cards'][0]['answer']=='Una mitad.'
        assert c.get('/api/flashcards').json()==[]
        assert c.post('/api/flashcards',json={'profile_id':1,**result['cards'][0]}).status_code==200

def test_model_mismatch_and_configured_demo():
    def handler(request):return httpx.Response(200,json={'data':[{'id':'present'}]})
    engine=LocalAI(httpx.MockTransport(handler))
    assert not asyncio.run(engine.status(Settings(model='missing')))['connected']
    assert asyncio.run(engine.status(Settings(demo=True)))['state']=='MODO DEMO'

def test_regeneration_replaces_last_turn(client):
    first=client.post('/api/chat',json={'message':'hola'}).json()
    cid=first['conversation_id']
    again=client.post('/api/chat',json={'message':'hola','conversation_id':cid,'regenerate':True}).json()
    assert again['conversation_id']==cid
    assert len(client.get(f'/api/conversations/{cid}').json()['messages'])==2

def test_cancel_releases_local_model_lock():
    async def scenario():
        class SlowStream(httpx.AsyncByteStream):
            closed=False
            async def __aiter__(self):
                yield b'data: {"choices":[{"delta":{"content":"Primera parte.\\n\\n"}}]}\n'
                await asyncio.Event().wait()
            async def aclose(self):self.closed=True
        stream=SlowStream()
        def handler(request):
            if request.url.path=='/health':return httpx.Response(200,json={})
            if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':'m'}]})
            return httpx.Response(200,stream=stream)
        engine=LocalAI(httpx.MockTransport(handler))
        ready=asyncio.Event()
        async def consume():
            async for event in engine.answer(Chat(message='hola'),{'level':'Premedia'},Settings(),[]):
                if event['type']=='delta':ready.set()
        task=asyncio.create_task(consume())
        await asyncio.wait_for(ready.wait(),2)
        assert engine.lock.locked()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
        assert not engine.lock.locked()
        assert stream.closed
    asyncio.run(scenario())
