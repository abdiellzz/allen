"""One-time migration tool for ALLEN's private Ed25519 signing key."""
from __future__ import annotations

from getpass import getpass
from pathlib import Path
import os
import sys

from cryptography.hazmat.primitives import serialization


def protect_key(path: Path, password: str) -> None:
    if len(password) < 12:
        raise ValueError("Usa una frase de paso de al menos 12 caracteres.")
    raw=path.read_bytes()
    if b"ENCRYPTED PRIVATE KEY" in raw:
        raise ValueError("La clave ya está cifrada.")
    key=serialization.load_pem_private_key(raw,password=None)
    encrypted=key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode("utf-8")),
    )
    temp=path.with_suffix(".pem.tmp")
    temp.write_bytes(encrypted)
    if os.name!="nt":
        temp.chmod(0o600)
    temp.replace(path)
    if os.name!="nt":
        path.chmod(0o600)


def main():
    path=Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else Path("license_private_key.pem")
    if not path.is_file():
        raise SystemExit(f"No se encontró: {path}")
    first=getpass("Nueva frase de paso (mínimo 12 caracteres): ")
    second=getpass("Repite la frase de paso: ")
    if first!=second:
        raise SystemExit("Las frases de paso no coinciden.")
    try:
        protect_key(path,first)
    except Exception as exc:
        raise SystemExit(str(exc))
    print(f"Clave protegida correctamente: {path}")
    print("Guarda la frase de paso en un gestor de contraseñas. No la pongas en Git.")


if __name__=="__main__":
    main()
