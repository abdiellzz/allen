"""Start the loopback-only ALLEN server, avoid duplicates, and open its URL."""
import json
import os
import argparse
from pathlib import Path
import sqlite3
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:8787'
LOG = ROOT / 'logs' / 'launcher.log'
PID_FILE = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'ALLEN' / 'launcher' / 'allen.pid'


def log(message):
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open('a', encoding='utf-8') as stream:
        stream.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {message}\n')


def healthy():
    try:
        with urllib.request.urlopen(URL + '/api/health', timeout=1) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError):
        return False


def port_open():
    with socket.socket() as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(('127.0.0.1', 8787)) == 0


def demo_selected():
    db = Path(os.environ.get('ALLEN_DB_PATH', Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'ALLEN' / 'allen.sqlite3'))
    if not db.is_file():
        return False
    try:
        with sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True) as connection:
            row = connection.execute('SELECT value FROM settings WHERE id=1').fetchone()
        return bool(json.loads(row[0]).get('demo')) if row else False
    except (sqlite3.Error, ValueError, TypeError):
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ai-status', type=Path)
    parser.add_argument('--no-open', action='store_true', help='Verifica e inicia ALLEN sin abrir navegador.')
    options = parser.parse_args()
    status = options.ai_status.read_text(encoding='ascii').strip() if options.ai_status and options.ai_status.is_file() else ('demo' if demo_selected() else 'error')
    if status == 'error':
        print('ALLEN no pudo iniciar su inteligencia artificial local. El backend no se iniciará.')
        print('Revisa la causa y los detalles en logs/launcher.log y logs/llama-server.log.')
        log('ERROR AI startup rejected backend launch')
        return 1
    if healthy():
        if options.no_open:
            print(f'ALLEN ya está activo en {URL}')
        else:
            print(f'ALLEN ya está activo. Abriendo {URL}')
            webbrowser.open(URL)
        return 0
    if port_open():
        print('El puerto 8787 está ocupado por otra aplicación, y no responde como ALLEN.')
        log('ERROR port 8787 occupied by non-ALLEN service')
        return 1
    print('Iniciando servidor ALLEN...')
    with LOG.open('a', encoding='utf-8') as stream:
        child = subprocess.Popen([sys.executable, str(ROOT / 'server.py')], cwd=ROOT,
                                 stdin=subprocess.DEVNULL, stdout=stream, stderr=stream,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(child.pid), encoding='ascii')
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if child.poll() is not None:
            PID_FILE.unlink(missing_ok=True)
            print('No se pudo iniciar el servidor ALLEN. Revisa logs/launcher.log.')
            log(f'ERROR backend exited code={child.returncode}')
            return 1
        if healthy():
            PID_FILE.parent.mkdir(parents=True, exist_ok=True)
            PID_FILE.write_text(str(child.pid), encoding='ascii')
            log(f'backend started pid={child.pid} url={URL}')
            print('ALLEN está listo.')
            if options.no_open:
                print(f'ALLEN listo en {URL}.')
            else:
                print(f'Abriendo: {URL}')
                webbrowser.open(URL)
            return 0
        time.sleep(0.5)
    child.terminate()
    PID_FILE.unlink(missing_ok=True)
    print('El servidor ALLEN no respondió en 60 segundos. Revisa logs/launcher.log.')
    log('ERROR backend health timeout')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
