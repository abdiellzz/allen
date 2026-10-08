"""Start the configured local llama.cpp server for the Windows launcher, without downloads or shell commands."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, HTTPRedirectHandler, build_opener

DATA=Path(os.environ.get('ALLEN_DATA_ROOT') or (Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'ALLEN'))

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None

def health(url):
    try:
        with build_opener(ProxyHandler({}),NoRedirect()).open(url+'/health',timeout=2) as response:
            return 'ready' if response.status==200 else 'unknown'
    except HTTPError as exc:
        return 'loading' if exc.code==503 else 'unknown'
    except (URLError,OSError):
        return 'offline'

def preferences():
    path=Path(os.environ.get('ALLEN_DB_PATH',DATA/'allen.sqlite3'))
    if not path.is_file():return {}
    with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as db:
        row=db.execute('SELECT value FROM settings WHERE id=1').fetchone()
    return json.loads(row[0]) if row else {}

def command(config,settings):
    executable=Path(config['executable']).resolve()
    model=Path(config['model']).resolve()
    if not executable.is_file() or executable.name.lower() not in ('llama-server.exe','llama-server'):
        raise ValueError('No encontramos llama-server en la ruta configurada.')
    if not model.is_file() or model.suffix.lower()!='.gguf':
        raise ValueError('No encontramos el modelo GGUF configurado.')
    url=urlsplit(settings.get('ai_server','http://127.0.0.1:8080'))
    if url.scheme!='http' or url.hostname not in ('127.0.0.1','localhost','::1') or not url.port or url.port==8787:
        raise ValueError('La IA necesita una dirección local con su propio puerto.')
    if url.username or url.password or url.query or url.fragment or url.path not in ('','/'):
        raise ValueError('La dirección local configurada no es válida.')
    context=int(settings.get('context_size',4096))
    if not 2048<=context<=32768:raise ValueError('El contexto configurado está fuera de rango.')
    host='::1' if url.hostname=='::1' else '127.0.0.1'
    return [str(executable),'-m',str(model),'--host',host,'--port',str(url.port),'-c',str(context),
            '--parallel','1','--threads','4','--reasoning','off','--log-disable']

def main():
    try:
        settings=preferences()
        if settings.get('demo'):
            print('Modo demo seleccionado; no se inicia el modelo.')
            return 0
        config_path=DATA/'local_model.json'
        if not config_path.is_file():
            print('Sin lanzador de modelo configurado. ALLEN puede usar el modo demo.')
            return 0
        config=json.loads(config_path.read_text(encoding='utf-8'))
        args=command(config,settings)
        url=settings.get('ai_server','http://127.0.0.1:8080')
        status=health(url)
        if status=='ready':
            print('IA local ya iniciada.')
            return 0
        process=None
        if status=='offline':
            process=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        elif status!='loading':
            print('El puerto configurado está ocupado por otro servicio. Se abrirá ALLEN para revisar Configuración.')
            return 1
        print('Cargando la IA local. La primera carga puede tardar...')
        for _ in range(60):
            if process and process.poll() is not None:
                print('No se pudo cargar el modelo. Revisa la instalación de llama.cpp; ALLEN abrirá en modo demo.')
                return 1
            if health(url)=='ready':
                print('IA LOCAL ACTIVA')
                return 0
            time.sleep(1)
        print('El modelo todavía no está listo. ALLEN abrirá; puedes comprobarlo de nuevo en Configuración.')
        return 0
    except (OSError,ValueError,KeyError,sqlite3.Error):
        print('No pudimos iniciar el modelo automáticamente. Revisa local_model.json; ALLEN puede abrir en modo demo.')
        return 1
