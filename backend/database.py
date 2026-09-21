import sqlite3
import os
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, level TEXT, avatar TEXT);
CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT, messages TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, kind TEXT, subject TEXT, xp INTEGER, day TEXT, reference TEXT, UNIQUE(user_id,kind,reference));
CREATE TABLE IF NOT EXISTS quiz_results(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, config TEXT, questions TEXT, result TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS flashcards(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, question TEXT, answer TEXT, due TEXT, interval INTEGER DEFAULT 0, reviews INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS learning_sessions(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, subject TEXT, seconds INTEGER, created TEXT);
CREATE TABLE IF NOT EXISTS library_packs(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT NOT NULL, documents TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS student_memory(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS saved_answers(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, title TEXT NOT NULL, content TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversation_states(conversation_id INTEGER PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE, value TEXT NOT NULL);
PRAGMA user_version=4;
'''

def now():
    return datetime.now(timezone.utc).isoformat()

class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)
            if not db.execute('SELECT 1 FROM users LIMIT 1').fetchone():
                db.execute("INSERT INTO users VALUES (1,'Explorador',NULL,'Premedia','🐵')")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA secure_delete=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

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
                     (user, kind, subject, xp, date.today().isoformat(), reference))

    def progress(self, user):
        events = self.all('SELECT * FROM progress WHERE user_id=?', (user,))
        days = {e['day'] for e in events}
        day = date.today()
        if day.isoformat() not in days:
            day -= timedelta(days=1)
        streak = 0
        while day.isoformat() in days:
            streak += 1
            day -= timedelta(days=1)
        xp = sum(e['xp'] for e in events)
        sessions = self.all('SELECT subject,SUM(seconds) seconds FROM learning_sessions WHERE user_id=? GROUP BY subject', (user,))
        return dict(xp=xp, streak=streak, level=['Explorador','Curioso','Aprendiz','Investigador','Inventor'][min(xp//100,4)],
                    lessons=sum(e['kind']=='exercise' for e in events), quizzes=sum(e['kind']=='quiz' for e in events),
                    cards=self.one('SELECT count(*) n FROM flashcards WHERE user_id=? AND interval>=3', (user,))['n'],
                    minutes=sum(s['seconds'] for s in sessions)//60, subjects=sessions)

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
