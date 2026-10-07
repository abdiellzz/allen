from __future__ import annotations
from datetime import datetime, timezone

BASE_VERSION=8
LATEST_SCHEMA_VERSION=10

MIGRATIONS={
    9: (
        "course_versions",
        """
        CREATE TABLE IF NOT EXISTS course_versions(
            id INTEGER PRIMARY KEY,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            version_number INTEGER NOT NULL,
            source_document_id INTEGER REFERENCES teacher_documents(id) ON DELETE SET NULL,
            structure_json TEXT NOT NULL,
            diff_json TEXT NOT NULL DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL,
            published_at TEXT,
            UNIQUE(course_id,version_number)
        );
        CREATE INDEX IF NOT EXISTS idx_course_versions_course ON course_versions(course_id,version_number DESC);
        """
    ),
    10: (
        "migration_history",
        """
        CREATE TABLE IF NOT EXISTS schema_migrations(
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );
        """
    ),
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def current_version(connection):
    return int(connection.execute("PRAGMA user_version").fetchone()[0])

def apply_migrations(connection):
    version=current_version(connection)
    # ALLEN historically reached schema 8 through idempotent CREATE/ALTER logic.
    # A fresh database therefore starts migration history at that compatible baseline.
    if version==0:
        version=BASE_VERSION
        connection.execute(f"PRAGMA user_version={BASE_VERSION}")
    connection.execute("""CREATE TABLE IF NOT EXISTS schema_migrations(
        version INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TEXT NOT NULL
    )""")
    applied=[]
    for target in range(version+1,LATEST_SCHEMA_VERSION+1):
        if target not in MIGRATIONS:
            raise RuntimeError(f"Falta la migración {target}.")
        name,sql=MIGRATIONS[target]
        connection.executescript(sql)
        connection.execute("INSERT OR REPLACE INTO schema_migrations(version,name,applied_at) VALUES(?,?,?)",(target,name,_now()))
        connection.execute(f"PRAGMA user_version={target}")
        applied.append({"version":target,"name":name})
    return applied
