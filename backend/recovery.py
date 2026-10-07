from __future__ import annotations
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

KEEP_SNAPSHOTS=5
SAFE_NAME=re.compile(r"^[A-Za-z0-9._-]+\.sqlite3$")

def _stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def recovery_dir(db_path):
    root=Path(db_path).parent/"recovery"
    root.mkdir(parents=True,exist_ok=True)
    return root

def create_snapshot(db_path,reason="manual",preserve=None):
    path=Path(db_path)
    if not path.exists() or path.stat().st_size==0:
        return None
    clean=re.sub(r"[^A-Za-z0-9_-]+","-",reason).strip("-")[:40] or "snapshot"
    target=recovery_dir(path)/f"{_stamp()}-{clean}.sqlite3"
    source=sqlite3.connect(path)
    dest=sqlite3.connect(target)
    try:
        source.backup(dest)
    finally:
        dest.close();source.close()
    _rotate(path,preserve or set())
    return target.name

def ensure_pre_migration_snapshot(db_path,current_version,target_version):
    path=Path(db_path)
    if path.exists() and path.stat().st_size and current_version<target_version:
        return create_snapshot(path,f"pre-migration-v{current_version}-to-v{target_version}")
    return None

def _rotate(db_path,preserve=None):
    preserve=set(preserve or ())
    files=sorted(recovery_dir(db_path).glob("*.sqlite3"),key=lambda p:p.stat().st_mtime,reverse=True)
    kept=0
    for old in files:
        if old.name in preserve:
            continue
        kept+=1
        if kept>KEEP_SNAPSHOTS:
            try: old.unlink()
            except OSError: pass

def list_snapshots(db_path):
    out=[]
    for p in sorted(recovery_dir(db_path).glob("*.sqlite3"),key=lambda x:x.stat().st_mtime,reverse=True):
        out.append({"name":p.name,"bytes":p.stat().st_size,"modified":datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()})
    return out

def integrity_report(db_path):
    path=Path(db_path)
    if not path.exists():
        return {"ok":False,"integrity":"missing","foreign_key_issues":[],"bytes":0}
    con=sqlite3.connect(path)
    try:
        integrity=con.execute("PRAGMA integrity_check").fetchone()[0]
        fk=[{"table":r[0],"rowid":r[1],"parent":r[2],"fk_index":r[3]} for r in con.execute("PRAGMA foreign_key_check").fetchall()]
        version=int(con.execute("PRAGMA user_version").fetchone()[0])
        return {"ok":integrity=="ok" and not fk,"integrity":integrity,"foreign_key_issues":fk,"schema_version":version,"bytes":path.stat().st_size}
    finally:
        con.close()

def restore_snapshot(db_path,name):
    if not SAFE_NAME.fullmatch(name or ""):
        raise ValueError("Nombre de snapshot no válido.")
    path=Path(db_path); source_path=recovery_dir(path)/name
    if not source_path.exists():
        raise ValueError("No encontramos ese snapshot.")
    check=integrity_report(source_path)
    if not check["ok"]:
        raise ValueError("El snapshot no supera la comprobación de integridad.")
    safety=create_snapshot(path,"before-recovery-restore",{name})
    source=sqlite3.connect(source_path)
    dest=sqlite3.connect(path)
    try:
        source.backup(dest)
    finally:
        dest.close();source.close()
    return {"restored":name,"safety_snapshot":safety,"integrity":integrity_report(path)}
