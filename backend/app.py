import hashlib
import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import secrets
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import httpx
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .ai import LocalAI
from .database import Database, now
from .education import catalog, generate, grade
from .library import Library
from .schemas import LearningMemory, SavedAnswer, LibraryImport, QuizAnswer, Settings, Profile, Chat, QuizRequest, Submission, Card, Review, Study, CardGeneration, StudyPlanCreate, StudySessionEvent, GuideRequest, AdventureStart, AdventureEvent, SimulationCreate, SimulationProgress, TeacherImport, CourseReview, CoursePublish, CourseEnroll, CourseProgress, CoursePackImport, CourseHelp, CourseExamProgress, CourseVersionImport, RecoveryRestore, TeacherPin, LicenseActivation
from .security import safe_reply
from .prompts import declared_name, topic_title
from .conversation import prepare, advance, guard_action
from .study_planner import build_plan, cornell_guide, study_guide
from .learning_events import record_event
from .learning_engine import recommend_next_action
from .recommendations import build_recommendation
from .backup import export_backup, validate_backup, restore_backup
from .backup_crypto import encrypt_backup,decrypt_backup
from .course_builder import decode_source, build_course, course_pack, validate_course_structure
from .curriculum_graph import build_graph, persist_graph, prerequisite_chain
from .course_quality import evaluate_course, publication_allowed
from .question_bank import sync_course_questions, stats_for_course
from .learning_intelligence import mastery_evidence, due_reviews, diagnostic_questions, score_diagnostic, recommended_start
from .course_versioning import compare_versions, seed_initial_version, apply_version, history as course_version_history
from .version import ALLEN_VERSION
from .licensing import LicenseManager, LicenseError
from .time_utils import local_day, local_day_iso

ROOT=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))

def create_app(db_path=None, ai=None, require_license=None, require_local_access=None, require_teacher_auth=None):
    local_root=Path(os.environ.get('ALLEN_DATA_ROOT') or (Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'ALLEN'))
    db=Database(db_path or os.environ.get('ALLEN_DB_PATH',local_root/'allen.sqlite3'))
    licensing=LicenseManager(local_root, ROOT/'config/license_public_key.pem')
    licensing_required = (db_path is None) if require_license is None else bool(require_license)
    library=Library(ROOT/'data/library')
    engine=ai or LocalAI()
    token=secrets.token_urlsafe(32)
    instance_id=secrets.token_urlsafe(24)
    fair_token_value=secrets.token_urlsafe(32)
    teacher_session=secrets.token_urlsafe(32)
    teacher_failures=[]
    access_key=secrets.token_urlsafe(32)
    launch_token=secrets.token_urlsafe(32)
    launch_token_used=False
    local_access_required = (db_path is None) if require_local_access is None else bool(require_local_access)
    teacher_auth_required = (db_path is None) if require_teacher_auth is None else bool(require_teacher_auth)
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

    app=FastAPI(title='ALLEN local',version=ALLEN_VERSION,docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.state.db=db
    app.state.instance_id=instance_id
    app.state.licensing=licensing
    app.state.access_key=access_key
    def issue_launch_token():
        nonlocal launch_token, launch_token_used
        launch_token=secrets.token_urlsafe(32)
        launch_token_used=False
        app.state.launch_token=launch_token
        return launch_token
    app.state.launch_token=launch_token
    app.state.issue_launch_token=issue_launch_token
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','[::1]']+(['testserver'] if db_path else []))

    def security_headers(response):
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='no-store'
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Cross-Origin-Opener-Policy']='same-origin'
        response.headers['Cross-Origin-Resource-Policy']='same-origin'
        return response

    @app.middleware('http')
    async def local_guard(request,call_next):
        if local_access_required and request.url.path != '/api/health':
            nonlocal launch_token_used
            launch_key=request.query_params.get('access','')
            cookie_key=request.cookies.get('allen_access','')
            if request.method=='GET' and launch_key and not launch_token_used and secrets.compare_digest(launch_key,launch_token):
                launch_token_used=True
                clean=[(k,v) for k,v in request.query_params.multi_items() if k!='access']
                target=request.url.path+('?' + urlencode(clean) if clean else '')
                response=RedirectResponse(target,status_code=303)
                response.set_cookie('allen_access',access_key,httponly=True,samesite='strict',secure=False,path='/')
                response.set_cookie('allen_mode','fair' if request.url.path=='/fair' else 'app',httponly=True,samesite='strict',secure=False,path='/')
                return security_headers(response)
            if not cookie_key or not secrets.compare_digest(cookie_key,access_key):
                return security_headers(JSONResponse({'error':'Abre ALLEN desde su aplicación de escritorio.'},403))
        fair_mode=request.cookies.get('allen_mode')=='fair'
        if fair_mode and request.url.path=='/api/fair/sessions' and request.method=='POST' and teacher_auth_required and not teacher_configured():
            return security_headers(JSONResponse({'error':'Configura un PIN de profesor antes de iniciar el Modo Feria.','teacher_setup_required':True},409))
        if fair_mode and request.url.path.startswith('/api/'):
            fair_allowed=(
                request.url.path.startswith('/api/fair/')
                or request.url.path in {'/api/health','/api/model/status','/api/teacher/security/status','/api/teacher/security/unlock'}
            )
            if not fair_allowed:
                return security_headers(JSONResponse({'error':'Modo Feria aislado: esta API no está disponible.','fair_restricted':True},403))
        origin=request.headers.get('origin')
        if origin and origin != str(request.base_url).rstrip('/'):
            return security_headers(JSONResponse({'error':'Abre Allen desde su dirección local.'},403))
        if request.headers.get('sec-fetch-site')=='cross-site':
            return security_headers(JSONResponse({'error':'Abre Allen desde su dirección local.'},403))
        if request.method in ('POST','PUT','DELETE','PATCH'):
            fair_auth_path=request.url.path.startswith('/api/fair/') or (fair_mode and request.url.path=='/api/teacher/security/unlock')
            expected_token=fair_token_value if fair_auth_path else token
            if not secrets.compare_digest(request.headers.get('x-allen-token',''),expected_token):
                return security_headers(JSONResponse({'error':'Recarga Allen para continuar.'},403))
        teacher_security_paths={
            '/api/teacher/security/status',
            '/api/teacher/security/setup',
            '/api/teacher/security/unlock',
            '/api/teacher/security/lock',
        }
        protected_teacher=(
            request.url.path.startswith('/api/teacher/')
            or request.url.path.startswith('/api/backup/')
            or request.url.path.startswith('/api/recovery/')
            or request.url.path.startswith('/api/system/')
        )
        if teacher_auth_required and protected_teacher and request.url.path not in teacher_security_paths and not teacher_unlocked(request):
            return security_headers(JSONResponse({'error':'Se requiere autorización de profesor.','teacher_auth_required':True},403))
        if licensing_required and request.url.path.startswith('/api/'):
            allowed = {
                '/api/bootstrap',
                '/api/health',
                '/api/license/status',
                '/api/license/machine-id',
                '/api/license/activate',
            }
            if request.url.path not in allowed and not licensing.status().get('active'):
                return security_headers(JSONResponse({'error':'ALLEN necesita una licencia activa para continuar.','license_required':True},402))
        if teacher_auth_required and request.url.path.startswith('/api/') and not teacher_configured():
            setup_allowed={
                '/api/bootstrap',
                '/api/health',
                '/api/license/status',
                '/api/license/machine-id',
                '/api/license/activate',
                '/api/teacher/security/status',
                '/api/teacher/security/setup',
            }
            if request.url.path not in setup_allowed:
                return security_headers(JSONResponse({'error':'Configura primero el PIN de profesor.','teacher_setup_required':True},428))
        if request.url.path.startswith('/api/'):
            max_body=12_500_000 if request.url.path=='/api/teacher/import' or request.url.path.endswith('/versions') else 3_500_000 if request.url.path=='/api/teacher/packs/import' or request.url.path.endswith('/review') else 8_000_000 if request.url.path.startswith('/api/backup/') else 200000
            try:
                if int(request.headers.get('content-length','0'))>max_body:
                    return security_headers(JSONResponse({'error':'El archivo o texto es demasiado largo.'},413))
            except ValueError:
                return security_headers(JSONResponse({'error':'Solicitud no válida.'},400))
            body=await request.body()
            if len(body)>max_body:
                return security_headers(JSONResponse({'error':'El archivo o texto es demasiado largo.'},413))
        response=await call_next(request)
        return security_headers(response)

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

    def student_structure(structure):
        """Return course material without assessment secrets."""
        def scrub(value):
            if isinstance(value,list):
                return [scrub(item) for item in value]
            if isinstance(value,dict):
                return {
                    key:scrub(item)
                    for key,item in value.items()
                    if key not in {'correct','answer_hint'}
                }
            return value
        safe=scrub(structure)
        if isinstance(safe,dict):
            safe.pop('final_exam',None)
        return safe

    def student_questions(questions):
        safe=[]
        for q in questions or []:
            if not isinstance(q,dict):
                continue
            safe.append({
                'question':q.get('question',q.get('prompt','')),
                'prompt':q.get('prompt',q.get('question','')),
                'topic':q.get('topic',''),
                'options':q.get('options',[]),
            })
        return safe


    def teacher_configured():
        return bool(db.one("SELECT id FROM teacher_security WHERE id=1"))

    def teacher_unlocked(request):
        value=request.cookies.get('allen_teacher','')
        return bool(value and secrets.compare_digest(value,teacher_session))

    def pin_digest(pin,salt_hex):
        return hashlib.scrypt(pin.encode('utf-8'),salt=bytes.fromhex(salt_hex),n=2**14,r=8,p=1,dklen=32).hex()


    @app.get('/api/bootstrap')
    def bootstrap():
        db.prune()
        license_status = licensing.status() if licensing_required else {
            'required': False,
            'active': True,
            'state': 'development',
            'machine_id': 'TEST-DEVELOPMENT',
            'message': 'Licensing desactivado para pruebas.'
        }
        return dict(
            version=ALLEN_VERSION,
            token=token,
            license=license_status,
            profiles=[user(p['id']) for p in db.all('SELECT id FROM users')],
            settings=db.settings().model_dump(),
            catalog=catalog(),
            teacher_security={'configured':teacher_configured()},
        )

    @app.get('/api/license/status')
    def license_status():
        if not licensing_required:
            return {'required':False,'active':True,'state':'development','machine_id':'TEST-DEVELOPMENT'}
        return licensing.status()

    @app.get('/api/license/machine-id')
    def license_machine_id():
        status = licensing.status() if licensing_required else {'machine_id':'TEST-DEVELOPMENT'}
        return {'machine_id':status['machine_id']}

    @app.post('/api/license/activate')
    def activate_license(value:LicenseActivation):
        if not licensing_required:
            return {'required':False,'active':True,'state':'development','machine_id':'TEST-DEVELOPMENT'}
        try:
            return licensing.install(value.content)
        except LicenseError as exc:
            raise HTTPException(422,str(exc))

    @app.get('/api/teacher/security/status')
    def teacher_security_status(request:Request):
        if not teacher_auth_required:
            return {'configured':teacher_configured(),'unlocked':True}
        return {'configured':teacher_configured(),'unlocked':teacher_unlocked(request)}

    @app.post('/api/teacher/security/setup')
    def teacher_security_setup(value:TeacherPin,request:Request):
        if teacher_configured():
            raise HTTPException(409,'El PIN de profesor ya está configurado.')
        salt=secrets.token_bytes(16).hex()
        digest=pin_digest(value.pin,salt)
        db.execute("INSERT INTO teacher_security(id,salt,pin_hash,updated_at) VALUES(1,?,?,?)",(salt,digest,now()))
        response=JSONResponse({'configured':True,'unlocked':True})
        response.set_cookie('allen_teacher',teacher_session,httponly=True,samesite='strict',secure=False,path='/')
        return response

    @app.post('/api/teacher/security/unlock')
    def teacher_security_unlock(value:TeacherPin):
        nonlocal teacher_session
        now_mono=time.monotonic()
        teacher_failures[:]=[attempt for attempt in teacher_failures if now_mono-attempt<60]
        if len(teacher_failures)>=5:
            raise HTTPException(429,'Demasiados intentos de PIN. Espera un minuto.')
        row=db.one("SELECT salt,pin_hash FROM teacher_security WHERE id=1")
        if not row:
            raise HTTPException(409,'Configura primero un PIN de profesor desde la aplicación principal.')
        candidate=pin_digest(value.pin,row['salt'])
        if not secrets.compare_digest(candidate,row['pin_hash']):
            teacher_failures.append(now_mono)
            raise HTTPException(403,'PIN de profesor incorrecto.')
        teacher_failures.clear()
        teacher_session=secrets.token_urlsafe(32)
        response=JSONResponse({'configured':True,'unlocked':True})
        response.set_cookie('allen_teacher',teacher_session,httponly=True,samesite='strict',secure=False,path='/')
        return response

    @app.post('/api/teacher/security/lock')
    def teacher_security_lock():
        nonlocal teacher_session
        teacher_session=secrets.token_urlsafe(32)
        response=JSONResponse({'configured':teacher_configured(),'unlocked':False})
        response.delete_cookie('allen_teacher',path='/')
        return response

    @app.get('/api/fair/token')
    def fair_token():
        return {'token':fair_token_value}

    @app.post('/api/fair/exit')
    def fair_exit(request:Request):
        if not teacher_unlocked(request):
            return JSONResponse({'error':'Se requiere el PIN de profesor para salir del Modo Feria.','teacher_auth_required':True},403)
        response=JSONResponse({'ok':True})
        response.set_cookie('allen_mode','app',httponly=True,samesite='strict',secure=False,path='/')
        return response

    @app.get('/api/health')
    def health():
        db.one('SELECT 1')
        return {'ok':True,'instance':instance_id}

    @app.get('/api/model/status')
    async def model_status():
        return await engine.status(db.settings())

    @app.get('/api/settings')
    def settings():
        return db.settings().model_dump()

    @app.put('/api/settings')
    def update_settings(value:Settings,request:Request):
        nonlocal privacy_epoch
        current=db.settings()
        sensitive=('ai_server','model','temperature','context_size','max_tokens','save_history','retention_days','demo','performance')
        changed_sensitive=any(getattr(current,key)!=getattr(value,key) for key in sensitive)
        if teacher_auth_required and changed_sensitive and not teacher_unlocked(request):
            raise HTTPException(403,'Se requiere autorización de profesor para cambiar ajustes globales.')
        if not value.save_history:
            privacy_epoch+=1
        db.execute('INSERT OR REPLACE INTO settings VALUES(1,?)',(value.model_dump_json(),))
        db.prune()
        return value.model_dump()

    @app.post('/api/profiles')
    def create_profile(value:Profile):
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
    def delete_profile(uid:int,request:Request):
        if teacher_auth_required and not teacher_unlocked(request):
            raise HTTPException(403,'Se requiere autorización de profesor para eliminar perfiles.')
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
        goal_date=local_day_iso() if value.set_goal or value.daily_goal!=memory['daily_goal'] else memory['goal_date']
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
        latest=db.one('SELECT created FROM learning_sessions WHERE user_id=? ORDER BY id DESC LIMIT 1',(value.profile_id,))
        if latest and latest.get('created'):
            try:
                previous=datetime.fromisoformat(str(latest['created']).replace('Z','+00:00'))
                if previous.tzinfo is None: previous=previous.replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc)-previous).total_seconds()<25:
                    return {'ok':True,'deduplicated':True}
            except ValueError:
                pass
        db.execute('INSERT INTO learning_sessions(user_id,subject,seconds,created) VALUES(?,?,?,?)',(value.profile_id,value.subject,value.seconds,now()))
        db.award(value.profile_id,'study',value.subject,5,local_day_iso())
        return {'ok':True,'deduplicated':False}


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
        today=local_day_iso()
        existing=db.one('SELECT * FROM study_sessions WHERE plan_id=? AND user_id=? AND day=?',(pid,profile_id,today))
        if existing: return existing
        sid=db.execute('INSERT INTO study_sessions(user_id,plan_id,day,status,started) VALUES(?,?,?,?,?)',(profile_id,pid,today,'active',now()))
        db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(profile_id,'study_session',sid,row['subject'],'','active',now()))
        record_event(db,profile_id,'lesson_started',row['subject'],'',reference_type='study_session',reference_id=sid)
        return db.one('SELECT * FROM study_sessions WHERE id=?',(sid,))

    @app.post('/api/study-sessions/{sid}/event')
    def study_session_event(sid:int,value:StudySessionEvent):
        user(value.profile_id)
        session=db.one('SELECT * FROM study_sessions WHERE id=? AND user_id=?',(sid,value.profile_id))
        if not session: raise HTTPException(404,'No encontramos esa sesión.')
        db.execute('INSERT INTO study_session_events(user_id,session_id,kind,activity_index,note,created) VALUES(?,?,?,?,?,?)',
            (value.profile_id,sid,value.kind,value.activity_index,value.note,now()))
        timestamp=now()
        status=session['status']
        completed=session.get('activities_completed',0); skipped=session.get('activities_skipped',0); difficulties=session.get('difficulties',0); hints=session.get('hints_used',0)
        if value.kind=='completed': completed+=1; status='completed'
        elif value.kind=='skipped': skipped+=1
        elif value.kind=='not_understood': difficulties+=1
        elif value.kind=='hint': hints+=1
        elif value.kind=='paused': status='paused'
        if status!='completed' and value.kind not in ('completed','paused'): status='active'
        completed_at=timestamp if status=='completed' else session.get('completed')
        db.execute("""UPDATE study_sessions
            SET current_activity_index=?,last_activity_at=?,activities_completed=?,activities_skipped=?,
                difficulties=?,hints_used=?,status=?,completed=?
            WHERE id=?""",
            (value.activity_index,timestamp,completed,skipped,difficulties,hints,status,completed_at,sid))
        plan=db.one("SELECT subject FROM study_plans WHERE id=?",(session['plan_id'],))
        subject=plan['subject'] if plan else ''
        if value.kind=='hint': record_event(db,value.profile_id,'hint_used',subject,'',reference_type='study_session',reference_id=sid)
        elif value.kind=='not_understood': record_event(db,value.profile_id,'explanation_requested',subject,'',reference_type='study_session',reference_id=sid)
        elif value.kind=='completed':
            record_event(db,value.profile_id,'study_session_completed',subject,'',reference_type='study_session',reference_id=sid)
            db.execute("DELETE FROM profile_current_activity WHERE user_id=? AND activity_type='study_session' AND reference_id=?",(value.profile_id,sid))
        else:
            db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(value.profile_id,'study_session',sid,subject,'',status,now()))
        return db.one('SELECT * FROM study_sessions WHERE id=?',(sid,))


    @app.post('/api/teacher/import')
    def teacher_import(value:TeacherImport):
        user(value.profile_id)
        try:
            extracted=decode_source(value.filename,value.mime,value.content_base64)
            structure=build_course(value.title,value.subject,value.level,extracted['pages'],extracted['text'])
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        doc_id=db.execute('INSERT INTO teacher_documents(user_id,title,filename,mime,page_count,source_text,pages_json,created_at) VALUES(?,?,?,?,?,?,?,?)',
            (value.profile_id,value.title,value.filename,value.mime,extracted['page_count'],extracted['text'],json.dumps(extracted['pages'],ensure_ascii=False),now()))
        cid=db.execute("INSERT INTO courses(owner_profile_id,source_document_id,title,subject,level,status,version,structure_json,created_at,updated_at) VALUES(?,?,?,?,?,'draft',1,?,?,?)",
            (value.profile_id,doc_id,value.title,value.subject,value.level,json.dumps(structure,ensure_ascii=False),now(),now()))
        seed_initial_version(db,cid,doc_id,structure,'draft')
        return {'course_id':cid,'document_id':doc_id,'structure':structure,'version':1}

    @app.post('/api/teacher/packs/import')
    def import_course_pack(value:CoursePackImport):
        user(value.profile_id)
        pack=value.pack
        if pack.get('format')!='allen-course-pack' or pack.get('version')!=1:
            raise HTTPException(422,'Course Pack no compatible.')
        structure=pack.get('course')
        try: validate_course_structure(structure)
        except ValueError as exc: raise HTTPException(422,str(exc))
        title=str(structure.get('title') or 'Curso importado')[:140]
        subject=str(structure.get('subject') or 'General')[:80]
        level=str(structure.get('level') or 'Premedia')
        structure['status']='draft'
        cid=db.execute("INSERT INTO courses(owner_profile_id,source_document_id,title,subject,level,status,version,structure_json,created_at,updated_at) VALUES(?,?,?, ?,?,'draft',1,?,?,?)",
            (value.profile_id,None,title,subject,level,json.dumps(structure,ensure_ascii=False),now(),now()))
        seed_initial_version(db,cid,None,structure,'draft')
        return {'course_id':cid,'status':'draft','version':1}

    @app.get('/api/teacher/courses/{cid}/versions')
    def teacher_course_versions(cid:int,profile_id:int=1):
        user(profile_id)
        row=db.one("SELECT id FROM courses WHERE id=? AND owner_profile_id=?",(cid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        return course_version_history(db,cid)

    @app.post('/api/teacher/courses/{cid}/versions')
    def create_course_version(cid:int,value:CourseVersionImport):
        user(value.profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND owner_profile_id=?",(cid,value.profile_id))
        if not course: raise HTTPException(404,'No encontramos ese curso.')
        try:
            extracted=decode_source(value.filename,value.mime,value.content_base64)
            new_structure=build_course(course['title'],course['subject'],course['level'],extracted['pages'],extracted['text'])
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        old_structure=json.loads(course['structure_json'])
        diff=compare_versions(old_structure,new_structure)
        db.create_snapshot(f"before-course-v{course['version']+1}")
        doc_id=db.execute('INSERT INTO teacher_documents(user_id,title,filename,mime,page_count,source_text,pages_json,created_at) VALUES(?,?,?,?,?,?,?,?)',
            (value.profile_id,course['title'],value.filename,value.mime,extracted['page_count'],extracted['text'],json.dumps(extracted['pages'],ensure_ascii=False),now()))
        version=apply_version(db,course,doc_id,new_structure,diff)
        return {'course_id':cid,'version':version,'status':'draft','diff':diff,'structure':new_structure}

    @app.get('/api/teacher/courses')
    def teacher_courses(profile_id:int=1):
        user(profile_id)
        rows=db.all("SELECT id,title,subject,level,status,version,created_at,updated_at,published_at,structure_json FROM courses WHERE owner_profile_id=? ORDER BY updated_at DESC",(profile_id,))
        for row in rows:
            structure=json.loads(row.pop('structure_json'))
            row['coverage']=structure.get('coverage',{})
        return rows

    @app.get('/api/teacher/courses/{cid}')
    def teacher_course(cid:int,profile_id:int=1):
        user(profile_id)
        row=db.one("SELECT * FROM courses WHERE id=? AND owner_profile_id=?",(cid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        row['structure']=json.loads(row.pop('structure_json'))
        if row.get('source_document_id'):
            doc=db.one("SELECT id,title,filename,mime,page_count,created_at FROM teacher_documents WHERE id=? AND user_id=?",(row['source_document_id'],profile_id))
        else: doc=None
        row['document']=doc
        return row

    @app.put('/api/teacher/courses/{cid}/review')
    def review_course(cid:int,value:CourseReview):
        user(value.profile_id)
        row=db.one("SELECT id FROM courses WHERE id=? AND owner_profile_id=?",(cid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        try: validate_course_structure(value.structure)
        except ValueError as exc: raise HTTPException(422,str(exc))
        value.structure['status']='reviewed'
        quality=evaluate_course(value.structure)
        serialized=json.dumps(value.structure,ensure_ascii=False)
        with db.connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            graph=persist_graph(db,cid,value.structure,conn=conn)
            synced=sync_course_questions(db,cid,value.structure,conn=conn)
            conn.execute("UPDATE question_bank SET status='approved' WHERE course_id=?",(cid,))
            conn.execute("INSERT INTO course_quality_reviews(course_id,score,blocking_issues,report_json,created_at) VALUES(?,?,?,?,?)",(cid,quality['score'],quality['blocking_issues'],json.dumps(quality,ensure_ascii=False),now()))
            conn.execute("UPDATE courses SET status='reviewed',structure_json=?,updated_at=? WHERE id=?",(serialized,now(),cid))
            current=conn.execute("SELECT version FROM courses WHERE id=?",(cid,)).fetchone()
            if current:
                conn.execute("UPDATE course_versions SET structure_json=?,status='reviewed' WHERE course_id=? AND version_number=?",(serialized,cid,current['version']))
        return {'ok':True,'quality':quality,'graph':{'nodes':len(graph['nodes']),'edges':len(graph['edges'])},'question_bank':synced}

    @app.post('/api/teacher/courses/{cid}/publish')
    def publish_course(cid:int,value:CoursePublish):
        user(value.profile_id)
        row=db.one("SELECT * FROM courses WHERE id=? AND owner_profile_id=?",(cid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        structure=json.loads(row['structure_json'])
        try: validate_course_structure(structure)
        except ValueError as exc: raise HTTPException(422,str(exc))
        if row['status']=='draft':
            raise HTTPException(409,'Revisa y aprueba el curso antes de publicarlo.')
        quality=evaluate_course(structure)
        if not publication_allowed(quality):
            raise HTTPException(409,'El curso todavía tiene problemas de calidad que deben revisarse antes de publicar.')
        published_at=now()
        with db.connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            persist_graph(db,cid,structure,conn=conn)
            sync_course_questions(db,cid,structure,conn=conn)
            conn.execute("UPDATE question_bank SET status='approved' WHERE course_id=?",(cid,))
            conn.execute("UPDATE courses SET status='published',published_at=?,updated_at=? WHERE id=?",(published_at,published_at,cid))
            conn.execute("UPDATE course_versions SET status='published',published_at=? WHERE course_id=? AND version_number=?",(published_at,cid,row['version']))
        return {'ok':True,'course_id':cid,'quality':quality,'version':row['version']}

    @app.get('/api/teacher/courses/{cid}/pack')
    def export_course_pack(cid:int,profile_id:int=1):
        user(profile_id)
        row=db.one("SELECT * FROM courses WHERE id=? AND owner_profile_id=?",(cid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        doc=db.one("SELECT title,filename,page_count FROM teacher_documents WHERE id=?",(row['source_document_id'],)) if row['source_document_id'] else {}
        return course_pack(json.loads(row['structure_json']),doc or {})

    @app.get('/api/teacher/courses/{cid}/quality')
    def course_quality(cid:int,profile_id:int=1):
        user(profile_id)
        row=db.one("SELECT * FROM courses WHERE id=? AND owner_profile_id=?",(cid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        structure=json.loads(row['structure_json'])
        report=evaluate_course(structure)
        report['question_bank']=stats_for_course(db,cid)
        return report

    @app.get('/api/teacher/courses/{cid}/questions')
    def teacher_question_bank(cid:int,profile_id:int=1):
        user(profile_id)
        course=db.one("SELECT id FROM courses WHERE id=? AND owner_profile_id=?",(cid,profile_id))
        if not course: raise HTTPException(404,'No encontramos ese curso.')
        rows=db.all("SELECT id,unit_index,topic_index,subject,topic,objective,prompt,answer,options_json,difficulty,kind,source_page,status,origin,attempts,correct_count,incorrect_count FROM question_bank WHERE course_id=? ORDER BY unit_index,topic_index,id",(cid,))
        for row in rows:
            row['options']=json.loads(row.pop('options_json') or '[]')
            row['correct_rate']=round(row['correct_count']/max(1,row['attempts'])*100) if row['attempts'] else None
        return rows

    @app.get('/api/teacher/courses/{cid}/graph')
    def course_graph(cid:int,profile_id:int=1):
        user(profile_id)
        row=db.one("SELECT * FROM courses WHERE id=? AND owner_profile_id=?",(cid,profile_id))
        if not row: raise HTTPException(404,'No encontramos ese curso.')
        structure=json.loads(row['structure_json'])
        graph=build_graph(structure)
        graph['persisted_edges']=db.all("SELECT from_node,to_node,relation,reason FROM curriculum_edges WHERE course_id=?",(cid,))
        return graph

    @app.get('/api/teacher/analytics')
    def teacher_analytics(profile_id:int=1):
        user(profile_id)
        courses=db.all("SELECT id,title,subject,status,structure_json FROM courses WHERE owner_profile_id=?",(profile_id,))
        out=[]
        for course in courses:
            structure=json.loads(course.pop('structure_json'))
            quality=evaluate_course(structure)
            enrollments=db.one("SELECT count(*) n FROM course_enrollments WHERE course_id=?",(course['id'],))['n']
            completions=db.one("SELECT count(*) n FROM course_enrollments WHERE course_id=? AND status='completed'",(course['id'],))['n']
            helps=db.one("SELECT count(*) n FROM learning_events WHERE reference_type='course' AND reference_id=? AND event_type='explanation_requested'",(course['id'],))['n']
            question_stats=stats_for_course(db,course['id'])
            weak=db.all("""SELECT tm.topic,ROUND(AVG(tm.mastery_score),1) mastery,COUNT(*) learners
                FROM topic_mastery tm JOIN course_enrollments ce ON ce.user_id=tm.user_id
                WHERE ce.course_id=? AND tm.subject=? GROUP BY tm.topic ORDER BY mastery ASC LIMIT 5""",(course['id'],course['subject']))
            active_positions=db.all("SELECT unit_index,topic_index,COUNT(*) learners FROM course_enrollments WHERE course_id=? AND status='active' GROUP BY unit_index,topic_index ORDER BY learners DESC LIMIT 5",(course['id'],))
            help_hotspots=db.all("SELECT topic,COUNT(*) requests FROM learning_events WHERE reference_type='course' AND reference_id=? AND event_type='explanation_requested' GROUP BY topic ORDER BY requests DESC LIMIT 5",(course['id'],))
            out.append({**course,'quality_score':quality['score'],'quality_issues':len(quality['issues']),'enrollments':enrollments,
                        'completions':completions,'help_requests':helps,'question_bank':question_stats,'weak_topics':weak,
                        'active_positions':active_positions,'help_hotspots':help_hotspots})
        total_enroll=sum(x['enrollments'] for x in out); total_complete=sum(x['completions'] for x in out)
        return {'courses':out,'summary':{'courses':len(out),'enrollments':total_enroll,'completion_rate':round(total_complete/max(1,total_enroll)*100)}}

    @app.get('/api/mastery/evidence')
    def mastery_evidence_api(profile_id:int=1,subject:str=Query(...,max_length=80),topic:str=Query(...,max_length=120)):
        user(profile_id)
        result=mastery_evidence(db,profile_id,subject,topic)
        if not result: raise HTTPException(404,'Todavía no hay evidencia de dominio para este tema.')
        return result

    @app.get('/api/reviews/due')
    def reviews_due(profile_id:int=1):
        user(profile_id)
        return due_reviews(db,profile_id)

    @app.get('/api/courses/{cid}/diagnostic')
    def course_diagnostic(cid:int,profile_id:int=1):
        user(profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        structure=json.loads(course['structure_json'])
        qs=diagnostic_questions(structure,7)
        if not qs: raise HTTPException(409,'Este curso todavía no tiene preguntas suficientes para diagnóstico.')
        safe=[{'topic':q['topic'],'prompt':q['prompt'],'options':q['options'],'source':q.get('source',{})} for q in qs]
        return {'course':{'id':cid,'title':course['title'],'subject':course['subject']},'questions':safe}

    @app.post('/api/courses/{cid}/diagnostic/submit')
    def submit_course_diagnostic(cid:int,value:Submission):
        user(value.profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        structure=json.loads(course['structure_json'])
        qs=diagnostic_questions(structure,7)
        if len(value.answers)!=len(qs): raise HTTPException(422,'Responde todas las preguntas del diagnóstico.')
        scores=score_diagnostic(qs,value.answers)
        start=recommended_start(structure,scores)
        db.execute("INSERT INTO diagnostic_results(course_id,user_id,answers_json,result_json,created_at) VALUES(?,?,?,?,?)",
                   (cid,value.profile_id,json.dumps(value.answers,ensure_ascii=False),json.dumps({'topics':scores,'recommended_start':start},ensure_ascii=False),now()))
        for q,answer in zip(qs,value.answers):
            correct=answer==q['correct']
            record_event(db,value.profile_id,'question_answered',course['subject'],q['topic'],reference_type='diagnostic',reference_id=cid,metadata={'correct':correct,'difficulty':'Normal'})
            bank=db.one("SELECT id FROM question_bank WHERE course_id=? AND topic=? AND prompt=? LIMIT 1",(cid,q['topic'],q['prompt']))
            if bank:
                db.execute("UPDATE question_bank SET attempts=attempts+1,correct_count=correct_count+?,incorrect_count=incorrect_count+? WHERE id=?",(int(correct),int(not correct),bank['id']))
        enrollment=db.one("SELECT * FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,value.profile_id))
        if enrollment:
            db.execute("UPDATE course_enrollments SET unit_index=?,topic_index=?,step_index=0,updated_at=? WHERE id=?",(start['unit_index'],start['topic_index'],now(),enrollment['id']))
        return {'topics':scores,'recommended_start':start,'skipped_topics':[t for t,d in scores.items() if d['percentage']>=80]}

    @app.get('/api/courses')
    def available_courses(profile_id:int=1):
        user(profile_id)
        rows=db.all("SELECT id,title,subject,level,version,structure_json FROM courses WHERE status='published' ORDER BY updated_at DESC LIMIT 100")
        enrolled={r['course_id']:r for r in db.all("SELECT * FROM course_enrollments WHERE user_id=?",(profile_id,))}
        out=[]
        for row in rows:
            structure=json.loads(row.pop('structure_json'))
            out.append({**row,'coverage':structure.get('coverage',{}),'enrollment':enrolled.get(row['id'])})
        return out

    @app.post('/api/courses/{cid}/enroll')
    def enroll_course(cid:int,value:CourseEnroll):
        user(value.profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        existing=db.one("SELECT * FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,value.profile_id))
        if existing:return existing
        eid=db.execute("INSERT INTO course_enrollments(course_id,user_id,status,unit_index,topic_index,step_index,started_at,updated_at) VALUES(?,?, 'active',0,0,0,?,?)",(cid,value.profile_id,now(),now()))
        db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(value.profile_id,'course',eid,course['subject'],'','active',now()))
        return db.one("SELECT * FROM course_enrollments WHERE id=?",(eid,))

    @app.get('/api/courses/{cid}/route')
    def course_route(cid:int,profile_id:int=1):
        user(profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        enrollment=db.one("SELECT * FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,profile_id))
        if not enrollment: raise HTTPException(409,'Primero inscríbete en este curso.')
        diagnostic=db.one("SELECT result_json FROM diagnostic_results WHERE course_id=? AND user_id=? ORDER BY id DESC LIMIT 1",(cid,profile_id))
        skip_topics=[]
        if diagnostic:
            try:
                result=json.loads(diagnostic['result_json'])
                skip_topics=[topic for topic,data in result.get('topics',{}).items() if data.get('percentage',0)>=80]
            except Exception:
                pass
        return {'course':{'id':cid,'title':course['title'],'subject':course['subject'],'level':course['level'],'structure':student_structure(json.loads(course['structure_json']))},'enrollment':enrollment,'diagnostic_skip_topics':skip_topics}

    @app.get('/api/courses/{cid}/exam')
    def course_exam(cid:int,profile_id:int=1):
        user(profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        enrollment=db.one("SELECT * FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,profile_id))
        if not enrollment: raise HTTPException(409,'Primero inscríbete en este curso.')
        structure=json.loads(course['structure_json'])
        questions=structure.get('final_exam',[])
        if not questions: raise HTTPException(409,'Este curso todavía no tiene examen final.')
        safe=[{'topic':q.get('topic',''),'prompt':q.get('prompt',''),'options':q.get('options',[]),'source':q.get('source',{})} for q in questions]
        session=db.one("SELECT * FROM course_exam_sessions WHERE course_id=? AND user_id=?",(cid,profile_id))
        if not session:
            sid=db.execute("INSERT INTO course_exam_sessions(course_id,user_id,answers_json,status,started_at,updated_at) VALUES(?,?,?,'active',?,?)",(cid,profile_id,json.dumps(['']*len(questions)),now(),now()))
            session=db.one("SELECT * FROM course_exam_sessions WHERE id=?",(sid,))
        answers=json.loads(session['answers_json'] or '[]')
        return {'course':{'id':cid,'title':course['title'],'subject':course['subject']},'questions':safe,'answers':answers,'exam_session_id':session['id']}

    @app.post('/api/courses/{cid}/exam/progress')
    def save_course_exam_progress(cid:int,value:CourseExamProgress):
        user(value.profile_id)
        course=db.one("SELECT id FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        enrollment=db.one("SELECT id FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,value.profile_id))
        if not enrollment: raise HTTPException(409,'Primero inscríbete en este curso.')
        existing=db.one("SELECT id FROM course_exam_sessions WHERE course_id=? AND user_id=?",(cid,value.profile_id))
        payload=json.dumps(value.answers,ensure_ascii=False)
        if existing:
            db.execute("UPDATE course_exam_sessions SET answers_json=?,status=?,updated_at=? WHERE id=?",(payload,value.status,now(),existing['id']))
        else:
            db.execute("INSERT INTO course_exam_sessions(course_id,user_id,answers_json,status,started_at,updated_at) VALUES(?,?,?,?,?,?)",(cid,value.profile_id,payload,value.status,now(),now()))
        return {'ok':True}

    @app.post('/api/courses/{cid}/exam/submit')
    def submit_course_exam(cid:int,value:Submission):
        user(value.profile_id)
        question_events=[]
        with db.connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            course=conn.execute("SELECT * FROM courses WHERE id=? AND status='published'",(cid,)).fetchone()
            if not course: raise HTTPException(404,'Ese curso no está publicado.')
            enrollment=conn.execute("SELECT * FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,value.profile_id)).fetchone()
            if not enrollment: raise HTTPException(409,'Primero inscríbete en este curso.')
            structure=json.loads(course['structure_json'])
            questions=structure.get('final_exam',[])
            if len(value.answers)!=len(questions): raise HTTPException(422,'Responde todas las preguntas del examen.')
            feedback=[];score=0
            for q,answer in zip(questions,value.answers):
                correct=answer==q.get('correct')
                score+=int(correct)
                feedback.append({'topic':q.get('topic',''),'correct':correct,'answer':answer,'correct_answer':q.get('correct',''),'source':q.get('source',{})})
                question_events.append((q.get('topic',''),correct))
                bank=conn.execute("SELECT id FROM question_bank WHERE course_id=? AND topic=? AND prompt=? LIMIT 1",(cid,q.get('topic',''),q.get('prompt',''))).fetchone()
                if bank:
                    conn.execute("UPDATE question_bank SET attempts=attempts+1,correct_count=correct_count+?,incorrect_count=incorrect_count+? WHERE id=?",(int(correct),int(not correct),bank['id']))
            total=len(questions)
            weak=list(dict.fromkeys(x['topic'] for x in feedback if not x['correct']))
            strong=list(dict.fromkeys(x['topic'] for x in feedback if x['correct']))
            result={'score':score,'total':total,'percentage':round(score/max(1,total)*100),'strong_topics':strong,'weak_topics':weak,'feedback':feedback}
            passed=result['percentage']>=70
            result['passed']=passed
            timestamp=now()
            conn.execute("INSERT INTO course_exam_results(course_id,user_id,answers_json,result_json,created_at) VALUES(?,?,?,?,?)",(cid,value.profile_id,json.dumps(value.answers,ensure_ascii=False),json.dumps(result,ensure_ascii=False),timestamp))
            conn.execute("DELETE FROM course_exam_sessions WHERE course_id=? AND user_id=?",(cid,value.profile_id))
            if passed:
                conn.execute("UPDATE course_enrollments SET status='completed',completed_at=?,updated_at=? WHERE course_id=? AND user_id=?",(timestamp,timestamp,cid,value.profile_id))
                conn.execute("DELETE FROM profile_current_activity WHERE user_id=? AND activity_type='course' AND reference_id=?",(value.profile_id,enrollment['id']))
            else:
                conn.execute("UPDATE course_enrollments SET status='active',completed_at=NULL,updated_at=? WHERE course_id=? AND user_id=?",(timestamp,cid,value.profile_id))
        for topic,correct in question_events:
            record_event(db,value.profile_id,'question_answered',course['subject'],topic,reference_type='course_exam',reference_id=cid,metadata={'correct':correct,'difficulty':'Normal'})
        record_event(db,value.profile_id,'quiz_completed',course['subject'],'Examen final',reference_type='course_exam',reference_id=cid,metadata={'score':score,'total':total,'difficulty':'Normal'})
        return result

    @app.post('/api/courses/{cid}/help')
    def course_help(cid:int,value:CourseHelp):
        user(value.profile_id)
        course=db.one("SELECT * FROM courses WHERE id=? AND status='published'",(cid,))
        if not course: raise HTTPException(404,'Ese curso no está publicado.')
        enrollment=db.one("SELECT id FROM course_enrollments WHERE course_id=? AND user_id=?",(cid,value.profile_id))
        if not enrollment: raise HTTPException(409,'Primero inscríbete en este curso.')
        structure=json.loads(course['structure_json'])
        try:
            topic=structure['units'][value.unit_index]['topics'][value.topic_index]
        except (IndexError,KeyError,TypeError):
            raise HTTPException(422,'Tema fuera de rango.')
        count=db.one("SELECT count(*) n FROM learning_events WHERE user_id=? AND event_type='explanation_requested' AND reference_type='course' AND reference_id=? AND topic=?",(value.profile_id,cid,topic['title']))['n']
        level=min(4,count+1)
        record_event(db,value.profile_id,'explanation_requested',course['subject'],topic['title'],reference_type='course',reference_id=cid,metadata={'help_level':level})
        if level==1:
            title='Vamos más simple'
            text=topic.get('objective','').replace('Explicar y aplicar','La idea que queremos entender es')
        elif level==2:
            title='Miremos un ejemplo concreto'
            text=topic.get('source_excerpt','')[:500]
        elif level==3:
            title='Conectemos las piezas'
            text='Lee el fragmento y dime qué palabras o relaciones reconoces: '+topic.get('source_excerpt','')[:420]
        else:
            title='Probemos con una mini práctica'
            text=(topic.get('questions') or [{'prompt':'Explícalo con tus propias palabras.'}])[0].get('prompt','Explícalo con tus propias palabras.')
        return {'level':level,'title':title,'text':text,'topic':topic['title'],'source':topic.get('source',{})}

    @app.post('/api/courses/{cid}/progress')
    def update_course_progress(cid:int,value:CourseProgress):
        user(value.profile_id)
        row=db.one("SELECT ce.*,c.subject,c.structure_json FROM course_enrollments ce JOIN courses c ON c.id=ce.course_id WHERE ce.course_id=? AND ce.user_id=?",(cid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos tu progreso en este curso.')
        structure=json.loads(row['structure_json'])
        units=structure.get('units',[])
        if value.unit_index>=len(units): raise HTTPException(422,'Unidad fuera de rango.')
        topics=units[value.unit_index].get('topics',[])
        if value.topic_index>=len(topics): raise HTTPException(422,'Tema fuera de rango.')
        route=topics[value.topic_index].get('route',[])
        if value.step_index>=max(1,len(route)): raise HTTPException(422,'Paso fuera de rango.')
        if value.status=='completed':
            raise HTTPException(409,'El curso solo se completa al aprobar el examen final.')
        positions=[]
        for ui,unit in enumerate(units):
            for ti,item in enumerate(unit.get('topics',[])):
                steps=item.get('route',[]) or [{}]
                positions.extend((ui,ti,si) for si in range(len(steps)))
        current=(row['unit_index'],row['topic_index'],row['step_index'])
        requested=(value.unit_index,value.topic_index,value.step_index)
        try:
            current_index=positions.index(current)
            requested_index=positions.index(requested)
        except ValueError:
            raise HTTPException(422,'Posición de curso no válida.')
        if requested_index < current_index or requested_index > current_index+1:
            raise HTTPException(409,'Avanza un paso a la vez en tu ruta.')
        # Evaluate evidence from the step the student just completed, not the destination step.
        previous_topic=''
        previous_step_type=''
        try:
            previous=units[row['unit_index']]['topics'][row['topic_index']]
            previous_topic=previous.get('title','')
            previous_route=previous.get('route',[])
            if previous_route and row['step_index']<len(previous_route):
                previous_step_type=previous_route[row['step_index']].get('type','')
        except (IndexError,KeyError,TypeError):
            pass
        completed_at=now() if value.status=='completed' else None
        db.execute("UPDATE course_enrollments SET unit_index=?,topic_index=?,step_index=?,status=?,updated_at=?,completed_at=? WHERE course_id=? AND user_id=?",
            (value.unit_index,value.topic_index,value.step_index,value.status,now(),completed_at,cid,value.profile_id))
        topic=topics[value.topic_index].get('title','')
        db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",
            (value.profile_id,'course',row['id'],row['subject'],topic,value.status,now()))
        if value.status=='completed':
            record_event(db,value.profile_id,'lesson_completed',row['subject'],previous_topic or topic,reference_type='course',reference_id=cid)
        elif previous_step_type in ('retrieval','practice','quiz','review'):
            record_event(db,value.profile_id,'topic_practiced',row['subject'],previous_topic or topic,reference_type='course',reference_id=cid,metadata={'step_type':previous_step_type})
        return {'ok':True}

    @app.get('/api/continuity')
    def continuity(profile_id:int=1):
        user(profile_id)
        activity=db.one("SELECT * FROM profile_current_activity WHERE user_id=?",(profile_id,))
        adventure=db.one("SELECT * FROM adventure_sessions WHERE user_id=? AND status IN ('active','paused') ORDER BY updated_at DESC LIMIT 1",(profile_id,))
        session=db.one("SELECT ss.*,sp.subject,sp.goal,sp.deadline,sp.plan FROM study_sessions ss JOIN study_plans sp ON sp.id=ss.plan_id WHERE ss.user_id=? AND ss.status IN ('active','paused') ORDER BY COALESCE(ss.last_activity_at,ss.started) DESC LIMIT 1",(profile_id,))
        if session: session['plan']=json.loads(session['plan'])
        plan=db.one("SELECT * FROM study_plans WHERE user_id=? ORDER BY id DESC LIMIT 1",(profile_id,))
        if plan:
            plan['topics']=json.loads(plan['topics']); plan['plan']=json.loads(plan['plan'])
        due_cards=db.one("SELECT count(*) n FROM flashcards WHERE user_id=? AND due<=?",(profile_id,local_day_iso()))['n']
        recommendation=build_recommendation(db,profile_id)
        mastery=db.all("SELECT * FROM topic_mastery WHERE user_id=? ORDER BY mastery_score ASC,last_seen DESC LIMIT 8",(profile_id,))
        topic_reviews=due_reviews(db,profile_id,5)
        return dict(current_activity=activity,adventure=adventure,study_session=session,study_plan=plan,due_cards=due_cards,due_topic_reviews=topic_reviews,recommendation=recommendation,mastery=mastery)

    @app.get('/api/mastery')
    def mastery(profile_id:int=1):
        user(profile_id)
        return db.all("SELECT * FROM topic_mastery WHERE user_id=? ORDER BY subject,topic",(profile_id,))

    @app.get('/api/recommendation')
    def recommendation(profile_id:int=1):
        user(profile_id)
        return build_recommendation(db,profile_id)

    @app.get('/api/backup/export')
    def backup_export(profile_id:int=1):
        user(profile_id)
        if teacher_auth_required:
            raise HTTPException(409,'En la aplicación distribuida los respaldos deben exportarse cifrados.')
        return export_backup(db)

    @app.post('/api/backup/export-encrypted')
    async def backup_export_encrypted(request:Request):
        body=await request.json()
        profile_id=int(body.get('profile_id',1))
        user(profile_id)
        try:
            return encrypt_backup(export_backup(db),body.get('password',''))
        except (ValueError,TypeError) as exc:
            raise HTTPException(422,str(exc))

    @app.post('/api/backup/decrypt')
    async def backup_decrypt(request:Request):
        body=await request.json()
        try:
            payload=decrypt_backup(body.get('envelope'),body.get('password',''))
            validate_backup(payload)
            return payload
        except (ValueError,TypeError) as exc:
            raise HTTPException(422,str(exc))

    @app.post('/api/backup/validate')
    async def backup_validate(request:Request):
        payload=await request.json()
        try:return validate_backup(payload)
        except ValueError as exc:raise HTTPException(422,str(exc))

    @app.post('/api/backup/restore')
    async def backup_restore(request:Request):
        payload=await request.json()
        try:
            safety=db.create_snapshot('before-backup-restore')
            summary=restore_backup(db,payload)
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        return {'ok':True,'summary':summary,'safety_snapshot':safety}

    @app.get('/api/system/integrity')
    def system_integrity():
        report=db.integrity()
        report['snapshots']=db.snapshots()
        report['schema_version']=db.schema_version()
        return report

    @app.get('/api/system/recovery/snapshots')
    def recovery_snapshots():
        return db.snapshots()

    @app.post('/api/system/recovery/snapshot')
    def recovery_snapshot():
        name=db.create_snapshot('manual')
        return {'ok':bool(name),'snapshot':name,'snapshots':db.snapshots()}

    @app.post('/api/system/recovery/restore')
    def recovery_restore(value:RecoveryRestore):
        try:
            result=db.restore_snapshot(value.snapshot)
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        return {'ok':True,**result}


    @app.post('/api/adventures/start')
    def start_adventure(value:AdventureStart):
        user(value.profile_id)
        current=db.one("SELECT * FROM adventure_sessions WHERE user_id=? AND adventure_id=? AND status IN ('active','paused') ORDER BY id DESC LIMIT 1",(value.profile_id,value.adventure_id))
        if current:
            db.execute("UPDATE adventure_sessions SET status='active',updated_at=? WHERE id=?",(now(),current['id']))
            db.execute("UPDATE adventure_sessions SET status='paused',updated_at=? WHERE user_id=? AND id<>? AND status='active'",(now(),value.profile_id,current['id']))
            db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(value.profile_id,'adventure',current['id'],'','', 'active',now()))
            return db.one('SELECT * FROM adventure_sessions WHERE id=?',(current['id'],))
        db.execute("UPDATE adventure_sessions SET status='paused',updated_at=? WHERE user_id=? AND status='active'",(now(),value.profile_id))
        sid=db.execute("INSERT INTO adventure_sessions(user_id,adventure_id,status,current_step,completed_steps,answers,mistakes,hints_used,started_at,updated_at) VALUES(?,?, 'active',0,0,'[]',0,0,?,?)",(value.profile_id,value.adventure_id,now(),now()))
        db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(value.profile_id,'adventure',sid,'','', 'active',now()))
        record_event(db,value.profile_id,'lesson_started',reference_type='adventure',reference_id=sid)
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
        if value.event=='hint':
            record_event(db,value.profile_id,'hint_used',reference_type='adventure',reference_id=sid)
        if value.event=='answer':
            record_event(db,value.profile_id,'question_answered',reference_type='adventure',reference_id=sid,metadata={'correct':value.correct})
        if value.event=='complete':
            record_event(db,value.profile_id,'adventure_completed',reference_type='adventure',reference_id=sid)
            db.execute("DELETE FROM profile_current_activity WHERE user_id=? AND activity_type='adventure' AND reference_id=?",(value.profile_id,sid))
        elif value.event=='abandon':
            db.execute("DELETE FROM profile_current_activity WHERE user_id=? AND activity_type='adventure' AND reference_id=?",(value.profile_id,sid))
        else:
            db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(value.profile_id,'adventure',sid,'','',status,now()))
        return db.one('SELECT * FROM adventure_sessions WHERE id=?',(sid,))

    @app.post('/api/simulations')
    def create_simulation(value:SimulationCreate):
        user(value.profile_id)
        questions=[]
        remaining=value.question_count
        try:
            for index,topic in enumerate(value.topics):
                slots=max(1,remaining//max(1,len(value.topics)-index))
                request=QuizRequest(profile_id=value.profile_id,subject=value.subject,topic=topic,difficulty='Normal',count=slots,kind='multiple')
                generated=generate(request)
                questions.extend(generated[:slots])
                remaining=value.question_count-len(questions)
                if remaining<=0:
                    break
        except ValueError as exc:
            raise HTTPException(422,str(exc))
        if not questions:
            raise HTTPException(422,'No pudimos crear preguntas para esos temas.')
        questions=questions[:value.question_count]
        sid=db.execute("INSERT INTO simulation_results(user_id,subject,topics,questions,result,minutes,started_at,status,answers,updated_at,remaining_seconds) VALUES(?,?,?,?,NULL,?,?,'active','[]',?,?)",(value.profile_id,value.subject,json.dumps(value.topics,ensure_ascii=False),json.dumps(questions,ensure_ascii=False),(value.minutes if value.timed else 0),now(),now(),(value.minutes*60 if value.timed else 0)))
        db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) VALUES(?,?,?,?,?,?,?)",(value.profile_id,'simulation',sid,value.subject,value.topics[0] if value.topics else '','active',now()))
        return dict(id=sid,subject=value.subject,topics=value.topics,questions=student_questions(questions),minutes=(value.minutes if value.timed else 0),timed=value.timed)

    @app.get('/api/simulations/active')
    def active_simulation(profile_id:int=1):
        user(profile_id)
        row=db.one("SELECT * FROM simulation_results WHERE user_id=? AND status IN ('active','paused','interrupted') AND result IS NULL ORDER BY COALESCE(updated_at,started_at) DESC LIMIT 1",(profile_id,))
        if not row:return None
        row['topics']=json.loads(row['topics']);row['questions']=student_questions(json.loads(row['questions']));row['answers']=json.loads(row['answers'] or '[]')
        return row

    @app.post('/api/simulations/{sid}/progress')
    def save_simulation_progress(sid:int,value:SimulationProgress):
        user(value.profile_id)
        row=db.one('SELECT id FROM simulation_results WHERE id=? AND user_id=?',(sid,value.profile_id))
        if not row:raise HTTPException(404,'No encontramos ese simulacro.')
        db.execute('UPDATE simulation_results SET answers=?,status=?,updated_at=?,remaining_seconds=COALESCE(?,remaining_seconds) WHERE id=?',(json.dumps(value.answers,ensure_ascii=False),value.status,now(),value.remaining_seconds,sid))
        db.execute("INSERT OR REPLACE INTO profile_current_activity(user_id,activity_type,reference_id,subject,topic,status,updated_at) SELECT user_id,'simulation',id,subject,'',?,? FROM simulation_results WHERE id=?",(value.status,now(),sid))
        return {'ok':True}

    @app.post('/api/simulations/{sid}/reinforcement')
    def simulation_reinforcement(sid:int,profile_id:int=1):
        profile=user(profile_id)
        row=db.one('SELECT * FROM simulation_results WHERE id=? AND user_id=?',(sid,profile_id))
        if not row or not row['result']:raise HTTPException(409,'Completa el simulacro antes de crear el refuerzo.')
        result=json.loads(row['result']);weak=result.get('review',[])
        if not weak:return {'plan_id':None,'message':'No hay temas débiles destacados.'}
        deadline=(local_day()+timedelta(days=3)).isoformat()
        quiz_rows=db.all('SELECT result FROM quiz_results WHERE user_id=? ORDER BY id DESC LIMIT 30',(profile_id,))
        cards=db.all('SELECT question,answer,due,interval FROM flashcards WHERE user_id=?',(profile_id,))
        plan=build_plan(row['subject'],weak,deadline,30,profile['level'],'Plan de refuerzo',quiz_rows,cards,db.progress(profile_id))
        pid=db.execute('INSERT INTO study_plans(user_id,subject,goal,deadline,minutes_per_day,level,topics,plan,created) VALUES(?,?,?,?,?,?,?,?,?)',
            (profile_id,row['subject'],'Plan de refuerzo',deadline,30,profile['level'],json.dumps(weak,ensure_ascii=False),json.dumps(plan,ensure_ascii=False),now()))
        return {'plan_id':pid,'topics':weak,'plan':plan}

    @app.post('/api/simulations/{sid}/submit')
    def submit_simulation(sid:int,value:Submission):
        user(value.profile_id)
        row=db.one('SELECT * FROM simulation_results WHERE id=? AND user_id=?',(sid,value.profile_id))
        if not row: raise HTTPException(404,'No encontramos ese simulacro.')
        if row.get('result'):
            result=json.loads(row['result'])
            weak=result.get('review',[]) if isinstance(result,dict) else []
            return dict(**result,reinforcement=dict(topics=weak,activities=[dict(type='explanation',minutes=10),dict(type='practice',minutes=15),dict(type='flashcards',minutes=5)] if weak else []))
        questions=json.loads(row['questions'])
        result=grade(questions,value.answers)
        db.execute("UPDATE simulation_results SET result=?,completed_at=?,status='completed',updated_at=? WHERE id=?",(json.dumps(result,ensure_ascii=False),now(),now(),sid))
        weak=result.get('review',[]) if isinstance(result,dict) else []
        topics=json.loads(row['topics'])
        for item in result.get('feedback',[]):
            record_event(db,value.profile_id,'question_answered',row['subject'],item.get('topic',topics[0] if topics else row['subject']),reference_type='simulation',reference_id=sid,metadata={'correct':item.get('correct'),'difficulty':'Normal'})
        record_event(db,value.profile_id,'simulation_completed',row['subject'],topics[0] if topics else row['subject'],reference_type='simulation',reference_id=sid,metadata={'score':result.get('score'),'total':result.get('total')})
        db.execute("DELETE FROM profile_current_activity WHERE user_id=? AND activity_type='simulation' AND reference_id=?",(value.profile_id,sid))
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
        active=db.one("SELECT * FROM profile_current_activity WHERE user_id=?",(value.profile_id,))
        mastery_rows=db.all("SELECT subject,topic,mastery_score,status,next_review FROM topic_mastery WHERE user_id=? ORDER BY last_seen DESC LIMIT 4",(value.profile_id,))
        profile['learning_context']={'active_journey':active,'mastery':mastery_rows}
        if value.conversation_id:
            row=db.one('SELECT messages FROM conversations WHERE id=? AND user_id=?',(value.conversation_id,value.profile_id))
            if not row:
                raise HTTPException(404,'La conversación ya no está disponible. Inicia una nueva.')
            stored_history=json.loads(row['messages'])
            if value.regenerate and len(stored_history)>=2 and stored_history[-1].get('role')=='assistant' and stored_history[-2].get('role')=='user':
                stored_history=stored_history[:-2]
            value=Chat.model_validate({**value.model_dump(),'history':stored_history})
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
            conn.execute('INSERT OR IGNORE INTO progress(user_id,kind,subject,xp,day,reference) VALUES(?,?,?,?,?,?)',(value.profile_id,kind,config['subject'],10 if kind=='exercise' else 30,local_day_iso(),str(qid)))
        config=json.loads(row['config'])
        for item in result.get('feedback',[]):
            record_event(db,value.profile_id,'question_answered',config.get('subject',''),item.get('topic',config.get('topic','')),reference_type='quiz',reference_id=qid,metadata={'correct':item.get('correct'),'difficulty':config.get('difficulty','Normal')})
        record_event(db,value.profile_id,'quiz_completed',config.get('subject',''),config.get('topic',''),reference_type='quiz',reference_id=qid,metadata={'score':result.get('score'),'total':result.get('total'),'difficulty':config.get('difficulty','Normal')})
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
        cid=db.execute('INSERT INTO flashcards(user_id,question,answer,due) VALUES(?,?,?,?)',(value.profile_id,value.question,value.answer,local_day_iso()))
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
        due=(local_day()+timedelta(days=interval)).isoformat()
        db.execute('UPDATE flashcards SET interval=?,due=?,reviews=reviews+1 WHERE id=?',(interval,due,cid))
        db.award(value.profile_id,'card','Tarjetas',5,f'{cid}:{local_day_iso()}')
        record_event(db,value.profile_id,'flashcard_reviewed','Tarjetas',row['question'][:80],reference_type='flashcard',reference_id=cid,metadata={'rating':value.rating})
        return {'due':due}

    @app.delete('/api/flashcards/{cid}')
    def delete_card(cid:int,profile_id:int=1):
        db.execute('DELETE FROM flashcards WHERE id=? AND user_id=?',(cid,profile_id))
        return {'ok':True}

    @app.get('/')
    def index(mode:str=''):
        if mode=='fair':
            response=FileResponse(ROOT/'frontend/fair.html')
            response.set_cookie('allen_mode','fair',httponly=True,samesite='strict',secure=False,path='/')
            return response
        response=FileResponse(ROOT/'frontend/index.html')
        response.set_cookie('allen_mode','app',httponly=True,samesite='strict',secure=False,path='/')
        return response

    from .fair import install_fair
    install_fair(app,db,engine)

    @app.get('/fair')
    def fair_index():
        response=FileResponse(ROOT/'frontend/fair.html')
        response.set_cookie('allen_mode','fair',httponly=True,samesite='strict',secure=False,path='/')
        return response

    app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')
    return app

app=create_app()
