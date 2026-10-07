import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

from backend.database import Database


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1",0))
        return s.getsockname()[1]


def _wait(url,seconds=20):
    deadline=time.time()+seconds
    while time.time()<deadline:
        try:
            with urllib.request.urlopen(url,timeout=1):
                return
        except OSError:
            time.sleep(.2)
    raise RuntimeError("ALLEN no inició para la prueba E2E.")


def test_desktop_guided_learning_smoke_and_viewports():
    with tempfile.TemporaryDirectory() as tmp:
        db_path=Path(tmp)/"allen.sqlite3"
        db=Database(db_path)
        db.remember(1,onboarded=True)
        port=_free_port()
        env={**os.environ,"ALLEN_DB_PATH":str(db_path)}
        process=subprocess.Popen(
            [sys.executable,"-m","uvicorn","backend.app:app","--host","127.0.0.1","--port",str(port),"--log-level","error"],
            env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
        )
        try:
            base=f"http://127.0.0.1:{port}"
            _wait(base+"/api/health")
            with sync_playwright() as p:
                browser=p.chromium.launch()
                page=browser.new_page(viewport={"width":1366,"height":768})
                page.goto(base,wait_until="networkidle")
                page.get_by_role("heading",name="¿Qué quieres descubrir hoy?").wait_for()
                assert page.locator(".brand-mascot").count()==1

                for width,height in ((1366,768),(1440,900),(1920,1080)):
                    page.set_viewport_size({"width":width,"height":height})
                    page.wait_for_timeout(80)
                    overflow=page.evaluate("document.documentElement.scrollWidth-window.innerWidth")
                    assert overflow <= 2

                page.locator('[data-page="Cursos"]').first.click()
                page.get_by_role("heading",name="Aprende con una ruta, no con páginas sueltas.").wait_for()
                assert page.locator("img[src*='allen-course-official.svg']").count()>=1

                page.locator('[data-page="Teacher Studio"]').first.click()
                page.get_by_role("heading",name="Convierte material docente en una ruta de aprendizaje.").wait_for()
                assert page.locator("#course-file").count()==1
                assert page.locator("img[src*='allen-teaching-official.svg']").count()>=1

                page.locator("#course-title").fill("Curso E2E")
                page.locator("#course-subject").fill("Redes")
                page.locator("#course-file").set_input_files({
                    "name":"curso.md",
                    "mimeType":"text/markdown",
                    "buffer":b"# Redes\nIPv4 identifica interfaces de red. DNS traduce nombres a direcciones IP. DHCP asigna parametros de red.\n# Seguridad\nMFA agrega otra comprobacion de identidad. Los backups permiten recuperar informacion."
                })
                page.get_by_role("button",name="Analizar y crear borrador").click()
                page.get_by_role("heading",name="Curso E2E").last.wait_for()
                page.get_by_role("button",name="Guardar revisión y aprobar").click()
                page.get_by_role("button",name="Publicar").wait_for()
                page.get_by_role("button",name="Publicar").click()
                page.get_by_text("Publicado",exact=True).wait_for()

                page.locator('[data-page="Cursos"]').first.click()
                page.get_by_role("heading",name="Curso E2E").wait_for()
                page.get_by_role("button",name="Empezar curso").click()
                page.locator(".allen-step-rail").wait_for()
                assert page.locator(".guided-course-shell").count()==1
                browser.close()
        finally:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill()
