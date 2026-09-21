import json
import pytest
from test_allen import client
from backend.education import catalog,generate
from backend.schemas import QuizRequest

@pytest.mark.parametrize('count',[5,10])
@pytest.mark.parametrize('kind',['multiple','boolean','short'])
def test_every_topic_has_requested_distinct_questions(count,kind):
    for subject,topics in catalog().items():
        for topic in topics:
            rows=generate(QuizRequest(subject=subject,topic=topic,count=count,kind=kind))
            assert len(rows)==count
            assert len({r['prompt'] for r in rows})==count

def test_custom_library_is_profile_scoped_and_deletable(client):
    other=client.post('/api/profiles',json={'name':'Otro','level':'Primaria','avatar':'🐵'}).json()['id']
    pack=client.post('/api/library/import',json={'profile_id':1,'filename':'mis-notas.json','content':json.dumps([{'title':'Xilófono','subject':'Música','content':'El xilófono tiene láminas.'}])})
    assert pack.status_code==200
    assert client.get('/api/library?q=xilófono&profile_id=1').json()[0]['title']=='Xilófono'
    assert client.get(f'/api/library?q=xilófono&profile_id={other}').json()==[]
    pid=pack.json()['id']
    assert client.delete(f'/api/library/packs/{pid}?profile_id={other}').status_code==404
    assert client.delete(f'/api/library/packs/{pid}?profile_id=1').status_code==200
    assert client.get('/api/library?q=xilófono').json()==[]

@pytest.mark.parametrize('filename,content',[('bad.exe','text'),('bad.json','[]'),('bad.json','{"content":23}'),('bad.json','bad')])
def test_invalid_import_is_atomic(client,filename,content):
    assert client.post('/api/library/import',json={'profile_id':1,'filename':filename,'content':content}).status_code==422
    assert client.get('/api/library/packs').json()==[]

def test_immediate_feedback_and_final_result(client):
    quiz=client.post('/api/quiz',json={'profile_id':1,'subject':'Historia','topic':'Fuentes históricas','count':5}).json()
    assert quiz['actual_count']==5
    answers=[]
    for i,q in enumerate(quiz['questions']):
        assert 'answer' not in q
        answer=q['options'][0];answers.append(answer)
        response=client.post(f"/api/quiz/{quiz['id']}/answer",json={'profile_id':1,'index':i,'answer':answer})
        assert response.status_code==200
        assert response.json()['explanation']
    result=client.post(f"/api/quiz/{quiz['id']}/submit",json={'profile_id':1,'answers':answers})
    assert result.status_code==200 and result.json()['total']==5
    assert client.post(f"/api/quiz/{quiz['id']}/submit",json={'profile_id':1,'answers':answers}).json()==result.json()
