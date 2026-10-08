"""Native Windows launcher for packaged ALLEN builds."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import urllib.request
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


def health_ready(url: str = "http://127.0.0.1:8787/api/health") -> bool:
    try:
        with urllib.request.urlopen(url, timeout=0.75) as response:
            return response.status == 200
    except OSError:
        return False


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
        from backend.app import create_app
        app = create_app()
        if not getattr(app, "state", None) or not app.state.db.path.parent.exists():
            return 3
        if not callable(getattr(app.state, "issue_launch_key", None)):
            return 4
    return 0


def run_gui() -> int:
    configure_distribution_mode()

    import tkinter as tk
    from tkinter import ttk
    import uvicorn

    from backend.app import app
    from backend.version import ALLEN_VERSION

    server_holder = {"server": None}
    stop_event = threading.Event()

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
        webbrowser.open("http://127.0.0.1:8787/?access="+app.state.issue_launch_key())

    ttk.Button(buttons, text="Abrir ALLEN", command=open_allen).pack(side="left")

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
        if health_ready():
            root.after(0, lambda: status.set("ALLEN ya está activo."))
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
            if stop_event.is_set():
                return
            if health_ready():
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
    raise SystemExit(run_gui())
