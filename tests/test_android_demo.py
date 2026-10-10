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
