# Auditoría de ciberseguridad — ALLEN 1.2.x

**Fecha:** 7 de octubre de 2026  
**Alcance:** aplicación local, licenciamiento, Teacher Studio, backups, landing y CI/CD.

## Threat model

ALLEN está diseñado como aplicación local de escritorio. Se consideran amenazas relevantes:

- página web externa intentando hablar con localhost;
- proceso local no autorizado intentando leer/modificar ALLEN;
- PDF, Course Pack, backup o biblioteca manipulados;
- licencia alterada o copiada;
- licencia falsa presentada al administrador para renovación;
- filtración accidental de la clave privada;
- dependencia Python vulnerable;
- compromiso de supply chain en GitHub Actions;
- exposición accidental de la app local en Vercel.

No se considera defendible frente a un atacante con control administrativo total del equipo y capacidad de parchear el binario de ALLEN.

## Hallazgos corregidos

### Alto — API local accesible a otros procesos locales

Antes del hardening, un proceso local podía consultar `/api/bootstrap`, obtener el token de mutación y usar la API.

Corrección:

- secreto criptográfico aleatorio por ejecución;
- launcher entrega el secreto al navegador;
- cookie de sesión `HttpOnly` + `SameSite=Strict`;
- la API rechaza clientes que no pasaron por el launcher;
- `/api/health` permanece sin autenticación para readiness y solo expone estado técnico limitado.

### Alto — renovación de una licencia sin verificar la licencia anterior

El License Manager leía el payload de la licencia previa pero no verificaba su firma antes de crear la renovación.

Un archivo manipulado presentado al operador podía acabar siendo firmado por el generador.

Corrección:

- toda licencia cargada para renovación debe tener firma Ed25519 válida;
- la firma debe corresponder al par de claves del operador;
- se valida schema, Machine ID y fechas antes de permitir renovar;
- pruebas cubren modificación y firma con clave ajena.

### Alto/Medio — dependencias criptográficas y PDF desactualizadas

Se actualizaron:

- `pypdf` a 6.19.0;
- `cryptography` a 50.0.2.

La aplicación procesa PDFs proporcionados por usuarios, por lo que vulnerabilidades de consumo excesivo de recursos en el parser son especialmente relevantes.

CI ejecuta ahora `pip-audit`.

### Medio — GitHub Actions con referencias movibles y permisos implícitos

Corrección:

- acciones oficiales fijadas por SHA;
- `GITHUB_TOKEN` limitado a `contents: read`;
- Dependabot revisa pip y GitHub Actions semanalmente.

### Medio — permisos de la clave privada en Linux/macOS

El License Manager fuerza `0600` sobre el PEM privado en sistemas POSIX.

Esto no protege frente a malware ejecutándose como el mismo usuario, pero evita exposición accidental a otros usuarios locales.

## Controles revisados y considerados adecuados

### Web/localhost

- bind a `127.0.0.1`;
- `TrustedHostMiddleware`;
- validación de `Origin`;
- bloqueo `Sec-Fetch-Site: cross-site`;
- token para operaciones mutables;
- CSP;
- `X-Content-Type-Options`;
- `Referrer-Policy`;
- `Permissions-Policy`;
- `X-Frame-Options`;
- COOP/CORP;
- cache deshabilitada para respuestas de la aplicación.

### IA local / SSRF

`ai_server` solo permite HTTP a:

- `127.0.0.1`;
- `localhost`;
- `::1`;

requiere puerto explícito, no admite credenciales, query/fragment ni redirecciones, y `httpx` usa `trust_env=False`.

### SQLite

- consultas de datos parametrizadas;
- foreign keys activadas;
- `secure_delete=ON`;
- snapshots mediante API de backup SQLite;
- nombres de snapshots validados antes de restaurar.

### Frontend / XSS

El contenido dinámico revisado pasa por funciones de escape y el renderer Markdown escapa HTML crudo. La CSP no permite scripts inline/remotos.

### Vercel

Solo `public/` se despliega. Backend, SQLite, configuración local, herramientas y secretos quedan fuera mediante configuración de build/ignore.

## Riesgos residuales

### DRM offline

Un atacante con control del binario puede parchear comprobaciones de licencia. Ed25519 protege autenticidad del archivo, no evita reverse engineering.

### Reloj offline

La detección de rollback depende de estado local. Borrar/restaurar todo el estado puede reducir su eficacia. Una garantía fuerte requeriría tiempo confiable externo o servidor local institucional.

### Clave privada sin HSM

El PEM permanece como secreto en disco. `0600` ayuda, pero para operación comercial seria conviene almacenarlo en:

- gestor de secretos local cifrado;
- volumen cifrado;
- hardware token/HSM si el volumen de negocio lo justifica.

### Archivos complejos

PDF, backup y Course Pack siguen siendo entradas no confiables. Hay límites de tamaño y validaciones, pero un parser complejo nunca debe considerarse libre de futuras vulnerabilidades.

### Perfiles

Los perfiles educativos no son cuentas autenticadas. Una persona con acceso a la misma sesión de Windows puede acceder a los datos locales. Esto es una decisión de producto, no aislamiento multiusuario.

## Recomendaciones siguientes

1. Mantener Dependabot y `pip-audit` verdes.
2. Proteger `main` exigiendo PR + checks, si la configuración de GitHub del plan lo permite.
3. Considerar firma Authenticode para instalador/EXE antes de distribución comercial amplia.
4. Mantener la clave privada fuera de Downloads y repositorios; usar almacenamiento cifrado.
5. Ejecutar smoke tests de seguridad en una VM Windows limpia por release.
6. Revisar PDFs y Course Packs como contenido no confiable incluso si provienen de una institución.
7. Considerar CodeQL/secret scanning si están disponibles para el repositorio privado.
