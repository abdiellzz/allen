"""Run the real ALLEN FastAPI backend inside Pyodide for the Android demo.

The Android WebView has no Python server, so the page's fetch('/api/...') calls are
handed to this module, which forwards them in-process to the ASGI app.
"""
import json
import os
from pathlib import Path

import anyio.to_thread


async def _run_inline(func, *args, abandon_on_cancel=False, cancellable=None, limiter=None):
    # WebAssembly has no threads: FastAPI's sync endpoints run on the event loop instead.
    return func(*args)


anyio.to_thread.run_sync = _run_inline

DATA = Path(os.environ.setdefault("ALLEN_DATA_ROOT", "/data"))
# The Android WebView serves the frontend from APK assets; the backend only needs the
# directory to exist for its StaticFiles mount.
(Path(__file__).resolve().parent / "frontend").mkdir(exist_ok=True)

import httpx  # noqa: E402

from backend.ai import LocalAI  # noqa: E402
from backend.app import create_app  # noqa: E402


class DemoAI(LocalAI):
    """No llama.cpp on the phone: always report the model as disconnected (demo mode)."""

    async def status(self, settings, refresh=False):
        return dict(state="MODO DEMO", connected=False, models=[], configured=False, metrics=dict(self.metrics))


app = create_app(
    db_path=DATA / "allen.sqlite3",
    ai=DemoAI(),
    require_license=False,
    require_local_access=False,
    require_teacher_auth=False,
)
client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1")


async def handle(method, url, headers_json, body):
    headers = {k: v for k, v in json.loads(headers_json).items() if k.lower() not in ("host", "origin", "content-length")}
    response = await client.request(method, url, headers=headers, content=body.encode("utf-8") if body else None)
    out_headers = {k: v for k, v in response.headers.items() if k.lower() not in ("content-length", "content-encoding")}
    return json.dumps({"status": response.status_code, "headers": out_headers, "body": response.text})
