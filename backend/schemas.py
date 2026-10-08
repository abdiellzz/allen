from typing import Literal
from datetime import date, datetime, timedelta
from urllib.parse import urlsplit
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

LEVELS = ['Primaria', 'Premedia', 'Media', 'Universidad / Técnico']
SUBJECTS = ['Matemáticas', 'Ciencias', 'Español', 'Inglés', 'Tecnología', 'Programación', 'Historia', 'Geografía']

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Settings(Strict):
    ai_server: str = 'http://127.0.0.1:8080'
    model: str = Field('', max_length=200)
    temperature: float = Field(0.6, ge=0, le=1.5)
    context_size: int = Field(4096, ge=2048, le=32768)
    max_tokens: int = Field(700, ge=64, le=4096)
    language: Literal['es'] = 'es'
    save_history: bool = True
    retention_days: int = Field(30, ge=1, le=90)
    demo: bool = False
    font_size: Literal['normal', 'grande', 'muy grande'] = 'normal'
    high_contrast: bool = False
    performance: Literal['Rápido','Equilibrado','Detallado'] = 'Equilibrado'

    @field_validator('ai_server')
    @classmethod
    def local_only(cls, value):
        u = urlsplit(value)
        if (u.scheme != 'http' or u.hostname not in ('127.0.0.1', 'localhost', '::1')
                or u.username or u.password or u.query or u.fragment
                or u.path not in ('', '/', '/v1/chat/completions') or not u.port or u.port == 8787):
            raise ValueError('Utiliza un servidor HTTP local con puerto, por ejemplo 127.0.0.1:8080.')
        return f'http://{"[::1]" if u.hostname == "::1" else "127.0.0.1"}:{u.port}'

    @model_validator(mode='after')
    def budget(self):
        if self.max_tokens > self.context_size // 2:
            raise ValueError('La respuesta máxima debe ocupar como mucho la mitad del contexto.')
        return self

class Profile(Strict):
    name: str = Field(min_length=1, max_length=40)
    age: int | None = Field(None, ge=5, le=120)
    level: Literal['Primaria', 'Premedia', 'Media', 'Universidad / Técnico'] = 'Premedia'
    avatar: Literal['🐵', '🦊', '🐼', '🐸', '🦉'] = '🐵'

class Message(Strict):
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=12000)

class ConversationState(Strict):
    current_topic: str = Field('',max_length=100)
    active_exercise: str = Field('',max_length=1200)
    answer_revealed: bool = False
    mode: Literal['conversation','explanation','guided_learning','quiz','quiz_feedback','final_answer','identity'] = 'conversation'
    last_action: str = Field('',max_length=40)
    pending_question: str = Field('',max_length=1200)

class Chat(Strict):
    profile_id: int = Field(1, ge=1)
    message: str = Field(min_length=1, max_length=12000)
    mode: Literal['Aprender', 'Tutor', 'Matemáticas', 'Explicar', 'Resumir', 'Idiomas', 'Programación', 'Futuro', 'Aprende IA'] = 'Aprender'
    subject: str = Field('General', max_length=60)
    option: str = Field('', max_length=150)
    history: list[Message] = Field(default_factory=list, max_length=30)
    conversation_id: int | None = Field(None, ge=1)
    regenerate: bool = False
    use_library: bool = False
    action: Literal['','simplify','another_example','step_by_step','quiz_me','different','dont_understand','lost','reveal_answer','summary_learning','hint','explain','next'] = ''
    conversation_state: ConversationState | None = None
    @field_validator('action',mode='before')
    @classmethod
    def canonical_action(cls,value):
        from .prompts import ALIASES
        return ALIASES.get(value,value)

class QuizRequest(Strict):
    profile_id: int = Field(1, ge=1)
    subject: str = Field('Matemáticas', max_length=60)
    topic: str = Field('Operaciones básicas', min_length=1, max_length=100)
    difficulty: Literal['Fácil', 'Normal', 'Difícil'] = 'Fácil'
    count: int = Field(5, ge=1, le=10)
    kind: Literal['multiple', 'boolean', 'short'] = 'multiple'

class Submission(Strict):
    profile_id: int = Field(ge=1)
    answers: list[str] = Field(max_length=10)
    @field_validator('answers')
    @classmethod
    def bounded(cls, values):
        if any(len(v) > 500 for v in values):
            raise ValueError('Respuesta demasiado larga')
        return values

class Card(Strict):
    profile_id: int = Field(ge=1)
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=2000)

class Review(Strict):
    profile_id: int = Field(ge=1)
    rating: Literal['No la sé', 'Difícil', 'Bien', 'Fácil']

class CardGeneration(Strict):
    profile_id: int = Field(ge=1)
    source: str = Field(min_length=1, max_length=8000)
    kind: Literal['Tema', 'Texto', 'Apuntes'] = 'Texto'
    count: int = Field(5, ge=1, le=10)

class Study(Strict):
    profile_id: int = Field(ge=1)
    subject: str = Field(min_length=1, max_length=60)
    seconds: int = Field(ge=10, le=60)

class LibraryImport(Strict):
    profile_id: int = Field(ge=1)
    filename: str = Field(min_length=1,max_length=200)
    content: str = Field(min_length=1,max_length=100000)

class QuizAnswer(Strict):
    profile_id: int = Field(ge=1)
    index: int = Field(ge=0,le=9)
    answer: str = Field(min_length=1,max_length=500)

class LearningMemory(Strict):
    preferences: list[Literal['Simple','Paso a paso','Con ejemplos','Normal']] = Field(default_factory=list,max_length=4)
    interests: list[str] = Field(default_factory=list,max_length=8)
    daily_goal: str = Field('',max_length=160)
    set_goal: bool = False
    @field_validator('interests')
    @classmethod
    def interest_lengths(cls,values):
        if any(not v.strip() or len(v)>60 for v in values): raise ValueError('Interés demasiado largo')
        return values

class SavedAnswer(Strict):
    profile_id: int = Field(ge=1)
    title: str = Field(min_length=1,max_length=120)
    content: str = Field(min_length=1,max_length=20000)


class StudyPlanCreate(Strict):
    profile_id: int = Field(ge=1)
    subject: str = Field(min_length=1,max_length=80)
    topics: list[str] = Field(min_length=1,max_length=12)
    deadline: str = Field(min_length=10,max_length=10)
    minutes_per_day: int = Field(ge=10,le=240)
    level: Literal['Primaria','Premedia','Media','Universidad / Técnico'] = 'Premedia'
    goal: str = Field(min_length=1,max_length=160)
    @field_validator('topics')
    @classmethod
    def topic_lengths(cls,values):
        if any(not v.strip() or len(v)>80 for v in values): raise ValueError('Tema no válido')
        return values

    @field_validator('deadline')
    @classmethod
    def bounded_deadline(cls,value):
        try:
            target=datetime.strptime(value,"%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError('Usa una fecha válida en formato AAAA-MM-DD.') from exc
        today=date.today()
        if target < today:
            raise ValueError('La fecha objetivo no puede estar en el pasado.')
        if target > today + timedelta(days=365):
            raise ValueError('La fecha objetivo no puede superar 365 días.')
        return value

class StudySessionEvent(Strict):
    profile_id: int = Field(ge=1)
    kind: Literal['started','completed','skipped','hint','understood','not_understood','paused']
    activity_index: int = Field(ge=0,le=100)
    note: str = Field('',max_length=500)

class GuideRequest(Strict):
    profile_id: int = Field(ge=1)
    title: str = Field('Guía de estudio',max_length=120)
    text: str = Field(min_length=20,max_length=20000)


class AdventureStart(Strict):
    profile_id: int = Field(ge=1)
    adventure_id: str = Field(min_length=1,max_length=80)

class AdventureEvent(Strict):
    profile_id: int = Field(ge=1)
    step: int = Field(ge=0,le=100)
    event: Literal['answer','hint','advance','pause','resume','complete','abandon']
    answer: str = Field('',max_length=500)
    correct: bool | None = None

class SimulationCreate(Strict):
    profile_id: int = Field(ge=1)
    subject: str = Field(min_length=1,max_length=80)
    topics: list[str] = Field(min_length=1,max_length=12)
    question_count: int = Field(5,ge=3,le=10)
    minutes: int = Field(20,ge=5,le=120)
    timed: bool = True
    level: Literal['Primaria','Premedia','Media','Universidad / Técnico'] = 'Premedia'


class SimulationProgress(Strict):
    profile_id: int = Field(ge=1)
    answers: list[str] = Field(default_factory=list,max_length=10)
    status: Literal['active','paused','interrupted'] = 'active'
    remaining_seconds: int | None = Field(None,ge=0,le=43200)


class TeacherImport(Strict):
    profile_id: int = Field(ge=1)
    title: str = Field(min_length=1,max_length=140)
    subject: str = Field(min_length=1,max_length=80)
    level: Literal['Primaria','Premedia','Media','Universidad / Técnico'] = 'Premedia'
    filename: str = Field(min_length=1,max_length=180)
    mime: str = Field(min_length=1,max_length=80)
    content_base64: str = Field(min_length=20,max_length=12_000_000)

class CourseReview(Strict):
    profile_id: int = Field(ge=1)
    structure: dict

class CoursePublish(Strict):
    profile_id: int = Field(ge=1)

class CourseEnroll(Strict):
    profile_id: int = Field(ge=1)

class CourseProgress(Strict):
    profile_id: int = Field(ge=1)
    unit_index: int = Field(ge=0,le=100)
    topic_index: int = Field(ge=0,le=100)
    step_index: int = Field(ge=0,le=100)
    status: Literal['active','paused','completed'] = 'active'


class CoursePackImport(Strict):
    profile_id: int = Field(ge=1)
    pack: dict


class CourseHelp(Strict):
    profile_id: int = Field(ge=1)
    unit_index: int = Field(ge=0,le=100)
    topic_index: int = Field(ge=0,le=100)


class CourseExamProgress(Strict):
    profile_id: int = Field(ge=1)
    answers: list[str] = Field(default_factory=list,max_length=50)
    status: Literal['active','paused'] = 'active'


class CourseVersionImport(Strict):
    profile_id: int = Field(ge=1)
    filename: str = Field(min_length=1,max_length=180)
    mime: str = Field(min_length=1,max_length=80)
    content_base64: str = Field(min_length=20,max_length=12_000_000)

class RecoveryRestore(Strict):
    snapshot: str = Field(min_length=1,max_length=180)



class TeacherPin(Strict):
    pin: str = Field(min_length=6,max_length=12,pattern=r'^\d{6,12}
    content: str = Field(min_length=20, max_length=64000)
)

class LicenseActivation(Strict):
    content: str = Field(min_length=20, max_length=64000)
