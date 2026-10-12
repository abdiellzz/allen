"""Native Windows launcher for packaged ALLEN builds."""
from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import http.client
import json
import webbrowser


def install_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def configure_distribution_mode() -> Path:
    root = install_root()
    if (root / "portable.flag").is_file():
        data_root = root / "ALLEN-Data"
        data_root.mkdir(parents=True, exist_ok=True)
        os.environ["ALLEN_DATA_ROOT"] = str(data_root)
    return root


def health_ready(expected_instance: str | None = None) -> bool:
    connection=http.client.HTTPConnection("127.0.0.1",8787,timeout=0.75)
    try:
        connection.request("GET","/api/health",headers={"Host":"127.0.0.1:8787"})
        response=connection.getresponse()
        if response.status != 200:
            return False
        payload=json.loads(response.read().decode("utf-8"))
        if payload.get("ok") is not True:
            return False
        return expected_instance is None or payload.get("instance")==expected_instance
    except (OSError,ValueError,json.JSONDecodeError,http.client.HTTPException):
        return False
    finally:
        connection.close()


def runtime_components():
    import tkinter as tk
    from tkinter import ttk
    import uvicorn
    from backend.app import app
    from backend.version import ALLEN_VERSION
    return tk, ttk, uvicorn, app, ALLEN_VERSION


def release_log_files() -> None:
    # Windows cannot delete a temporary data folder while allen.log is still open.
    logger = logging.getLogger("allen")
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)


def self_test() -> int:
    root = configure_distribution_mode()
    bundle_root = Path(getattr(sys, "_MEIPASS", root))
    required = [
        bundle_root / "frontend" / "index.html",
        bundle_root / "data" / "library",
        bundle_root / "VERSION",
    ]
    if not all(path.exists() for path in required):
        return 2
    with tempfile.TemporaryDirectory(prefix="allen-self-test-") as tmp:
        os.environ["ALLEN_DATA_ROOT"] = tmp
        try:
            from backend.app import create_app
            app = create_app()
            if not getattr(app, "state", None) or not app.state.db.path.parent.exists():
                return 3
            # Import the same runtime dependencies used by run_gui so packaging cannot
            # hide a missing launcher import until a customer opens ALLEN.
            runtime_components()
        finally:
            release_log_files()
    return 0


def server_smoke_test() -> int:
    with tempfile.TemporaryDirectory(prefix="allen-server-smoke-") as tmp:
        os.environ["ALLEN_DATA_ROOT"] = tmp
        try:
            tk, ttk, uvicorn, app, _ = runtime_components()
            config=uvicorn.Config(app,host="127.0.0.1",port=8787,access_log=False,log_level="warning")
            server=uvicorn.Server(config)
            thread=threading.Thread(target=server.run,daemon=True)
            thread.start()
            ready=False
            for _ in range(80):
                if health_ready(expected_instance=app.state.instance_id):
                    ready=True
                    break
                time.sleep(0.25)
            server.should_exit=True
            thread.join(timeout=5)
            return 0 if ready else 4
        finally:
            release_log_files()


def run_gui() -> int:
    configure_distribution_mode()

    tk, ttk, uvicorn, app, ALLEN_VERSION = runtime_components()

    server_holder = {"server": None}
    stop_event = threading.Event()
    other_instance = threading.Event()

    root = tk.Tk()
    root.title(f"ALLEN {ALLEN_VERSION}")
    root.geometry("430x250")
    root.minsize(430, 250)
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="ALLEN", font=("Segoe UI", 24, "bold")).pack(anchor="w")
    ttk.Label(frame, text=f"Versión {ALLEN_VERSION} · local y privada").pack(anchor="w", pady=(0, 20))

    status = tk.StringVar(value="Iniciando ALLEN…")
    ttk.Label(frame, textvariable=status, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 18))

    buttons = ttk.Frame(frame)
    buttons.pack(fill="x")

    def open_allen():
        # Our launch token only works on our own server; never send it to another process on 8787.
        if other_instance.is_set():
            return
        webbrowser.open("http://127.0.0.1:8787/?access="+app.state.issue_launch_token())

    open_button = ttk.Button(buttons, text="Abrir ALLEN", command=open_allen)
    open_button.pack(side="left")

    def close_allen():
        stop_event.set()
        server = server_holder.get("server")
        if server is not None:
            server.should_exit = True
        root.after(150, root.destroy)

    ttk.Button(buttons, text="Cerrar ALLEN", command=close_allen).pack(side="right")

    ttk.Label(
        frame,
        text="Tus datos se guardan en este equipo. El modo Portable usa la carpeta ALLEN-Data.",
        wraplength=370,
    ).pack(anchor="w", pady=(22, 0))

    root.protocol("WM_DELETE_WINDOW", close_allen)

    def server_worker():
        if health_ready(expected_instance=app.state.instance_id):
            root.after(0, lambda: status.set("ALLEN ya está activo."))
            return
        if health_ready():
            # Another ALLEN window already serves 8787; a second server could not bind the port.
            other_instance.set()
            root.after(0, lambda: status.set("ALLEN ya está abierto en otra ventana. Usa esa ventana o ciérrala antes de abrir otra."))
            root.after(0, lambda: open_button.state(["disabled"]))
            return
        config = uvicorn.Config(app, host="127.0.0.1", port=8787, access_log=False, log_level="warning")
        server = uvicorn.Server(config)
        server_holder["server"] = server
        try:
            server.run()
        finally:
            server_holder["server"] = None

    def readiness_worker():
        for _ in range(80):
            if stop_event.is_set() or other_instance.is_set():
                return
            if health_ready(expected_instance=app.state.instance_id):
                root.after(0, lambda: status.set("ALLEN está listo."))
                root.after(0, open_allen)
                return
            time.sleep(0.25)
        root.after(0, lambda: status.set("No se pudo iniciar. Comprueba si el puerto 8787 está ocupado."))

    threading.Thread(target=server_worker, daemon=True).start()
    threading.Thread(target=readiness_worker, daemon=True).start()

    root.mainloop()
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    if "--server-smoke-test" in sys.argv:
        raise SystemExit(server_smoke_test())
    raise SystemExit(run_gui())
