"""Assemble the web assets for the ALLEN Android demo APK.

Output: android/app/src/main/assets/www (git-ignored). The APK only ships the mobile learning
experience from public/mobile/: no Python runtime, no backend source and no network downloads.
Only allowlisted file types are copied, and the page gets a strict Content-Security-Policy
because WebViewAssetLoader serves files without HTTP security headers.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"
MOBILE = ROOT / "public" / "mobile"
OUT = ANDROID / "app" / "src" / "main" / "assets" / "www"
# Runtime files of the mobile experience. sw.js (web-only offline cache) and catalogue.json (desktop
# backend snapshot) are deliberately left out.
ALLOWED_SUFFIXES = {".html", ".mjs", ".css", ".webmanifest", ".png", ".svg", ".webp"}
EXCLUDED = {"sw.js", "catalogue.json"}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; "
    "manifest-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'"
)
CHARSET = '<meta charset="utf-8">'


def apk_version() -> str:
    """Same versionName that android/app/build.gradle computes."""
    properties = dict(
        line.split("=", 1) for line in (ANDROID / "gradle.properties").read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    )
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return f"{version}-android-demo.{properties['allenApkRevision'].strip()}"


def harden(html: str, entry: bool = False) -> str:
    """Add the CSP right after the charset (before any resource); mark the bundled runtime on the entry page."""
    if CHARSET not in html or "</head>" not in html:
        raise SystemExit("página HTML sin <meta charset> o </head>")
    html = html.replace(CHARSET, CHARSET + f'<meta http-equiv="Content-Security-Policy" content="{CSP}">', 1)
    return html.replace("</head>", '<meta name="allen-runtime" content="bundled-android"></head>', 1) if entry else html


def assemble(output: Path) -> None:
    for path in sorted(MOBILE.rglob("*")):
        if not path.is_file() or path.name in EXCLUDED or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        target = output / "mobile" / path.relative_to(MOBILE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    # Every page (legal, contact, error pages included) gets the CSP: the WebView sends no headers.
    for page in (output / "mobile").rglob("*.html"):
        page.write_text(harden(page.read_text(encoding="utf-8"), entry=page.name == "index.html" and page.parent.name == "mobile"), encoding="utf-8")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest = {"allen": version, "apk": apk_version()}
    (output / "allen-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    assemble(OUT)
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"assets listos en {OUT.relative_to(ROOT)} ({size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
