import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import httpx
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.ai import LocalAI
from backend.fair import BANK

class FairTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.ai=LocalAI(httpx.MockTransport(lambda request:httpx.Response(503)))
        self.app=create_app(Path(self.temp.name)/'fair.sqlite3',self.ai)
        self.client=TestClient(self.app)
        self.client.headers['X-Allen-Token']=self.client.get('/api/fair/token').json()['token']
        self.sid=self.client.post('/api/fair/sessions',json={}).json()['session']
    def tearDown(self):
        self.client.close();self.temp.cleanup()
    def test_routes_and_protection(self):
        for path in ['/','/fair','/?mode=fair','/static/fair.js']:
            self.assertEqual(self.client.get(path).status_code,200)
        self.assertIn('fair.js',self.client.get('/?mode=fair').text)
        self.assertEqual(self.client.post('/api/fair/sessions',json={},headers={'X-Allen-Token':''}).status_code,403)
        self.assertEqual(set(self.client.get('/api/fair/token').json()),{'token'})
    def test_qr_local_and_invalid_protocol(self):
        response=self.client.get('/api/fair/qr',params={'url':'https://github.com/abdiellzz/allen'})
        self.assertEqual(response.status_code,200)
        self.assertIn('<svg',response.text)
        self.assertIn('<path',response.text)
        self.assertEqual(self.client.get('/api/fair/qr',params={'url':'javascript:alert(1)'}).status_code,422)
    def test_expired_session_and_engine_failure_recover(self):
        with patch('backend.fair.time.monotonic',return_value=10**12):
            self.assertEqual(self.client.post('/api/fair/event',json={'session':self.sid,'kind':'heartbeat'}).status_code,410)
        new=self.client.post('/api/fair/sessions',json={}).json()['session']
        async def failed(*args):
            raise TimeoutError('simulated')
            yield
        self.ai.answer=failed
        self.assertEqual(self.client.post('/api/fair/chat',json={'session':new,'chat':{'message':'hola'}}).status_code,503)
        self.assertEqual(self.client.post('/api/fair/challenge',json={'session':new}).status_code,200)
    def test_challenge_once_and_stats(self):
        result=self.client.post('/api/fair/challenge',json={'session':self.sid,'category':'Matemáticas'}).json()
        self.assertEqual(len(result['questions']),3)
        self.assertNotIn('correct',result['questions'][0])
        for i in range(3):
            response=self.client.post('/api/fair/answer',json={'session':self.sid,'index':i,'choice':BANK['Matemáticas'][i][2]})
            self.assertTrue(response.json()['correct'])
        self.assertEqual(response.json()['score'],3)
        self.assertEqual(self.client.post('/api/fair/answer',json={'session':self.sid,'index':2,'choice':0}).status_code,409)
        stats=self.client.get('/api/fair/stats').json()
        self.assertEqual(stats['fair_challenges']['count'],1)
    def test_chat_does_not_persist_and_reset_revokes(self):
        response=self.client.post('/api/fair/chat',json={'session':self.sid,'chat':{'message':'Yo me llamo Privado'}})
        self.assertEqual(response.status_code,200,response.text)
        self.assertIn('Privado',response.json()['text'])
        db=self.app.state.db
        for table in ['conversations','student_memory','saved_answers','conversation_states','progress']:
            self.assertEqual(db.all(f'SELECT * FROM {table}'),[])
        self.client.post('/api/fair/end',json={'session':self.sid})
        self.assertEqual(self.client.post('/api/fair/chat',json={'session':self.sid,'chat':{'message':'hola'}}).status_code,410)
        self.assertEqual(self.client.get('/api/fair/stats').json()['fair_questions']['count'],1)
    def test_demo_and_reconnect(self):
        payload={'session':self.sid,'chat':{'message':'Explícame la fotosíntesis'}}
        self.assertTrue(self.client.post('/api/fair/chat',json=payload).json()['demo'])
        def online(request):
            if request.url.path=='/health':return httpx.Response(200,json={})
            if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':'test'}]})
            return httpx.Response(200,text='data: {"choices":[{"delta":{"content":"Una explicación local."}}]}\n\ndata: [DONE]\n\n')
        self.ai.transport=httpx.MockTransport(online)
        response=self.client.post('/api/fair/chat',json=payload)
        self.assertEqual(response.status_code,200,response.text)
        self.assertFalse(response.json()['demo'])
        self.assertIn('explicación local',response.json()['text'])
    def test_lesson_count_is_idempotent_and_no_identity_columns(self):
        for _ in range(2):self.client.post('/api/fair/event',json={'session':self.sid,'kind':'lesson'})
        self.assertEqual(self.client.get('/api/fair/stats').json()['fair_quizzes']['count'],1)
        for table in ['fair_sessions','fair_questions','fair_quizzes','fair_challenges']:
            self.assertEqual([r['name'] for r in self.app.state.db.all(f'PRAGMA table_info({table})')],['day','count','seconds'])

if __name__=='__main__':unittest.main()
