import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_web_assets", ANDROID / "build_web_assets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_python_and_javascript_load_the_same_pyodide_packages():
    builder = load_builder()
    script = (ANDROID / "web" / "allen-worker.js").read_text(encoding="utf-8")
    packages = json.loads(re.search(r"const PACKAGES = (\[[^\]]*\]);", script).group(1))
    assert packages == list(builder.PYODIDE_PACKAGES)


def test_bridge_is_injected_before_the_app_module():
    builder = load_builder()
    for page in ("index.html", "fair.html"):
        html = builder.inject((ROOT / "frontend" / page).read_text(encoding="utf-8"))
        assert html.index("/static/android/allen-android.js") < html.index('type="module"')


def test_android_app_requests_no_permissions_and_ignores_generated_assets():
    manifest = (ANDROID / "app" / "src" / "main" / "AndroidManifest.xml").read_text(encoding="utf-8")
    assert "uses-permission" not in manifest
    assert 'android:allowBackup="false"' in manifest
    ignored = (ANDROID / ".gitignore").read_text(encoding="utf-8")
    assert "app/src/main/assets/www/" in ignored



def test_both_interfaces_are_bundled_without_starting_python(tmp_path):
    builder = load_builder()
    builder.assemble_interfaces(tmp_path)
    mobile = (tmp_path/'mobile/index.html').read_text()
    assert 'content="bundled-android"' in mobile
    assert 'allen-android.js' not in mobile
    assert (tmp_path/'mobile/scenario-courses.mjs').is_file()
    assert (tmp_path/'index.html').is_file()
    assert (tmp_path/'fair.html').is_file()
    # Existing app requests are still routed to Python when explicitly opened.
    assert '/static/android/allen-android.js' in (tmp_path/'index.html').read_text()


def test_backend_archive_uses_the_shared_course_snapshot(tmp_path):
    import zipfile
    builder = load_builder()
    archive = tmp_path/'source.zip'
    builder.source_zip(archive)
    with zipfile.ZipFile(archive) as source:
        assert source.read('public/mobile/catalogue.json') == (ROOT/'public/mobile/catalogue.json').read_bytes()
        assert 'backend/mobile_tutor.py' in source.namelist()
