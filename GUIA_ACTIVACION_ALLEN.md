# Activación institucional offline de ALLEN

## Flujo del equipo cliente

1. `ALLEN_Setup.exe` copia ALLEN, el runtime llama.cpp y el GGUF; el registrador crea Installation ID UUIDv4 y fingerprint local, escribe el registro HKLM y genera `%PROGRAMDATA%\ALLEN\activation-request.allen`.
2. El administrador envía ese archivo al emisor autorizado de licencias por un canal institucional.
3. El emisor firma una licencia Ed25519 con el Installation ID y fingerprint recibidos y la devuelve al administrador.
4. El administrador guarda el archivo firmado en `%PROGRAMDATA%\ALLEN\license.allen`.
5. Al abrir `ALLEN.exe`, la aplicación valida el registro, la ruta oficial, el hash del fingerprint, la firma Ed25519, el equipo, la edición, la expiración y el manifest antes de iniciar llama-server.

El instalador genera la solicitud, pero no puede firmar una licencia válida por sí mismo: la clave privada de producción debe permanecer en el sistema privado del emisor. La instalación queda preparada hasta recibir el `license.allen` firmado.

## Herramientas privadas del emisor

Las herramientas están en `tools/license_generator/allen_licensing.py`. No se incluyen en `dist/` ni en el Setup.

Crear una clave Ed25519 cifrada en el equipo/servicio privado del emisor:

```powershell
python tools\license_generator\allen_licensing.py generate-key --private C:\ruta-privada\allen-ed25519.pem --public licensing\release_public_key.pem
```

Firmar una licencia por solicitud de equipo:

```powershell
python tools\license_generator\allen_licensing.py issue-license --private C:\ruta-privada\allen-ed25519.pem --request activation-request.allen --customer "Colegio ABC" --edition institutional --issued 2026-09-24 --expires 2027-09-24 --output license.allen
```

Para una licencia sin vencimiento, omite `--expires`. Antes de emitir licencias institucionales, el build de distribución debe compilar el hash de la clave pública de producción en `licensing/trust_anchor.py` y empaquetar su PEM público. La clave de desarrollo que existe en la máquina local **no es para licencias de clientes**.

## Varias computadoras, renovación y migración

- Cada equipo debe emitir su propia solicitud y recibir una licencia con `max_devices=1`; para diez equipos se gestionan diez activaciones.
- Para renovar, el emisor genera una nueva licencia para la instalación actual; el administrador reemplaza `license.allen`. El progreso y la base de datos quedan en ProgramData y no se borran por expiración.
- Al migrar, se genera una nueva solicitud en la computadora nueva y el emisor autoriza esa huella. En un equipo completamente offline, una licencia previamente emitida no puede revocarse a distancia: para impedir el uso posterior en el equipo antiguo debe retirarse físicamente o la licencia antigua debe tener una expiración que ya haya pasado. El formato local evita clonar la activación a otra huella, pero no permite revocación instantánea offline.

## Huella técnica

El fingerprint normaliza `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` y `HKLM\SYSTEM\CurrentControlSet\Control\SystemInformation\ComputerHardwareId` (si Windows entrega una lista, ordena sus valores), concatena esos dos datos y guarda solo SHA-256. No usa MAC, nombre de usuario ni serial de disco. Esos identificadores originales no se escriben en los datos de ALLEN.

## Firmar el manifest de distribución

Después del build, la herramienta `sign-manifest` calcula hashes SHA-256 de los ejecutables, DLL del runtime, frontend y datos críticos, y firma el documento con la misma clave Ed25519. El runtime contiene únicamente el ancla pública compilada. No incluir en el manifest logs, progreso, licencia, base de datos o preferencias.

```powershell
python tools\license_generator\allen_licensing.py sign-manifest --private C:\ruta-privada\allen-ed25519.pem --root dist\ALLEN --version 1.0.0 --files ALLEN.exe allen_backend.exe allen_ai.exe runtime/llama/llama-server.exe
```
