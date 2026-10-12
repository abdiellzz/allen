"""Sign and verify the published ALLEN Android APK.

    python android/sign_release.py init   # once per maintainer machine: release key + rotation lineage
    python android/sign_release.py        # sign app-release-unsigned.apk into android/release/

Releases up to 1.2.4-android-demo were signed with this machine's Android *debug* key. Switching
keys would block in-place updates (users would have to uninstall and lose their progress), so the
release key is introduced with APK Signature Scheme v3 key rotation: the lineage, signed by the old
key, tells Android 9+ to accept the new key and to stop trusting the old one for updates
(no rollback). Android 8.x does not understand rotation and keeps verifying the old key (v2).

Signing material lives outside the repository (and outside OneDrive):
%LOCALAPPDATA%\\allen-android-signing, or ALLEN_ANDROID_SIGNING_DIR. Losing it means no further
updates can be installed over existing installs: keep an offline backup of the whole folder.
"""
from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"
UNSIGNED = ANDROID / "app" / "build" / "outputs" / "apk" / "release" / "app-release-unsigned.apk"
PUBLISHED = ANDROID / "release" / "ALLEN-demo-android.apk"
# Certificates that published APKs are allowed to carry.
LEGACY_CERT = "a2e095c7ab3bc9fa878fcd79b3460622d2153b38448bd053e663697d5cc7eda4"  # Android Debug, <= 1.2.4-android-demo
RELEASE_CERT_FILE = ANDROID / "release" / "signing-certificate.sha256"
RELEASE_ALIAS = "allen-release"
LEGACY_ALIAS = "androiddebugkey"
ROTATION_MIN_SDK = "28"  # first Android version that understands key rotation (v3)


def signing_dir() -> Path:
    custom = os.environ.get("ALLEN_ANDROID_SIGNING_DIR")
    if custom:
        return Path(custom)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "allen-android-signing"


def sdk_dir() -> Path:
    local = ANDROID / "local.properties"
    if local.is_file():
        for line in local.read_text(encoding="utf-8").splitlines():
            if line.startswith("sdk.dir="):
                return Path(line.split("=", 1)[1].replace("\\:", ":").replace("\\\\", "\\"))
    for name in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(name):
            return Path(os.environ[name])
    raise SystemExit("No se encontró el Android SDK (local.properties sdk.dir o ANDROID_HOME).")


def build_tool(name: str) -> str:
    versions = sorted((sdk_dir() / "build-tools").iterdir(), key=lambda p: [int(x) for x in re.findall(r"\d+", p.name)])
    for version in reversed(versions):
        for candidate in (name + ".bat", name + ".exe", name):
            if (version / candidate).is_file():
                return str(version / candidate)
    raise SystemExit(f"No se encontró {name} en build-tools.")


def keytool() -> str:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        for candidate in ("keytool.exe", "keytool"):
            if (Path(java_home) / "bin" / candidate).is_file():
                return str(Path(java_home) / "bin" / candidate)
    found = shutil.which("keytool")
    if not found:
        raise SystemExit("No se encontró keytool: define JAVA_HOME con un JDK 17.")
    return found


def run(*args: str) -> str:
    # Fixed SDK/JDK tools with argument lists; never a shell.
    result = subprocess.run(args, capture_output=True, text=True, check=False)  # nosec B603
    if result.returncode != 0:
        raise SystemExit(f"falló {Path(args[0]).name}:\n{result.stdout}{result.stderr}")
    return result.stdout


def cert_sha256(keystore: Path, alias: str, password_args: list[str]) -> str:
    out = run(keytool(), "-exportcert", "-rfc", "-keystore", str(keystore), "-alias", alias, *password_args)
    der = base64.b64decode("".join(line for line in out.splitlines() if "CERTIFICATE" not in line))
    return hashlib.sha256(der).hexdigest()


def paths() -> dict[str, Path]:
    folder = signing_dir()
    return {
        "dir": folder,
        "legacy": folder / "legacy-debug.keystore",
        "release": folder / "release.p12",
        "password": folder / "release-password.txt",
        "lineage": folder / "lineage.bin",
    }


def init() -> None:
    p = paths()
    if p["release"].exists() or p["lineage"].exists():
        raise SystemExit(f"Ya existe material de firma en {p['dir']}. No se sobrescribe.")
    if ROOT in p["dir"].resolve().parents or "onedrive" in str(p["dir"]).lower():
        raise SystemExit("La carpeta de firma no puede estar dentro del repositorio ni de OneDrive.")
    debug = Path.home() / ".android" / "debug.keystore"
    if cert_sha256(debug, LEGACY_ALIAS, ["-storepass", "android"]) != LEGACY_CERT:
        raise SystemExit(f"{debug} no es la clave que firmó las versiones publicadas; no se puede rotar.")
    p["dir"].mkdir(parents=True, exist_ok=True)
    shutil.copy2(debug, p["legacy"])
    p["password"].write_text(secrets.token_urlsafe(32), encoding="ascii")
    password = ["-storepass:file", str(p["password"]), "-keypass:file", str(p["password"])]
    run(keytool(), "-genkeypair", "-keystore", str(p["release"]), "-storetype", "PKCS12", "-alias", RELEASE_ALIAS,
        "-keyalg", "RSA", "-keysize", "4096", "-validity", "10950", "-dname", "CN=ALLEN Android, O=ALLEN", *password)
    run(build_tool("apksigner"), "rotate", "--out", str(p["lineage"]),
        "--old-signer", "--ks", str(p["legacy"]), "--ks-key-alias", LEGACY_ALIAS, "--ks-pass", "pass:android",
        "--set-rollback", "false",
        "--new-signer", "--ks", str(p["release"]), "--ks-key-alias", RELEASE_ALIAS, "--ks-pass", f"file:{p['password']}")
    fingerprint = cert_sha256(p["release"], RELEASE_ALIAS, ["-storepass:file", str(p["password"])])
    RELEASE_CERT_FILE.write_text(fingerprint + "\n", encoding="ascii")
    print(f"clave de release creada en {p['dir']}")
    print(f"certificado SHA-256: {fingerprint} (guardado en {RELEASE_CERT_FILE.relative_to(ROOT)})")
    print("IMPORTANTE: guarda una copia offline de toda la carpeta; sin ella no habrá más actualizaciones.")


def verify(apk: Path) -> str:
    """Fail unless the APK is signed for rotation, not debuggable and permission-free."""
    release_cert = RELEASE_CERT_FILE.read_text(encoding="ascii").strip()
    out = run(build_tool("apksigner"), "verify", "-v", "--print-certs", "--min-sdk-version", "26", str(apk))
    if "Verified using v2 scheme (APK Signature Scheme v2): true" not in out or \
            "Verified using v3 scheme (APK Signature Scheme v3): true" not in out:
        raise SystemExit("firma incompleta: se requieren los esquemas v2 y v3\n" + out)
    lineage = run(build_tool("apksigner"), "lineage", "--in", str(apk), "--print-certs").lower()
    digests = re.findall(r"sha-256 digest: ([0-9a-f]{64})", lineage)
    if digests[:1] != [LEGACY_CERT] or digests[-1:] != [release_cert]:
        raise SystemExit("la línea de rotación no va de la clave publicada a la de release\n" + lineage)
    badging = run(build_tool("aapt2"), "dump", "badging", str(apk))
    if "application-debuggable" in badging:
        raise SystemExit("el APK es depurable; compila con assembleRelease")
    if "uses-permission" in badging:
        raise SystemExit("el APK declara permisos de Android:\n" + "\n".join(
            line for line in badging.splitlines() if "uses-permission" in line))
    return re.search(r"versionName='([^']+)'", badging).group(1)


def sign() -> None:
    p = paths()
    for key in ("legacy", "release", "password", "lineage"):
        if not p[key].is_file():
            raise SystemExit(f"Falta {p[key]}. Ejecuta primero: python android/sign_release.py init")
    if not UNSIGNED.is_file():
        raise SystemExit("Falta el APK sin firmar. Ejecuta: cd android; gradlew assembleRelease")
    with tempfile.TemporaryDirectory(prefix="allen-apk-") as tmp:
        aligned, signed = Path(tmp) / "aligned.apk", Path(tmp) / "signed.apk"
        run(build_tool("zipalign"), "-f", "4", str(UNSIGNED), str(aligned))
        run(build_tool("apksigner"), "sign",
            "--ks", str(p["legacy"]), "--ks-key-alias", LEGACY_ALIAS, "--ks-pass", "pass:android",
            "--next-signer", "--ks", str(p["release"]), "--ks-key-alias", RELEASE_ALIAS,
            "--ks-pass", f"file:{p['password']}",
            "--lineage", str(p["lineage"]), "--rotation-min-sdk-version", ROTATION_MIN_SDK,
            "--v4-signing-enabled", "false", "--out", str(signed), str(aligned))
        version = verify(signed)
        shutil.copy2(signed, PUBLISHED)
    digest = hashlib.sha256(PUBLISHED.read_bytes()).hexdigest()
    PUBLISHED.with_name(PUBLISHED.name + ".sha256").write_text(f"{digest}  {PUBLISHED.name}\n", encoding="ascii")
    print(f"publicado {PUBLISHED.relative_to(ROOT)} ({version}, {PUBLISHED.stat().st_size / 1_000_000:.1f} MB)")
    print(f"SHA-256 del APK: {digest}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["init"]:
        init()
    elif sys.argv[1:] == ["verify"]:
        print(verify(PUBLISHED))
    elif not sys.argv[1:]:
        sign()
    else:
        raise SystemExit(__doc__)
