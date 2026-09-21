"""Conversation state shared by prompt, persistence and UI; no model-generated commands."""
import re
from .schemas import ConversationState
from .prompts import normalized,topic_title,identity_reply
from .tutoring import EXPRESSION

TEXT_ACTIONS={'dame la respuesta':'reveal_answer','just give me the answer':'reveal_answer','mas facil':'simplify','otro ejemplo':'another_example','paso a paso':'step_by_step','ponme a prueba':'quiz_me','no entiendo':'dont_understand','estoy perdido':'lost','¿que aprendi?':'summary_learning'}

def exercise_from(text):
    if EXPRESSION.fullmatch(text):return text[:1200]
    if re.search(r'\b(resuelve|calcula|resolver|depura|ejercicio|problema de|corrige este codigo)\b',normalized(text)):
        return text[:1200]
    return ''

def advance(state,text,action='',answer=None):
    state=state.model_copy(deep=True)
    if answer is None:
        state.last_action=action
        if action:
            if action=='quiz_me':state.mode='quiz';state.pending_question=''
            elif action=='next': pass
            return state
        if identity_reply(text):
            return ConversationState(mode='identity')
        exercise=exercise_from(text)
        if exercise:
            return ConversationState(current_topic=topic_title(text),active_exercise=exercise,mode='guided_learning')
        topic=topic_title(text)
        if topic!='Conversación con Allen' and topic!=state.current_topic:
            return ConversationState(current_topic=topic,mode='explanation')
        if state.mode in ('quiz','guided_learning') and (re.fullmatch(r'-?\d+(?:[/.]\d+)?',text.strip()) or state.mode=='quiz'):
            return state
        # New substantive question replaces the previous exercise; short follow-ups keep topic only.
        topic=topic_title(text)
        return ConversationState(current_topic=topic if topic!='Conversación con Allen' else state.current_topic,mode='explanation')
    if state.mode=='identity':return state
    if action in ('quiz_me','next'):
        questions=re.findall(r'¿[^?]+\?',answer)
        state.pending_question=(questions[-1] if questions else answer)[-1200:]
        state.mode='quiz';state.answer_revealed=False
    elif state.mode=='quiz' and not action:
        state.mode='quiz_feedback';state.answer_revealed=True
    elif state.active_exercise and (action=='reveal_answer' or re.search(r'(?:el resultado(?: completo)? es|resultado completo de|la respuesta (?:final )?es)',normalized(answer))):
        state.answer_revealed=True;state.mode='final_answer';state.pending_question=''
    return state

def prepare(request,persisted=None):
    if persisted is not None:
        state=ConversationState.model_validate(persisted)
    elif request.conversation_state:
        state=request.conversation_state
    else:
        state=ConversationState()
        previous='';action=''
        for message in request.history:
            if message.role=='user':
                previous=message.content;action=TEXT_ACTIONS.get(normalized(previous).strip().rstrip('.!'),'')
                state=advance(state,previous,action)
            else:state=advance(state,previous,action,message.content)
    action=request.action or TEXT_ACTIONS.get(normalized(request.message).strip().rstrip('.!'),'')
    return request.model_copy(update={'action':action,'conversation_state':advance(state,request.message,action)})

def guard_action(request):
    state=request.conversation_state
    if request.action=='reveal_answer' and (not state or not (state.active_exercise or state.pending_question)):
        return 'No tengo un ejercicio pendiente todavía. Escríbeme uno y lo resolvemos.'
    if request.action=='next' and (not state or state.mode!='quiz_feedback'):
        return 'Primero vamos a terminar la pregunta actual.'
    return None
