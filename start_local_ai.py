"""Find, start, and verify the configured loopback llama.cpp server."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, HTTPRedirectHandler, build_opener

ROOT = Path(os.environ.get('ALLEN_APP_ROOT', Path(__file__).resolve().parent)).resolve()
DATA = Path(os.environ.get('ALLEN_DATA_HOME', Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local/share')) / 'ALLEN'))
LOGS = ROOT / 'logs'
LAUNCH_LOG = LOGS / 'launcher.log'
LLAMA_LOG = LOGS / 'llama-server.log'
MODEL_REPO = 'ggml-org/Qwen3.5-0.8B-GGUF'
MODEL_FILE = 'Qwen3.5-0.8B-Q8_0.gguf'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def log(message):
    LOGS.mkdir(exist_ok=True)
    with LAUNCH_LOG.open('a', encoding='utf-8') as stream:
        stream.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {message}\n')


def health(url):
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(url + '/health', timeout=2) as response:
            return 'ready' if response.status == 200 else 'loading'
    except HTTPError as exc:
        return 'loading' if exc.code in (202, 503) else 'unavailable'
    except (URLError, OSError):
        return 'offline'


def preferences():
    path = Path(os.environ.get('ALLEN_DB_PATH', DATA / 'allen.sqlite3'))
    if not path.is_file():
        return {}
    with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as db:
        row = db.execute('SELECT value FROM settings WHERE id=1').fetchone()
    return json.loads(row[0]) if row else {}


def disable_demo_preference():
    path = Path(os.environ.get('ALLEN_DB_PATH', DATA / 'allen.sqlite3'))
    path.parent.mkdir(parents=True, exist_ok=True)
    defaults = {'ai_server': 'http://127.0.0.1:8080', 'model': '', 'temperature': 0.6,
                'context_size': 4096, 'max_tokens': 700, 'language': 'es', 'demo': False,
                'save_history': True, 'retention_days': 30, 'font_size': 'normal', 'high_contrast': False}
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL)')
        row = db.execute('SELECT value FROM settings WHERE id=1').fetchone()
        if row:
            defaults.update(json.loads(row[0]))
        defaults['demo'] = False
        db.execute('INSERT OR REPLACE INTO settings(id,value) VALUES(1,?)', (json.dumps(defaults, ensure_ascii=False),))


def known_executable(configured):
    candidates = [configured]
    path_exe = shutil.which('llama-server')
    if path_exe:
        candidates.append(path_exe)
    local = Path(os.environ.get('LOCALAPPDATA', DATA))
    candidates.extend(str(p) for p in (local / 'Microsoft' / 'WinGet' / 'Packages').glob('ggml.llamacpp*/*/llama-server.exe'))
    candidates.extend(str(p) for p in (ROOT / 'models').glob('*/llama-server.exe'))
    candidates.extend([str(ROOT / 'llama-server.exe'), str(ROOT / 'tools' / 'llama' / 'llama-server.exe')])
    for value in candidates:
        if value and Path(value).expanduser().is_file():
            candidate = Path(value).expanduser().resolve()
            if candidate.name.lower() in ('llama-server.exe', 'llama-server'):
                return candidate
    return None


def known_model(configured):
    if configured:
        path = Path(configured).expanduser()
        if path.is_file() and path.suffix.lower() == '.gguf':
            return path.resolve()
    roots = [ROOT / 'models', DATA / 'models']
    env_cache = os.environ.get('LLAMA_CACHE') or os.environ.get('HF_HUB_CACHE') or os.environ.get('HUGGINGFACE_HUB_CACHE')
    if env_cache:
        roots.append(Path(env_cache))
    if os.environ.get('HF_HOME'):
        roots.append(Path(os.environ['HF_HOME']) / 'hub')
    if os.environ.get('XDG_CACHE_HOME'):
        roots.append(Path(os.environ['XDG_CACHE_HOME']) / 'huggingface' / 'hub')
    roots.append(Path(os.environ.get('USERPROFILE', Path.home())) / '.cache' / 'huggingface' / 'hub')
    repo_dir = 'models--' + MODEL_REPO.replace('/', '--')
    for root in roots[:2]:
        if root.is_dir():
            for file in root.glob('*.gguf'):
                if file.is_file():
                    return file.resolve()
    for root in roots[2:]:
        snapshot = root / repo_dir / 'snapshots'
        if snapshot.is_dir():
            for file in snapshot.glob('*/Qwen3.5-0.8B*.gguf'):
                if file.is_file():
                    return file.resolve()
    return None


def save_config(path, executable, model):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {'executable': str(executable), 'model': str(model) if model else ''}
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    temp.replace(path)


def load_config(allow_missing_model=False):
    config_path = Path(os.environ.get('ALLEN_MODEL_CONFIG', DATA / 'local_model.json'))
    config = {}
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise ValueError(f'Configuración local inválida ({config_path}): {exc}') from exc
    executable = known_executable(config.get('executable'))
    if not executable:
        raise FileNotFoundError('No se encontró llama-server en la configuración, PATH, WinGet ni carpetas locales de ALLEN.')
    model = known_model(config.get('model'))
    if not model and not allow_missing_model:
        raise FileNotFoundError(f'No se encontró {MODEL_FILE} en la ruta configurada, modelos de ALLEN ni caché Hugging Face.')
    if config.get('executable') != str(executable) or (model and config.get('model') != str(model)):
        save_config(config_path, executable, model)
        disable_demo_preference()
        log(f'Updated model configuration path={config_path} executable={executable} model={model}')
    version = subprocess.run([str(executable), '--version'], capture_output=True, text=True, timeout=15)
    if version.returncode != 0:
        raise RuntimeError(f'llama-server no superó --version (código {version.returncode}): {(version.stderr or version.stdout)[-800:]}')
    return config_path, executable, model


def download_model(executable, config_path, settings, timeout):
    settings = {**settings, 'ai_server': settings.get('ai_server', 'http://127.0.0.1:8080')}
    _, url = command(executable, Path('placeholder.gguf'), settings)
    help_result = subprocess.run([str(executable), '--help'], capture_output=True, text=True, timeout=30)
    help_text = help_result.stdout + help_result.stderr
    if '--hf-repo' not in help_text or '--hf-file' not in help_text:
        raise RuntimeError('La versión instalada de llama-server no admite --hf-repo y --hf-file; actualiza llama.cpp desde WinGet.')
    cache_root = Path(os.environ.get('LLAMA_CACHE') or os.environ.get('HF_HUB_CACHE') or
                      os.environ.get('HUGGINGFACE_HUB_CACHE') or
                      (Path(os.environ['HF_HOME']) / 'hub' if os.environ.get('HF_HOME') else
                       Path(os.environ.get('USERPROFILE', Path.home())) / '.cache' / 'huggingface' / 'hub'))
    cache_root.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(cache_root).free < 1_200_000_000:
        raise OSError(f'No hay espacio suficiente para descargar el modelo Q8_0 (~0,78 GiB) en {cache_root}.')
    host = urlsplit(url).hostname
    port = urlsplit(url).port
    context = int(settings.get('context_size', 4096))
    args = [str(executable), '--hf-repo', MODEL_REPO + ':Q8_0', '--hf-file', MODEL_FILE,
            '--host', host, '--port', str(port), '-c', str(context), '--parallel', '1', '--threads', '4',
            '--reasoning', 'off', '--log-file', str(LLAMA_LOG)]
    log(f'DOWNLOAD model repo={MODEL_REPO} file={MODEL_FILE} executable={executable} command={subprocess.list2cmdline(args)}')
    print(f'Descargando {MODEL_REPO}:{MODEL_FILE} desde Hugging Face...', flush=True)
    LLAMA_LOG.parent.mkdir(parents=True, exist_ok=True)
    with LLAMA_LOG.open('a', encoding='utf-8') as stream:
        process = subprocess.Popen(args, cwd=str(executable.parent), stdin=subprocess.DEVNULL,
                                   stdout=stream, stderr=stream,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    try:
        deadline = time.monotonic() + max(60, min(timeout, 7200))
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'llama-server terminó durante la descarga/carga (código {process.returncode}).')
            if health(url) == 'ready':
                selected_model = model_id(url)
                answer = infer(url, selected_model)
                model = known_model(None)
                if not model:
                    raise RuntimeError('La inferencia respondió, pero no se encontró el GGUF descargado en la caché Hugging Face.')
                save_config(config_path, executable, model)
                log(f'DOWNLOAD_READY pid={process.pid} model={model} response={answer!r}')
                return process, model, selected_model, answer
            time.sleep(1)
        raise TimeoutError(f'La descarga o carga del modelo excedió {timeout} segundos.')
    except Exception:
        if process.poll() is None:
            process.terminate()
        raise


def command(executable, model, settings):
    url = urlsplit(settings.get('ai_server', 'http://127.0.0.1:8080'))
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1', 'localhost', '::1') or not url.port or url.port == 8787:
        raise ValueError('La IA necesita una dirección local con su propio puerto.')
    if url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
        raise ValueError('La dirección local configurada no es válida.')
    context = int(settings.get('context_size', 4096))
    if not 2048 <= context <= 32768:
        raise ValueError('El contexto configurado está fuera de rango.')
    host = '::1' if url.hostname == '::1' else '127.0.0.1'
    args = [str(executable), '-m', str(model), '--host', host, '--port', str(url.port), '-c', str(context),
            '--parallel', '1', '--threads', '4', '--reasoning', 'off', '--log-file', str(LLAMA_LOG)]
    return args, f'http://{host}:{url.port}'


def model_id(url):
    with build_opener(ProxyHandler({}), NoRedirect()).open(url + '/v1/models', timeout=10) as response:
        body = json.load(response)
    data = body.get('data') or []
    if not data or not data[0].get('id'):
        raise RuntimeError('llama-server respondió a /health, pero /v1/models no anunció un modelo.')
    return str(data[0]['id'])


def infer(url, selected_model):
    import httpx
    payload = {'model': selected_model, 'messages': [{'role': 'user', 'content': 'Responde únicamente: OK'}],
               'temperature': 0, 'max_tokens': 32, 'stream': True}
    pieces = []
    with httpx.Client(timeout=90, trust_env=False, follow_redirects=False) as client:
        with client.stream('POST', url + '/v1/chat/completions', json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith('data:'):
                    continue
                raw = line[5:].strip()
                if raw == '[DONE]':
                    break
                event = json.loads(raw)
                choices = event.get('choices') or []
                if choices:
                    content = choices[0].get('delta', {}).get('content') or ''
                    if content:
                        pieces.append(content)
    answer = ''.join(pieces).strip()
    if not answer:
        raise RuntimeError('El endpoint de chat respondió, pero la inferencia no produjo texto.')
    return answer


def tail(path, limit=14):
    try:
        return '\n'.join(path.read_text(encoding='utf-8', errors='replace').splitlines()[-limit:])
    except OSError:
        return '(sin log de llama-server)'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int, default=int(os.environ.get('ALLEN_AI_TIMEOUT', '120')))
    parser.add_argument('--status-file', type=Path)
    parser.add_argument('--allow-demo', action='store_true', help='Permite explícitamente abrir en modo demo.')
    parser.add_argument('--install-model', action='store_true', help='Descarga una vez Qwen3.5-0.8B-Q8_0 tras autorización explícita.')
    args = parser.parse_args()
    process = None
    owned_process = False
    started = time.monotonic()

    def write_status(value):
        if args.status_file:
            args.status_file.parent.mkdir(parents=True, exist_ok=True)
            args.status_file.write_text(value, encoding='ascii')

    try:
        settings = preferences()
        if (settings.get('demo') or args.allow_demo) and not args.install_model:
            write_status('demo')
            print('Modo demo activado explícitamente; no se iniciará la IA.', flush=True)
            return 0
        config_path, executable, model = load_config(allow_missing_model=True)
        if not model:
            install_requested = args.install_model
            if not install_requested and sys.stdin.isatty():
                print('ALLEN necesita instalar su modelo de inteligencia artificial local.', flush=True)
                print(f'Modelo: Qwen3.5-0.8B-Q8_0 ({MODEL_FILE}). Esta instalación se realiza una sola vez.', flush=True)
                try:
                    install_requested = input('¿Deseas instalarlo ahora? [S/N] ').strip().upper() in ('S', 'SI', 'SÍ')
                except EOFError:
                    install_requested = False
            if not install_requested:
                raise FileNotFoundError(f'No se encontró el modelo GGUF. Ejecuta Instalar_ALLEN.bat para instalar {MODEL_FILE}.')
            process, model, selected_model, answer = download_model(executable, config_path, settings, args.timeout)
            owned_process = True
            if os.name == 'nt':
                pid_path = DATA / 'launcher' / 'llama.pid'
                pid_path.parent.mkdir(parents=True, exist_ok=True)
                pid_path.write_text(str(process.pid), encoding='ascii')
            log(f'READY llama-server pid={process.pid} model={selected_model} inference={answer!r}')
            write_status('ready')
            print(f'[OK] Modelo descargado, IA lista e inferencia confirmada: {answer}', flush=True)
            return 0
        args_cmd, url = command(executable, model, settings)
        LLAMA_LOG.parent.mkdir(parents=True, exist_ok=True)
        if not LLAMA_LOG.exists():
            LLAMA_LOG.touch()
        state = health(url)
        if state == 'unavailable':
            raise RuntimeError(f'El puerto de la IA ({url}) está ocupado por un servicio que no responde como llama-server.')
        if state == 'offline':
            command_line = subprocess.list2cmdline(args_cmd)
            log(f'START llama-server executable={executable} model={model} pid=pending endpoint={url} command={command_line}')
            print(f'[OK] Motor de IA: {executable.name}', flush=True)
            print(f'[OK] Modelo local: {model.name} ({model.stat().st_size / (1024**3):.2f} GiB)', flush=True)
            print('Iniciando inteligencia artificial...', flush=True)
            print(f'Cargando {model.stem}... Esto puede tardar unos segundos.', flush=True)
            with LLAMA_LOG.open('a', encoding='utf-8') as stream:
                process = subprocess.Popen(args_cmd, cwd=str(executable.parent), stdin=subprocess.DEVNULL,
                                           stdout=stream, stderr=stream,
                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            owned_process = True
            log(f'llama-server pid={process.pid} started')
            deadline = time.monotonic() + max(1, min(args.timeout, 1800))
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f'El motor de IA se cerró durante el inicio (código {process.returncode}).')
                state = health(url)
                if state == 'ready':
                    break
                if state == 'unavailable':
                    raise RuntimeError(f'El puerto de la IA ({url}) está ocupado por otra aplicación.')
                time.sleep(1)
            else:
                raise TimeoutError(f'llama-server no respondió en /health en {args.timeout} segundos.')
        print('[OK] IA local lista (/health). Probando una inferencia real...', flush=True)
        selected_model = model_id(url)
        if Path(selected_model).is_absolute() and Path(selected_model).resolve() != model.resolve():
            raise RuntimeError(f'El servidor en {url} está cargando un modelo distinto del configurado para ALLEN.')
        answer = infer(url, selected_model)
        elapsed = time.monotonic() - started
        print(f'[OK] Inferencia de prueba: {answer}', flush=True)
        log(f'READY llama-server pid={process.pid if process else "existing"} model={selected_model} elapsed={elapsed:.2f}s health=200 inference={answer!r}')
        if process and os.name == 'nt':
            pid_path = DATA / 'launcher' / 'llama.pid'
            pid_path.parent.mkdir(parents=True, exist_ok=True)
            pid_path.write_text(str(process.pid), encoding='ascii')
        write_status('ready')
        print('[OK] IA comprobada mediante inferencia real.', flush=True)
        return 0
    except (OSError, ValueError, KeyError, sqlite3.Error, RuntimeError, TimeoutError, json.JSONDecodeError) as exc:
        detail = f'{type(exc).__name__}: {exc}'
        write_status('error')
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
        if owned_process:
            (DATA / 'launcher' / 'llama.pid').unlink(missing_ok=True)
        log(f'FAILED llama-server after {time.monotonic()-started:.2f}s {detail}')
        print('ALLEN no pudo iniciar su inteligencia artificial local.', file=sys.stderr, flush=True)
        print(f'Causa: {exc}', file=sys.stderr, flush=True)
        print('Últimas líneas de logs/llama-server.log:', file=sys.stderr, flush=True)
        print(tail(LLAMA_LOG), file=sys.stderr, flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
