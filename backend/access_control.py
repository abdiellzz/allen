from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets


class TeacherAuth:
    def __init__(self, data_root: Path):
        self.path = Path(data_root) / "teacher_auth.json"
        self.session_token = secrets.token_urlsafe(32)

    def configured(self) -> bool:
        return self.path.is_file()

    def _read(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("La configuración de acceso docente no es válida.") from exc

    @staticmethod
    def _derive(pin: str, salt: bytes) -> bytes:
        return hashlib.scrypt(
            pin.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=32,
        )

    @staticmethod
    def validate_pin(pin: str) -> str:
        value = str(pin).strip()
        if not value.isdigit() or not 4 <= len(value) <= 12:
            raise ValueError("El PIN docente debe tener entre 4 y 12 dígitos.")
        return value

    def setup(self, pin: str) -> None:
        if self.configured():
            raise ValueError("El PIN docente ya está configurado.")
        pin = self.validate_pin(pin)
        salt = secrets.token_bytes(16)
        digest = self._derive(pin, salt)
        payload = {"version": 1, "salt": salt.hex(), "hash": digest.hex()}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        temp.replace(self.path)
        if os.name != "nt":
            self.path.chmod(0o600)

    def verify(self, pin: str) -> bool:
        if not self.configured():
            return False
        try:
            pin = self.validate_pin(pin)
            data = self._read()
            salt = bytes.fromhex(data["salt"])
            expected = bytes.fromhex(data["hash"])
            actual = self._derive(pin, salt)
            return hmac.compare_digest(actual, expected)
        except (ValueError, KeyError):
            return False
