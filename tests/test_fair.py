import tempfile
import unittest
import json
import logging
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
        self.client.headers['X-Allen-Token']=self.client.get('/api/bootstrap').json()['token']
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
        timed_out=self.client.post('/api/fair/chat',json={'session':new,'chat':{'message':'Quiero aprender Python'},'name':'Daniel'})
        self.assertEqual(timed_out.status_code,504)
        self.assertIn('TIMEOUT',timed_out.json()['error'])
        self.assertEqual(self.client.post('/api/fair/challenge',json={'session':new}).status_code,200)
    def test_evaluation_diagnostics_log_error_and_redacted_response(self):
        result=self.client.post('/api/fair/evaluation-log',json={'project_id':'steam:semaforo','endpoint':'/api/fair/chat','http_status':200,'duration_ms':1400,'prompt_bytes':2300,'response':'No pude evaluar. contacto estudiante@example.org','error':'JSON inválido'})
        self.assertEqual(result.status_code,200,result.text)
        logger=logging.getLogger('allen.steam_evaluation')
        log_path=next(Path(h.baseFilename) for h in logger.handlers if hasattr(h,'baseFilename') and h.baseFilename.endswith('steam-evaluation.log'))
        rows=[json.loads(line) for line in log_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        self.assertEqual(rows[-1]['project_id'],'steam:semaforo')
        self.assertIn('[email]',rows[-1]['response'])
        self.assertNotIn('estudiante@example.org',log_path.read_text(encoding='utf-8'))
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
        unavailable=self.client.post('/api/fair/chat',json=payload)
        self.assertEqual(unavailable.status_code,503)
        self.assertIn('IA_LOCAL_UNAVAILABLE',unavailable.json()['error'])
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

    def test_all_local_datasets_and_anonymous_aggregate_extensions(self):
        from backend.fair import DATASETS
        for dataset in DATASETS:
            response=self.client.get('/api/fair/data/'+dataset)
            self.assertEqual(response.status_code,200,dataset)
        self.assertEqual(self.client.get('/api/fair/data/secrets').status_code,404)
        for kind in ['simulation','game','project','activity','project_completed','route']:
            response=self.client.post('/api/fair/event',json={'session':self.sid,'kind':kind})
            self.assertEqual(response.status_code,200,response.text)
        summary=self.client.get('/api/fair/stats').json()['eventStats']
        self.assertEqual(summary['simulations'],1)
        self.assertEqual(summary['games'],1)
        self.assertEqual(summary['activitiesCompleted'],1)
        self.assertNotIn('name',str(summary))
        for table in ['fair_simulations','fair_games','fair_projects','fair_activities','fair_projects_completed','fair_routes']:
            self.assertEqual([r['name'] for r in self.app.state.db.all(f'PRAGMA table_info({table})')],['day','count','seconds'])

    def test_fair_is_default_and_study_is_preserved(self):
        self.assertIn('fair.js',self.client.get('/').text)
        self.assertIn('app.js',self.client.get('/study').text)
        fair=self.client.get('/fair').text
        self.assertNotIn('Presentador',fair)

    def test_educational_prompt_fits_default_model_and_uses_visitor_level(self):
        from backend.schemas import Chat,Settings
        from backend.prompts import system_prompt
        from backend.conversation import prepare
        request=prepare(Chat(message='Explícame qué es Python',option='Feria educativa: ejemplo'))
        profile={'name':'Daniel','level':'Primaria'}
        messages=self.ai.messages(request,profile,Settings(),[])
        self.assertIn('Daniel',messages[0]['content'])
        self.assertIn('Palabras sencillas',system_prompt(request,profile,[]))
        self.assertEqual(messages[-1]['content'],'Explícame qué es Python')

    def test_project_idea_prompt_covers_varied_projects_without_affecting_other_chat(self):
        from backend.schemas import Chat
        from backend.prompts import system_prompt
        from backend.conversation import prepare
        examples=[
            'Dame una idea de proyecto: detector de humedad para plantas.',
            'Dame una idea de proyecto de semáforo con LEDs.',
            'Dame una idea de proyecto de alarma con sensor de movimiento.',
            'Dame una idea de proyecto de Python para principiantes.',
            'Dame una idea de proyecto de ciberseguridad básica.',
        ]
        for message in examples:
            with self.subTest(message=message):
                request=prepare(Chat(message=message,option='Feria educativa: responde primero con claridad.'))
                prompt=system_prompt(request,{'name':'Daniel','level':'Premedia'},[])
                self.assertIn('2–4 párrafos breves',prompt)
                self.assertIn('No inventes capacidades ni exageres el impacto',prompt)
                for robotic in ('Comentario complementario','Análisis adicional','Observación técnica','Conclusión:'):
                    self.assertNotIn(robotic,prompt)
                self.assertIn('si agregas',prompt)
                if 'ciberseguridad' not in message:
                    self.assertNotIn('esta idea concreta de ciberseguridad',prompt)
        ordinary=prepare(Chat(message='¿Qué es la fotosíntesis?',option='Feria educativa: responde primero con claridad.'))
        self.assertNotIn('Estilo para IDEAS Y EXPLICACIONES DE PROYECTOS',system_prompt(ordinary,{'name':'Daniel','level':'Premedia'},[]))

    def test_project_idea_prompt_remains_with_short_followup_in_project_chat(self):
        from backend.schemas import Chat,Message
        from backend.prompts import system_prompt
        from backend.conversation import prepare
        request=prepare(Chat(message='¿Cómo lo puedo mejorar?',history=[Message(role='user',content='Dame una idea de proyecto de Python.')],option='Feria educativa: responde primero con claridad.'))
        self.assertIn('Estilo para IDEAS Y EXPLICACIONES DE PROYECTOS',system_prompt(request,{'name':'Daniel','level':'Premedia'},[]))

    def test_five_project_ideas_use_grounded_natural_catalog_responses(self):
        examples=[
            ('Dame una idea de proyecto: detector de humedad para plantas.','Detector de humedad para plantas'),
            ('Dame una idea de proyecto de semáforo con LEDs.','Semáforo con Arduino'),
            ('Dame una idea de proyecto de alarma con sensor de movimiento.','Detector de movimiento con alarma'),
            ('Dame una idea de proyecto de Python para principiantes.','Chatbot educativo local simple'),
            ('Dame una idea de proyecto de ciberseguridad básica.','Simulador de phishing educativo'),
        ]
        for message,expected in examples:
            with self.subTest(message=message):
                response=self.client.post('/api/fair/chat',json={'session':self.sid,'name':'Daniel','chat':{'message':message}})
                self.assertEqual(response.status_code,200,response.text)
                result=response.json()
                self.assertEqual(result['source'],'project_catalog')
                self.assertIn(expected,result['text'])
                self.assertIn('puedes practicar',result['text'])
                self.assertIn('Por ejemplo',result['text'])
                self.assertRegex(result['text'],r'Después|Si luego')
                self.assertNotRegex(result['text'].lower(),r'comentario complementario|análisis adicional|observación técnica|conclusión:')
        plant=self.client.post('/api/fair/chat',json={'session':self.sid,'chat':{'message':examples[0][0]}}).json()['text'].lower()
        self.assertNotRegex(plant,r'ciberseguridad|inundaci|salva cultivos|humedad del aire')
        semaphore=self.client.post('/api/fair/chat',json={'session':self.sid,'chat':{'message':examples[1][0]}}).json()['text'].lower()
        self.assertNotIn('movimiento',semaphore)
        generic=self.client.post('/api/fair/chat',json={'session':self.sid,'chat':{'message':'Dame una idea de proyecto de horno solar para principiantes.'}}).json()
        self.assertEqual(generic['source'],'project_catalog')
        self.assertIn('horno solar',generic['text'].lower())
        self.assertIn('boceto o una simulación',generic['text'])
        self.assertIn('cambiando una sola cosa',generic['text'])

    def test_normal_chat_prompt_fits_default_4096_context(self):
        from backend.schemas import Chat,Settings
        from backend.ai import LocalAI
        from backend.conversation import prepare
        request=prepare(Chat(message='¿Qué es una variable?',mode='Explicar'))
        messages=LocalAI().messages(request,{'name':'Explorador','level':'Premedia','memory':{}},Settings(),[])
        budget=Settings().context_size-Settings().max_tokens-256
        self.assertLessEqual(sum(len(message['content'].encode('utf-8')) for message in messages),budget)

    def test_verified_intro_is_precise_and_does_not_hijack_other_python_questions(self):
        from backend.fair import verified_intro
        text=verified_intro('Explícame qué es Python','Premedia','Daniel')
        self.assertIn('lenguaje de programación',text)
        self.assertIn('print',text)
        self.assertNotIn('mono',text)
        self.assertIsNone(verified_intro('¿Por qué mi código Python falla?','Premedia'))
        result=self.client.post('/api/fair/chat',json={'session':self.sid,'name':'Daniel','chat':{'message':'Explícame qué es Python'}}).json()
        self.assertEqual(result['source'],'local_lesson')
        self.assertIn('Daniel',result['text'])

if __name__=='__main__':unittest.main()
