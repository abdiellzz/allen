"""Anonymous fair sessions. Visitor text and names are never written to SQLite."""
import asyncio
import random
import secrets
import time
import os
from urllib.parse import urlsplit
from datetime import date
from .time_utils import local_day_iso
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import Field
from .schemas import Strict, Chat
from .conversation import prepare, advance

# question, choices, correct index, explanation; all resources ship locally.
BANK = {
 'Matemáticas': [('¿Cuánto es 15% de 200?', ['15','30','200'],1,'10% son 20 y 5% son 10: juntos suman 30.'),('¿Cuánto es 8 × 7?', ['54','56','64'],1,'8 × 7 = 56. Puedes sumar 7 ocho veces.'),('Si 2x + 6 = 20, ¿cuánto vale x?', ['7','10','14'],0,'Resta 6: 2x = 14. Divide entre 2: x = 7.')],
 'Inglés': [('¿Qué significa computer?', ['Computadora','Carpeta','Compañero'],0,'Computer significa computadora.'),('Completa: She ___ a book.', ['have','has','having'],1,'Con she usamos has: ella tiene un libro.'),('¿Qué frase habla del pasado?', ['I learn','I will learn','I learned'],2,'Learned es el pasado de learn: aprendí.')],
 'Programación': [('¿Qué guarda una variable?', ['Un valor','Solo imágenes','Una pantalla'],0,'Una variable permite dar un nombre a un valor.'),('Python: print(nombre). ¿Qué falta si nombre no existe?', ['Definir nombre','Borrar print','Agregar HTML'],0,'Antes de leer una variable necesitas asignarle un valor.'),('¿Qué produce len([2, 4, 6]) en Python?', ['12','3','6'],1,'len cuenta elementos; esta lista tiene tres.')],
 'Tecnología': [('¿Cuál contraseña es más difícil de adivinar?', ['123456','Un conjunto largo de palabras aleatorias','Mi nombre'],1,'La longitud y la imprevisibilidad ayudan. Usa una contraseña distinta por cuenta.'),('¿Para qué sirve una dirección IP?', ['Identificar una interfaz en una red','Cargar la batería','Crear contraseñas'],0,'Permite dirigir datos a un destino en una red.'),('¿Qué conviene hacer antes de abrir un enlace inesperado?', ['Abrirlo rápido','Verificar remitente y dirección','Enviar la contraseña'],1,'Verificar el origen reduce el riesgo de engaños.')],
 'Lógica': [('Sigue la serie: 2, 4, 6, …', ['7','8','10'],1,'Sumamos 2 en cada paso.'),('Todos los gatos son mamíferos. Luna es un gato. Entonces…', ['Luna es mamífero','Todos los mamíferos son gatos','No sabemos nada'],0,'La regla general se aplica a Luna.'),('Si llueve, Ana usa paraguas. Ana usa paraguas. ¿Seguro que llueve?', ['Sí','No necesariamente','Nunca llueve'],1,'Podría usarlo para protegerse del sol. La implicación no funciona al revés.')],
 'IA': [('¿Qué es una IA?', ['Un sistema que realiza tareas usando modelos computacionales','Un animal real','Una fuente infalible'],0,'Una IA puede reconocer patrones y generar respuestas, pero puede equivocarse.'),('¿Puede una IA funcionar sin Internet?', ['Nunca','Sí, con el modelo en el dispositivo','Solo los domingos'],1,'Un modelo instalado puede procesar preguntas en el propio equipo.'),('¿Por qué conviene revisar una respuesta de IA?', ['Porque siempre es cierta','Porque puede inventar información','Porque nunca aprende patrones'],1,'Una respuesta convincente puede ser incorrecta: verifica los datos importantes.')]
}

class Start(Strict):
    level: str = Field('Premedia', pattern=r'^(Primaria|Premedia|Universidad / Técnico)$')
class Visitor(Strict):
    session: str = Field(min_length=20,max_length=60)
class Event(Visitor):
    kind: str = Field(pattern=r'^(heartbeat|lesson)$')
    lesson: str = Field('',max_length=30)
class Challenge(Visitor):
    category: str = Field('Todas',max_length=30)
    difficulty: str = Field('Normal',pattern=r'^(Fácil|Normal|Difícil)$')
class Answer(Visitor):
    index: int = Field(ge=0,le=2)
    choice: int = Field(ge=0,le=2)
class FairChat(Visitor):
    chat: Chat

def install_fair(app, db, engine):
    router=APIRouter(prefix='/api/fair')
    sessions={}
    for table in ('fair_sessions','fair_questions','fair_quizzes','fair_challenges'):
        db.execute(f'CREATE TABLE IF NOT EXISTS {table}(day TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0, seconds INTEGER NOT NULL DEFAULT 0)')
    def count(table, seconds=0, amount=1):
        db.execute(f'INSERT INTO {table}(day,count,seconds) VALUES(?,?,?) ON CONFLICT(day) DO UPDATE SET count=count+excluded.count,seconds=seconds+excluded.seconds',(local_day_iso(),amount,seconds))
    def visitor(key):
        item=sessions.get(key)
        if not item or time.monotonic()-item['seen']>210:
            sessions.pop(key,None)
            raise HTTPException(410,'La sesión terminó. Pulsa Nueva persona para comenzar.')
        elapsed=min(30,int(time.monotonic()-item['seen']))
        if elapsed: count('fair_sessions',elapsed,0)
        item['seen']=time.monotonic()
        return item
    @router.get('/bootstrap')
    def bootstrap():
        return {'categories':list(BANK)}
    @router.get('/qr')
    def qr(url:str):
        if len(url)>500:raise HTTPException(422,'Enlace demasiado largo.')
        parsed=urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
            raise HTTPException(422,'Usa una URL HTTP o HTTPS sin credenciales.')
        import qrcode
        from qrcode.image.svg import SvgPathImage
        # Only encode text; never fetch the URL or send it to an external service.
        image=qrcode.make(url,image_factory=SvgPathImage,box_size=8,border=4)
        return Response(image.to_string(),media_type='image/svg+xml')
    @router.get('/links')
    def links():
        return {name:os.environ.get(name,'') for name in ('PROJECT_URL','GITHUB_URL','SOCIAL_URL')}
    @router.post('/sessions')
    def start(value:Start):
        for key in list(sessions):
            if time.monotonic()-sessions[key]['seen']>210:sessions.pop(key,None)
        if len(sessions)>=100: raise HTTPException(429,'Hay muchas sesiones abiertas. Inténtalo en unos minutos.')
        key=secrets.token_urlsafe(24)
        sessions[key]={'seen':time.monotonic(),'level':value.level,'quiz':None,'busy':False,'lessons':set()}
        count('fair_sessions')
        return {'session':key}
    @router.post('/end')
    def end(value:Visitor):
        if value.session in sessions:
            visitor(value.session)
            sessions.pop(value.session,None)
        return {'ok':True}
    @router.post('/event')
    def event(value:Event):
        item=visitor(value.session)
        if value.kind=='lesson' and value.lesson not in item['lessons']:
            if value.lesson not in ('','Matemáticas','Inglés','Programación','Tecnología','IA','Curiosidades'):raise HTTPException(422,'Microlección desconocida.')
            count('fair_quizzes');item['lessons'].add(value.lesson)
        return {'ok':True}
    @router.get('/stats')
    def stats():
        return {table:db.one(f'SELECT count,seconds FROM {table} WHERE day=?',(local_day_iso(),)) or {'count':0,'seconds':0} for table in ('fair_sessions','fair_questions','fair_quizzes','fair_challenges')}
    @router.post('/challenge')
    def challenge(value:Challenge):
        item=visitor(value.session)
        if value.category!='Todas' and value.category not in BANK:raise HTTPException(422,'Categoría desconocida.')
        categories=random.sample(list(BANK),3) if value.category=='Todas' else [value.category]*3
        difficulty=['Fácil','Normal','Difícil'].index(value.difficulty)
        questions=[BANK[cat][difficulty if value.category=='Todas' else i] for i,cat in enumerate(categories)]
        item['quiz']={'questions':questions,'answers':[],'score':0}
        return {'questions':[{'question':q[0],'options':q[1]} for q in questions]}
    @router.post('/answer')
    def answer(value:Answer):
        quiz=visitor(value.session)['quiz']
        if not quiz or value.index!=len(quiz['answers']):raise HTTPException(409,'Esta pregunta ya fue respondida o no está activa.')
        question=quiz['questions'][value.index]
        correct=value.choice==question[2]
        quiz['answers'].append(value.choice);quiz['score']+=int(correct)
        if len(quiz['answers'])==3:count('fair_challenges')
        return {'correct':correct,'explanation':question[3],'score':quiz['score'],'finished':len(quiz['answers'])==3}
    @router.post('/chat')
    async def chat(value:FairChat):
        item=visitor(value.session)
        if item['busy']:raise HTTPException(409,'Allen todavía está pensando.')
        item['busy']=True
        request=prepare(value.chat.model_copy(update={'profile_id':1,'conversation_id':None,'use_library':False,'option':'Feria: da una explicación corta y directa, con un ejemplo concreto. No pidas permiso para responder.'}))
        profile={'name':'Visitante','level':item['level'],'memory':{}}
        text='';demo=False
        try:
            async with asyncio.timeout(60):
                async for event in engine.answer(request,profile,db.settings().model_copy(update={'max_tokens':min(db.settings().max_tokens,300)}),[]):
                    if event['type']=='delta':text+=event['text']
                    if event['type']=='meta':demo=event.get('demo',False)
            visitor(value.session)  # A reset during generation must discard the result.
            count('fair_questions')
            if demo:text='Allen está despertando de nuevo. Puedes reintentar la conexión o probar un reto y una microlección offline.'
            return {'text':text,'demo':demo,'conversation_state':advance(request.conversation_state,request.message,request.action,text).model_dump()}
        except HTTPException:raise
        except Exception:raise HTTPException(503,'Allen está despertando de nuevo. Intenta otra vez o explora los retos offline.')
        finally:item['busy']=False
    app.include_router(router)
