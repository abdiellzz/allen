"""Phone-size visual review of ALLEN with the APK stylesheet applied.

Starts the FastAPI app on a throwaway database (no license, no PIN, onboarding done), opens it in
Chromium at 375x812 in light and dark, injects android/web/allen-android.css plus the
`allen-android` class on <html> (as allen-android.js does), and screenshots the key pages into .agents/review/. Reports horizontal
overflow and controls hidden behind a fixed bottom bar. Exit code 1 when issues are found.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".agents" / "review"
ANDROID_WEB = ROOT / "android" / "web"
PAGES = ("Inicio", "Cursos", "Quiz", "Tarjetas", "Progreso", "Configuración")
CSS_LINK = '<link rel="stylesheet" href="/static/android/allen-android.css">'

INIT_SCRIPT = """
(scheme => {
  try {
    localStorage.setItem('allen-theme', scheme);
    localStorage.setItem('allen-workspace-mode', 'student');
  } catch {}
  // <html> may not exist yet when init scripts run; mark it as soon as it does.
  const mark = () => document.documentElement && document.documentElement.classList.add('allen-android');
  mark();
  document.addEventListener('readystatechange', mark);
  document.addEventListener('DOMContentLoaded', mark);
})(%s);
"""

# Returns overflow offenders and interactive elements covered by a fixed/sticky bottom bar.
AUDIT_SCRIPT = """
() => {
  const vw = document.documentElement.clientWidth, vh = window.innerHeight;
  const label = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const cls = [...el.classList].slice(0, 3).join('.');
    if (cls) s += '.' + cls;
    if (el.dataset.page) s += `[data-page="${el.dataset.page}"]`;
    return s;
  };
  for (const el of [document.scrollingElement, ...document.querySelectorAll('*')]) {
    const st = el === document.scrollingElement ? null : getComputedStyle(el);
    if (!st || /(auto|scroll)/.test(st.overflowY)) el.scrollTop = el.scrollHeight;
  }
  const overflow = [];
  const scrollWidth = document.documentElement.scrollWidth;
  if (scrollWidth > vw) {
    for (const el of document.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.width && r.right > vw + 1 && getComputedStyle(el).visibility !== 'hidden') {
        if (!el.parentElement || el.parentElement.getBoundingClientRect().right <= vw + 1) {
          overflow.push({ element: label(el), right: Math.round(r.right) });
        }
      }
    }
  }
  const bars = [...document.body.querySelectorAll('*')].filter(el => {
    const st = getComputedStyle(el);
    if (!['fixed', 'sticky'].includes(st.position) || st.display === 'none' || st.visibility === 'hidden') return false;
    if (el.id === 'allen-android-boot') return false;
    const r = el.getBoundingClientRect();
    return r.height > 0 && r.height < vh * 0.3 && r.width >= vw * 0.6 && Math.abs(r.bottom - vh) <= 2;
  });
  const covered = [];
  for (const bar of bars) {
    const b = bar.getBoundingClientRect();
    for (const el of document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex]:not([tabindex="-1"])')) {
      if (bar.contains(el) || el.contains(bar) || el.closest('[hidden], [aria-hidden="true"]')) continue;
      if (el.checkVisibility && !el.checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })) continue;  // e.g. inside a closed <details>
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height || r.bottom <= b.top || r.top >= b.bottom) continue;
      const top = document.elementFromPoint(r.left + r.width / 2, Math.max(b.top, r.top) + 1);
      if (top && bar.contains(top)) covered.push({ element: label(el), bar: label(bar), overlap: Math.round(Math.min(r.bottom, b.bottom) - Math.max(r.top, b.top)) });
    }
  }
  return { scrollWidth, clientWidth: vw, overflow: overflow.slice(0, 8), bottomBars: bars.map(label), covered: covered.slice(0, 8) };
}
"""


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return plain.lower().replace(" ", "-")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for(url: str, seconds: float = 30) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):  # nosec B310: loopback only
                return
        except OSError:
            time.sleep(0.3)
    raise SystemExit("ALLEN no respondió en " + url)


def start_server(tmp: Path) -> tuple[subprocess.Popen, str]:
    sys.path.insert(0, str(ROOT))
    from backend.database import Database

    db_path = tmp / "allen.sqlite3"
    Database(db_path).remember(1, onboarded=True)
    port = free_port()
    env = {**os.environ, "ALLEN_DB_PATH": str(db_path), "ALLEN_DATA_ROOT": str(tmp)}
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "tests.e2e_server:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "error"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    wait_for(base + "/api/health")
    return process, base


def serve_android(route) -> None:
    name = route.request.url.split("/static/android/", 1)[1].split("?", 1)[0]
    path = ANDROID_WEB / name
    if name != "allen-android.css" or not path.is_file():
        route.fulfill(status=404, body="")
        return
    route.fulfill(status=200, body=path.read_text(encoding="utf-8"), headers={"content-type": "text/css; charset=utf-8"})


def inject_css(route) -> None:
    response = route.fetch()
    html = response.text()
    route.fulfill(response=response, body=html.replace("</head>", CSS_LINK + "</head>", 1))


def review(base: str, schemes: list[str], pages: list[str]) -> list[dict]:
    from playwright.sync_api import sync_playwright

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scheme in schemes:
            context = browser.new_context(
                viewport={"width": 375, "height": 812}, device_scale_factor=2,
                is_mobile=True, has_touch=True, color_scheme=scheme, locale="es-ES",
            )
            context.add_init_script(INIT_SCRIPT % json.dumps(scheme))
            context.route("**/static/android/**", serve_android)
            page = context.new_page()
            errors: list[str] = []
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.route(base + "/", inject_css)
            page.goto(base + "/", wait_until="networkidle")
            page.locator("main, #app, body").first.wait_for()
            for name in pages:
                errors.clear()
                if name != "Inicio":
                    clicked = page.evaluate(
                        "n => { const b = document.querySelector(`[data-page=\"${n}\"]`); if (b) b.click(); return !!b; }", name
                    )
                    if not clicked:
                        results.append({"page": name, "scheme": scheme, "error": "no existe [data-page] en el DOM"})
                        continue
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(500)
                stem = f"{slug(name)}-{scheme}"
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=OUT / f"{stem}.png")
                page.screenshot(path=OUT / f"{stem}-full.png", full_page=True)
                audit = page.evaluate(AUDIT_SCRIPT)
                page.screenshot(path=OUT / f"{stem}-bottom.png")
                results.append({"page": name, "scheme": scheme, **audit, "consoleErrors": errors[:5]})
            context.close()
        browser.close()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", nargs="+", default=list(PAGES))
    parser.add_argument("--schemes", nargs="+", default=["light", "dark"], choices=["light", "dark"])
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="allen-review-", ignore_cleanup_errors=True) as tmp:
        process, base = start_server(Path(tmp))
        try:
            results = review(base, args.schemes, args.pages)
        finally:
            process.terminate()
            process.wait(timeout=10)

    (OUT / "report.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    issues = 0
    for r in results:
        head = f"{r['page']:<14} {r['scheme']:<5}"
        if "error" in r:
            issues += 1
            print(f"{head} ERROR {r['error']}")
            continue
        problems = []
        if r["scrollWidth"] > r["clientWidth"]:
            causes = ", ".join(f"{o['element']} (→{o['right']}px)" for o in r["overflow"][:3])
            problems.append(f"desborde horizontal {r['scrollWidth']}>{r['clientWidth']}: {causes}")
        if r["covered"]:
            problems.append("tapado por barra inferior: " + ", ".join(c["element"] for c in r["covered"][:3]))
        if r["consoleErrors"]:
            problems.append(f"{len(r['consoleErrors'])} error(es) de consola")
        issues += bool(problems)
        print(f"{head} " + ("; ".join(problems) if problems else "OK"))
    print(f"\nCapturas e informe en {OUT.relative_to(ROOT)} ({len(results)} vistas, {issues} con problemas)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
