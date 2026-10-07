import asyncio
import json
import httpx
import time
from .security import safe_reply

from .prompts import system_prompt, identity_reply
from .tutoring import arithmetic_reply, network_intro
from .conversation import prepare, guard_action

class LocalAI:
    def __init__(self, transport=None):
        self.transport = transport
        self.lock = asyncio.Semaphore(1)
        self._status_cache = None
        self._status_cache_key = None
        self._status_cache_until = 0.0

    def client(self, timeout=90):
        return httpx.AsyncClient(timeout=timeout, trust_env=False, follow_redirects=False, transport=self.transport)

    async def status(self, settings, refresh=False):
        if settings.demo:
            return dict(state='MODO DEMO', connected=False, models=[], configured=bool(settings.model))
        key=(settings.ai_server, settings.model)
        now=time.monotonic()
        if not refresh and self._status_cache_key==key and self._status_cache and now < self._status_cache_until:
            return self._status_cache
        try:
            # One OpenAI-compatible request is enough to prove the local server is alive.
            # Caching avoids two extra round trips before every chat response.
            async with self.client(2) as client:
                response = await client.get(settings.ai_server+'/v1/models')
                response.raise_for_status()
                models = [str(m['id']) for m in response.json()['data']]
                connected = bool(models) and (not settings.model or settings.model in models)
                result=dict(state='IA LOCAL ACTIVA' if connected else 'IA LOCAL DESCONECTADA', connected=connected,
                            models=models, configured=bool(settings.model), effective_model=settings.model or (models[0] if models else ''))
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            result=dict(state='IA LOCAL DESCONECTADA', connected=False, models=[], configured=bool(settings.model))
        self._status_cache_key=key
        self._status_cache=result
        # Cache healthy local servers; disconnected states are checked again immediately so
        # starting/restarting llama.cpp is detected without making the user wait.
        self._status_cache_until=now+(15.0 if result.get('connected') else 0.0)
        return result

    def messages(self, request, profile, settings, sources):
        system = system_prompt(request, profile, sources)
        budget = settings.context_size-settings.max_tokens-256
        # context_size is measured in tokens, not bytes. Use a conservative local
        # estimate so Spanish prompts are not rejected merely for containing UTF-8 text.
        estimate=lambda text:max(1,(len(text)+2)//3)
        used = estimate(system)+estimate(request.message)
        if used > budget:
            raise ValueError('El texto es largo para el contexto configurado. Divídelo en partes o aumenta el contexto en Configuración y en llama.cpp.')
        history=[]
        # Long histories increase prompt-evaluation time on CPU. Keep the most recent
        # turns while preserving enough continuity for tutoring.
        for message in reversed(request.history[-12:]):
            size=estimate(message.content)
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
        # Most tutoring turns do not need hundreds of tokens. Smaller decode budgets
        # improve response time on CPU while summaries and explanations still get room.
        if request.action in ('hint','quiz_me','next') or request.mode in ('Tutor','Matemáticas'):
            token_budget=min(settings.max_tokens,320)
        elif request.mode in ('Resumir','Explicar') or request.action in ('summary_learning','step_by_step'):
            token_budget=min(settings.max_tokens,520)
        else:
            token_budget=min(settings.max_tokens,420)
        payload=dict(model=status['effective_model'],messages=messages,temperature=settings.temperature,max_tokens=token_budget,stream=True)
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
                        # Flush small chunks instead of waiting for a full paragraph.
                        # This makes the first visible text arrive much sooner on slow CPU inference.
                        should_flush = '\n\n' in pending or len(pending) >= 36 or (len(pending) >= 18 and pending.rstrip().endswith(('.', '?', '!', ':')))
                        if should_flush:
                            if '\n\n' in pending:
                                chunk,pending=pending.rsplit('\n\n',1)
                                chunk += '\n\n'
                            else:
                                chunk,pending=pending,''
                            safe=safe_reply(chunk)
                            yield {'type':'delta','text':safe or chunk}
                            if safe:
                                return
                    if pending:
                        yield {'type':'delta','text':safe_reply(pending) or pending}
