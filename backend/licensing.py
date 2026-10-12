"""Offline license validation for ALLEN.

ALLEN contains only the public Ed25519 key. Licenses are signed externally by
ALLEN License Manager with the private key and are bound to one machine.
"""
from __future__ import annotations

import base64
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization


class LicenseError(ValueError):
    pass


def _canonical(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _windows_machine_guid() -> str | None:
    if os.name != "nt":
        return None
    try:
        import winreg
        flags = winreg.KEY_READ
        try:
            flags |= winreg.KEY_WOW64_64KEY
        except AttributeError:
            pass
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            flags,
        ) as key:
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            return str(value).strip()
    except OSError:
        return None


def _format_machine_source(source: str) -> str:
    digest = hashlib.sha256(("ALLEN-LICENSE|" + source).encode("utf-8")).hexdigest().upper()[:24]
    return "-".join(digest[i : i + 4] for i in range(0, len(digest), 4))


def legacy_machine_id() -> str:
    """Identifier used by ALLEN 1.2.0/1.2.1 for backwards-compatible licenses."""
    source=_windows_machine_guid()
    if source:
        return _format_machine_source(source)
    source="|".join([platform.system(),platform.machine(),platform.node(),str(uuid.getnode())])
    return _format_machine_source(source)


def machine_id() -> str:
    """Prefer two stable local factors while preserving the old ID as fallback."""
    guid=_windows_machine_guid()
    node=uuid.getnode()
    # Python marks a randomly generated node by setting the multicast bit.
    stable_node = None if ((node >> 40) & 1) else f"{node:012X}"
    if guid and stable_node:
        return _format_machine_source(f"{guid}|{platform.machine()}|{stable_node}")
    return legacy_machine_id()


def machine_id_candidates() -> set[str]:
    return {machine_id(),legacy_machine_id()}


class LicenseManager:
    def __init__(self, data_root: Path, public_key_path: Path):
        self.data_root = Path(data_root)
        self.license_dir = self.data_root / "license"
        self.license_path = self.license_dir / "allen.license"
        self.state_path = self.license_dir / "state.json"
        self.public_key_path = Path(public_key_path)
        self._status_cache = None
        self._status_cache_until = 0.0

    def _public_key(self):
        try:
            raw = self.public_key_path.read_bytes()
            return serialization.load_pem_public_key(raw)
        except (OSError, ValueError) as exc:
            raise LicenseError("La clave pública de ALLEN no está disponible.") from exc

    def _decode(self, raw: str | bytes) -> tuple[dict, str]:
        if isinstance(raw, bytes):
            try:
                raw = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise LicenseError("El archivo de licencia no es texto UTF-8 válido.") from exc
        if len(raw) > 64_000:
            raise LicenseError("El archivo de licencia es demasiado grande.")
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LicenseError("El archivo de licencia no tiene un formato válido.") from exc
        if not isinstance(document, dict):
            raise LicenseError("El archivo de licencia no tiene un formato válido.")
        payload = document.get("payload")
        signature = document.get("signature")
        if not isinstance(payload, dict) or not isinstance(signature, str):
            raise LicenseError("El archivo de licencia está incompleto.")
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
        if set(payload) != required:
            raise LicenseError("La licencia contiene campos no reconocidos o incompletos.")
        if payload.get("schema") != 1:
            raise LicenseError("Esta versión de licencia no es compatible.")
        if payload.get("unlimited_profiles") is not True:
            raise LicenseError("La licencia no corresponde a la edición actual de ALLEN.")
        for field in ("license_id", "customer", "plan", "machine_id", "valid_from", "valid_until", "issued_at"):
            value = payload.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > 160:
                raise LicenseError("La licencia contiene datos no válidos.")
        renewal = payload.get("renewal_number")
        if not isinstance(renewal, int) or renewal < 1 or renewal > 10000:
            raise LicenseError("El número de renovación no es válido.")
        try:
            signature_bytes = base64.b64decode(signature, validate=True)
        except Exception as exc:
            raise LicenseError("La firma de la licencia no tiene un formato válido.") from exc
        try:
            self._public_key().verify(signature_bytes, _canonical(payload))
        except InvalidSignature as exc:
            raise LicenseError("La licencia no fue emitida por ALLEN o fue modificada.") from exc
        return payload, signature

    @staticmethod
    def _dates(payload: dict) -> tuple[date, date]:
        try:
            start = date.fromisoformat(payload["valid_from"])
            end = date.fromisoformat(payload["valid_until"])
        except ValueError as exc:
            raise LicenseError("Las fechas de la licencia no son válidas.") from exc
        if end < start:
            raise LicenseError("El periodo de la licencia no es válido.")
        if (end - start).days > 3660:
            raise LicenseError("El periodo de la licencia excede el máximo permitido.")
        return start, end

    def _read_state(self) -> dict:
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            return state if isinstance(state, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _last_seen(self) -> date | None:
        try:
            return date.fromisoformat(str(self._read_state().get("last_seen")))
        except ValueError:
            return None

    def _write_state(self, payload: dict, today: date) -> None:
        current=self._read_state()
        last_seen=max(filter(None,(self._last_seen(),today)))
        if (
            current.get("license_id")==payload["license_id"]
            and current.get("machine_id")==payload["machine_id"]
            and current.get("last_seen")==last_seen.isoformat()
        ):
            return
        self.license_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "license_id": payload["license_id"],
            "machine_id": payload["machine_id"],
            "last_seen": last_seen.isoformat(),
        }
        temp = self.state_path.with_suffix(".tmp")
        temp.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
        temp.replace(self.state_path)

    def status(self, today: date | None = None) -> dict:
        explicit_today=today is not None
        if not explicit_today and self._status_cache is not None and time.monotonic()<self._status_cache_until:
            return dict(self._status_cache)
        today = today or date.today()
        machine = machine_id()
        base = {
            "required": True,
            "machine_id": machine,
            "active": False,
            "state": "missing",
            "message": "Importa una licencia válida para utilizar ALLEN.",
        }
        if not self.license_path.exists():
            if not explicit_today:
                self._status_cache=dict(base); self._status_cache_until=time.monotonic()+15
            return base
        try:
            payload, _ = self._decode(self.license_path.read_text(encoding="utf-8"))
            start, end = self._dates(payload)
        except (OSError, LicenseError) as exc:
            result={**base, "state": "invalid", "message": str(exc)}
            if not explicit_today:
                self._status_cache=dict(result); self._status_cache_until=time.monotonic()+15
            return result

        public = {
            "license_id": payload["license_id"],
            "customer": payload["customer"],
            "plan": payload["plan"],
            "valid_from": payload["valid_from"],
            "valid_until": payload["valid_until"],
            "renewal_number": payload["renewal_number"],
            "unlimited_profiles": True,
        }
        if payload["machine_id"] not in machine_id_candidates():
            return {
                **base,
                **public,
                "state": "wrong_machine",
                "message": "Esta licencia pertenece a otro equipo.",
            }
        if today < start:
            return {
                **base,
                **public,
                "state": "not_yet_valid",
                "message": f"La licencia comienza el {start.isoformat()}.",
            }
        if today > end:
            return {
                **base,
                **public,
                "state": "expired",
                "message": f"La licencia expiró el {end.isoformat()}. Importa una renovación.",
            }

        last_seen = self._last_seen()
        if last_seen and today < last_seen:
            return {
                **base,
                **public,
                "state": "clock_rollback",
                "message": "La fecha del sistema retrocedió. Corrige la fecha de Windows para continuar.",
            }

        self._write_state(payload, today)
        days_remaining = (end - today).days + 1
        result={
            **base,
            **public,
            "active": True,
            "state": "active",
            "days_remaining": days_remaining,
            "message": f"Licencia activa. Quedan {days_remaining} días.",
        }
        if not explicit_today:
            self._status_cache=dict(result)
            self._status_cache_until=time.monotonic()+60
        return result

    def install(self, raw: str, today: date | None = None) -> dict:
        self._status_cache=None
        self._status_cache_until=0.0
        today = today or date.today()
        payload, signature = self._decode(raw)
        start, end = self._dates(payload)
        current_machine = machine_id()
        if payload["machine_id"] not in machine_id_candidates():
            raise LicenseError("Esta licencia fue emitida para otro equipo.")
        if today < start:
            raise LicenseError(f"Esta licencia todavía no está activa. Comienza el {start.isoformat()}.")
        if today > end:
            raise LicenseError(f"Esta licencia expiró el {end.isoformat()}.")
        last_seen = self._last_seen()
        if last_seen and today < last_seen:
            raise LicenseError("La fecha del sistema retrocedió. Corrige la fecha de Windows antes de activar la licencia.")

        current_payload = None
        if self.license_path.exists():
            try:
                current_payload, _ = self._decode(self.license_path.read_text(encoding="utf-8"))
                _, current_end = self._dates(current_payload)
            except (OSError, LicenseError):
                # A damaged or foreign license file must not prevent installing a valid one.
                current_payload = None
        if (
            current_payload
            and current_payload.get("license_id") == payload["license_id"]
            and end < current_end
        ):
            raise LicenseError("La renovación no puede reducir la fecha de vencimiento actual.")

        normalized = {
            "payload": payload,
            "signature": signature,
        }
        self.license_dir.mkdir(parents=True, exist_ok=True)
        temp = self.license_path.with_suffix(".tmp")
        temp.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temp.replace(self.license_path)
        self._write_state(payload, today)
        result = self.status(today=today)
        if not result["active"]:
            raise LicenseError(result["message"])
        return result
