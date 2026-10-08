# Seguridad y privacidad

ALLEN es una aplicación local. La seguridad del proyecto depende tanto del código como de mantener secretos y datos reales fuera del repositorio.

## Datos que nunca deben entrar a Git

No subas:

- `license_private_key.pem`;
- archivos `*.license` emitidos a clientes;
- `.env`;
- tokens o credenciales;
- bases `*.sqlite3`;
- backups reales;
- modelos `*.gguf`;
- documentos privados de estudiantes o instituciones;
- logs con información sensible.

Las reglas principales ya están en `.gitignore`, pero el desarrollador debe revisar cada commit.

## Licenciamiento

ALLEN contiene únicamente la **clave pública** Ed25519.

La **clave privada**:

- pertenece exclusivamente al administrador de licencias;
- no debe subirse a GitHub;
- no debe incluirse en el instalador;
- no debe incluirse en el Portable;
- no debe incrustarse en `ALLEN-License-Manager.exe`;
- debe conservarse con backup cifrado.

Si la clave privada se filtra, hay que considerar comprometida la capacidad de emitir licencias y rotar el par de claves en una release posterior.

## Aplicación local

El servidor de ALLEN escucha solamente en:

`127.0.0.1:8787`

Además, las instalaciones normales usan un secreto aleatorio por ejecución. El launcher abre el navegador con ese secreto una sola vez y ALLEN establece una cookie de sesión `HttpOnly` + `SameSite=Strict`. Esto evita que otro proceso local pueda leer `/api/bootstrap` y obtener el token de mutación simplemente por conocer el puerto.

La conexión al modelo local debe permanecer igualmente en loopback.

No abras estos servicios a la LAN o Internet sin un diseño de autenticación, autorización y transporte adecuado.

## Controles actuales

Entre las defensas del producto:

- validación Host/Origin;
- bloqueo de solicitudes cross-site;
- token para mutaciones;
- CSP;
- `X-Content-Type-Options`;
- `Referrer-Policy`;
- entradas acotadas;
- SQL parametrizado;
- Markdown sin HTML activo;
- sin ejecución de código del estudiante;
- logs sin conversaciones;
- licencia firmada Ed25519;
- secreto efímero de acceso local por ejecución;
- auditoría de dependencias con `pip-audit` en CI;
- GitHub Actions fijadas a SHAs inmutables y token del workflow con `contents: read`.

Estos controles reducen riesgo; no convierten ALLEN en un sistema certificado.

## Datos locales

Instalación:

`%LOCALAPPDATA%\ALLEN`

Portable:

`ALLEN-Data`

Los perfiles no son cuentas de seguridad. Personas que compartan la misma cuenta de Windows pueden tener acceso a los mismos datos locales.

## Backups y snapshots

Los backups externos quedan bajo responsabilidad de quien los exporta.

No subas backups reales al repositorio ni los uses como fixtures de pruebas.

## Landing Vercel

`public/` es estática.

`vercel.json` publica únicamente esa superficie y añade cabeceras defensivas.

La landing no debe contener:

- claves;
- tokens;
- SQLite;
- endpoints privados;
- datos reales.

## Dependencias

Antes de una release:

1. instala desde los requirements versionados;
2. ejecuta pruebas;
3. revisa cambios de dependencias;
4. construye desde CI limpio;
5. distribuye artefactos provenientes del workflow/release esperado.

## Reportar una vulnerabilidad

No publiques secretos, claves privadas, datos personales ni una prueba explotable contra una instalación real en una issue pública.

Contacta al propietario del repositorio de forma privada y aporta:

- versión;
- componente afectado;
- pasos mínimos para reproducir;
- impacto;
- mitigación conocida, si existe.
