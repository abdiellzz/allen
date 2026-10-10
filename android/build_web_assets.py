"""Assemble the web assets for the ALLEN Android demo APK.

Output: android/app/src/main/assets/www (git-ignored). Downloads are cached in
android/.cache and verified against the SHA-256 published in pyodide-lock.json / PyPI.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"
OUT = ANDROID / "app" / "src" / "main" / "assets" / "www"
CACHE = ANDROID / ".cache"
PYODIDE_VERSION = "0.29.5"
CDN = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"
CORE_FILES = ("pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json")
# Keep in sync with PACKAGES in web/allen-worker.js.
PYODIDE_PACKAGES = ("fastapi", "httpx", "pydantic", "cryptography", "micropip", "sqlite3", "hashlib", "ssl")
PYPI_WHEELS = ("pypdf", "qrcode")
HEAD_INJECTION = (
    '<link rel="stylesheet" href="/static/android/allen-android.css">'
    '<script src="/static/android/allen-android.js"></script>'
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url: str, name: str, expected_sha256: str | None = None) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / name
    if not target.exists() or (expected_sha256 and sha256(target) != expected_sha256):
        print("descargando", name)
        with urllib.request.urlopen(url, timeout=120) as response:  # nosec B310: fixed https URLs
            target.write_bytes(response.read())
    if expected_sha256 and sha256(target) != expected_sha256:
        target.unlink()
        raise SystemExit(f"hash SHA-256 incorrecto para {name}")
    return target


def pyodide_closure(lock: dict) -> list[dict]:
    canonical = lambda name: name.lower().replace("_", "-")  # noqa: E731
    packages = {canonical(name): package for name, package in lock["packages"].items()}
    seen: dict[str, dict] = {}
    pending = [canonical(name) for name in PYODIDE_PACKAGES]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen[name] = packages[name]
        pending.extend(canonical(dep) for dep in packages[name].get("depends", []))
    return list(seen.values())


def pinned_version(package: str) -> str:
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        name, _, version = line.partition("==")
        if name.strip().lower() == package:
            return version.strip()
    raise SystemExit(f"{package} no está fijado en requirements.txt")


def pypi_wheel(package: str) -> Path:
    version = pinned_version(package)
    with urllib.request.urlopen(f"https://pypi.org/pypi/{package}/{version}/json", timeout=60) as response:  # nosec B310
        files = json.load(response)["urls"]
    wheel = next(f for f in files if f["filename"].endswith("py3-none-any.whl"))
    return download(wheel["url"], wheel["filename"], wheel["digests"]["sha256"])


def inject(html: str) -> str:
    if "</head>" not in html:
        raise SystemExit("HTML sin </head>")
    return html.replace("</head>", HEAD_INJECTION + "</head>", 1)


def source_zip(target: Path) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / "backend").rglob("*.py")):
            archive.write(path, path.relative_to(ROOT).as_posix())
        for path in sorted((ROOT / "data" / "library").rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(ROOT).as_posix())
        archive.write(ROOT / "config" / "license_public_key.pem", "config/license_public_key.pem")
        archive.write(ROOT / "VERSION", "VERSION")
        archive.write(ANDROID / "web" / "allen_bridge.py", "allen_bridge.py")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "pyodide").mkdir(parents=True)
    (OUT / "wheels").mkdir()

    shutil.copytree(ROOT / "frontend", OUT / "static")
    (OUT / "static" / "android").mkdir()
    for name in ("allen-android.js", "allen-worker.js", "allen-android.css"):
        shutil.copy2(ANDROID / "web" / name, OUT / "static" / "android" / name)
    for page in ("index.html", "fair.html"):
        html = (ROOT / "frontend" / page).read_text(encoding="utf-8")
        (OUT / page).write_text(inject(html), encoding="utf-8")

    for name in CORE_FILES:
        shutil.copy2(download(CDN + name, f"pyodide-{PYODIDE_VERSION}-{name}"), OUT / "pyodide" / name)
    lock = json.loads((OUT / "pyodide" / "pyodide-lock.json").read_text(encoding="utf-8"))
    for package in pyodide_closure(lock):
        cached = download(CDN + package["file_name"], package["file_name"], package["sha256"])
        shutil.copy2(cached, OUT / "pyodide" / package["file_name"])

    wheels = [pypi_wheel(package) for package in PYPI_WHEELS]
    for wheel in wheels:
        shutil.copy2(wheel, OUT / "wheels" / wheel.name)

    source_zip(OUT / "allen-src.zip")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest = {"allen": version, "pyodide": PYODIDE_VERSION, "wheels": [w.name for w in wheels]}
    (OUT / "allen-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"assets listos en {OUT.relative_to(ROOT)} ({size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
