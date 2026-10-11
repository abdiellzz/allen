"""Optional mobile tutor bridge; inherits ALLEN's local access, license and CSRF guard.

No cloud provider, arbitrary model URL, remote profile database or chat persistence.
"""
import asyncio
import json
import time
from collections import deque
from typing import Literal

import httpx
from fastapi import HTTPException
from pydantic import Field

from .schemas import Strict, Chat, ConversationState


class MobileTutorRequest(Strict):
    message: str = Field(min_length=1, max_length=600)
    topic_id: str = Field(min_length=1, max_length=80)
    question_id: str | None = Field(None, max_length=80)
    last_answer: str | None = Field(None, max_length=200)
    level: Literal['bases', 'practice', 'challenge'] = 'bases'


def install_mobile_tutor(app, db, engine, token, directory):
    path = directory/'catalogue.json'
    catalogue = json.loads(path.read_text(encoding='utf-8'))
    topics = {t['id']: {**t, 'source': c['source'], 'subject': c['subject']}
              for c in catalogue for t in c['topics']}
    recent = deque(maxlen=30)

    @app.get('/api/mobile/bootstrap')
    async def bootstrap():
        status = await engine.status(db.settings())
        return dict(token=token, connected=bool(status.get('connected')),
                    local=True, max_message=600, response_tokens=320)

    @app.post('/api/mobile/tutor')
    async def tutor(value: MobileTutorRequest):
        topic = topics.get(value.topic_id)
        if not topic:
            raise HTTPException(422, 'Tema no disponible en el catálogo revisable.')
        question = next((q for q in topic['questions'] if q['id']==value.question_id), None)
        if value.question_id and not question:
            raise HTTPException(422, 'La pregunta no pertenece al tema.')
        if value.last_answer and (not question or value.last_answer not in question['options']):
            raise HTTPException(422, 'Respuesta contextual no válida.')
        now = time.monotonic()
        while recent and recent[0] < now-600:
            recent.popleft()
        if len(recent)>=20:
            raise HTTPException(429, 'Espera unos minutos. El tutor permite 20 consultas por diez minutos en esta instalación.')
        recent.append(now)
        # The URL is validated as loopback by existing Settings. Not supplied by the client.
        settings = db.settings().model_copy(update={'max_tokens': min(db.settings().max_tokens,320), 'save_history':False})
        context = dict(objective=topic['objective'], explanation=topic['explanation'],
                       example=topic['example'], alternative=topic['alternative'])
        if question:
            context['exercise'] = question['prompt']
            if value.last_answer:
                context['student_answer'] = value.last_answer
                context['feedback'] = question['feedback']
        source = dict(title=topic['source'],content=json.dumps(context,ensure_ascii=False))
        request = Chat(message=value.message,subject=topic['subject'],mode='Tutor',
                       action='dont_understand',history=[],use_library=False,
                       conversation_state=ConversationState(current_topic=topic['title'],
                           active_exercise=question['prompt'] if question else '',
                           answer_revealed=bool(value.last_answer),mode='guided_learning'))
        profile = dict(name='Estudiante',age=None,level='Primaria' if value.level=='bases' else 'Premedia',avatar='🐵')

        async def collect():
            if not (await engine.status(settings)).get('connected'):
                raise HTTPException(503, 'Inicia tu modelo local. El tutor guiado sigue disponible sin IA.')
            text = ''
            async for event in engine.answer(request,profile,settings,[source]):
                if event.get('demo'):
                    raise HTTPException(503, 'La IA local dejó de estar disponible.')
                if event.get('type')=='delta':
                    text += event.get('text','')
                if len(text)>12000:
                    raise HTTPException(503, 'La respuesta fue demasiado larga. Usa una pregunta más breve.')
            if not text.strip():
                raise HTTPException(503, 'La IA no devolvió una explicación. Prueba la ayuda preparada.')
            return dict(answer=text,generated=True,source=topic['source'],local=True)
        try:
            return await asyncio.wait_for(collect(),timeout=35)
        except (TimeoutError, httpx.HTTPError, ValueError, KeyError, TypeError):
            raise HTTPException(503, 'La IA local no respondió a tiempo. Puedes continuar con el tutor guiado.') from None
