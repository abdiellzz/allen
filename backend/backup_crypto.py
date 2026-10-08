from __future__ import annotations

import base64
import json
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

AAD=b"ALLEN-BACKUP-V1"
FORMAT="allen-backup-encrypted"
VERSION=1


def _password(value: str) -> bytes:
    if not isinstance(value,str) or not 8<=len(value)<=128:
        raise ValueError("La contraseña del respaldo debe tener entre 8 y 128 caracteres.")
    return value.encode("utf-8")


def _key(password: str, salt: bytes) -> bytes:
    return Scrypt(salt=salt,length=32,n=2**14,r=8,p=1).derive(_password(password))


def encrypt_backup(payload: dict, password: str) -> dict:
    raw=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    if len(raw)>5_500_000:
        raise ValueError("El respaldo es demasiado grande para cifrarlo.")
    salt=os.urandom(16)
    nonce=os.urandom(12)
    ciphertext=AESGCM(_key(password,salt)).encrypt(nonce,raw,AAD)
    return {
        "format":FORMAT,
        "version":VERSION,
        "kdf":"scrypt-n16384-r8-p1",
        "cipher":"AES-256-GCM",
        "salt":base64.b64encode(salt).decode("ascii"),
        "nonce":base64.b64encode(nonce).decode("ascii"),
        "ciphertext":base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_backup(envelope: dict, password: str) -> dict:
    if not isinstance(envelope,dict) or envelope.get("format")!=FORMAT or envelope.get("version")!=VERSION:
        raise ValueError("Este archivo no es un respaldo cifrado compatible de ALLEN.")
    if envelope.get("kdf")!="scrypt-n16384-r8-p1" or envelope.get("cipher")!="AES-256-GCM":
        raise ValueError("El método de cifrado del respaldo no es compatible.")
    try:
        salt=base64.b64decode(envelope["salt"],validate=True)
        nonce=base64.b64decode(envelope["nonce"],validate=True)
        ciphertext=base64.b64decode(envelope["ciphertext"],validate=True)
    except (KeyError,ValueError,TypeError) as exc:
        raise ValueError("El respaldo cifrado está dañado.") from exc
    if len(salt)!=16 or len(nonce)!=12 or len(ciphertext)>7_500_000:
        raise ValueError("El respaldo cifrado no tiene un formato válido.")
    try:
        raw=AESGCM(_key(password,salt)).decrypt(nonce,ciphertext,AAD)
    except InvalidTag as exc:
        raise ValueError("Contraseña incorrecta o respaldo modificado.") from exc
    try:
        payload=json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError) as exc:
        raise ValueError("El contenido descifrado no es un respaldo válido.") from exc
    if not isinstance(payload,dict):
        raise ValueError("El contenido descifrado no es un respaldo válido.")
    return payload
