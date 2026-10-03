"""Anonymous fair sessions. Visitor text and names are never written to SQLite."""
import asyncio
import random
import secrets
import time
import os
import json
import re
import logging
import httpx
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urlsplit
from datetime import date
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import Field
from .schemas import Strict, Chat
from .conversation import prepare, advance
from .prompts import normalized, is_project_idea_request

DATA_ROOT=Path(os.environ.get('ALLEN_APP_ROOT',Path(__file__).resolve().parent.parent))/'data'
DATASETS=('lessons','challenges','simulations','steam_projects','tech_topics','curiosities','routes','ranks','achievements','motivational_messages','assessments')

def prepared_reply(message, level='Premedia', name=''):
    """Honest, topic-matched local fallback; never invent an answer on model failure."""
    query=normalized(message)
    lessons=json.loads((DATA_ROOT/'lessons.json').read_text(encoding='utf-8'))['lessons']
    matches=[lesson for lesson in lessons if normalized(lesson['topic']) in query]
    if not matches and 'python' in query:
        matches=[lesson for lesson in lessons if lesson['id']=='prog_python']
    prefix='Allen está usando contenido disponible en el dispositivo.\n\n'
    if not matches:
        return prefix+'No tengo una respuesta preparada para esa pregunta. Puedes elegir un tema en Enséñame algo, practicar un reto o explorar una simulación.'
    lesson=max(matches,key=lambda l:len(l['topic']))
    explanation=lesson['conceptEasy'] if level=='Primaria' else lesson['concept']
    return prefix+explanation+'\n\nEjemplo: '+lesson['example']+'\n\n'+lesson['realWorld']+'\n\n'+('Vamos a practicar, '+name+'. ' if name else '')+lesson['question']

def prepared_project_idea(request,name=''):
    """Give concise, grounded ideas from ALLEN's project catalogue when one fits."""
    if not is_project_idea_request(request):return None
    query=normalized(request.message)
    if re.search(r'\b(paso a paso|como (?:lo )?(?:hago|construyo|programo)|escribe (?:el )?codigo|ayudame a programar|mejorar|mejorarlo|agregar|anadir|ampliar)\b',query):return None
    terms=set(re.findall(r'[a-z0-9]+',query))-{'dame','idea','ideas','proyecto','proyectos','para','desde','cero','basica','basico','principiantes','quiero','una','un','de','del','con','por','favor','recomienda','recomiendame','propone','proponme','crear','hacer'}
    term_weights={term:1 for term in terms}
    if 'ciberseguridad' in terms:term_weights['phishing']=2
    beginner=bool(re.search(r'\b(principiante|principiantes|desde cero|inicial)\b',query))
    if beginner and 'python' in terms:term_weights['simple']=1
    if not terms:return None
    projects=json.loads((DATA_ROOT/'steam_projects.json').read_text(encoding='utf-8'))['projects']
    def score(project):
        title=normalized(project['name'])
        description=normalized(' '.join([project.get('problem',''),project.get('solution','')]))
        details=normalized(' '.join(project.get('materials',[])+project.get('learnings',[])+project.get('steps',[])+project.get('interest',[])))
        relevance=sum(term_weights[term]*((5 if term in title.split() else 0)+(3 if term in description.split() else 0)+(1 if term in details.split() else 0)) for term in term_weights)
        return relevance+(8 if relevance and beginner and project.get('difficulty')=='Fácil' else 0)
    ranked=sorted(((score(project),project) for project in projects),key=lambda item:item[0],reverse=True)
    if not ranked or ranked[0][0]==0:
        subject_match=re.search(r'\b(?:proyecto|prototipo)\s+(?:de|para|sobre)?\s*[:\-]?\s*([^.!?\n]+)',request.message,re.I)
        if not subject_match:return None
        subject=re.sub(r'\s+(?:para principiantes|desde cero|básico|básica)$','',subject_match.group(1).strip(),flags=re.I).strip(' :,-')
        if not subject:return None
        greeting=f'¡Buena idea{", "+name if name else ""}! Un proyecto sobre **{subject}** puede ayudarte a planear una pregunta, probar una idea sencilla y explicar lo que observas.'
        example='Para empezar, haz un boceto o una simulación pequeña relacionada con el tema. Por ejemplo, anota qué esperas que ocurra y compáralo con el resultado de una prueba segura.'
        next_step='Después, repite la prueba cambiando una sola cosa y compara los resultados; con eso puedes decidir una mejora concreta.'
        return '\n\n'.join((greeting,example,next_step))
    project=ranked[0][1]
    solution=project.get('solution','un prototipo sencillo relacionado con el tema').strip().rstrip('.!?')
    def natural_fragment(value):
        return value if (len(value)>1 and value[:2].isupper()) or re.match(r'^[A-Z]/',value) else value[0].lower()+value[1:]
    greeting=(f'¡Buena idea{", "+name if name else ""}! Con **{project["name"]}** crearás algo práctico y descubrirás cómo funciona. '
              'No necesitas experiencia previa: Allen te explica desde cero y te acompaña paso a paso.')
    if re.match(r'^(construir|crear|programar|diseñar|desarrollar)\b',normalized(solution)):
        proposal='Podrías '+natural_fragment(solution)
    else:
        proposal='Una versión sencilla podría ser '+natural_fragment(solution)
    if 'humedad' in normalized(project['name']) and 'plantas' in normalized(project['name']):
        example='Por ejemplo, puedes practicar comparando qué nota el sensor cuando la tierra está seca y cuando está húmeda; Allen te ayuda a entender cada parte con calma.'
    else:
        example='Por ejemplo, puedes practicar con una parte pequeña: pruébala, observa qué ocurre y entiende cada paso antes de continuar.'
    explanation=f'{proposal}. {example}'
    optional=next((re.sub(r'^.*?opcional:\s*','',step,flags=re.I).strip().rstrip('.!?') for step in project.get('steps',[]) if re.search(r'opcional:',step,re.I)),None)
    next_step=(f'Si luego quieres ampliarlo, {optional[0].lower()+optional[1:]}.' if optional else 'Después, pruébalo con varios casos y anota qué funciona para decidir qué mejorar.')
    return '\n\n'.join((greeting,explanation,next_step))

def verified_intro(message,level,name=''):
    """Use the reviewed lesson for an exact introductory intent, not arbitrary chat."""
    query=normalized(message).strip(' ¿?¡!.')
    match=re.fullmatch(r'(?:explicame (?:que es |que son )?|que es |que son |define )(?:el |la |los |las )?(.+)',query)
    if not match:return None
    topic=match.group(1).strip()
    lessons=json.loads((DATA_ROOT/'lessons.json').read_text(encoding='utf-8'))['lessons']
    aliases={'una ia':'que es ia','ia':'que es ia','una variable':'variables','python':'python','phishing':'phishing'}
    topic=aliases.get(topic,topic)
    lesson=next((l for l in lessons if normalized(l['topic'])==topic),None)
    if not lesson:return None
    content=prepared_reply(lesson['topic'],level,name)
    return content.replace('Allen está usando contenido disponible en el dispositivo.','Contenido educativo preparado en este dispositivo.',1)

# question, choices, correct index, explanation, hint; all resources ship locally.
BANK = {
 'Matemáticas': [
  ('¿Cuánto es 15% de 200?', ['15','30','200'],1,'10% son 20 y 5% son 10: juntos suman 30.','Calcula primero el 10%.'),
  ('¿Cuánto es 8 × 7?', ['54','56','64'],1,'8 × 7 = 56. Puedes sumar 7 ocho veces.','Divide: 8 × 5 más 8 × 2.'),
  ('Si 2x + 6 = 20, ¿cuánto vale x?', ['7','10','14'],0,'Resta 6: 2x = 14. Divide entre 2: x = 7.','Primero quita el 6 de los dos lados.'),
  ('¿Cuánto es 3/4 de 100?', ['25','50','75'],2,'100 ÷ 4 = 25; 25 × 3 = 75.','Empieza calculando 1/4 de 100.'),
  ('Sigue la serie: 5, 10, 20, 40, …', ['45','60','80'],2,'Cada número es el doble del anterior: 40 × 2 = 80.','¿Qué operación repite la serie?')],
 'Inglés': [
  ('¿Qué significa computer?', ['Computadora','Carpeta','Compañero'],0,'Computer significa computadora.','Es el dispositivo que estás usando ahora.'),
  ('Completa: She ___ a book.', ['have','has','having'],1,'Con she usamos has: ella tiene un libro.','She es tercera persona singular.'),
  ('¿Qué frase habla del pasado?', ['I learn','I will learn','I learned'],2,'Learned es el pasado de learn: aprendí.','Busca la terminación -ed.'),
  ('¿Cómo se dice "gracias" en inglés?', ['Please','Thank you','Hello'],1,'Thank you significa gracias.','La dices cuando alguien te ayuda.'),
  ('Elige la forma correcta: They ___ playing.', ['is','are','am'],1,'They va con are: ellos están jugando.','They es plural.')],
 'Programación': [
  ('¿Qué guarda una variable?', ['Un valor','Solo imágenes','Una pantalla'],0,'Una variable permite dar un nombre a un valor.','Piensa en una caja con etiqueta.'),
  ('Python: print(nombre). ¿Qué falta si nombre no existe?', ['Definir nombre','Borrar print','Agregar HTML'],0,'Antes de leer una variable necesitas asignarle un valor.','Primero hay que crear la variable.'),
  ('¿Qué produce len([2, 4, 6]) en Python?', ['12','3','6'],1,'len cuenta elementos; esta lista tiene tres.','len significa longitud.'),
  ('¿Qué imprime print(2 + 3 * 4)?', ['20','14','24'],1,'Primero la multiplicación: 3 × 4 = 12; más 2 = 14.','Python respeta el orden de las operaciones.'),
  ('¿Para qué sirve un bucle for?', ['Repetir acciones','Borrar datos','Crear imágenes'],0,'Un bucle repite un bloque de código las veces que indiques.','Piensa en dar varias vueltas a lo mismo.')],
 'Tecnología': [
  ('¿Cuál contraseña es más difícil de adivinar?', ['123456','Un conjunto largo de palabras aleatorias','Mi nombre'],1,'La longitud y la imprevisibilidad ayudan. Usa una contraseña distinta por cuenta.','Larga y difícil de imaginar.'),
  ('¿Para qué sirve una dirección IP?', ['Identificar una interfaz en una red','Cargar la batería','Crear contraseñas'],0,'Permite dirigir datos a un destino en una red.','Como la dirección de una casa.'),
  ('¿Qué conviene hacer antes de abrir un enlace inesperado?', ['Abrirlo rápido','Verificar remitente y dirección','Enviar la contraseña'],1,'Verificar el origen reduce el riesgo de engaños.','Piensa en quién lo envió.'),
  ('¿Qué significa apagar el Wi-Fi?', ['Quedar sin conexión inalámbrica','Apagar la computadora','Borrar los archivos'],0,'El Wi-Fi es la conexión inalámbrica; sin él puedes seguir usando programas locales.','Wi-Fi es la red sin cables.'),
  ('¿Cuál de estos archivos suele pesar más?', ['Una foto','Un texto corto','Un emoji'],0,'Las fotos contienen mucha más información que unas letras.','Piensa en cuánta información guarda cada uno.')],
 'Lógica': [
  ('Sigue la serie: 2, 4, 6, …', ['7','8','10'],1,'Sumamos 2 en cada paso.','¿Cuánto aumenta cada número?'),
  ('Todos los gatos son mamíferos. Luna es un gato. Entonces…', ['Luna es mamífero','Todos los mamíferos son gatos','No sabemos nada'],0,'La regla general se aplica a Luna.','Aplica la regla a Luna.'),
  ('Si llueve, Ana usa paraguas. Ana usa paraguas. ¿Seguro que llueve?', ['Sí','No necesariamente','Nunca llueve'],1,'Podría usarlo para protegerse del sol. La implicación no funciona al revés.','¿El paraguas solo sirve para la lluvia?'),
  ('Si todos los perros ladran y Toby es un perro, entonces…', ['Toby ladra','Toby es un gato','Toby no ladra'],0,'La regla de los perros también cubre a Toby.','Toby pertenece al grupo de la regla.'),
  ('Tres cajas dicen "manzanas", "peras" y "mezcla", pero todas las etiquetas están mal. ¿De cuál sacas una fruta para corregirlas?', ['La de mezcla','La de manzanas','La de peras'],0,'La etiqueta "mezcla" es falsa: esa caja tiene una sola fruta y la que saques la define.','Recuerda: todas las etiquetas mienten.')],
 'IA': [
  ('¿Qué es una IA?', ['Un sistema que realiza tareas usando modelos computacionales','Un animal real','Una fuente infalible'],0,'Una IA puede reconocer patrones y generar respuestas, pero puede equivocarse.','Es un programa, no una persona.'),
  ('¿Puede una IA funcionar sin Internet?', ['Nunca','Sí, con el modelo en el dispositivo','Solo los domingos'],1,'Un modelo instalado puede procesar preguntas en el propio equipo.','¿Dónde está instalado el modelo?'),
  ('¿Por qué conviene revisar una respuesta de IA?', ['Porque siempre es cierta','Porque puede inventar información','Porque nunca aprende patrones'],1,'Una respuesta convincente puede ser incorrecta: verifica los datos importantes.','¿Suena seguro? Puede que no sea correcto.'),
  ('¿Qué necesita una IA para producir una respuesta?', ['Datos y cálculos en un procesador','Magia','Una pantalla táctil'],0,'El modelo calcula con datos; no hay magia, solo matemáticas.','Piensa en lo que hace una computadora.'),
  ('¿Qué es un chatbot?', ['Un programa que conversa','Un robot de limpieza','Un videojuego'],0,'Chat significa conversación: un chatbot conversa contigo.','Chat significa charlar.')],
 'Ciberseguridad': [
  ('¿Cuál de estas contraseñas es más segura?', ['123456','password','M!k3_2024#'],2,'Las contraseñas largas que mezclan símbolos, números y letras son más resistentes a ataques.','Busca la que tenga caracteres variados.'),
  ('¿Qué debes hacer ante un correo urgente que pide tu contraseña bancaria?', ['Enviarla de inmediato','Verificar llamando al banco por su canal oficial','Responder preguntando quién es'],1,'Los bancos nunca solicitan contraseñas por correo electrónico. Desconfía de la urgencia.','No uses enlaces del correo sospechoso.'),
  ('¿Qué añade la autenticación de dos factores (MFA)?', ['Una segunda contraseña igual','Una capa extra como un código en tu teléfono','Un antivirus adicional'],1,'MFA asegura que aunque roben tu clave, no puedan entrar sin tu dispositivo.','Dos factores significan dos pruebas distintas.'),
  ('¿Qué riesgo tiene una Wi-Fi pública sin contraseña?', ['Gasta más batería','Alguien en la misma red podría interceptar datos','Se borran tus fotos'],1,'En redes abiertas el tráfico puede ser capturado por terceros si no hay cifrado seguro.','Es una red compartida con desconocidos.'),
  ('¿Qué debes hacer si encuentras una memoria USB en la calle?', ['Conectarla para ver de quién es','Entregarla a una autoridad sin conectarla','Formatearla en tu laptop'],1,'Las memorias desconocidas pueden contener malware que se ejecuta al conectarlas.','No arriesgues tu equipo con dispositivos extraños.')],
 'Ciencia': [
  ('¿Cuántos planetas tiene el sistema solar?', ['7','8','9'],1,'El sistema solar cuenta con ocho planetas principales tras reclasificar a Plutón en 2006.','Mercurio a Neptuno.'),
  ('¿Qué proceso usan las plantas para producir energía con luz solar?', ['Respiración celular','Fotosíntesis','Digestión'],1,'La fotosíntesis transforma agua, CO2 y luz solar en glucosa y oxígeno.','Foto significa luz.'),
  ('¿A qué temperatura hierve el agua a nivel del mar?', ['90 °C','100 °C','120 °C'],1,'A nivel del mar y una atmósfera de presión, el punto de ebullición del agua es 100 °C.','Es la base de la escala Celsius.'),
  ('¿Qué órgano del cuerpo humano bombea sangre a todo el organismo?', ['El cerebro','El corazón','Los pulmones'],1,'El corazón funciona como una bomba muscular continua que distribuye oxígeno y nutrientes.','Late en tu pecho.'),
  ('¿Cuál es la fuerza que nos mantiene atraídos hacia la Tierra?', ['Magnetismo','Gravedad','Fricción'],1,'La gravedad es la atracción mutua entre masas descubierta por Isaac Newton.','Hace caer los objetos al suelo.')],
 'Redes': [
  ('¿Qué dispositivo conecta los equipos de tu hogar con Internet?', ['El monitor','El router','El teclado'],1,'El router encamina los paquetes de datos entre tu red local y la red global.','Tiene luces de Wi-Fi y puertos de red.'),
  ('¿Para qué sirve el servicio DNS en Internet?', ['Traducir nombres como google.com a direcciones IP','Guardar fotos en la nube','Dar contraseñas seguras'],0,'DNS es la guía telefónica de Internet: traduce nombres comprensibles a números IP.','Como buscar un nombre en una agenda.'),
  ('¿Qué tipo de cable se usa comúnmente para conectar redes locales?', ['Cable HDMI','Cable Ethernet (RJ-45)','Cable de audio'],1,'El cable Ethernet conecta tarjetas de red a switches y routers con alta velocidad y estabilidad.','Tiene un conector plástico con pestaña.'),
  ('¿Qué significa que una conexión use HTTPS en lugar de HTTP?', ['Que es más lenta','Que los datos viajan cifrados y seguros','Que no usa Internet'],1,'La "S" final indica Security: el tráfico entre tu navegador y el servidor está encriptado.','Fíjate en el candado del navegador.'),
  ('¿Cuál es una dirección IP privada típica de una red doméstica?', ['8.8.8.8','192.168.1.1','256.300.1.0'],1,'192.168.x.x es un rango reservado para redes locales privadas de hogares y oficinas.','Empieza por 192.168.')],
 'STEAM': [
  ('¿Qué figura geométrica da mayor rigidez y resistencia a una estructura?', ['El cuadrado','El triángulo','El pentágono'],1,'El triángulo es indeformable bajo cargas, por eso se usa en puentes y torres de grúa.','Tiene tres lados.'),
  ('¿Qué componente convierte electricidad en movimiento giratorio?', ['Un motor eléctrico','Una resistencia','Un condensador'],0,'El motor eléctrico transforma la energía electromagnética en rotación mecánica.','Hace girar hélices y ruedas.'),
  ('¿Qué sensor mide la temperatura del ambiente?', ['Un termistor o sensor de temperatura','Un micrófono','Un potenciómetro'],0,'Un sensor térmico varía su resistencia según el calor del entorno para medir grados.','Mide calor y frío.'),
  ('¿Qué material es un buen conductor de la electricidad?', ['El plástico','El cobre','La madera seca'],1,'Los metales como el cobre tienen electrones libres que permiten el flujo de corriente.','Los cables por dentro son de este metal.'),
  ('En diseño de prototipos, ¿qué significa iterar?', ['Copiar sin cambios','Probar, aprender del resultado y mejorar el diseño en ciclos','Rendirse al primer fallo'],1,'Iterar es la base del método de ingeniería: construir, probar, evaluar y refinar.','Ciclo continuo de mejora.')]
}

class Start(Strict):
    level: str = Field('Premedia', pattern=r'^(Primaria|Premedia|Universidad / Técnico)$')
class Visitor(Strict):
    session: str = Field(min_length=20,max_length=60)
class Event(Visitor):
    kind: str = Field(pattern=r'^(heartbeat|lesson|guided_activity|challenge|simulation|game|project|activity|project_completed|route)$')
    lesson: str = Field('',max_length=80)
class Challenge(Visitor):
    category: str = Field('Todas',max_length=30)
    difficulty: str = Field('Normal',pattern=r'^(Fácil|Normal|Difícil)$')
    count: int = Field(3,ge=3,le=5)
class Answer(Visitor):
    index: int = Field(ge=0,le=4)
    choice: int = Field(ge=0,le=2)
class FairChat(Visitor):
    chat: Chat
    name: str = Field('',max_length=40)
    level: str = Field('Premedia',pattern=r'^(Primaria|Premedia|Universidad / Técnico)$')
class EvaluationDiagnostic(Strict):
    project_id: str = Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9:_-]+$')
    endpoint: str = Field('/api/fair/chat',max_length=80)
    phase: str = Field('complete',max_length=16)
    http_status: int = Field(0,ge=0,le=599)
    duration_ms: int = Field(0,ge=0,le=600000)
    prompt_chars: int = Field(0,ge=0,le=100000)
    prompt_bytes: int = Field(0,ge=0,le=100000)
    approx_tokens: int = Field(0,ge=0,le=30000)
    empty_fields: list[str] = Field(default_factory=list,max_length=20)
    response: str = Field('',max_length=4000)
    error: str = Field('',max_length=600)
    exception: str = Field('',max_length=100)

def evaluation_logger():
    root=Path(os.environ.get('ALLEN_DATA_HOME',Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'ALLEN'))/'logs'
    logger=logging.getLogger('allen.steam_evaluation');logger.setLevel(logging.INFO)
    if not any(getattr(h,'baseFilename','').lower()==str(root/'steam-evaluation.log').lower() for h in logger.handlers):
        try:
            root.mkdir(parents=True,exist_ok=True)
            handler=RotatingFileHandler(root/'steam-evaluation.log',maxBytes=500000,backupCount=2,encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(message)s'));logger.addHandler(handler)
        except OSError:logger.exception('No se pudo abrir el log de evaluación STEAM')
    return logger

def install_fair(app, db, engine):
    router=APIRouter(prefix='/api/fair')
    eval_log=evaluation_logger()
    sessions={}
    tables=('fair_sessions','fair_questions','fair_quizzes','fair_challenges','fair_simulations','fair_games','fair_projects','fair_activities','fair_projects_completed','fair_routes')
    for table in tables:
        db.execute(f'CREATE TABLE IF NOT EXISTS {table}(day TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0, seconds INTEGER NOT NULL DEFAULT 0)')
    def count(table, seconds=0, amount=1):
        db.execute(f'INSERT INTO {table}(day,count,seconds) VALUES(?,?,?) ON CONFLICT(day) DO UPDATE SET count=count+excluded.count,seconds=seconds+excluded.seconds',(date.today().isoformat(),amount,seconds))
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
    @router.get('/data/{dataset}')
    def local_data(dataset:str):
        if dataset not in DATASETS:
            raise HTTPException(404,'Conjunto de datos no disponible.')
        target = os.path.join(os.path.dirname(os.path.dirname(__file__)),'data',f'{dataset}.json')
        if not os.path.exists(target):
            raise HTTPException(404,'Archivo no disponible.')
        import json
        with open(target, 'r', encoding='utf-8') as f:
            return json.load(f)
    @router.get('/qr')
    def qr(url:str):
        if len(url)>500:raise HTTPException(422,'Enlace demasiado largo.')
        parsed=urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
            raise HTTPException(422,'Usa una URL HTTP o HTTPS sin credenciales.')
        try:
            import qrcode
            from qrcode.image.svg import SvgPathImage
            image=qrcode.make(url,image_factory=SvgPathImage,box_size=8,border=4)
            return Response(image.to_string(),media_type='image/svg+xml')
        except ImportError:
            svg_fallback=f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#fff8ed"/><path d="M10 10h180v180H10z" fill="none"/><text x="100" y="100" font-size="12" text-anchor="middle" fill="#bb5316">QR Code</text></svg>'
            return Response(svg_fallback,media_type='image/svg+xml')
    @router.get('/links')
    def links():
        return {name:os.environ.get(name,'') for name in ('PROJECT_URL','GITHUB_URL','SOCIAL_URL')}
    @router.post('/evaluation-log')
    def evaluation_log(value:EvaluationDiagnostic):
        response=re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[email]',value.response)
        response=re.sub(r'(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)','[phone]',response)
        entry={'timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'project_id':value.project_id,'phase':value.phase,'endpoint':value.endpoint,'http_status':value.http_status,'duration_ms':value.duration_ms,'prompt_chars':value.prompt_chars,'prompt_bytes':value.prompt_bytes,'approx_tokens':value.approx_tokens,'empty_fields':value.empty_fields,'exception':value.exception.replace('\r',' ').replace('\n',' ')[:100],'error':value.error.replace('\r',' ').replace('\n',' ')[:600],'response':response.replace('\r',' ').replace('\n',' ')[:2000]}
        eval_log.info(json.dumps(entry,ensure_ascii=False,separators=(',',':')))
        return {'logged':True}
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
            valid={l['id'] for l in json.loads((DATA_ROOT/'lessons.json').read_text(encoding='utf-8'))['lessons']}
            if value.lesson not in valid|{'','Matemáticas','Inglés','Programación','Tecnología','IA','Curiosidades'}:raise HTTPException(422,'Microlección desconocida.')
            count('fair_quizzes');item['lessons'].add(value.lesson)
        if value.kind in ('challenge','simulation','game','project'):
            count({'challenge':'fair_challenges','simulation':'fair_simulations','game':'fair_games','project':'fair_projects'}[value.kind])
        if value.kind in ('activity','project_completed','route'):
            count({'activity':'fair_activities','project_completed':'fair_projects_completed','route':'fair_routes'}[value.kind])
        return {'ok':True}
    @router.get('/stats')
    def stats():
        result={table:db.one(f'SELECT count,seconds FROM {table} WHERE day=?',(date.today().isoformat(),)) or {'count':0,'seconds':0} for table in tables}
        result['eventStats']={key:result[table]['count'] for key,table in {'visitors':'fair_sessions','questions':'fair_questions','challenges':'fair_challenges','simulations':'fair_simulations','games':'fair_games','projects':'fair_projects'}.items()}
        result['eventStats']['learningMinutes']=round(result['fair_sessions']['seconds']/60,1)
        result['eventStats']['activitiesCompleted']=result['fair_activities']['count']
        return result
    @router.post('/challenge')
    def challenge(value:Challenge):
        item=visitor(value.session)
        if value.category!='Todas' and value.category not in BANK:raise HTTPException(422,'Categoría desconocida.')
        categories=(random.sample(list(BANK),value.count) if value.count<=len(BANK) else random.choices(list(BANK),k=value.count)) if value.category=='Todas' else [value.category]*value.count
        difficulty=['Fácil','Normal','Difícil'].index(value.difficulty)
        questions=[BANK[cat][difficulty if value.category=='Todas' else i] for i,cat in enumerate(categories)]
        item['quiz']={'questions':questions,'answers':[],'score':0}
        return {'questions':[{'question':q[0],'options':q[1],'hint':q[4]} for q in questions]}
    @router.post('/answer')
    def answer(value:Answer):
        quiz=visitor(value.session)['quiz']
        if not quiz:raise HTTPException(409,'No hay un reto activo.')
        total=len(quiz['questions'])
        if value.index>=total:raise HTTPException(409,'Esta pregunta no está activa.')
        current=len(quiz['answers'])
        if value.index==current:
            question=quiz['questions'][value.index]
            correct=value.choice==question[2]
            quiz['answers'].append({'choice':value.choice,'correct':correct,'attempts':1})
            quiz['score']+=int(correct)
            if len(quiz['answers'])==total:count('fair_challenges')
            return {'correct':correct,'explanation':question[3],'score':quiz['score'],'finished':len(quiz['answers'])==total,'attempts':1}
        last=quiz['answers'][-1]
        if value.index==current-1 and not last['correct'] and last['attempts']==1:
            question=quiz['questions'][value.index]
            correct=value.choice==question[2] and value.choice!=last['choice']
            last['attempts']=2;last['choice']=value.choice
            if correct:last['correct']=True;quiz['score']+=1
            return {'correct':correct,'explanation':question[3],'score':quiz['score'],'finished':len(quiz['answers'])==total,'attempts':2}
        raise HTTPException(409,'Esta pregunta ya fue respondida o no está activa.')
    @router.post('/chat')
    async def chat(value:FairChat):
        item=visitor(value.session)
        if item['busy']:raise HTTPException(409,'Allen todavía está pensando.')
        item['busy']=True
        request=prepare(value.chat.model_copy(update={'profile_id':1,'conversation_id':None,'use_library':False,'option':'Feria educativa: responde primero la pregunta con claridad, contexto y un ejemplo concreto. Termina con un breve siguiente paso.'}))
        profile={'name':value.name.strip() or 'Visitante','level':value.level,'memory':{}}
        text='';demo=False;unavailable=False
        try:
            idea=prepared_project_idea(request,value.name.strip() if not request.history else '') if not request.action else None
            if idea:
                visitor(value.session);count('fair_questions')
                return {'text':idea,'demo':False,'source':'project_catalog','conversation_state':advance(request.conversation_state,request.message,request.action,idea).model_dump()}
            intro=verified_intro(request.message,value.level,value.name.strip() if not request.history else '') if not request.action else None
            if intro:
                visitor(value.session);count('fair_questions')
                return {'text':intro,'demo':False,'source':'local_lesson','conversation_state':advance(request.conversation_state,request.message,request.action,intro).model_dump()}
            async with asyncio.timeout(120):
                async for event in engine.answer(request,profile,db.settings(),[]):
                    if event['type']=='delta':text+=event['text']
                    if event['type']=='meta':demo=event.get('demo',False);unavailable=event.get('unavailable',False)
            visitor(value.session)  # A reset during generation must discard the result.
            count('fair_questions')
            if demo:
                text=prepared_reply(request.message,value.level,value.name.strip() if not request.history else '')
            elif unavailable:
                raise HTTPException(503,'IA_LOCAL_UNAVAILABLE: la IA local no está activa; la entrega está guardada y puedes reintentar.')
            elif not text.strip():
                raise HTTPException(502,'IA_LOCAL_EMPTY: la IA local no produjo una respuesta válida.')
            return {'text':text,'demo':demo,'conversation_state':advance(request.conversation_state,request.message,request.action,text).model_dump()}
        except HTTPException:raise
        except (TimeoutError,httpx.TimeoutException) as exc:
            visitor(value.session)
            count('fair_questions')
            raise HTTPException(504,'TIMEOUT: la IA local tardó demasiado. Tu entrega se conserva y puedes reintentar.') from exc
        except Exception as exc:
            visitor(value.session)
            count('fair_questions')
            if db.settings().demo:
                text=prepared_reply(request.message,value.level,value.name.strip() if not request.history else '')
                return {'text':text,'demo':True,'conversation_state':advance(request.conversation_state,request.message,request.action,text).model_dump()}
            logging.getLogger('allen.steam_evaluation').warning('fair_chat_unavailable exception=%s',type(exc).__name__)
            raise HTTPException(503,'IA_LOCAL_UNAVAILABLE: la IA local no respondió; la entrega está guardada y puedes reintentar.') from exc
        finally:item['busy']=False
    app.include_router(router)
