import sqlite3
import os
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .migrations import apply_migrations, LATEST_SCHEMA_VERSION
from .recovery import ensure_pre_migration_snapshot, create_snapshot, list_snapshots, integrity_report, restore_snapshot
from .time_utils import utc_now_iso, local_day, local_day_iso, local_day_from_timestamp

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, level TEXT, avatar TEXT);
CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS teacher_security(id INTEGER PRIMARY KEY CHECK(id=1), salt TEXT NOT NULL, pin_hash TEXT NOT NULL, kdf_n INTEGER NOT NULL DEFAULT 65536, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT, messages TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, kind TEXT, subject TEXT, xp INTEGER, day TEXT, reference TEXT, UNIQUE(user_id,kind,reference));
CREATE TABLE IF NOT EXISTS quiz_results(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, config TEXT, questions TEXT, result TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS flashcards(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, question TEXT, answer TEXT, due TEXT, interval INTEGER DEFAULT 0, reviews INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS learning_sessions(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, subject TEXT, seconds INTEGER, created TEXT);
CREATE TABLE IF NOT EXISTS library_packs(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT NOT NULL, documents TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS student_memory(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS saved_answers(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT NOT NULL, content TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversation_states(conversation_id INTEGER PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS study_plans(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, subject TEXT NOT NULL, goal TEXT NOT NULL, deadline TEXT NOT NULL, minutes_per_day INTEGER NOT NULL, level TEXT NOT NULL, topics TEXT NOT NULL, plan TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS study_sessions(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, plan_id INTEGER REFERENCES study_plans(id) ON DELETE CASCADE, day TEXT NOT NULL, status TEXT NOT NULL, started TEXT, completed TEXT, current_activity_index INTEGER NOT NULL DEFAULT 0, last_activity_at TEXT, activities_completed INTEGER NOT NULL DEFAULT 0, activities_skipped INTEGER NOT NULL DEFAULT 0, difficulties INTEGER NOT NULL DEFAULT 0, hints_used INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS study_session_events(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, session_id INTEGER REFERENCES study_sessions(id) ON DELETE CASCADE, kind TEXT NOT NULL, activity_index INTEGER NOT NULL, note TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS adventure_sessions(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, adventure_id TEXT NOT NULL, status TEXT NOT NULL, current_step INTEGER NOT NULL DEFAULT 0, completed_steps INTEGER NOT NULL DEFAULT 0, answers TEXT NOT NULL DEFAULT '[]', mistakes INTEGER NOT NULL DEFAULT 0, hints_used INTEGER NOT NULL DEFAULT 0, started_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT);
CREATE TABLE IF NOT EXISTS adventure_events(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, session_id INTEGER REFERENCES adventure_sessions(id) ON DELETE CASCADE, event TEXT NOT NULL, step INTEGER NOT NULL, answer TEXT NOT NULL DEFAULT '', correct INTEGER, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS simulation_results(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, subject TEXT NOT NULL, topics TEXT NOT NULL, questions TEXT NOT NULL, result TEXT, minutes INTEGER NOT NULL, started_at TEXT NOT NULL, completed_at TEXT, status TEXT NOT NULL DEFAULT 'active', answers TEXT NOT NULL DEFAULT '[]', updated_at TEXT, remaining_seconds INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS topic_mastery(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, subject TEXT NOT NULL, topic TEXT NOT NULL, mastery_score INTEGER NOT NULL DEFAULT 0, confidence INTEGER NOT NULL DEFAULT 0, attempts INTEGER NOT NULL DEFAULT 0, correct_answers INTEGER NOT NULL DEFAULT 0, incorrect_answers INTEGER NOT NULL DEFAULT 0, hints_used INTEGER NOT NULL DEFAULT 0, explanations_requested INTEGER NOT NULL DEFAULT 0, practice_count INTEGER NOT NULL DEFAULT 0, quiz_count INTEGER NOT NULL DEFAULT 0, last_seen TEXT, next_review TEXT, difficulty TEXT NOT NULL DEFAULT 'Normal', status TEXT NOT NULL DEFAULT 'new', UNIQUE(user_id,subject,topic));
CREATE TABLE IF NOT EXISTS learning_events(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, event_type TEXT NOT NULL, subject TEXT NOT NULL DEFAULT '', topic TEXT NOT NULL DEFAULT '', reference_type TEXT NOT NULL DEFAULT '', reference_id INTEGER, metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS profile_current_activity(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, activity_type TEXT NOT NULL, reference_id INTEGER, subject TEXT NOT NULL DEFAULT '', topic TEXT NOT NULL DEFAULT '', status TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS curriculum_edges(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, from_node TEXT NOT NULL, to_node TEXT NOT NULL, relation TEXT NOT NULL, reason TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS question_bank(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, unit_index INTEGER NOT NULL DEFAULT 0, topic_index INTEGER NOT NULL DEFAULT 0, subject TEXT NOT NULL DEFAULT '', topic TEXT NOT NULL DEFAULT '', objective TEXT NOT NULL DEFAULT '', prompt TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '', options_json TEXT NOT NULL DEFAULT '[]', difficulty TEXT NOT NULL DEFAULT 'Normal', kind TEXT NOT NULL DEFAULT 'open', source_page INTEGER, status TEXT NOT NULL DEFAULT 'reviewed', origin TEXT NOT NULL DEFAULT 'generated', attempts INTEGER NOT NULL DEFAULT 0, correct_count INTEGER NOT NULL DEFAULT 0, incorrect_count INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS course_quality_reviews(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, score INTEGER NOT NULL, blocking_issues INTEGER NOT NULL DEFAULT 0, report_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS diagnostic_results(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, answers_json TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_curriculum_course_relation ON curriculum_edges(course_id,relation,to_node);
CREATE INDEX IF NOT EXISTS idx_question_bank_course_topic ON question_bank(course_id,topic,status);
CREATE INDEX IF NOT EXISTS idx_diagnostics_user_course ON diagnostic_results(user_id,course_id,created_at);
CREATE INDEX IF NOT EXISTS idx_quality_course_created ON course_quality_reviews(course_id,created_at);
CREATE TABLE IF NOT EXISTS teacher_documents(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT NOT NULL, filename TEXT NOT NULL, mime TEXT NOT NULL, page_count INTEGER NOT NULL, source_text TEXT NOT NULL, pages_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY, owner_profile_id INTEGER REFERENCES users(id) ON DELETE CASCADE, source_document_id INTEGER REFERENCES teacher_documents(id) ON DELETE SET NULL, title TEXT NOT NULL, subject TEXT NOT NULL, level TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', version INTEGER NOT NULL DEFAULT 1, structure_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, published_at TEXT);
CREATE TABLE IF NOT EXISTS course_enrollments(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, status TEXT NOT NULL DEFAULT 'active', unit_index INTEGER NOT NULL DEFAULT 0, topic_index INTEGER NOT NULL DEFAULT 0, step_index INTEGER NOT NULL DEFAULT 0, started_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT, UNIQUE(course_id,user_id));
CREATE TABLE IF NOT EXISTS course_exam_results(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, answers_json TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS course_exam_sessions(id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, answers_json TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'active', started_at TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(course_id,user_id));
CREATE INDEX IF NOT EXISTS idx_course_exam_session_user ON course_exam_sessions(user_id,status,updated_at);
CREATE INDEX IF NOT EXISTS idx_course_exam_user ON course_exam_results(user_id,course_id,created_at);
CREATE INDEX IF NOT EXISTS idx_courses_status_subject ON courses(status,subject,updated_at);
CREATE INDEX IF NOT EXISTS idx_course_enrollment_user ON course_enrollments(user_id,status,updated_at);
CREATE INDEX IF NOT EXISTS idx_teacher_docs_user ON teacher_documents(user_id,created_at);
CREATE INDEX IF NOT EXISTS idx_mastery_user_status ON topic_mastery(user_id,status,mastery_score);
CREATE INDEX IF NOT EXISTS idx_mastery_review ON topic_mastery(user_id,next_review);
CREATE INDEX IF NOT EXISTS idx_learning_events_user_created ON learning_events(user_id,created_at);
CREATE INDEX IF NOT EXISTS idx_adventure_user_status ON adventure_sessions(user_id,status,updated_at);
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_status ON study_sessions(user_id,status,last_activity_at);
CREATE INDEX IF NOT EXISTS idx_flashcards_user_due ON flashcards(user_id,due);
CREATE UNIQUE INDEX IF NOT EXISTS idx_study_session_unique_day ON study_sessions(user_id,plan_id,day);
'''

def _ensure_compat_columns(db):
    study_existing={row['name'] for row in db.execute("PRAGMA table_info(study_sessions)").fetchall()}
    study_migrations={
        'current_activity_index':"ALTER TABLE study_sessions ADD COLUMN current_activity_index INTEGER NOT NULL DEFAULT 0",
        'last_activity_at':"ALTER TABLE study_sessions ADD COLUMN last_activity_at TEXT",
        'activities_completed':"ALTER TABLE study_sessions ADD COLUMN activities_completed INTEGER NOT NULL DEFAULT 0",
        'activities_skipped':"ALTER TABLE study_sessions ADD COLUMN activities_skipped INTEGER NOT NULL DEFAULT 0",
        'difficulties':"ALTER TABLE study_sessions ADD COLUMN difficulties INTEGER NOT NULL DEFAULT 0",
        'hints_used':"ALTER TABLE study_sessions ADD COLUMN hints_used INTEGER NOT NULL DEFAULT 0",
    }
    for column,sql in study_migrations.items():
        if column not in study_existing:
            db.execute(sql)

    sim_existing={row['name'] for row in db.execute("PRAGMA table_info(simulation_results)").fetchall()}
    sim_migrations={
        'status':"ALTER TABLE simulation_results ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
        'answers':"ALTER TABLE simulation_results ADD COLUMN answers TEXT NOT NULL DEFAULT '[]'",
        'updated_at':"ALTER TABLE simulation_results ADD COLUMN updated_at TEXT",
        'remaining_seconds':"ALTER TABLE simulation_results ADD COLUMN remaining_seconds INTEGER NOT NULL DEFAULT 0",
    }
    for column,sql in sim_migrations.items():
        if column not in sim_existing:
            db.execute(sql)

    teacher_existing={row['name'] for row in db.execute("PRAGMA table_info(teacher_security)").fetchall()}
    if 'kdf_n' not in teacher_existing:
        db.execute("ALTER TABLE teacher_security ADD COLUMN kdf_n INTEGER NOT NULL DEFAULT 16384")


def now():
    return utc_now_iso()

class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        previous_version=0
        if self.path.exists() and self.path.stat().st_size:
            try:
                probe=sqlite3.connect(self.path)
                previous_version=int(probe.execute('PRAGMA user_version').fetchone()[0])
                probe.close()
            except sqlite3.DatabaseError:
                previous_version=0
        ensure_pre_migration_snapshot(self.path,previous_version,LATEST_SCHEMA_VERSION)
        with self.connect() as db:
            db.executescript(SCHEMA)
            _ensure_compat_columns(db)
            apply_migrations(db)
            # Backfill a baseline history row for courses created before numbered migrations existed.
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='course_versions'").fetchone():
                db.execute("""INSERT OR IGNORE INTO course_versions(course_id,version_number,source_document_id,structure_json,diff_json,status,created_at,published_at)
                    SELECT id,version,source_document_id,structure_json,'{"summary":{"initial":true}}',status,created_at,published_at FROM courses""")
            if not db.execute('SELECT 1 FROM users LIMIT 1').fetchone():
                db.execute("INSERT INTO users VALUES (1,'Explorador',NULL,'Premedia','🐵')")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA secure_delete=ON')
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA synchronous=NORMAL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def schema_version(self):
        with self.connect() as db:
            return int(db.execute('PRAGMA user_version').fetchone()[0])

    def create_snapshot(self,reason='manual'):
        return create_snapshot(self.path,reason)

    def snapshots(self):
        return list_snapshots(self.path)

    def integrity(self):
        return integrity_report(self.path)

    def restore_snapshot(self,name):
        result=restore_snapshot(self.path,name)
        with self.connect() as db:
            db.executescript(SCHEMA)
            _ensure_compat_columns(db)
            apply_migrations(db)
        return result

    def all(self, sql, args=()):
        with self.connect() as db:
            return [dict(r) for r in db.execute(sql, args).fetchall()]

    def one(self, sql, args=()):
        rows = self.all(sql, args)
        return rows[0] if rows else None

    def execute(self, sql, args=()):
        with self.connect() as db:
            return db.execute(sql, args).lastrowid

    def settings(self):
        from .schemas import Settings
        row = self.one('SELECT value FROM settings WHERE id=1')
        if row:
            return Settings.model_validate_json(row['value'])
        legacy_url=os.environ.get('ALLEN_LLM_URL')
        if legacy_url:
            try:
                return Settings(ai_server=legacy_url)
            except ValueError:
                pass  # Never preserve an old external endpoint.
        return Settings()

    def prune(self):
        settings = self.settings()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=settings.retention_days)).isoformat()
        self.execute('DELETE FROM conversations WHERE updated < ? OR ?=0', (cutoff, int(settings.save_history)))
        self.execute('DELETE FROM quiz_results WHERE result IS NULL AND created < ?', (cutoff,))

    def award(self, user, kind, subject, xp, reference):
        self.execute('INSERT OR IGNORE INTO progress(user_id,kind,subject,xp,day,reference) VALUES(?,?,?,?,?,?)',
                     (user, kind, subject, xp, local_day_iso(), reference))

    def progress(self, user):
        events = self.all('SELECT * FROM progress WHERE user_id=?', (user,))
        days = {e['day'] for e in events}
        day = local_day()
        if day.isoformat() not in days:
            day -= timedelta(days=1)
        streak = 0
        while day.isoformat() in days:
            streak += 1
            day -= timedelta(days=1)
        xp = sum(e['xp'] for e in events)
        sessions = self.all('SELECT subject,SUM(seconds) seconds FROM learning_sessions WHERE user_id=? GROUP BY subject', (user,))
        session_rows = self.all("SELECT created,seconds FROM learning_sessions WHERE user_id=?", (user,))
        daily={}
        for row in session_rows:
            try:
                key=local_day_from_timestamp(row['created'])
            except Exception:
                key=str(row['created'])[:10]
            daily[key]=daily.get(key,0)+(row['seconds'] or 0)
        week = []
        today=local_day()
        for offset in range(6,-1,-1):
            current = today - timedelta(days=offset)
            week.append(dict(day=current.isoformat(), seconds=daily.get(current.isoformat(),0)))
        adventures_done=self.one("SELECT count(*) n FROM adventure_sessions WHERE user_id=? AND status='completed'",(user,))['n']
        adventure_active=self.one("SELECT count(*) n FROM adventure_sessions WHERE user_id=? AND status IN ('active','paused')",(user,))['n']
        study_plans=self.one('SELECT count(*) n FROM study_plans WHERE user_id=?',(user,))['n']
        study_active=self.one("SELECT count(*) n FROM study_sessions WHERE user_id=? AND status IN ('active','paused')",(user,))['n']
        simulations=self.one('SELECT count(*) n FROM simulation_results WHERE user_id=? AND result IS NOT NULL',(user,))['n']
        return dict(xp=xp, streak=streak, level=['Explorador','Curioso','Aprendiz','Investigador','Inventor'][min(xp//100,4)],
                    lessons=sum(e['kind']=='exercise' for e in events), quizzes=sum(e['kind']=='quiz' for e in events),
                    cards=self.one('SELECT count(*) n FROM flashcards WHERE user_id=? AND interval>=3', (user,))['n'],
                    minutes=sum(s['seconds'] for s in sessions)//60, subjects=sessions, week=week,
                    adventures_completed=adventures_done, adventures_active=adventure_active,
                    study_plans=study_plans, study_sessions_active=study_active, simulations=simulations)

    def erase_profile(self, user):
        with self.connect() as db:
            db.execute('DELETE FROM users WHERE id=?', (user,))
            if not db.execute('SELECT 1 FROM users LIMIT 1').fetchone():
                db.execute("INSERT INTO users VALUES (1,'Explorador',NULL,'Premedia','🐵')")

    def memory(self, user_id):
        import json
        row=self.one('SELECT data FROM student_memory WHERE user_id=?',(user_id,))
        if row: return json.loads(row['data'])
        profile=self.one('SELECT name FROM users WHERE id=?',(user_id,))
        return dict(onboarded=bool(profile and profile['name']!='Explorador'),preferences=[],interests=[],recent_topics=[],difficult_topics=[],daily_goal='',goal_date='')

    def remember(self, user_id, **changes):
        import json
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            row=connection.execute('SELECT data FROM student_memory WHERE user_id=?',(user_id,)).fetchone()
            memory=json.loads(row['data']) if row else self.memory(user_id)
            memory.update(changes)
            connection.execute('INSERT OR REPLACE INTO student_memory(user_id,data) VALUES(?,?)',(user_id,json.dumps(memory,ensure_ascii=False)))
        return memory
