"""Security regressions for the Android demo APK (debuggable builds, payload, CSP, backups, signing)."""
import hashlib
import importlib.util
import json
import re
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"
MAIN = ANDROID / "app" / "src" / "main"
# Official checksum of gradle-8.11.1-wrapper.jar (services.gradle.org).
GRADLE_WRAPPER_JAR_SHA256 = "2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046"


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ANDROID / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_only_requests_opt_in_reminders_and_keeps_data_on_the_phone():
    manifest = (MAIN / "AndroidManifest.xml").read_text(encoding="utf-8")
    # Local study reminders only: notifications (asked at runtime) and rescheduling after a reboot.
    permissions = re.findall(r'uses-permission android:name="([^"]+)"', manifest)
    assert set(permissions) == {"android.permission.POST_NOTIFICATIONS", "android.permission.RECEIVE_BOOT_COMPLETED"}
    assert "android.permission.INTERNET" not in manifest
    assert "SCHEDULE_EXACT_ALARM" not in manifest
    assert 'android:exported="false"' in manifest
    assert 'android:allowBackup="false"' in manifest
    assert 'android:usesCleartextTraffic="false"' in manifest
    assert 'android:dataExtractionRules="@xml/data_extraction_rules"' in manifest
    assert manifest.count('android:exported="true"') == 1
    rules = (MAIN / "res" / "xml" / "data_extraction_rules.xml").read_text(encoding="utf-8")
    for section in ("cloud-backup", "device-transfer"):
        body = rules.split(f"<{section}>", 1)[1].split(f"</{section}>", 1)[0]
        for domain in ("root", "file", "database", "sharedpref", "external", "device_root"):
            assert f'<exclude domain="{domain}" path="." />' in body


def test_release_build_is_not_debuggable_and_build_inputs_are_pinned():
    gradle = (ANDROID / "app" / "build.gradle").read_text(encoding="utf-8")
    release = gradle.split("release {", 1)[1].split("}", 1)[0]
    assert "debuggable false" in release and "minifyEnabled true" in release
    assert "signingConfig" not in release  # published builds are signed only by android/sign_release.py
    wrapper = (ANDROID / "gradle" / "wrapper" / "gradle-wrapper.properties").read_text(encoding="utf-8")
    assert re.search(r"^distributionSha256Sum=[0-9a-f]{64}$", wrapper, re.M)
    jar = (ANDROID / "gradle" / "wrapper" / "gradle-wrapper.jar").read_bytes()
    assert hashlib.sha256(jar).hexdigest() == GRADLE_WRAPPER_JAR_SHA256


def test_webview_only_loads_bundled_assets_and_denies_web_permissions():
    activity = (MAIN / "java" / "com" / "allen" / "tutor" / "demo" / "MainActivity.java").read_text(encoding="utf-8")
    assert '"https".equals(url.getScheme()) && HOST.equals(url.getHost())' in activity
    assert "return blocked();" in activity
    assert "intent.addCategory(Intent.CATEGORY_BROWSABLE)" in activity
    assert "request.deny();" in activity and "callback.invoke(origin, false, false);" in activity
    assert "setAllowFileAccess(false)" in activity and "setAllowContentAccess(false)" in activity
    assert "setWebContentsDebuggingEnabled(true)" in activity.split("FLAG_DEBUGGABLE", 1)[1].split("}", 1)[0]


def test_apk_bundles_only_the_mobile_experience(tmp_path):
    builder = load_module("build_web_assets")
    builder.assemble(tmp_path)
    files = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    assert "mobile/index.html" in files and "mobile/android-extras.mjs" in files
    assert all(f == "allen-manifest.json" or f.startswith("mobile/") for f in files), files
    assert not any(f.endswith((".py", ".zip", ".whl", ".wasm", ".sqlite3", ".pem", "sw.js", "catalogue.json")) for f in files)
    manifest = json.loads((tmp_path / "allen-manifest.json").read_text(encoding="utf-8"))
    assert re.fullmatch(r"\d+\.\d+\.\d+-android-demo\.\d+", manifest["apk"])
    assert not (ANDROID / "web").exists()


def test_apk_page_gets_a_strict_csp_before_any_resource(tmp_path):
    builder = load_module("build_web_assets")
    builder.assemble(tmp_path)
    html = (tmp_path / "mobile" / "index.html").read_text(encoding="utf-8")
    csp = html.index('http-equiv="Content-Security-Policy"')
    assert csp < html.index("<link") and csp < html.index("<script")
    assert "default-src 'none'" in html and "script-src 'self'" in html and "'unsafe-inline'" not in html
    assert '<meta name="allen-runtime" content="bundled-android">' in html
    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html), "inline scripts would be blocked by the CSP"


def test_course_text_is_escaped_before_reaching_innerhtml():
    app = (ROOT / "public" / "mobile" / "app.mjs").read_text(encoding="utf-8")
    # Course text written straight into an HTML tag or attribute (plain strings later escaped are fine).
    unescaped = re.findall(r'(?:>|="|de )\$\{(?:q|t|c|topic|m|s|target)\.(?:prompt|feedback|title|id|profile\.id)\}', app)
    assert unescaped == [], unescaped


def test_published_apk_rotation_constants():
    signer = load_module("sign_release")
    assert re.fullmatch(r"[0-9a-f]{64}", signer.LEGACY_CERT)
    assert signer.ROTATION_MIN_SDK == "28"
    certificate = ANDROID / "release" / "signing-certificate.sha256"
    assert re.fullmatch(r"[0-9a-f]{64}\n", certificate.read_text(encoding="ascii"))
    assert certificate.read_text(encoding="ascii").strip() != signer.LEGACY_CERT
    published = ANDROID / "release" / "ALLEN-demo-android.apk"
    recorded = (ANDROID / "release" / "ALLEN-demo-android.apk.sha256").read_text(encoding="ascii").split()[0]
    assert hashlib.sha256(published.read_bytes()).hexdigest() == recorded


def test_bundled_apk_runs_under_its_csp_without_leaving_the_device(tmp_path):
    """Serve the assembled assets without HTTP headers, as WebViewAssetLoader does."""
    from playwright.sync_api import sync_playwright

    builder = load_module("build_web_assets")
    builder.assemble(tmp_path)

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(tmp_path)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors, foreign = [], []
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.on("request", lambda req: foreign.append(req.url) if not req.url.startswith((origin, "data:", "blob:")) else None)
            page.goto(origin + "/mobile/index.html")
            page.get_by_label("¿Cómo quieres que te llame?").fill('<img src=x onerror="window.pwned=1">')
            page.get_by_role("button", name="Crear mi perfil", exact=True).click()
            page.get_by_text("Contenido incluido · sin Internet", exact=True).wait_for()
            page.locator(".allen-tour").wait_for()
            page.get_by_role("button", name="Saltar recorrido", exact=True).click()
            page.get_by_role("button", name="Perfiles", exact=True).click()
            page.get_by_role("heading", name="Actualizar ALLEN").wait_for()
            version = builder.apk_version()
            page.locator(".allen-apk-version", has_text=version).wait_for()
            assert page.evaluate("window.pwned") is None
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    assert foreign == []
    assert errors == []
