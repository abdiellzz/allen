"""Private-side Ed25519 licensing tools. Never copy this directory into a client package."""
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
from pathlib import Path
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def load_private(path: Path) -> Ed25519PrivateKey:
    raw = path.read_bytes()
    try:
        key = serialization.load_pem_private_key(raw, password=None)
    except TypeError:
        try:
            password = getpass.getpass('Contraseña de la clave privada: ').encode('utf-8')
            key = serialization.load_pem_private_key(raw, password=password)
        except (ValueError, TypeError):
            raise SystemExit('No se pudo descifrar la clave privada Ed25519.')
    if not isinstance(key, Ed25519PrivateKey):
        raise SystemExit('El archivo seleccionado no contiene una clave Ed25519.')
    return key


def signed(payload: dict, key: Ed25519PrivateKey) -> dict:
    signature = key.sign(canonical(payload))
    return {'payload': payload, 'signature': base64.b64encode(signature).decode('ascii')}


def generate_key(args):
    private_path = args.private.resolve()
    public_path = args.public.resolve()
    if private_path.exists() and not args.force:
        raise SystemExit(f'La clave ya existe; no se sobrescribió: {private_path}')
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    key = Ed25519PrivateKey.generate()
    encryption = serialization.NoEncryption() if args.unencrypted_development_key else serialization.BestAvailableEncryption(
        getpass.getpass('Contraseña para cifrar la clave privada: ').encode('utf-8'))
    private_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, encryption))
    public_path.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    warning = private_path.with_suffix(private_path.suffix + '.WARNING.txt')
    protection = 'protected by the current Windows user ACL' if args.unencrypted_development_key else 'encrypted with your passphrase'
    warning.write_text(f'PRIVATE KEY — DO NOT DISTRIBUTE. This development key is {protection}; never place in the repository, build, dist, or installer. Do not use it for production releases.\n', encoding='utf-8')
    if args.unencrypted_development_key:
        print(f'Clave privada de desarrollo SIN CIFRAR (ACL local de usuario): {private_path}')
        print('NO usar esta clave para producción ni copiarla a un build.')
    else:
        print(f'Clave privada cifrada (solo desarrollo): {private_path}')
    print(f'Clave pública (se puede empaquetar solo en builds de prueba): {public_path}')
    print(f'PRIVATE KEY — DO NOT DISTRIBUTE: {warning}')


def issue_license(args):
    request = json.loads(args.request.read_text(encoding='utf-8'))
    if request.get('format') != 'ALLEN-ACTIVATION-REQUEST-1':
        raise SystemExit('El archivo no es una solicitud de activación ALLEN reconocida.')
    payload = {
        'license_id': 'ALLEN-LIC-' + uuid.uuid4().hex,
        'customer': args.customer,
        'edition': args.edition,
        'issued_at': args.issued,
        'expires_at': args.expires or None,
        'installation_id': request['installation_id'],
        'machine_fingerprint': request['machine_fingerprint'],
        'max_devices': 1,
    }
    document = signed(payload, load_private(args.private))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Licencia firmada guardada: {args.output}')


def sign_manifest(args):
    root = args.root.resolve()
    files = {}
    for relative in args.files:
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file():
            raise SystemExit(f'Archivo crítico fuera del paquete o ausente: {relative}')
        files[Path(relative).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    payload = {'format': 'ALLEN-MANIFEST-1', 'version': args.version, 'files': files}
    document = signed(payload, load_private(args.private))
    (root / 'manifest.allen').write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
    print(f'Manifest firmado para {len(files)} archivos: {root / "manifest.allen"}')


def main():
    profile = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
    parser = argparse.ArgumentParser(description='Herramientas privadas para firmar licencias/manifests ALLEN.')
    sub = parser.add_subparsers(dest='command', required=True)
    key = sub.add_parser('generate-key', help='Genera una clave Ed25519 de desarrollo cifrada fuera del repositorio.')
    key.add_argument('--private', type=Path, default=profile / 'ALLEN/license-keys/development-private.pem')
    key.add_argument('--public', type=Path, default=Path(__file__).resolve().parents[2] / 'licensing/development_public_key.pem')
    key.add_argument('--force', action='store_true')
    key.add_argument('--unencrypted-development-key', action='store_true',
                     help='Solo para claves efímeras locales de desarrollo bajo ACL de usuario; nunca producción.')
    key.set_defaults(func=generate_key)
    issue = sub.add_parser('issue-license', help='Firma una license.allen para una solicitud de activación.')
    issue.add_argument('--private', type=Path, required=True)
    issue.add_argument('--request', type=Path, required=True)
    issue.add_argument('--customer', required=True)
    issue.add_argument('--edition', choices=('institutional', 'development'), default='institutional')
    issue.add_argument('--issued', required=True, help='Fecha UTC YYYY-MM-DD.')
    issue.add_argument('--expires', help='Fecha UTC YYYY-MM-DD; omitir para licencia sin vencimiento.')
    issue.add_argument('--output', type=Path, required=True)
    issue.set_defaults(func=issue_license)
    manifest = sub.add_parser('sign-manifest', help='Firma hashes SHA-256 de los binarios críticos de una distribución.')
    manifest.add_argument('--private', type=Path, required=True)
    manifest.add_argument('--root', type=Path, required=True)
    manifest.add_argument('--version', required=True)
    manifest.add_argument('--files', nargs='+', required=True)
    manifest.set_defaults(func=sign_manifest)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
