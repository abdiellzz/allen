"""Phone-size visual review of the ALLEN Android APK interface.

Assembles the APK web assets (android/build_web_assets.py) into a temporary folder and serves them
without HTTP headers, exactly like the WebView's asset loader, so the APK's own CSP applies. Opens
Chromium at 375x812 in light and dark, creates a profile, skips the guided tour and screenshots the
main views into .agents/review/. Reports horizontal overflow, controls hidden behind a fixed bottom
bar and console errors (including CSP violations). Exit code 1 when issues are found.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import threading
import unicodedata
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".agents" / "review"
# View name → label of its button in the section menu (None: reached another way).
PAGES = {"Hoy": "Hoy", "Aprender": "Aprender", "Practicar": "Practicar", "Allen": "Allen",
         "Mi progreso": "Mi progreso", "Perfiles": None}

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


def assemble(target: Path) -> None:
    spec = importlib.util.spec_from_file_location("build_web_assets", ROOT / "android" / "build_web_assets.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.assemble(target)


def serve(directory: Path) -> tuple[ThreadingHTTPServer, str]:
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(directory)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def open_view(page, name: str) -> None:
    if name == "Perfiles":
        page.get_by_role("button", name="Perfiles", exact=True).click()
        return
    if page.locator("#section-menu[open]").count() == 0:
        page.locator("#section-menu summary").click()
    page.locator("#navigation").get_by_role("button", name=PAGES[name], exact=True).click()


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
            page = context.new_page()
            errors: list[str] = []
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(base + "/mobile/index.html", wait_until="networkidle")
            page.get_by_label("¿Cómo quieres que te llame?").fill("Estudiante")
            page.get_by_role("button", name="Crear mi perfil", exact=True).click()
            page.get_by_role("button", name="Saltar recorrido", exact=True).click()
            for name in pages:
                errors.clear()
                if name != "Hoy":
                    open_view(page, name)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(500)
                stem = f"{slug(name)}-{scheme}"
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=OUT / f"{stem}.png")
                page.screenshot(path=OUT / f"{stem}-full.png", full_page=True)
                audit = page.evaluate(AUDIT_SCRIPT)
                page.screenshot(path=OUT / f"{stem}-bottom.png")
                results.append({"page": name, "scheme": scheme, **audit, "consoleErrors": errors[:5]})
                if name == "Perfiles" and pages[-1] != name:
                    page.get_by_role("button", name="Abrir", exact=True).first.click()
            context.close()
        browser.close()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", nargs="+", default=list(PAGES), choices=list(PAGES))
    parser.add_argument("--schemes", nargs="+", default=["light", "dark"], choices=["light", "dark"])
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="allen-review-", ignore_cleanup_errors=True) as tmp:
        assemble(Path(tmp))
        server, base = serve(Path(tmp))
        try:
            results = review(base, args.schemes, args.pages)
        finally:
            server.shutdown()
            server.server_close()

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
