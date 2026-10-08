from datetime import date
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from tools.license_manager import load_private_key
from tools.protect_license_key import protect_key

from tools.license_manager import make_new_payload, parse_existing, sign_document


MACHINE = "ABCD-1234-EF56-7890-ABCD-1234"


def write_license(tmp_path, document):
    path = tmp_path / "client.license"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_existing_license_signature_is_verified_before_renewal(tmp_path):
    key = Ed25519PrivateKey.generate()
    payload = make_new_payload("Cliente", "Institution", MACHINE, 30, today=date(2026, 10, 7))
    document = sign_document(payload, key)
    path = write_license(tmp_path, document)

    loaded = parse_existing(path, key)

    assert loaded["license_id"] == payload["license_id"]
    assert loaded["machine_id"] == MACHINE


def test_tampered_existing_license_is_rejected_before_renewal(tmp_path):
    key = Ed25519PrivateKey.generate()
    payload = make_new_payload("Cliente", "Institution", MACHINE, 30, today=date(2026, 10, 7))
    document = sign_document(payload, key)
    document["payload"]["valid_until"] = "2036-12-31"
    path = write_license(tmp_path, document)

    try:
        parse_existing(path, key)
    except RuntimeError as exc:
        assert "firma válida" in str(exc)
    else:
        raise AssertionError("A tampered prior license must never be renewed")


def test_license_signed_by_another_key_is_rejected(tmp_path):
    owner_key = Ed25519PrivateKey.generate()
    attacker_key = Ed25519PrivateKey.generate()
    payload = make_new_payload("Cliente", "Institution", MACHINE, 30, today=date(2026, 10, 7))
    document = sign_document(payload, attacker_key)
    path = write_license(tmp_path, document)

    try:
        parse_existing(path, owner_key)
    except RuntimeError as exc:
        assert "firma válida" in str(exc)
    else:
        raise AssertionError("A license signed by another key must never be renewed")


def test_private_key_permissions_are_hardened_on_posix(tmp_path):
    import os
    if os.name == "nt":
        return
    key = Ed25519PrivateKey.generate()
    path = tmp_path / "license_private_key.pem"
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    path.chmod(0o644)

    loaded = load_private_key(path, allow_unencrypted=True)

    assert loaded is not None
    assert path.stat().st_mode & 0o077 == 0


def test_unencrypted_private_key_is_rejected_for_signing(tmp_path):
    key = Ed25519PrivateKey.generate()
    path = tmp_path / "license_private_key.pem"
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    try:
        load_private_key(path)
    except RuntimeError as exc:
        assert "sin cifrar" in str(exc)
    else:
        raise AssertionError("Signing must reject unencrypted private keys")


def test_private_key_can_be_migrated_to_encrypted_pem(tmp_path):
    key = Ed25519PrivateKey.generate()
    path = tmp_path / "license_private_key.pem"
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    protect_key(path,"correct-horse-battery")
    assert b"ENCRYPTED PRIVATE KEY" in path.read_bytes()
    loaded=load_private_key(path,password="correct-horse-battery")
    assert loaded.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    ) == key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
