"""Stop only ALLEN/llama-server processes recorded as launcher-owned."""
import os
from pathlib import Path
import subprocess
import sys

DATA = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'ALLEN' / 'launcher'


def stop(name):
    path = DATA / name
    if not path.is_file():
        print(f'{name[:-4]}: no fue iniciado por el launcher.')
        return
    try:
        pid = int(path.read_text(encoding='ascii').strip())
    except (ValueError, OSError):
        path.unlink(missing_ok=True)
        print(f'{name[:-4]}: archivo PID no válido; no se cerró ningún proceso.')
        return
    try:
        query = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'], check=False,
                               capture_output=True, text=True, encoding='mbcs')
        process_rows = [row for row in query.stdout.splitlines() if row.startswith('"')]
        executable = process_rows[0].split('","', 1)[0].strip('"').lower() if process_rows else ''
        expected = 'llama-server.exe' if name == 'llama.pid' else 'python.exe'
        if executable != expected:
            path.unlink(missing_ok=True)
            print(f'{name[:-4]}: el PID ya no corresponde al proceso esperado; no se cerró.')
            return
    except (OSError, IndexError):
        print(f'{name[:-4]}: no se pudo verificar el proceso; no se cerró.')
        return
    try:
        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'{name[:-4]} detenido (PID {pid}).')
    except subprocess.CalledProcessError:
        print(f'{name[:-4]} (PID {pid}) ya no estaba activo.')
    finally:
        path.unlink(missing_ok=True)


if os.name != 'nt':
    print('Este botón está disponible en Windows.')
    raise SystemExit(1)
stop('allen.pid')
stop('llama.pid')
