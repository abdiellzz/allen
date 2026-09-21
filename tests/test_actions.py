import json
import pytest
from test_allen import client
from backend.prompts import identity_reply,ALLEN_IDENTITY_PROMPT,system_prompt
from backend.schemas import Chat
from backend.conversation import prepare

@pytest.mark.parametrize('prompt,fragment',[
 ('Allen eres un mono?','mono compañero'),('¿Eres un mono de verdad?','No soy un animal de verdad'),
 ('Tu nombre es Pedro.','Mi nombre sigue siendo Allen'),('Yo me llamo Pedro.','Mucho gusto, Pedro'),
 ('¿Quién de los dos es el mono?','El mono soy yo')])
def test_monkey_identity(client,prompt,fragment):
    response=client.post('/api/chat',json={'message':prompt}).json()
    assert fragment in response['answer']
    if prompt=='Yo me llamo Pedro.': assert client.get('/api/bootstrap').json()['profiles'][0]['name']=='Pedro'
    assert 'mono naranja' in ALLEN_IDENTITY_PROMPT

def test_structured_reveal_persisted_exercise_without_history(client):
    first=client.post('/api/chat',json={'message':'¿Cuánto es 18 × 7?'}).json()
    cid=first['conversation_id']
    assert '126' not in first['answer']
    assert first['conversation_state']['active_exercise']=='¿Cuánto es 18 × 7?'
    result=client.post('/api/chat',json={'message':'Dame la respuesta','action':'reveal_answer','conversation_id':cid}).json()
    assert '126' in result['answer'] and '70 + 56' in result['answer']
    assert '¿Quieres' not in result['answer']
    assert result['conversation_state']['answer_revealed']
    saved=client.get(f'/api/conversations/{cid}').json()
    assert saved['conversation_state']['answer_revealed']
    assert saved['conversation_state']['last_action']=='reveal_answer'

def test_reveal_without_exercise_does_not_invent(client):
    response=client.post('/api/chat',json={'message':'Dame la respuesta','action':'reveal_answer'}).json()
    assert response['answer']=='No tengo un ejercicio pendiente todavía. Escríbeme uno y lo resolvemos.'
    assert not response['conversation_state']['active_exercise']

@pytest.mark.parametrize('action',['simplify','another_example','quiz_me','lost','step_by_step','dont_understand'])
def test_canonical_actions_keep_context(client,action):
    first=client.post('/api/chat',json={'message':'18 × 7'}).json()
    response=client.post('/api/chat',json={'message':'Acción educativa','action':action,'conversation_id':first['conversation_id']}).json()
    assert response['ok']
    assert response['conversation_state']['active_exercise']=='18 × 7'
    assert response['conversation_state']['last_action']==action
    assert '126' not in response['answer']
    request=prepare(Chat(message='Acción educativa',action=action,history=[{'role':'user','content':'18 × 7'}]))
    prompt=system_prompt(request,{'name':'Carlos','level':'Primaria'},[])
    assert 'intención confirmada' in prompt and '18 × 7' in prompt

def test_quiz_waits_and_next_requires_attempt(client):
    first=client.post('/api/chat',json={'message':'18 × 7'}).json()
    cid=first['conversation_id']
    quiz=client.post('/api/chat',json={'message':'Ponme a prueba','action':'quiz_me','conversation_id':cid}).json()
    assert quiz['conversation_state']['mode']=='quiz' and '56' not in quiz['answer']
    too_soon=client.post('/api/chat',json={'message':'Siguiente','action':'next','conversation_id':cid}).json()
    assert 'Primero' in too_soon['answer']

def test_state_does_not_cross_profiles(client):
    first=client.post('/api/chat',json={'message':'18 × 7'}).json()
    other=client.post('/api/profiles',json={'name':'Otro'}).json()['id']
    assert client.post('/api/chat',json={'profile_id':other,'message':'Dame la respuesta','action':'reveal_answer','conversation_id':first['conversation_id']}).status_code==404


def test_quiz_feedback_then_next_question(client):
    first=client.post('/api/chat',json={'message':'18 × 7'}).json()
    cid=first['conversation_id']
    quiz=client.post('/api/chat',json={'message':'Ponme a prueba','action':'quiz_me','conversation_id':cid}).json()
    answered=client.post('/api/chat',json={'message':'56','conversation_id':cid}).json()
    assert answered['conversation_state']['mode']=='quiz_feedback'
    next_question=client.post('/api/chat',json={'message':'Siguiente','action':'next','conversation_id':cid}).json()
    assert next_question['conversation_state']['mode']=='quiz'
    assert next_question['conversation_state']['pending_question']!=quiz['conversation_state']['pending_question']
    assert '63' not in next_question['answer']
    saved=client.get(f'/api/conversations/{cid}').json()
    assert saved['messages'][0]['content']=='18 × 7'


def test_topic_switch_clears_previous_exercise(client):
    first=client.post('/api/chat',json={'message':'18 × 7'}).json()
    cid=first['conversation_id']
    new=client.post('/api/chat',json={'message':'¿Qué es una dirección IP?','conversation_id':cid}).json()
    assert new['conversation_state']['current_topic']=='Direcciones IP'
    assert not new['conversation_state']['active_exercise']
    reveal=client.post('/api/chat',json={'message':'Dame la respuesta','action':'reveal_answer','conversation_id':cid}).json()
    assert 'No tengo un ejercicio pendiente' in reveal['answer']
