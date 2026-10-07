import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import secrets
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .ai import LocalAI
from .database import Database, now
from .education import catalog, generate, grade
from .library import Library
from .schemas import LearningMemory, SavedAnswer, LibraryImport, QuizAnswer, Settings, Profile, Chat, QuizRequest, Submission, Card, Review, Study, CardGeneration, StudyPlanCreate, StudySessionEvent, GuideRequest, AdventureStart, AdventureEvent, SimulationCreate
from .security import safe_reply
from .prompts import declared_name, topic_title
from .conversation import prepare, advance, guard_action
from .study_planner import build_plan, cornell_guide, study_guide

ROOT=Path(__file__).resolve().parent.parent

def create_app(db_path=None, ai=None):
    local_root=Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'ALLEN'
    db=Database(db_path or os.environ.get('ALLEN_DB_PATH',local_root/'allen.sqlite3'))
    library=Library(ROOT/'data/library')
    engine=ai or LocalAI()
    token=secrets.token_urlsafe(32)
    privacy_epoch=0
    logger=logging.getLogger('allen')
    if not logger.handlers:
        db.path.parent.mkdir(parents=True,exist_ok=True)
        handler=RotatingFileHandler(db.path.parent/'allen.log',maxBytes=200000,backupCount=2,encoding='utf-8')
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

    @asynccontextmanager
    async def lifespan(app):
        db.prune()
        yield

    app=FastAPI(title='ALLEN local',docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.state.db=db
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','[::1]']+(['testserver'] if db_path else []))

    @app.middleware('http')
    async def local_guard(request,call_next):
        origin=request.headers.get('origin')
        if origin and origin != str(request.base_url).rstrip('/'):
            return JSONResponse({'error':'Abre Allen desde su dirección local.'},403)
        if request.headers.get('sec-fetch-site')=='cross-site':
            return JSONResponse({'error':'Abre Allen desde su dirección local.'},403)
        if request.method in ('POST','PUT','DELETE','PATCH'):
            if not secrets.compare_digest(request.headers.get('x-allen-token',''),token):
                return JSONResponse({'error':'Recarga Allen para continuar.'},403)
            try:
                if int(request.headers.get('content-length','0'))>200000:
                    return JSONResponse({'error':'El texto es demasiado largo.'},413)
            except ValueError:
                return JSONResponse({'error':'Solicitud no válida.'},400)
            body=await request.body()
            if len(body)>200000:
                return JSONResponse({'error':'El texto es demasiado largo.'},413)
        response=await call_next(request)
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='no-store'
        return response

    @app.exception_handler(RequestValidationError)
    async def validation(request,exc):
        return JSONResponse({'error':'Revisa los campos: hay un valor vacío, demasiado largo o fuera del rango permitido.'},422)

    @app.exception_handler(HTTPException)
    async def http_error(request,exc):
        return JSONResponse({'error':exc.detail},exc.status_code)

    @app.exception_handler(Exception)
    async def unexpected(request,exc):
        # Do not log user text, prompts, model responses or URL parameters.
        logger.error('Request failed: %s',type(exc).__name__)
        return JSONResponse({'error':'Allen tuvo un pequeño problema. Inténtalo de nuevo.'},500)

    def user(user_id):
        found=db.one('SELECT * FROM users WHERE id=?',(user_id,))
        if not found:
            raise HTTPException(404,'No encontramos ese perfil. Selecciona otro.')
        found['memory']=db.memory(user_id)
        return found

    @app.get('/api/bootstrap')
    def bootstrap():
        db.prune()
        return dict(token=token,profiles=[user(p['id']) for p in db.all('SELECT id FROM users')],settings=db.settings().model_dump(),catalog=catalog())

    @app.get('/api/fair/token')
    def fair_token():
        return {'token':token}

    @app.get('/api/health')
    def health():
        db.one('SELECT 1')
        return dict(application=True,database=True,library=len(library.documents()),internet='No se consulta Internet; el navegador informa de la red.')

    @app.get('/api/model/status')
    async def model_status():
        return await engine.status(db.settings())

    @app.get('/api/settings')
    def settings():
        return db.settings().model_dump()

    @app.put('/api/settings')
    def update_settings(value:Settings):
        nonlocal privacy_epoch
        if not value.save_history:
            privacy_epoch+=1
        db.execute('INSERT OR REPLACE INTO settings VALUES(1,?)',(value.model_dump_json(),))
        db.prune()
        return value.model_dump()

    @app.post('/api/profiles')
    def create_profile(value:Profile):
        if len(db.all('SELECT id FROM users'))>=20:
            raise HTTPException(400,'Este dispositivo ya tiene 20 perfiles.')
        uid=db.execute('INSERT INTO users(name,age,level,avatar) VALUES(?,?,?,?)',(value.name,value.age,value.level,value.avatar))
        db.remember(uid,onboarded=True)
        return user(uid)

    @app.put('/api/profiles/{uid}')
    def edit_profile(uid:int,value:Profile):
        user(uid)
        db.execute('UPDATE users SET name=?,age=?,level=?,avatar=? WHERE id=?',(value.name,value.age,value.level,value.avatar,uid))
        db.remember(uid,onboarded=True)
        return user(uid)

    @app.delete('/api/profiles/{uid}')
    def delete_profile(uid:int):
        nonlocal privacy_epoch
        privacy_epoch+=1
        user(uid); db.erase_profile(uid)
        return {'ok':True}

    @app.get('/api/memory')
    def memory(profile_id:int=1):
        user(profile_id)
        return db.memory(profile_id)

    @app.put('/api/memory')
    def update_memory(value:LearningMemory,profile_id:int=1):
        user(profile_id)
        memory=db.memory(profile_id)
        goal_date=date.today().isoformat() if value.set_goal or value.daily_goal!=memory['daily_goal'] else memory['goal_date']
        return db.remember(profile_id,**value.model_dump(exclude={'set_goal'}),goal_date=goal_date)

    @app.delete('/api/memory')
    def forget_memory(profile_id:int=1):
        nonlocal privacy_epoch
        privacy_epoch+=1
        user(profile_id)
        db.execute('DELETE FROM student_memory WHERE user_id=?',(profile_id,))
        return db.remember(profile_id,onboarded=True)

    @app.get('/api/saved')
    def saved(profile_id:int=1):
        user(profile_id)
        return db.all('SELECT * FROM saved_answers WHERE user_id=? ORDER BY id DESC LIMIT 200',(profile_id,))

    @app.post('/api/saved')
    def save_answer(value:SavedAnswer):
        user(value.profile_id)
        existing=db.one('SELECT id FROM saved_answers WHERE user_id=? AND content=?',(value.profile_id,value.content))
        if existing: return existing
        sid=db.execute('INSERT INTO saved_answers(user_id,title,content,created) VALUES(?,?,?,?)',(value.profile_id,value.title,value.content,now()))
        return {'id':sid}

    @app.delete('/api/saved/{sid}')
    def delete_saved(sid:int,profile_id:int=1):
        user(profile_id)
        db.execute('DELETE FROM saved_answers WHERE id=? AND user_id=?',(sid,profile_id))
        return {'ok':True}

    @app.get('/api/progress')
    def progress(profile_id:int=1):
        user(profile_id)
        return db.progress(profile_id)

    @app.post('/api/study')
    def study(value:Study):
        user(value.profile_id)
        db.execute('INSERT INTO learning_sessions(user_id,subject,seconds,created) VALUES(?,?,?,?)',(value.profile_id,value.subject,value.seconds,now()))
        db.award(value.profile_id,'study',value.subject,5,date.today().isoformat())
        return {'ok':True}


    @app.post('/api/study-plans')
    def create_study_plan(value:StudyPlanCreate):
        user(value.profile_id)
        quiz_rows=db.all('SELECT result FROM quiz_results WHERE user_id=? ORDER BY id DESC LIMIT 30',(value.profile_id,))
        cards=db.all('SELECT question,answer,due,interval FROM flashcards WHERE user_id=?',(value.profile_id,))
        try:
            plan=build_plan(value.subject,value.topics,value.deadline,value.minutes_per_day,value.level,value.goal,quiz_rows,cards,db.progress(value.profile_id))
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        pid=db.execute('INSERT INTO study_plans(user_id,subject,goal,deadline,minutes_per_day,level,topics,plan,created) VALUES(?,?,?,?,?,?,?,?,?)',
            (value.profile_id,value.subject,value.goal,value.deadline,value.minutes_per_day,value.level,json.dumps(value.topics,ensure_ascii=False),json.dumps(plan,ensure_ascii=False),now()))
        return {'id':pid,**plan}

    @app.get('/api/study-plans')
    def study_plans(profile_id:int=1):
        user(profile_id)
        rows=db.all('SELECT id,subject,goal,deadline,minutes_per_day,level,topics,plan,created FROM study_plans WHERE user_id=? ORDER BY id DESC LIMIT 50',(profile_id,))
        for row in rows:
            row['topics']=json.loads(row['topics']); row['plan']=json.loads(row['plan'])
        return rows

    @app.get('/api/study-plans/{pid}')
    def study_plan(pid:int,profile_id:int=1):
        user(profile_id)
        row=db.one('SELECT * FROM study_plans WHERE id=? AND user_id=?',(pid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese plan.')
        row['topics']=json.loads(row['topics']); row['plan']=json.loads(row['plan'])
        return row

    @app.post('/api/study-plans/{pid}/start')
    def start_study_plan(pid:int,profile_id:int=1):
        user(profile_id)
        row=db.one('SELECT * FROM study_plans WHERE id=? AND user_id=?',(pid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese plan.')
        today=date.today().isoformat()
        existing=db.one('SELECT * FROM study_sessions WHERE plan_id=? AND user_id=? AND day=?',(pid,profile_id,today))
        if existing: return existing
        sid=db.execute('INSERT INTO study_sessions(user_id,plan_id,day,status,started) VALUES(?,?,?,?,?)',(profile_id,pid,today,'active',now()))
        return db.one('SELECT * FROM study_sessions WHERE id=?',(sid,))

    @app.post('/api/study-sessions/{sid}/event')
    def study_session_event(sid:int,value:StudySessionEvent):
        user(value.profile_id)
        session=db.one('SELECT * FROM study_sessions WHERE id=? AND user_id=?',(sid,value.profile_id))
        if not session: raise HTTPException(404,'No encontramos esa sesión.')
        db.execute('INSERT INTO study_session_events(user_id,session_id,kind,activity_index,note,created) VALUES(?,?,?,?,?,?)',
            (value.profile_id,sid,value.kind,value.activity_index,value.note,now()))
        fields=['current_activity_index=?','last_activity_at=?']; args=[value.activity_index,now()]
        status=session['status']
        completed=session.get('activities_completed',0); skipped=session.get('activities_skipped',0); difficulties=session.get('difficulties',0); hints=session.get('hints_used',0)
        if value.kind=='completed': completed+=1; status='completed'
        elif value.kind=='skipped': skipped+=1
        elif value.kind=='not_understood': difficulties+=1
        elif value.kind=='hint': hints+=1
        elif value.kind=='paused': status='paused'
        if status!='completed' and value.kind not in ('completed','paused'): status='active'
        fields += ['activities_completed=?','activities_skipped=?','difficulties=?','hints_used=?','status=?']
        args += [completed,skipped,difficulties,hints,status]
        if status=='completed': fields.append('completed=?'); args.append(now())
        args.append(sid)
        db.execute('UPDATE study_sessions SET '+','.join(fields)+' WHERE id=?',tuple(args))
        return db.one('SELECT * FROM study_sessions WHERE id=?',(sid,))


    @app.get('/api/continuity')
    def continuity(profile_id:int=1):
        user(profile_id)
        adventure=db.one("SELECT * FROM adventure_sessions WHERE user_id=? AND status IN ('active','paused') ORDER BY updated_at DESC LIMIT 1",(profile_id,))
        session=db.one("SELECT ss.*,sp.subject,sp.goal,sp.deadline,sp.plan FROM study_sessions ss JOIN study_plans sp ON sp.id=ss.plan_id WHERE ss.user_id=? AND ss.status IN ('active','paused') ORDER BY COALESCE(ss.last_activity_at,ss.started) DESC LIMIT 1",(profile_id,))
        if session: session['plan']=json.loads(session['plan'])
        plan=db.one("SELECT * FROM study_plans WHERE user_id=? ORDER BY id DESC LIMIT 1",(profile_id,))
        if plan:
            plan['topics']=json.loads(plan['topics']); plan['plan']=json.loads(plan['plan'])
        due_cards=db.one("SELECT count(*) n FROM flashcards WHERE user_id=? AND due<=?",(profile_id,date.today().isoformat()))['n']
        memory=db.memory(profile_id)
        recommendation=None
        if adventure: recommendation='Continúa tu aventura desde el punto exacto donde la dejaste.'
        elif session: recommendation='Retoma tu Sesión Allen antes de empezar algo nuevo.'
        elif due_cards: recommendation=f'Tienes {due_cards} tarjetas listas para repasar.'
        elif memory.get('difficult_topics'): recommendation='Podemos reforzar '+memory['difficult_topics'][-1]+'.'
        elif memory.get('recent_topics'): recommendation='Puedes profundizar en '+memory['recent_topics'][-1]+'.'
        return dict(adventure=adventure,study_session=session,study_plan=plan,due_cards=due_cards,recommendation=recommendation)

    @app.post('/api/adventures/start')
    def start_adventure(value:AdventureStart):
        user(value.profile_id)
        current=db.one("SELECT * FROM adventure_sessions WHERE user_id=? AND adventure_id=? AND status IN ('active','paused') ORDER BY id DESC LIMIT 1",(value.profile_id,value.adventure_id))
        if current:
            db.execute("UPDATE adventure_sessions SET status='active',updated_at=? WHERE id=?",(now(),current['id']))
            return db.one('SELECT * FROM adventure_sessions WHERE id=?',(current['id'],))
        sid=db.execute("INSERT INTO adventure_sessions(user_id,adventure_id,status,current_step,completed_steps,answers,mistakes,hints_used,started_at,updated_at) VALUES(?,?, 'active',0,0,'[]',0,0,?,?)",(value.profile_id,value.adventure_id,now(),now()))
        return db.one('SELECT * FROM adventure_sessions WHERE id=?',(sid,))

    @app.get('/api/adventures/active')
    def active_adventure(profile_id:int=1):
        user(profile_id)
        return db.one("SELECT * FROM adventure_sessions WHERE user_id=? AND status IN ('active','paused') ORDER BY updated_at DESC LIMIT 1",(profile_id,))

    @app.post('/api/adventures/{sid}/event')
    def adventure_event(sid:int,value:AdventureEvent):
        user(value.profile_id)
        row=db.one('SELECT * FROM adventure_sessions WHERE id=? AND user_id=?',(sid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos esa aventura.')
        answers=json.loads(row['answers'] or '[]'); mistakes=row['mistakes']; hints=row['hints_used']; status=row['status']; completed=row['completed_steps']; current=row['current_step']; completed_at=row['completed_at']
        if value.event=='answer':
            answers.append(dict(step=value.step,answer=value.answer,correct=value.correct))
            if value.correct is False: mistakes+=1
        elif value.event=='hint': hints+=1
        elif value.event=='advance': current=max(current,value.step); completed=max(completed,value.step)
        elif value.event=='pause': status='paused'
        elif value.event=='resume': status='active'
        elif value.event=='complete': status='completed'; completed_at=now()
        elif value.event=='abandon': status='abandoned'; completed_at=now()
        db.execute('INSERT INTO adventure_events(user_id,session_id,event,step,answer,correct,created) VALUES(?,?,?,?,?,?,?)',(value.profile_id,sid,value.event,value.step,value.answer,None if value.correct is None else int(value.correct),now()))
        db.execute('UPDATE adventure_sessions SET status=?,current_step=?,completed_steps=?,answers=?,mistakes=?,hints_used=?,updated_at=?,completed_at=? WHERE id=?',(status,current,completed,json.dumps(answers,ensure_ascii=False),mistakes,hints,now(),completed_at,sid))
        return db.one('SELECT * FROM adventure_sessions WHERE id=?',(sid,))

    @app.post('/api/simulations')
    def create_simulation(value:SimulationCreate):
        user(value.profile_id)
        topic=value.topics[0]
        request=QuizRequest(profile_id=value.profile_id,subject=value.subject,topic=topic,difficulty='Normal',count=value.question_count,kind='multiple')
        questions=generate(request)
        sid=db.execute('INSERT INTO simulation_results(user_id,subject,topics,questions,result,minutes,started_at) VALUES(?,?,?,?,NULL,?,?)',(value.profile_id,value.subject,json.dumps(value.topics,ensure_ascii=False),json.dumps(questions,ensure_ascii=False),value.minutes,now()))
        return dict(id=sid,subject=value.subject,topics=value.topics,questions=questions,minutes=value.minutes)

    @app.post('/api/simulations/{sid}/submit')
    def submit_simulation(sid:int,value:Submission):
        user(value.profile_id)
        row=db.one('SELECT * FROM simulation_results WHERE id=? AND user_id=?',(sid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos ese simulacro.')
        questions=json.loads(row['questions'])
        result=grade(questions,value.answers)
        db.execute('UPDATE simulation_results SET result=?,completed_at=? WHERE id=?',(json.dumps(result,ensure_ascii=False),now(),sid))
        weak=result.get('review',[]) if isinstance(result,dict) else []
        return dict(**result,reinforcement=dict(topics=weak,activities=[dict(type='explanation',minutes=10),dict(type='practice',minutes=15),dict(type='flashcards',minutes=5)] if weak else []))

    @app.post('/api/guides/cornell')
    def cornell(value:GuideRequest):
        user(value.profile_id)
        return cornell_guide(value.text,value.title)

    @app.post('/api/guides/study')
    def guide(value:GuideRequest):
        user(value.profile_id)
        return study_guide(value.text,value.title)

    @app.get('/api/conversations')
    def conversations(profile_id:int=1):
        user(profile_id); db.prune()
        return db.all('SELECT id,title,updated FROM conversations WHERE user_id=? ORDER BY updated DESC LIMIT 100',(profile_id,))

    @app.get('/api/conversations/{cid}')
    def conversation(cid:int,profile_id:int=1):
        db.prune()
        row=db.one('SELECT * FROM conversations WHERE id=? AND user_id=?',(cid,profile_id))
        if not row:
            raise HTTPException(404,'La conversación ya no está guardada.')
        row['messages']=json.loads(row['messages'])
        saved=db.one('SELECT value FROM conversation_states WHERE conversation_id=?',(cid,))
        row['conversation_state']=json.loads(saved['value']) if saved else None
        return row

    @app.delete('/api/conversations/{cid}')
    def delete_conversation(cid:int,profile_id:int=1):
        db.execute('DELETE FROM conversations WHERE id=? AND user_id=?',(cid,profile_id))
        return {'ok':True}

    async def chat_response(value:Chat,stream:bool):
        starting_epoch=privacy_epoch
        profile=user(value.profile_id)
        name=declared_name(value.message)
        if name:
            db.execute('UPDATE users SET name=? WHERE id=?',(name,value.profile_id))
            db.remember(value.profile_id,onboarded=True)
            profile=user(value.profile_id)
        db.prune()
        if value.conversation_id:
            row=db.one('SELECT messages FROM conversations WHERE id=? AND user_id=?',(value.conversation_id,value.profile_id))
            if not row:
                raise HTTPException(404,'La conversación ya no está disponible. Inicia una nueva.')
            if not value.history and not value.regenerate:
                value=Chat.model_validate({**value.model_dump(),'history':json.loads(row['messages'])})
        stored=db.one('SELECT value FROM conversation_states WHERE conversation_id=?',(value.conversation_id,)) if value.conversation_id else None
        value=prepare(value,json.loads(stored['value']) if stored else None)
        sources=library.search(value.message,2,custom_documents(value.profile_id)) if value.use_library else []

        async def events():
            answer=''; demo=False
            try:
                async for event in engine.answer(value,profile,db.settings(),sources):
                    if event['type']=='meta':
                        demo=event.get('demo',False)
                    if event['type']=='delta':
                        answer+=event['text']
                    yield event
                if not answer:
                    raise RuntimeError('empty response')
                completed_state=advance(value.conversation_state,value.message,value.action,answer) if not demo and not guard_action(value) else value.conversation_state
                cid=value.conversation_id
                if starting_epoch==privacy_epoch and db.one('SELECT id FROM users WHERE id=?',(value.profile_id,)):
                    topic=topic_title(value.message)
                    if topic=='Conversación con Allen':
                        topic=next((topic_title(m.content) for m in reversed(value.history) if m.role=='user' and topic_title(m.content)!='Conversación con Allen'),topic)
                    memory=db.memory(value.profile_id)
                    if topic!='Conversación con Allen':
                        recent=[t for t in memory['recent_topics'] if t!=topic]+[topic]
                        difficult=memory['difficult_topics']
                        if value.action in ('dont_understand','lost','simplify'): difficult=[t for t in difficult if t!=topic]+[topic]
                        db.remember(value.profile_id,recent_topics=recent[-12:],difficult_topics=difficult[-12:])
                if starting_epoch==privacy_epoch and db.settings().save_history and db.one('SELECT id FROM users WHERE id=?',(value.profile_id,)):
                    messages=[m.model_dump() for m in value.history]+[{'role':'user','content':value.message},{'role':'assistant','content':answer}]
                    packed=json.dumps(messages[-30:],ensure_ascii=False)
                    if cid:
                        # Do not resurrect a deleted conversation during generation.
                        db.execute("UPDATE conversations SET messages=?,updated=?,title=CASE WHEN title='Conversación con Allen' THEN ? ELSE title END WHERE id=? AND user_id=?",(packed,now(),topic,cid,value.profile_id))
                    else:
                        cid=db.execute('INSERT INTO conversations(user_id,title,messages,updated) VALUES(?,?,?,?)',(value.profile_id,topic,packed,now()))
                    if cid and db.one('SELECT id FROM conversations WHERE id=? AND user_id=?',(cid,value.profile_id)):
                        db.execute('INSERT OR REPLACE INTO conversation_states(conversation_id,value) VALUES(?,?)',(cid,completed_state.model_dump_json()))
                yield dict(type='done',conversation_id=cid,conversation_state=completed_state.model_dump(),demo=demo,sources=[{'title':s['title'],'id':s['id']} for s in sources])
            except asyncio.CancelledError:
                raise
            except ValueError as exc:
                # Only our deliberate friendly errors may be exposed.
                message=str(exc) if str(exc).startswith(('El texto es largo','La respuesta fue')) else 'La IA local envió una respuesta que Allen no pudo leer. Inténtalo de nuevo.'
                yield dict(type='error',message=message)
            except Exception as exc:
                logger.warning('AI request failed: %s',type(exc).__name__)
                yield dict(type='error',message='Allen perdió la conexión con su cerebro local. Revisa que la IA esté iniciada e inténtalo de nuevo.')

        if stream:
            async def encoded():
                async for event in events():
                    yield json.dumps(event,ensure_ascii=False)+'\n'
            return StreamingResponse(encoded(),media_type='application/x-ndjson')
        result={'ok':True,'answer':'','offline':True}
        async for event in events():
            if event['type']=='delta':result['answer']+=event['text']
            elif event['type']=='error':return JSONResponse({'error':event['message']},503)
            else:result.update({k:v for k,v in event.items() if k!='type'})
        return result

    @app.post('/api/chat')
    async def chat(value:Chat,stream:bool=False):
        return await chat_response(value,stream)

    @app.post('/api/tutor')
    async def tutor(value:Chat):
        return await chat_response(value.model_copy(update={'mode':'Tutor'}),False)

    @app.post('/api/summarize')
    async def summarize(value:Chat):
        return await chat_response(value.model_copy(update={'mode':'Resumir'}),False)

    @app.post('/api/translate')
    async def translate(value:Chat):
        return await chat_response(value.model_copy(update={'mode':'Idiomas'}),False)

    def custom_documents(profile_id):
        return [dict(d,id=f"custom:{row['id']}:{i}",pack_id=row['id']) for row in db.all('SELECT * FROM library_packs WHERE user_id=?',(profile_id,)) for i,d in enumerate(json.loads(row['documents']))]

    @app.get('/api/library')
    def search_library(q:str=Query('',max_length=200),profile_id:int=1):
        user(profile_id)
        return library.search(q,100,custom_documents(profile_id))

    @app.get('/api/library/packs')
    def library_packs(profile_id:int=1):
        user(profile_id)
        return db.all('SELECT id,title FROM library_packs WHERE user_id=?',(profile_id,))

    @app.post('/api/library/import')
    def import_library(value:LibraryImport):
        user(value.profile_id)
        suffix=Path(value.filename).suffix.lower()
        if suffix not in ('.json','.md','.txt'): raise HTTPException(422,'Elige un archivo JSON, Markdown o TXT.')
        try:
            items=json.loads(value.content) if suffix=='.json' else [{'title':Path(value.filename).stem,'content':value.content,'subject':'Mis lecturas'}]
            if isinstance(items,dict): items=[items]
            if not isinstance(items,list) or not 1<=len(items)<=100: raise ValueError()
            docs=[]
            for item in items:
                if not isinstance(item,dict) or not isinstance(item.get('content'),str) or not item['content'].strip() or len(item['content'])>20000: raise ValueError()
                docs.append(dict(title=str(item.get('title',Path(value.filename).stem))[:200],subject=str(item.get('subject','Mis lecturas'))[:60],content=item['content']))
        except (ValueError,TypeError): raise HTTPException(422,'Usa un objeto o lista JSON con title, subject y content; cada lectura admite hasta 20.000 caracteres.')
        pack_id=db.execute('INSERT INTO library_packs(user_id,title,documents) VALUES(?,?,?)',(value.profile_id,value.filename,json.dumps(docs,ensure_ascii=False)))
        return dict(id=pack_id,count=len(docs))

    @app.delete('/api/library/packs/{pack_id}')
    def delete_library(pack_id:int,profile_id:int=1):
        user(profile_id)
        if not db.one('SELECT id FROM library_packs WHERE id=? AND user_id=?',(pack_id,profile_id)): raise HTTPException(404,'No encontramos esa biblioteca.')
        db.execute('DELETE FROM library_packs WHERE id=? AND user_id=?',(pack_id,profile_id))
        return {'ok':True}

    @app.post('/api/quiz/{qid}/answer')
    def check_answer(qid:int,value:QuizAnswer):
        row=db.one('SELECT questions FROM quiz_results WHERE id=? AND user_id=?',(qid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos ese quiz.')
        questions=json.loads(row['questions'])
        if value.index>=len(questions): raise HTTPException(422,'Esa pregunta no existe.')
        return grade([questions[value.index]],[value.answer])['feedback'][0]

    @app.post('/api/quiz')
    def quiz(value:QuizRequest):
        user(value.profile_id)
        try:questions=generate(value)
        except ValueError as exc:raise HTTPException(422,str(exc))
        qid=db.execute('INSERT INTO quiz_results(user_id,config,questions,created) VALUES(?,?,?,?)',(value.profile_id,value.model_dump_json(),json.dumps(questions,ensure_ascii=False),now()))
        return dict(id=qid,questions=[{k:v for k,v in q.items() if k not in ('answer','explanation')} for q in questions],source='Banco local',actual_count=len(questions))

    @app.post('/api/quiz/{qid}/submit')
    def submit(qid:int,value:Submission):
        with db.connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            row=conn.execute('SELECT * FROM quiz_results WHERE id=? AND user_id=?',(qid,value.profile_id)).fetchone()
            if not row:raise HTTPException(404,'No encontramos ese quiz.')
            if row['result']:return json.loads(row['result'])
            try:result=grade(json.loads(row['questions']),value.answers)
            except ValueError as exc:raise HTTPException(422,str(exc))
            conn.execute('UPDATE quiz_results SET result=? WHERE id=?',(json.dumps(result,ensure_ascii=False),qid))
            config=json.loads(row['config'])
            kind='exercise' if config['count']==1 else 'quiz'
            conn.execute('INSERT OR IGNORE INTO progress(user_id,kind,subject,xp,day,reference) VALUES(?,?,?,?,?,?)',(value.profile_id,kind,config['subject'],10 if kind=='exercise' else 30,date.today().isoformat(),str(qid)))
        return result

    @app.get('/api/quiz/results')
    def results(profile_id:int=1):
        user(profile_id)
        return [dict(id=r['id'],created=r['created'],config=json.loads(r['config']),result=json.loads(r['result'])) for r in db.all('SELECT * FROM quiz_results WHERE user_id=? AND result IS NOT NULL ORDER BY id DESC LIMIT 30',(profile_id,))]

    @app.get('/api/flashcards')
    def cards(profile_id:int=1):
        user(profile_id)
        return db.all('SELECT * FROM flashcards WHERE user_id=? ORDER BY due,id',(profile_id,))

    @app.post('/api/flashcards')
    def create_card(value:Card):
        user(value.profile_id)
        cid=db.execute('INSERT INTO flashcards(user_id,question,answer,due) VALUES(?,?,?,?)',(value.profile_id,value.question,value.answer,date.today().isoformat()))
        return {'id':cid}

    @app.post('/api/flashcards/generate')
    async def generate_cards(value:CardGeneration):
        profile=user(value.profile_id)
        if safe_reply(value.source):
            raise HTTPException(422,'Elige un tema educativo seguro para tus tarjetas.')
        settings=db.settings()
        if not (await engine.status(settings))['connected']:
            raise HTTPException(409,'Necesitas conectar la IA local para generar tarjetas. Puedes crearlas manualmente sin Internet.')
        request=Chat(profile_id=value.profile_id,message=value.source,mode='Resumir',
                     option=f'Genera {value.count} tarjetas desde {value.kind}. Devuelve SOLO un array JSON con question y answer, sin Markdown.')
        raw=''
        try:
            async for event in engine.answer(request,profile,settings,[]):
                if event.get('demo') or event.get('safety'):
                    raise ValueError('unavailable')
                if event['type']=='delta':raw+=event['text']
            raw=raw.strip()
            if raw.startswith('```'):
                raw=raw.split('\n',1)[1].rsplit('```',1)[0].strip()
            parsed=json.loads(raw)
            if not isinstance(parsed,list) or not 1<=len(parsed)<=10:raise ValueError('shape')
            cards=[Card(profile_id=value.profile_id,**item) for item in parsed[:value.count]]
            if any(safe_reply(c.question+' '+c.answer) for c in cards):raise ValueError('safety')
            return {'cards':[c.model_dump(exclude={'profile_id'}) for c in cards]}
        except Exception as exc:
            logger.warning('Card generation failed: %s',type(exc).__name__)
            raise HTTPException(422,'Allen no pudo crear tarjetas válidas. Prueba un texto más corto o créalas manualmente.')

    @app.post('/api/flashcards/{cid}/review')
    def review_card(cid:int,value:Review):
        row=db.one('SELECT * FROM flashcards WHERE id=? AND user_id=?',(cid,value.profile_id))
        if not row:raise HTTPException(404,'No encontramos esa tarjeta.')
        interval={'No la sé':0,'Difícil':1,'Bien':max(3,row['interval']*2),'Fácil':max(7,row['interval']*3)}[value.rating]
        interval=min(interval,180)
        due=(date.today()+timedelta(days=interval)).isoformat()
        db.execute('UPDATE flashcards SET interval=?,due=?,reviews=reviews+1 WHERE id=?',(interval,due,cid))
        db.award(value.profile_id,'card','Tarjetas',5,f'{cid}:{date.today().isoformat()}')
        return {'due':due}

    @app.delete('/api/flashcards/{cid}')
    def delete_card(cid:int,profile_id:int=1):
        db.execute('DELETE FROM flashcards WHERE id=? AND user_id=?',(cid,profile_id))
        return {'ok':True}

    @app.get('/')
    def index(mode:str=''):return FileResponse(ROOT/('frontend/fair.html' if mode=='fair' else 'frontend/index.html'))

    from .fair import install_fair
    install_fair(app,db,engine)

    @app.get('/fair')
    def fair_index():return FileResponse(ROOT/'frontend/fair.html')

    app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')
    return app

app=create_app()
