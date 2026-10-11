"""Public legal pages, scoped offline errors, metadata and real browser failures."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from playwright.sync_api import expect, sync_playwright

from tests.test_mobile_e2e import create_profile, mobile_url, navigate  # noqa: F401


@pytest.fixture
def disconnectable_mobile_url():
    root = Path(__file__).resolve().parent.parent
    headers = json.loads((root / 'vercel.json').read_text())['headers'][0]['headers']

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def end_headers(self):
            for header in headers:
                self.send_header(header['key'], header['value'])
            super().end_headers()

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root / 'public')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    stopped = False

    def disconnect():
        nonlocal stopped
        if not stopped:
            server.shutdown()
            server.server_close()
            thread.join()
            stopped = True

    yield f'http://127.0.0.1:{server.server_port}/mobile/', disconnect
    disconnect()


def test_legal_pages_and_responsive_contact(mobile_url):
    root = mobile_url.removesuffix('mobile/')
    titles = {'privacidad': 'Política de privacidad', 'terminos': 'Términos y condiciones',
              'contacto': 'Contacto', '404': 'No encontramos esta página',
              'error': 'Algo no salió como esperábamos'}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for prefix in [root, mobile_url]:
            for slug, title in titles.items():
                page.goto(prefix + slug + '.html')
                expect(page).to_have_title(title + ' · ALLEN')
                expect(page.get_by_role('heading', name=title, exact=True)).to_be_visible()
                assert page.locator('meta[name="title"]').get_attribute('content') == title + ' · ALLEN'
                assert page.locator('meta[name="description"]').get_attribute('content')
                assert page.get_by_role('link', name='iallenbussinesss@gmail.com', exact=True).first.get_attribute('href').startswith('mailto:iallenbussinesss@gmail.com')
                for width in [320, 480, 768, 1024, 1440]:
                    page.set_viewport_size({'width': width, 'height': 900})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (prefix, slug, width)
                assert page.locator('script:not([src]),style').count() == 0
        for route in ['', 'education/', 'agents/']:
            page.goto(root + route)
            expect(page.get_by_role('navigation', name='Información legal')).to_be_visible()
            assert page.locator('meta[name="title"]').get_attribute('content') == page.title()
            for width in [320, 480, 768, 1024, 1440]:
                page.set_viewport_size({'width': width, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, width)
        assert not errors
        browser.close()


def test_metadata_and_offline_legal_navigation(disconnectable_mobile_url):
    mobile_url, disconnect = disconnectable_mobile_url
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': 375, 'height': 812})
        page = context.new_page()
        page.goto(mobile_url)
        expect(page).to_have_title('Perfiles · ALLEN')
        create_profile(page, name='Privado')
        for section, title in [('Aprender', 'Aprender'), ('Allen', 'Habla con Allen'),
                               ('Mi progreso', 'Mi progreso')]:
            navigate(page, section)
            expect(page).to_have_title(title + ' · ALLEN')
            assert 'Privado' not in page.locator('meta[name="description"]').get_attribute('content')
        expect(page.locator('#offline-status')).to_contain_text('sin conexión', timeout=30000)
        page.evaluate('navigator.serviceWorker.ready')
        page.reload()
        page.wait_for_function('navigator.serviceWorker.controller !== null')
        response = page.goto(mobile_url + 'no-existe/ruta')
        assert response.status == 404
        assert "script-src 'self'" in response.headers['content-security-policy']
        expect(page.get_by_role('heading', name='No encontramos esta página')).to_be_visible()
        assert page.locator('.legal-error img').evaluate('(img) => img.complete && img.naturalWidth > 0')
        context.set_offline(True)
        page.goto(mobile_url + 'privacidad.html')
        expect(page).to_have_title('Política de privacidad · ALLEN')
        page.get_by_role('link', name='Términos y condiciones', exact=True).click()
        expect(page).to_have_title('Términos y condiciones · ALLEN')
        # Stop the real origin too: Chromium's offline emulation alone may not
        # disable requests made by the service worker itself.
        disconnect()
        response = page.goto(mobile_url + 'otra/ruta')
        assert response.status == 503
        assert "script-src 'self'" in response.headers['content-security-policy']
        expect(page.get_by_role('heading', name='Algo no salió como esperábamos')).to_be_visible()
        assert page.locator('.legal-error img').evaluate('(img) => img.complete && img.naturalWidth > 0')
        page.get_by_role('link', name='Volver a ALLEN', exact=True).click()
        expect(page.get_by_role('heading', name='Hola, Privado', exact=True)).to_be_visible()
        browser.close()


def test_storage_and_module_failures_have_recovery(mobile_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(service_workers='block')
        context.add_init_script("Object.defineProperty(window, 'indexedDB', {get() {throw new Error('denied');}})")
        page = context.new_page()
        page.goto(mobile_url)
        expect(page.get_by_role('heading', name='No pudimos abrir el almacenamiento')).to_be_visible()
        expect(page.get_by_role('button', name='Intentar de nuevo')).to_be_enabled()
        expect(page).to_have_title('No pudimos abrir ALLEN · ALLEN')
        context.close()
        context = browser.new_context(service_workers='block')
        page = context.new_page()
        page.route('**/course.mjs', lambda route: route.abort())
        page.goto(mobile_url)
        expect(page.get_by_role('heading', name='No pudimos abrir ALLEN', exact=True)).to_be_visible()
        expect(page.get_by_role('link', name='Ver opciones de ayuda')).to_be_visible()
        assert page.get_by_text('No hemos borrado tus datos.', exact=False).count() == 1
        browser.close()


def test_action_error_persists_without_losing_profile(mobile_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(mobile_url)
        create_profile(page)
        # A real failed export must not be acknowledged as a successful download.
        page.evaluate("window.AllenFiles = {exportProgress() {throw new Error('No se pudo guardar la copia. Inténtalo otra vez.');}}")
        navigate(page, 'Mi progreso')
        page.get_by_role('button', name='Exportar mi progreso', exact=True).click()
        expect(page.locator('#action-error')).to_be_visible()
        expect(page.locator('#action-error')).to_contain_text('No se pudo guardar la copia')
        page.get_by_role('button', name='Entendido', exact=True).click()
        expect(page.locator('#action-error')).to_be_hidden()
        page.reload()
        expect(page.get_by_role('heading', name='Hola, Estudiante', exact=True)).to_be_visible()
        browser.close()
