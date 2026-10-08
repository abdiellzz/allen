"""Private desktop utility used to issue and renew ALLEN offline licenses.

The executable intentionally does not embed the private signing key. Place
license_private_key.pem next to the executable or set ALLEN_LICENSE_PRIVATE_KEY.
"""
from __future__ import annotations

import argparse
import base64
from datetime import date, timedelta
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization


MACHINE_RE = re.compile(r"^[A-F0-9]{4}(?:-[A-F0-9]{4}){5}$")


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def key_path() -> Path:
    configured = os.environ.get("ALLEN_LICENSE_PRIVATE_KEY")
    return Path(configured).expanduser() if configured else app_dir() / "license_private_key.pem"


def load_private_key(path: Path | None = None):
    target = path or key_path()
    try:
        raw = target.read_bytes()
        if os.name != "nt":
            target.chmod(0o600)
        key = serialization.load_pem_private_key(raw, password=None)
    except (OSError, ValueError) as exc:
        raise RuntimeError(
            f"No se pudo abrir la clave privada: {target}. "
            "Coloca license_private_key.pem junto al generador."
        ) from exc
    if key.__class__.__name__ != "Ed25519PrivateKey":
        raise RuntimeError("La clave privada no es Ed25519.")
    return key


def canonical(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sign_document(payload: dict, private_key) -> dict:
    signature = private_key.sign(canonical(payload))
    return {
        "payload": payload,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def parse_existing(path: Path, private_key) -> dict:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or set(document) != {"payload", "signature"}:
            raise TypeError
        payload = document["payload"]
        signature = document["signature"]
        if not isinstance(payload, dict) or not isinstance(signature, str):
            raise TypeError
        required = {
            "schema",
            "license_id",
            "customer",
            "plan",
            "machine_id",
            "valid_from",
            "valid_until",
            "issued_at",
            "renewal_number",
            "unlimited_profiles",
        }
        if set(payload) != required or payload.get("schema") != 1 or payload.get("unlimited_profiles") is not True:
            raise TypeError
        if not isinstance(payload.get("renewal_number"), int) or payload["renewal_number"] < 1:
            raise TypeError
        normalized_machine(str(payload["machine_id"]))
        date.fromisoformat(str(payload["valid_from"]))
        date.fromisoformat(str(payload["valid_until"]))
        signature_bytes = base64.b64decode(signature, validate=True)
        private_key.public_key().verify(signature_bytes, canonical(payload))
        return payload
    except InvalidSignature as exc:
        raise RuntimeError("La licencia seleccionada no tiene una firma válida de ALLEN.") from exc
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("No se pudo validar la licencia seleccionada.") from exc


def normalized_machine(value: str) -> str:
    value = value.strip().upper()
    if not MACHINE_RE.fullmatch(value):
        raise ValueError("El Machine ID debe tener 6 grupos de 4 caracteres, por ejemplo ABCD-1234-EF56-7890-ABCD-1234.")
    return value


def make_new_payload(customer: str, plan: str, machine: str, days: int, today: date | None = None) -> dict:
    today = today or date.today()
    if not customer.strip() or len(customer.strip()) > 160:
        raise ValueError("Escribe un nombre de cliente válido.")
    if not plan.strip() or len(plan.strip()) > 80:
        raise ValueError("Escribe un plan válido.")
    if days < 1 or days > 3660:
        raise ValueError("La duración debe estar entre 1 y 3660 días.")
    machine = normalized_machine(machine)
    return {
        "schema": 1,
        "license_id": "ALLEN-" + secrets.token_hex(6).upper(),
        "customer": customer.strip(),
        "plan": plan.strip(),
        "machine_id": machine,
        "valid_from": today.isoformat(),
        "valid_until": (today + timedelta(days=days - 1)).isoformat(),
        "issued_at": today.isoformat(),
        "renewal_number": 1,
        "unlimited_profiles": True,
    }


def renew_payload(existing: dict, days: int, today: date | None = None) -> dict:
    today = today or date.today()
    if days < 1 or days > 3660:
        raise ValueError("La duración debe estar entre 1 y 3660 días.")
    end = date.fromisoformat(existing["valid_until"])
    if end >= today:
        valid_from = date.fromisoformat(existing["valid_from"])
        valid_until = end + timedelta(days=days)
    else:
        valid_from = today
        valid_until = today + timedelta(days=days - 1)
    return {
        "schema": 1,
        "license_id": str(existing["license_id"]),
        "customer": str(existing["customer"]),
        "plan": str(existing["plan"]),
        "machine_id": normalized_machine(str(existing["machine_id"])),
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "issued_at": today.isoformat(),
        "renewal_number": int(existing.get("renewal_number", 1)) + 1,
        "unlimited_profiles": True,
    }


def save_license(document: dict, destination: Path) -> None:
    destination.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


class LicenseManagerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ALLEN License Manager")
        self.root.geometry("720x610")
        self.root.minsize(720, 610)
        self.loaded_payload: dict | None = None

        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="ALLEN License Manager", font=("Segoe UI", 22, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(frame, text="Generador privado de licencias offline", font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        self.key_status = tk.StringVar()
        ttk.Label(frame, textvariable=self.key_status).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 18))
        self._refresh_key_status()

        ttk.Label(frame, text="Cliente").grid(row=3, column=0, sticky="w", pady=6)
        self.customer = ttk.Entry(frame)
        self.customer.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Machine ID").grid(row=4, column=0, sticky="w", pady=6)
        self.machine = ttk.Entry(frame)
        self.machine.grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Plan").grid(row=5, column=0, sticky="w", pady=6)
        self.plan = ttk.Combobox(frame, values=["Teacher", "Institution", "Institution Pro", "Custom"])
        self.plan.set("Institution")
        self.plan.grid(row=5, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Duración").grid(row=6, column=0, sticky="w", pady=6)
        duration_row = ttk.Frame(frame)
        duration_row.grid(row=6, column=1, sticky="w", pady=6)
        self.days = tk.IntVar(value=30)
        ttk.Spinbox(duration_row, from_=1, to=3660, textvariable=self.days, width=8).pack(side="left")
        ttk.Label(duration_row, text=" días").pack(side="left")

        buttons = ttk.Frame(frame)
        buttons.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(20, 8))
        ttk.Button(buttons, text="Nueva licencia", command=self.new_license).pack(side="left")
        ttk.Button(buttons, text="Cargar para renovar", command=self.load_for_renewal).pack(side="left", padx=8)
        ttk.Button(buttons, text="Generar archivo .license", command=self.generate).pack(side="right")

        self.mode = tk.StringVar(value="Nueva licencia")
        ttk.Label(frame, textvariable=self.mode, font=("Segoe UI", 11, "bold")).grid(row=8, column=0, columnspan=2, sticky="w", pady=(18, 6))

        self.preview = tk.Text(frame, height=14, wrap="word", state="disabled", font=("Consolas", 10))
        self.preview.grid(row=9, column=0, columnspan=2, sticky="nsew")
        self._preview_text("Completa los datos del cliente y genera una licencia.")

        ttk.Label(
            frame,
            text="Perfiles, estudiantes y profesores: sin límite. La licencia queda vinculada al Machine ID.",
            wraplength=640,
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(14, 0))

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(9, weight=1)

    def _refresh_key_status(self):
        target = key_path()
        try:
            load_private_key(target)
            self.key_status.set(f"Clave privada: OK · {target}")
        except RuntimeError:
            self.key_status.set(f"Clave privada NO encontrada · {target}")

    def _preview_text(self, value: str):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", value)
        self.preview.configure(state="disabled")

    def new_license(self):
        self.loaded_payload = None
        self.customer.configure(state="normal")
        self.machine.configure(state="normal")
        self.plan.configure(state="normal")
        self.customer.delete(0, "end")
        self.machine.delete(0, "end")
        self.plan.set("Institution")
        self.days.set(30)
        self.mode.set("Nueva licencia")
        self._preview_text("Se generará un license_id único automáticamente.")

    def load_for_renewal(self):
        filename = filedialog.askopenfilename(
            title="Selecciona la licencia actual",
            filetypes=[("ALLEN license", "*.license"), ("JSON", "*.json"), ("Todos", "*.*")],
        )
        if not filename:
            return
        try:
            key = load_private_key()
            payload = parse_existing(Path(filename), key)
            normalized_machine(str(payload["machine_id"]))
            self.loaded_payload = payload
            for widget, value in (
                (self.customer, payload["customer"]),
                (self.machine, payload["machine_id"]),
                (self.plan, payload["plan"]),
            ):
                widget.configure(state="normal")
                if isinstance(widget, ttk.Entry):
                    widget.delete(0, "end")
                    widget.insert(0, str(value))
                else:
                    widget.set(str(value))
                widget.configure(state="disabled")
            self.mode.set(f"Renovación · {payload['license_id']} · #{int(payload.get('renewal_number',1))+1}")
            self._preview_text(
                f"Licencia actual: {payload['license_id']}\n"
                f"Cliente: {payload['customer']}\n"
                f"Machine ID: {payload['machine_id']}\n"
                f"Vence actualmente: {payload['valid_until']}\n\n"
                "Los días nuevos se suman a la fecha vigente si todavía no ha expirado."
            )
        except Exception as exc:
            messagebox.showerror("No se pudo cargar", str(exc))

    def generate(self):
        try:
            key = load_private_key()
            days = int(self.days.get())
            if self.loaded_payload is None:
                payload = make_new_payload(
                    self.customer.get(),
                    self.plan.get(),
                    self.machine.get(),
                    days,
                )
            else:
                payload = renew_payload(self.loaded_payload, days)
            document = sign_document(payload, key)
            default_name = f"{payload['license_id']}-R{payload['renewal_number']}.license"
            destination = filedialog.asksaveasfilename(
                title="Guardar licencia",
                defaultextension=".license",
                initialfile=default_name,
                filetypes=[("ALLEN license", "*.license")],
            )
            if not destination:
                return
            save_license(document, Path(destination))
            self._preview_text(
                f"LICENCIA GENERADA\n\n"
                f"ID: {payload['license_id']}\n"
                f"Cliente: {payload['customer']}\n"
                f"Plan: {payload['plan']}\n"
                f"Machine ID: {payload['machine_id']}\n"
                f"Válida desde: {payload['valid_from']}\n"
                f"Válida hasta: {payload['valid_until']}\n"
                f"Renovación: {payload['renewal_number']}\n"
                f"Perfiles: sin límite\n\n"
                f"Archivo: {destination}"
            )
            messagebox.showinfo("Licencia generada", f"Archivo creado:\n{destination}")
            self.loaded_payload = payload
            self.mode.set(f"Renovación · {payload['license_id']} · #{payload['renewal_number']+1}")
        except Exception as exc:
            messagebox.showerror("No se pudo generar", str(exc))

    def run(self):
        self.root.mainloop()


def self_test() -> int:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key = Ed25519PrivateKey.generate()
    payload = make_new_payload(
        "Self Test",
        "Institution",
        "ABCD-1234-EF56-7890-ABCD-1234",
        30,
        today=date(2026, 1, 1),
    )
    document = sign_document(payload, key)
    key.public_key().verify(base64.b64decode(document["signature"]), canonical(document["payload"]))
    renewed = renew_payload(payload, 30, today=date(2026, 1, 10))
    return 0 if renewed["license_id"] == payload["license_id"] and renewed["valid_until"] == "2026-03-01" else 2


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--self-test", action="store_true")
    args, _ = parser.parse_known_args()
    if args.self_test:
        raise SystemExit(self_test())
    LicenseManagerUI().run()


if __name__ == "__main__":
    main()
