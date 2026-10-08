import base64
from datetime import date
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

import backend.licensing as licensing
from backend.licensing import LicenseManager


MACHINE = "ABCD-1234-EF56-7890-ABCD-1234"


def make_manager(tmp_path, monkeypatch):
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_path = tmp_path / "public.pem"
    public_path.write_bytes(
        public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    monkeypatch.setattr(licensing, "machine_id", lambda: MACHINE)
    return LicenseManager(tmp_path / "data", public_path), private_key


def signed_document(private_key, **changes):
    payload = {
        "schema": 1,
        "license_id": "ALLEN-TEST123456",
        "customer": "Cliente de prueba",
        "plan": "Institution",
        "machine_id": MACHINE,
        "valid_from": "2026-10-07",
        "valid_until": "2026-11-05",
        "issued_at": "2026-10-07",
        "renewal_number": 1,
        "unlimited_profiles": True,
    }
    payload.update(changes)
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    signature = base64.b64encode(private_key.sign(canonical)).decode("ascii")
    return json.dumps({"payload": payload, "signature": signature})


def test_valid_license_is_bound_to_machine_and_has_unlimited_profiles(tmp_path, monkeypatch):
    manager, private_key = make_manager(tmp_path, monkeypatch)
    status = manager.install(signed_document(private_key), today=date(2026, 10, 7))
    assert status["active"] is True
    assert status["machine_id"] == MACHINE
    assert status["unlimited_profiles"] is True
    assert status["license_id"] == "ALLEN-TEST123456"


def test_tampered_license_is_rejected(tmp_path, monkeypatch):
    manager, private_key = make_manager(tmp_path, monkeypatch)
    raw = signed_document(private_key)
    document = json.loads(raw)
    document["payload"]["valid_until"] = "2036-11-05"
    try:
        manager.install(json.dumps(document), today=date(2026, 10, 7))
    except ValueError as exc:
        assert "modificada" in str(exc) or "emitida" in str(exc)
    else:
        raise AssertionError("A modified license must be rejected")


def test_license_for_another_machine_is_rejected(tmp_path, monkeypatch):
    manager, private_key = make_manager(tmp_path, monkeypatch)
    raw = signed_document(private_key, machine_id="FFFF-FFFF-FFFF-FFFF-FFFF-FFFF")
    try:
        manager.install(raw, today=date(2026, 10, 7))
    except ValueError as exc:
        assert "otro equipo" in str(exc)
    else:
        raise AssertionError("A license for another machine must be rejected")


def test_expired_license_stays_expired_after_reinstall(tmp_path, monkeypatch):
    manager, private_key = make_manager(tmp_path, monkeypatch)
    raw = signed_document(private_key, valid_until="2026-10-08")
    try:
        manager.install(raw, today=date(2026, 10, 9))
    except ValueError as exc:
        assert "expiró" in str(exc)
    else:
        raise AssertionError("Expired licenses cannot be activated")


def test_clock_rollback_is_detected(tmp_path, monkeypatch):
    manager, private_key = make_manager(tmp_path, monkeypatch)
    manager.install(signed_document(private_key), today=date(2026, 10, 20))
    status = manager.status(today=date(2026, 10, 19))
    assert status["active"] is False
    assert status["state"] == "clock_rollback"


def test_renewal_can_extend_same_license(tmp_path, monkeypatch):
    manager, private_key = make_manager(tmp_path, monkeypatch)
    manager.install(signed_document(private_key), today=date(2026, 10, 7))
    renewed = signed_document(
        private_key,
        valid_until="2026-12-05",
        issued_at="2026-11-01",
        renewal_number=2,
    )
    status = manager.install(renewed, today=date(2026, 11, 1))
    assert status["active"] is True
    assert status["license_id"] == "ALLEN-TEST123456"
    assert status["renewal_number"] == 2
    assert status["valid_until"] == "2026-12-05"
