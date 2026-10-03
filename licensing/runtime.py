"""Offline Ed25519 license, registration, machine fingerprint and integrity checks."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
from datetime import date, datetime, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .trust_anchor import PUBLIC_KEY_SHA256

APP_NAME = 'ALLEN'
REGISTRY_PATH = r'SOFTWARE\ALLEN'
PUBLIC_KEY_FILE = 'license_public_key.pem'


def canonical_json(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def data_home() -> Path:
    if os.environ.get('ALLEN_DATA_HOME'):
        return Path(os.environ['ALLEN_DATA_HOME']).resolve()
    base = Path(os.environ.get('PROGRAMDATA', r'C:\ProgramData')) if os.name == 'nt' else Path.home() / '.local' / 'share'
    return base / APP_NAME


def machine_fingerprint() -> str:
    """Hash MachineGuid plus Windows ComputerHardwareId; retain neither source value."""
    if os.name != 'nt':
        raise RuntimeError('La activación institucional de ALLEN solo está disponible en Windows.')
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography') as key:
        machine_guid = winreg.QueryValueEx(key, 'MachineGuid')[0]
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\SystemInformation') as key:
        hardware_id = winreg.QueryValueEx(key, 'ComputerHardwareId')[0]
    if isinstance(hardware_id, (list, tuple)):
        hardware_id = '|'.join(sorted(str(value).strip().lower() for value in hardware_id))
    normalized = '|'.join((str(machine_guid).strip().lower(), str(hardware_id).strip().lower()))
    if not machine_guid or not hardware_id:
        raise RuntimeError('Windows no proporcionó los identificadores técnicos necesarios para activar ALLEN.')
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def register_installation(install_root: Path, version: str, *, write_registry: bool = True) -> dict:
    """Create or preserve the local install identity; registry writes require Setup/admin rights."""
    root = install_root.resolve()
    state_dir = data_home()
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / 'installation.json'
    fingerprint = machine_fingerprint()
    previous = {}
    try:
        previous = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        pass
    installation_id = previous.get('installation_id') if (
        previous.get('machine_fingerprint') == fingerprint and
        Path(previous.get('install_path', root)).resolve() == root
    ) else None
    record = {
        'installation_id': installation_id or f'ALLEN-INSTALL-{__import__("uuid").uuid4().hex}',
        'machine_fingerprint': fingerprint,
        'install_path': str(root),
        'version': version,
        'edition': 'institutional',
    }
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(record, indent=2), encoding='utf-8')
    temp.replace(path)
    if write_registry:
        if os.name != 'nt':
            raise RuntimeError('El registro oficial de ALLEN requiere Windows.')
        import winreg
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, 'InstallationId', 0, winreg.REG_SZ, record['installation_id'])
            winreg.SetValueEx(key, 'Version', 0, winreg.REG_SZ, version)
            winreg.SetValueEx(key, 'InstallPath', 0, winreg.REG_SZ, str(root))
            winreg.SetValueEx(key, 'Edition', 0, winreg.REG_SZ, record['edition'])
    return record


def activation_request(install_root: Path, version: str) -> dict:
    record = register_installation(install_root, version)
    request = {
        'format': 'ALLEN-ACTIVATION-REQUEST-1',
        'installation_id': record['installation_id'],
        'machine_fingerprint': record['machine_fingerprint'],
        'version': version,
        'edition': record['edition'],
    }
    path = data_home() / 'activation-request.allen'
    path.write_text(json.dumps(request, indent=2), encoding='utf-8')
    return request


def _public_key(install_root: Path) -> Ed25519PublicKey:
    key_path = install_root / PUBLIC_KEY_FILE
    raw = key_path.read_bytes()
    if (not re.fullmatch(r'[0-9a-f]{64}', PUBLIC_KEY_SHA256) or
            not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), PUBLIC_KEY_SHA256)):
        raise ValueError('La clave pública de ALLEN no coincide con el ancla de confianza compilada.')
    key = serialization.load_pem_public_key(raw)
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError('La clave pública configurada no es Ed25519.')
    return key


def _signed_payload(document: dict, public_key: Ed25519PublicKey) -> dict:
    payload, signature = document.get('payload'), document.get('signature')
    if not isinstance(payload, dict) or not isinstance(signature, str):
        raise ValueError('El documento firmado no tiene el formato ALLEN esperado.')
    public_key.verify(base64.b64decode(signature, validate=True), canonical_json(payload))
    return payload


def verify_registration(install_root: Path, *, require_registry: bool = True) -> dict:
    root = install_root.resolve()
    record_path = data_home() / 'installation.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    if not re.fullmatch(r'ALLEN-INSTALL-[0-9a-f]{32}', record.get('installation_id', '')):
        raise ValueError('El identificador de instalación de ALLEN no es válido.')
    if Path(record.get('install_path', '')).resolve() != root:
        raise ValueError('ALLEN debe ejecutarse desde su instalación oficial registrada.')
    if record.get('machine_fingerprint') != machine_fingerprint():
        raise ValueError('Esta instalación de ALLEN no está activada para este equipo.')
    if require_registry:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH) as key:
            registered_id = winreg.QueryValueEx(key, 'InstallationId')[0]
            registered_path = Path(winreg.QueryValueEx(key, 'InstallPath')[0]).resolve()
        if registered_id != record['installation_id'] or registered_path != root:
            raise ValueError('La instalación de ALLEN no coincide con su registro oficial.')
    return record


def verify_license(install_root: Path, record: dict, *, today: date | None = None) -> dict:
    key = _public_key(install_root)
    license_path = data_home() / 'license.allen'
    try:
        document = json.loads(license_path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise ValueError(f'No se encontró {license_path}. Guarda allí el license.allen firmado para activar ALLEN.') from exc
    payload = _signed_payload(document, key)
    required = ('license_id', 'customer', 'edition', 'issued_at', 'installation_id', 'machine_fingerprint', 'max_devices')
    if any(not payload.get(field) for field in required):
        raise ValueError('La licencia de ALLEN está incompleta.')
    if payload['installation_id'] != record['installation_id']:
        raise ValueError('La licencia no corresponde a este Installation ID.')
    if payload['machine_fingerprint'] != record['machine_fingerprint']:
        raise ValueError('La licencia no está emitida para este equipo.')
    if not isinstance(payload['max_devices'], int) or payload['max_devices'] != 1:
        raise ValueError('La licencia no respeta el límite de un equipo por instalación.')
    now = today or datetime.now(timezone.utc).date()
    issued = date.fromisoformat(payload['issued_at'][:10])
    if issued > now:
        raise ValueError('La licencia todavía no está vigente.')
    expires = payload.get('expires_at')
    if expires and date.fromisoformat(expires[:10]) < now:
        raise ValueError('La licencia de ALLEN ha expirado. Reemplaza license.allen por la renovación; tus datos permanecen en ProgramData.')
    return payload


def verify_manifest(install_root: Path) -> dict:
    root = install_root.resolve()
    key = _public_key(root)
    document = json.loads((root / 'manifest.allen').read_text(encoding='utf-8'))
    payload = _signed_payload(document, key)
    files = payload.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('El manifest de integridad está vacío o no es válido.')
    for relative, expected in files.items():
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file():
            raise ValueError(f'Falta un archivo crítico de ALLEN: {relative}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not isinstance(expected, str) or not hmac.compare_digest(digest, expected):
            raise ValueError(f'Los archivos de ALLEN fueron modificados o están dañados: {relative}')
    return payload


def authorize(install_root: Path, *, require_registry: bool = True) -> dict:
    record = verify_registration(install_root, require_registry=require_registry)
    verify_manifest(install_root)
    license_info = verify_license(install_root, record)
    return {'registration': record, 'license': license_info}
