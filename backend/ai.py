import asyncio
import json
import httpx
from .security import safe_reply

from .prompts import system_prompt, identity_reply
from .tutoring import arithmetic_reply, network_intro
from .conversation import prepare, guard_action

class LocalAI:
    def __init__(self, transport=None):
        self.transport = transport
        self.lock = asyncio.Semaphore(1)

    def client(self, timeout=90):
        return httpx.AsyncClient(timeout=timeout, trust_env=False, follow_redirects=False, transport=self.transport)

    async def status(self, settings):
        if settings.demo:
            return dict(state='MODO DEMO', connected=False, models=[], configured=bool(settings.model))
        try:
            async with self.client(2) as client:
                health = await client.get(settings.ai_server+'/health')
                health.raise_for_status()
                response = await client.get(settings.ai_server+'/v1/models')
                response.raise_for_status()
                models = [str(m['id']) for m in response.json()['data']]
                connected = bool(models) and (not settings.model or settings.model in models)
                return dict(state='IA LOCAL ACTIVA' if connected else 'IA LOCAL DESCONECTADA', connected=connected,
                            models=models, configured=bool(settings.model), effective_model=settings.model or (models[0] if models else ''))
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return dict(state='IA LOCAL DESCONECTADA', connected=False, models=[], configured=bool(settings.model))

    def messages(self, request, profile, settings, sources):
        system = system_prompt(request, profile, sources)
        budget = settings.context_size-settings.max_tokens-256
        used = len(system.encode('utf-8'))+len(request.message.encode('utf-8'))
        if used > budget:
            raise ValueError('El texto es largo para el contexto configurado. Divídelo en partes o aumenta el contexto en Configuración y en llama.cpp.')
        history=[]
        for message in reversed(request.history):
            size=len(message.content.encode('utf-8'))
            if used+size > budget:
                break
            history.insert(0,message.model_dump())
            used+=size
        return [{'role':'system','content':system}, *history, {'role':'user','content':request.message}]

    async def answer(self, request, profile, settings, sources):
        if request.conversation_state is None: request=prepare(request)
        blocked = safe_reply(request.message) or guard_action(request) or identity_reply(request.message) or arithmetic_reply(request) or network_intro(request)
        if blocked:
            yield {'type':'meta','demo':False,'safety':True}
            yield {'type':'delta','text':blocked}
            return
        status = await self.status(settings)
        if not status['connected']:
            yield {'type':'meta','demo':True}
            text = '**MODO DEMO · IA local sin conectar** · Allen todavía está despertando. Revisa que la IA esté iniciada en Configuración.\n\nMientras tanto, puedes practicar con los quizzes, crear tarjetas y explorar la biblioteca: todo funciona en este dispositivo.'
            if sources:
                text += '\n\n**Lectura local: '+sources[0]['title']+'**\n\n'+sources[0]['content'][:1500]
            yield {'type':'delta','text':text}
            return
        messages=self.messages(request,profile,settings,sources)
        yield {'type':'meta','demo':False}
        payload=dict(model=status['effective_model'],messages=messages,temperature=settings.temperature,max_tokens=settings.max_tokens,stream=True)
        async with self.lock:
            async with self.client() as client:
                async with client.stream('POST',settings.ai_server+'/v1/chat/completions',json=payload) as response:
                    response.raise_for_status()
                    pending=''
                    total=0
                    async for line in response.aiter_lines():
                        if not line.startswith('data:'):
                            continue
                        raw=line[5:].strip()
                        if raw=='[DONE]':
                            break
                        data=json.loads(raw)
                        choices=data.get('choices',[])
                        if not choices:
                            continue
                        piece=choices[0].get('delta',{}).get('content') or ''
                        pending+=piece
                        total+=len(piece)
                        if total>50000:
                            raise ValueError('La respuesta fue demasiado larga. Prueba una pregunta más breve.')
                        if '\n\n' in pending:
                            paragraph,pending=pending.rsplit('\n\n',1)
                            safe=safe_reply(paragraph)
                            yield {'type':'delta','text':safe or paragraph+'\n\n'}
                            if safe:
                                return
                    if pending:
                        yield {'type':'delta','text':safe_reply(pending) or pending}
