"""Real browser tests with production CSP, IndexedDB and a scoped service worker."""
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def mobile_url():
    headers = json.loads((ROOT/'vercel.json').read_text())['headers'][0]['headers']

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def end_headers(self):
            for header in headers:
                self.send_header(header['key'], header['value'])
            super().end_headers()

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT/'public')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/mobile/'
    server.shutdown()
    server.server_close()
    thread.join()


def create_profile(page, name='Estudiante', goal='school'):
    page.get_by_label('¿Cómo quieres que te llame?').fill(name)
    page.get_by_label('¿Qué quieres hacer?').select_option(goal)
    page.get_by_role('button', name='Crear mi perfil', exact=True).click()
    page.get_by_role('heading', name=f'Hola, {name}', exact=True).wait_for()


def answer(page, value, last=False):
    page.get_by_role('radio', name=value, exact=True).check()
    page.get_by_role('button', name='Comprobar respuesta', exact=True).click()
    page.get_by_role('button', name='Terminar y guardar' if last else 'Siguiente actividad', exact=True).click()
    page.locator('#content[aria-busy="true"]').wait_for(state="detached")


def state(page):
    return page.evaluate("""async () => {
        const s=await import('./storage.mjs');const db=await s.openStorage();
        const value=await s.loadProfile(db,await s.activeProfile(db));db.close();return value;
    }""")


def diagnose(page):
    page.get_by_role('button', name='Comenzar diagnóstico').click()
    for index, value in enumerate(['1/4', '8', '2/4', '4/6', '3/4', '5/8']):
        answer(page, value, last=index==5)
    page.get_by_role('heading', name='Ya tenemos una primera orientación').wait_for()
    page.get_by_role('button', name='Ver mi siguiente paso').click()


def test_learning_survives_offline_reload_and_all_lessons_complete(mobile_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width':390, 'height':844})
        page = context.new_page()
        errors, requests = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type=='error' else None)
        page.on('request', lambda req: requests.append(req.url))
        page.goto(mobile_url)
        create_profile(page)
        page.get_by_text('Curso guardado · listo sin conexión', exact=True).wait_for()
        diagnose(page)
        page.get_by_role('button', name='Empezar lección', exact=True).click()
        page.get_by_role('button', name='No entendí', exact=True).click()
        page.get_by_role('heading', name='Vamos paso a paso').wait_for()
        page.get_by_role('button', name='Entendido, vamos a practicar').click()
        page.get_by_role('button', name='Dame una pista').click()
        answer(page, '3/8')
        # After cache download the full learning cycle runs with no server connection.
        context.set_offline(True)
        page.reload()
        page.get_by_text('Sin conexión · curso disponible', exact=True).wait_for()
        page.get_by_role('button', name='Continuar aprendiendo').click()
        page.get_by_role('heading', name='Coloreas 2 de 6 regiones iguales. ¿Qué fracción está coloreada?').wait_for()
        answer(page, '2/6')
        answer(page, '4/5', last=True)
        page.get_by_role('heading', name='Comprobación superada').wait_for()
        assert state(page)['completed']==['parts']
        page.get_by_role('button', name='Ver mi siguiente paso').click()
        for answers in (['3', '6/8', '4/10'], ['3/6', '5/7', '6/9']):
            page.get_by_role('button', name='Empezar lección', exact=True).click()
            page.get_by_role('button', name='Entendido, vamos a practicar').click()
            for i, value in enumerate(answers):
                answer(page, value, last=i==2)
            page.get_by_role('heading', name='Comprobación superada').wait_for()
            page.get_by_role('button', name='Ver mi siguiente paso').click()
        assert state(page)['completed']==['parts','equivalent','sum']
        page.get_by_role('button', name='Mi progreso', exact=True).click()
        page.get_by_role('heading', name='Tu progreso tiene una historia').wait_for()
        for width in [320,360,390,768,1366]:
            page.set_viewport_size({'width':width,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth-innerWidth')<=2
        page.set_viewport_size({'width':390,'height':844})
        path=ROOT/'artifacts/mobile';path.mkdir(parents=True,exist_ok=True)
        page.screenshot(path=str(path/'progress.png'),full_page=True)
        page.get_by_role('button', name='Practicar', exact=True).click()
        page.get_by_role('button', name='Repasar tarjeta').first.click()
        page.get_by_role('button', name='Ver explicación').click()
        page.get_by_role('button', name='Necesito repasarlo').click()
        assert state(page)['cards']['parts']['remembered'] is False
        page.get_by_role('button', name='Hoy', exact=True).click()
        page.screenshot(path=str(path/'today.png'),full_page=True)
        page.get_by_role('button',name='Comenzar repaso',exact=True).click()
        page.get_by_role('button',name='Entendido, vamos a practicar').click()
        page.screenshot(path=str(path/'practice.png'),full_page=True)
        assert not errors, errors
        assert all(url.startswith(mobile_url) for url in requests), requests
        browser.close()


def test_backup_recovery_profile_isolation_and_safe_import(mobile_url, tmp_path):
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.goto(mobile_url)
        create_profile(page, 'Uno')
        diagnose(page)
        page.get_by_role('button', name='Mi progreso', exact=True).click()
        with page.expect_download() as download:
            page.get_by_role('button', name='Exportar mi progreso').click()
        backup=tmp_path/'copy.json';download.value.save_as(backup)
        original=state(page)
        page.get_by_role('button', name='Perfiles', exact=True).click()
        create_profile(page, 'Dos', 'explore')
        assert state(page)['events']==[]
        assert state(page)['profile']['goal']=='explore'
        page.get_by_role('button', name='Allen', exact=True).click()
        page.get_by_text('La IA generativa está desconectada por defecto.', exact=False).wait_for()
        assert 'Uno' not in page.locator('#content').inner_text()
        page.get_by_role('button', name='Mi progreso', exact=True).click()
        with page.expect_file_chooser() as chooser:
            page.get_by_role('button', name='Recuperar una copia').click()
        chooser.value.set_files(backup)
        page.get_by_role('heading', name='Hola, Uno · recuperado', exact=True).wait_for()
        restored=state(page)
        assert restored['profile']['id']!=original['profile']['id']
        assert restored['events']==original['events']
        page.get_by_role('button', name='Perfiles', exact=True).click()
        page.get_by_role('heading', name='Elegir perfil').wait_for()
        assert page.get_by_role('button', name='Abrir', exact=True).count()==3
        # Payload is rendered as text; no markup or instructions from the file execute.
        payload=json.loads(backup.read_text());payload['state']['profile']['name']='<svg onload=alert(1)>'
        payload['state']['entitlements']={'premium':True}
        with page.expect_file_chooser() as chooser:
            page.get_by_role('button',name='Importar una copia local').click()
        chooser.value.set_files({'name':'untrusted.json','mimeType':'application/json','buffer':json.dumps(payload).encode()})
        page.get_by_role('heading',name='Hola, <svg onload=alert(1)> · recuperado',exact=True).wait_for()
        assert page.locator('svg[onload]').count()==0
        assert 'entitlements' not in state(page)
        page.get_by_role('button', name='Perfiles', exact=True).click()
        page.locator('.profile-item').filter(has_text='Dos').get_by_role('button',name='Eliminar',exact=True).click()
        page.get_by_role('button',name='Eliminar este perfil definitivamente').click()
        page.get_by_role('heading',name='Elegir perfil').wait_for()
        assert page.get_by_role('button',name='Abrir',exact=True).count()==3
        assert not page.locator('.profile-item').filter(has_text='Dos').count()
        browser.close()


def test_stale_tab_and_failed_write_do_not_overwrite_saved_progress(mobile_url):
    with sync_playwright() as p:
        browser=p.chromium.launch();context=browser.new_context();page=context.new_page()
        page.goto(mobile_url);create_profile(page);other=context.new_page();other.goto(mobile_url)
        other.get_by_role('heading',name='Hola, Estudiante',exact=True).wait_for()
        page.get_by_role('button',name='Comenzar diagnóstico').click()
        other.get_by_role('button',name='Comenzar diagnóstico').click()
        other.get_by_text('El perfil cambió en otra pestaña. Recarga para continuar.',exact=True).wait_for()
        assert state(page)['session']['answers']==[]
        page.evaluate("""() => {window.originalPut=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw new DOMException('Sin espacio disponible','QuotaExceededError');};}""")
        page.get_by_role('radio',name='1/4',exact=True).check()
        page.get_by_role('button',name='Comprobar respuesta').click()
        page.get_by_text('Sin espacio disponible',exact=True).wait_for()
        assert state(page)['events']==[]
        page.evaluate('() => {IDBObjectStore.prototype.put=window.originalPut;}')
        page.reload();page.get_by_role('button',name='Continuar aprendiendo').click()
        page.get_by_role('heading',name='Pregunta 1 de 6').wait_for()
        assert state(page)['events']==[]
        browser.close()


def test_new_courses_and_optional_tutor_keep_progress_offline(mobile_url):
    catalogue = json.loads((ROOT/'public/mobile/catalogue.json').read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width':390,'height':844})
        page = context.new_page()
        page.goto(mobile_url)
        create_profile(page, 'Luna', 'explore')
        page.get_by_text('Curso guardado · listo sin conexión',exact=True).wait_for()
        page.get_by_role('button',name='Aprender',exact=True).click()
        page.screenshot(path=str(ROOT/'docs/images/mobile/catalogue.png'),full_page=True)
        assert page.locator('.course-card').count() == 4
        context.set_offline(True)
        for c in catalogue[1:]:
            page.get_by_role('button',name='Aprender',exact=True).click()
            page.locator(f'[data-course="{c["id"]}"]').click()
            page.get_by_role('button',name='Hacer diagnóstico',exact=True).click()
            diagnostic = [q for t in c['topics'] for q in t['questions'] if q['kind']=='diagnostic']
            for i,q in enumerate(diagnostic):
                answer(page,q['answer'],last=i==len(diagnostic)-1)
            page.get_by_role('button',name='Ver mi siguiente paso',exact=True).click()
            for t in c['topics']:
                page.get_by_role('button',name='Empezar lección',exact=True).click()
                page.get_by_role('button',name='Dame otro ejemplo',exact=True).click()
                page.get_by_role('button',name='Entendido, vamos a practicar',exact=True).click()
                practice = [q for q in t['questions'] if q['kind']!='diagnostic']
                for i,q in enumerate(practice):
                    answer(page,q['answer'],last=i==len(practice)-1)
                page.get_by_role('button',name='Ver mi siguiente paso',exact=True).click()
        assert len(state(page)['completed']) == 6
        page.reload()
        page.get_by_role('heading',name='Hola, Luna',exact=True).wait_for()
        assert len(state(page)['completed']) == 6
        context.set_offline(False)
        # UI contract only: the backend adapter is verified separately with TestClient.
        page.route('**/api/mobile/bootstrap',lambda route:route.fulfill(json={'connected':True,'token':'test-token'}))
        sent = []
        def tutor(route):
            sent.append(route.request.post_data_json)
            route.fulfill(json={'answer':'Una explicación de prueba','source':'Contenido revisable','generated':True})
        page.route('**/api/mobile/tutor',tutor)
        page.get_by_role('button',name='Allen',exact=True).click()
        before = state(page)['events']
        page.get_by_role('button',name='Comprobar y conectar IA local',exact=True).click()
        page.get_by_label('¿Qué quieres entender?').fill('Dame otra explicación')
        page.get_by_role('button',name='Pedir explicación',exact=True).click()
        page.get_by_text('Respuesta generada · verificar con el curso',exact=True).wait_for()
        assert sent[0]['topic_id']=='python-output'
        assert set(sent[0])=={'message','topic_id','question_id','last_answer','level'}
        assert state(page)['events']==before
        page.screenshot(path=str(ROOT/'docs/images/mobile/tutor-local.png'),full_page=True)
        page.get_by_role('button',name='Mi progreso',exact=True).click()
        page.get_by_label('Tamaño del texto').select_option('large')
        page.get_by_role('button',name='Guardar preferencias',exact=True).click()
        page.get_by_text('Preferencias guardadas.',exact=True).wait_for()
        page.reload()
        page.get_by_role('heading',name='Hola, Luna',exact=True).wait_for()
        assert page.locator('html').get_attribute('data-text-size')=='large'
        page.get_by_role('button',name='Perfiles',exact=True).click()
        create_profile(page,'Sol')
        page.get_by_role('button',name='Allen',exact=True).click()
        assert page.get_by_role('button',name='Comprobar y conectar IA local',exact=True).is_visible()
        assert page.get_by_text('Una explicación de prueba',exact=True).count()==0
        assert state(page)['events']==[]
        browser.close()


def test_browser_uses_desktop_bridge_and_handles_model_loss(tmp_path):
    import socket
    import time
    import uvicorn
    from backend.app import create_app
    from tests.test_mobile_tutor import ModelStub

    model = ModelStub()
    app = create_app(tmp_path/'bridge.sqlite3',ai=model,require_license=False,
                     require_local_access=False,require_teacher_auth=False)
    sock = socket.socket()
    sock.bind(('127.0.0.1',0))
    server = uvicorn.Server(uvicorn.Config(app,log_level='error'))
    thread = threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True)
    thread.start()
    try:
        deadline = time.monotonic()+10
        while not server.started and time.monotonic()<deadline:
            time.sleep(.02)
        assert server.started
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width':390,'height':844})
            page.goto(f'http://127.0.0.1:{sock.getsockname()[1]}/mobile/')
            create_profile(page)
            page.get_by_role('button',name='Comenzar diagnóstico').click()
            page.get_by_role('button',name='Allen',exact=True).click()
            page.get_by_role('button',name='Comprobar y conectar IA local',exact=True).click()
            page.get_by_label('¿Qué quieres entender?').fill('Ayúdame a razonar')
            before = state(page)
            page.get_by_role('button',name='Pedir explicación',exact=True).click()
            page.get_by_text('Respuesta generada · verificar con el curso',exact=True).wait_for()
            assert len(model.calls)==1
            assert state(page)==before
            model.connected = False
            page.get_by_label('¿Qué quieres entender?').fill('Otro ejemplo')
            page.get_by_role('button',name='Pedir explicación',exact=True).click()
            page.get_by_text('Inicia tu modelo local. El tutor guiado sigue disponible sin IA.',exact=True).wait_for()
            page.get_by_role('button',name='No entendí',exact=True).click()
            page.get_by_text('Explicación preparada',exact=True).wait_for()
            assert len(state(page)['events'])==1
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
