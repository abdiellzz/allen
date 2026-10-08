# Auditoría de seguridad — ALLEN 1.2.4

**Fecha:** 8 de octubre de 2026

## Superficie revisada

- servidor local FastAPI;
- launcher Windows;
- autenticación local y PIN docente;
- licensing;
- SQLite y backups;
- Teacher Studio / Course Packs / PDF;
- Modo Feria;
- frontend/CSP;
- CI/CD y dependencias.

## Hallazgos cerrados en esta revisión

### Suplantación local del puerto 8787

El launcher anteriormente podía interpretar un HTTP 200 como una instancia válida. Ahora cada proceso genera un `instance_id` aleatorio y el launcher exige que /api/health devuelva exactamente ese valor antes de abrir el navegador.

### Configuración inicial del PIN

En una instalación comercial, el producto queda bloqueado después de activar licencia hasta configurar un PIN docente. Esto reduce el riesgo de que un usuario estudiante configure primero el secreto administrativo.

### Privilegios destructivos/globales

- borrar perfiles exige profesor;
- cambiar configuración global de IA, historial, retención o performance exige profesor;
- preferencias visuales siguen disponibles sin elevar privilegios.

### Course Packs / estructuras manipuladas

Se limitan:

- 1.5 MB de JSON estructural;
- profundidad máxima 10;
- 20 unidades;
- 40 temas por unidad;
- rutas, preguntas, flashcards y examen;
- longitud de strings y número total de nodos.

### PDF

- máximo 8 MB;
- máximo 250 páginas;
- PDF cifrado rechazado;
- texto por página limitado;
- texto total limitado.

### SAST

CI ejecuta:

- pip-audit;
- compileall;
- Ruff;
- Bandit;
- pytest/E2E;
- pruebas frontend.

## Defensa en profundidad ya presente

- loopback únicamente;
- TrustedHost;
- validación Origin/Sec-Fetch-Site;
- secreto de lanzamiento one-time;
- cookie HttpOnly/SameSite=Strict;
- token de mutación;
- PIN docente con scrypt y rate limiting;
- CSP y cabeceras anti-frame/cross-origin;
- SSRF restringido a loopback para IA local;
- SQLite parametrizado;
- WAL;
- backups cifrados AES-256-GCM;
- licencias Ed25519;
- clave privada de licencias cifrada para emisión;
- workflows fijados a SHA;
- Dependabot.

## Riesgos que no deben describirse como eliminados

ALLEN no puede impedir que un administrador local con capacidades de reverse engineering modifique el binario. Tampoco sustituye aislamiento de cuentas de Windows: los perfiles educativos no son identidades OS independientes.

La seguridad de una distribución comercial también mejora significativamente al firmar los ejecutables con Authenticode.
