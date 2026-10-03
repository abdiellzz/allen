"""Graphical, license-first Windows launcher compiled to ALLEN.exe with Nuitka."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import webbrowser

from licensing.runtime import authorize, data_home

APP_VERSION = '1.0.0'
AI_URL = 'http://127.0.0.1:8080'
ALLEN_URL = 'http://127.0.0.1:8787'
IS_COMPILED = bool(getattr(sys, 'frozen', False) or '__compiled__' in globals())
APP_ROOT = Path(sys.argv[0]).resolve().parent if IS_COMPILED else Path(__file__).resolve().parents[1]
LOG_DIR = data_home() / 'logs'
LOG_PATH = LOG_DIR / 'launcher.log'


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open('a', encoding='utf-8') as stream:
        stream.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {message}\n')


def request_json(url: str, timeout: float = 2.0):
    with build_opener(ProxyHandler({})).open(url, timeout=timeout) as response:
        return response.status, json.load(response)


class AllenLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('ALLEN')
        self.root.geometry('460x455')
        self.root.resizable(False, False)
        self.root.configure(bg='#fff8ed')
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.logo = tk.PhotoImage(file=str(APP_ROOT / 'allen.png')).subsample(2, 2)
        tk.Label(self.root, image=self.logo, bg='#fff8ed').pack(pady=(12, 0))
        tk.Label(self.root, text=f'ALLEN {APP_VERSION}', font=('Segoe UI', 23, 'bold'), fg='#9a4d1a', bg='#fff8ed').pack(pady=(0, 0))
        tk.Label(self.root, text='Preparando tu experiencia…', font=('Segoe UI', 10), fg='#5d4537', bg='#fff8ed').pack(pady=(0, 6))
        self.steps = {}
        for name in ('Sistema', 'Licencia', 'Inteligencia artificial local', 'Modelo', 'ALLEN'):
            value = tk.StringVar(value=f'○  {name}')
            self.steps[name] = value
            tk.Label(self.root, textvariable=value, font=('Segoe UI', 9), fg='#66584e', bg='#fff8ed', anchor='w', width=38).pack(pady=1)
        self.state = tk.StringVar(value='Comprobando instalación y licencia…')
        tk.Label(self.root, textvariable=self.state, font=('Segoe UI', 10), fg='#4a4038', bg='#fff8ed', wraplength=410).pack(pady=5)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=260)
        self.progress.pack(pady=2)
        self.detail_button = tk.Button(self.root, text='Ver detalles', command=self.show_details, state='disabled')
        self.detail_button.pack(pady=8)
        self.activate_button = tk.Button(self.root, text='Abrir carpeta de activación', command=self.open_data, state='disabled')
        self.activate_button.pack(pady=2)
        self.details = ''
        self.backend = None
        threading.Thread(target=self.start, daemon=True).start()

    def set_state(self, value):
        self.root.after(0, self.state.set, value)

    def mark(self, name):
        self.root.after(0, self.steps[name].set, f'✓  {name}')

    def fail(self, detail, activation=False):
        self.details = str(detail)
        log(f'FAILED {type(detail).__name__}: {detail}')
        self.set_state('No fue posible iniciar ALLEN. Revisa los detalles.')
        self.root.after(0, self.progress.stop)
        self.root.after(0, self.detail_button.configure, {'state': 'normal'})
        if activation:
            self.root.after(0, self.activate_button.configure, {'state': 'normal'})

    def show_details(self):
        messagebox.showerror('ALLEN no pudo iniciarse', self.details or 'Error desconocido. Consulta el log local de ALLEN.')

    def open_data(self):
        os.startfile(str(data_home()))

    def start(self):
        try:
            self.root.after(0, self.progress.start, 12)
            self.set_state('Validando instalación, firma y licencia…')
            authorize(APP_ROOT, require_registry=True)
            self.mark('Sistema')
            self.mark('Licencia')
            self.set_state('Verificando modelo e inteligencia artificial local…')
            config_path = data_home() / 'local_model.json'
            config = json.loads(config_path.read_text(encoding='utf-8'))
            expected_server = (APP_ROOT / 'runtime' / 'llama' / 'llama-server.exe').resolve()
            server = Path(config['executable']).resolve()
            model = Path(config['model']).resolve()
            expected_models = (data_home() / 'models').resolve()
            if server != expected_server or not server.is_file():
                raise FileNotFoundError('No se encontró el runtime de llama.cpp distribuido con ALLEN.')
            if expected_models not in model.parents or not model.is_file():
                raise FileNotFoundError('No se encontró el modelo local en ProgramData\\ALLEN\\models.')
            self.mark('Modelo')
            ai_worker = APP_ROOT / 'allen_ai.exe'
            backend_exe = APP_ROOT / 'allen_backend.exe'
            if not ai_worker.is_file() or not backend_exe.is_file():
                raise FileNotFoundError('Faltan componentes compilados de ALLEN. Ejecuta Reparar desde el instalador.')

            env = os.environ.copy()
            env.update(ALLEN_APP_ROOT=str(APP_ROOT), ALLEN_DATA_HOME=str(data_home()),
                       ALLEN_MODEL_CONFIG=str(config_path), ALLEN_DISTRIBUTION='1')
            self.set_state('Cargando inteligencia artificial local…')
            status_file = Path(tempfile.gettempdir()) / f'allen-ai-{os.getpid()}.status'
            status_file.unlink(missing_ok=True)
            result = subprocess.run([str(ai_worker), '--status-file', str(status_file)], cwd=APP_ROOT,
                                    env=env, capture_output=True, text=True, timeout=1800,
                                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            log(f'AI worker exit={result.returncode}; stdout={result.stdout[-1200:]}; stderr={result.stderr[-1200:]}')
            if result.returncode != 0 or not status_file.is_file() or status_file.read_text(encoding='ascii').strip() != 'ready':
                raise RuntimeError('La IA local no superó /health y la inferencia real. Consulta logs/llama-server.log.')
            status_file.unlink(missing_ok=True)
            self.mark('Inteligencia artificial local')

            try:
                status, api_health = request_json(ALLEN_URL + '/api/health')
                backend_ready = status == 200 and api_health.get('application') is True and api_health.get('database') is True
            except (URLError, OSError):
                backend_ready = False
            if not backend_ready:
                self.set_state('Iniciando ALLEN…')
                self.backend = subprocess.Popen([str(backend_exe)], cwd=APP_ROOT, env=env,
                                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL,
                                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                deadline = time.monotonic() + 90
                while time.monotonic() < deadline:
                    if self.backend.poll() is not None:
                        raise RuntimeError(f'El backend compilado terminó con código {self.backend.returncode}.')
                    try:
                        status, api_health = request_json(ALLEN_URL + '/api/health')
                        if status == 200 and api_health.get('application') is True and api_health.get('database') is True:
                            break
                    except (URLError, OSError):
                        pass
                    time.sleep(0.5)
                else:
                    raise TimeoutError('ALLEN no respondió a /api/health en 90 segundos.')
            self.set_state('ALLEN está listo.')
            self.mark('ALLEN')
            self.root.after(0, self.progress.stop)
            log('READY distribution launcher; license, IA, inference and backend health passed')
            self.root.after(900, webbrowser.open, ALLEN_URL)
            self.root.after(1400, self.root.destroy)
        except Exception as exc:
            self.fail(exc, activation=isinstance(exc, (FileNotFoundError, ValueError)))

    def close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    AllenLauncher().run()
