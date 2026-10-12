# AGENTS.md — ALLEN

Guía para agentes de código que trabajan en este repositorio. Las reglas específicas de la APK
están en [android/AGENTS.md](android/AGENTS.md) y prevalecen dentro de `android/`.

## Regla principal

**Un compañero trabaja en paralelo; nunca modificar archivos fuera del alcance de la tarea y reportar si algo requiere tocarlos.**

- Antes de editar, define qué rutas cubre la tarea. Si un cambio necesario cae fuera, no lo hagas:
  descríbelo (archivo, motivo y cambio propuesto) para coordinarlo.
- No reformatees, reordenes ni "limpies" código ajeno a la tarea.
- Antes de cada commit ejecuta la skill `scope-check`.
- No hagas `push` ni abras PR sin confirmación explícita.
- Commits con autor `sebas <sebastiaenriquerivera12@gmail.com>`, mensajes en español con prefijo
  convencional (`feat:`, `fix:`, `docs:`, `chore:`, `style:`) y **sin** líneas `Co-Authored-By`.

## Qué es ALLEN

Tutor educativo **local, privado y offline**. Funciona en el dispositivo sin cuenta en la nube.

Funciones: tutor/chat con IA local opcional (llama.cpp en `127.0.0.1:8080`), quizzes, simulacros,
examen final, flashcards con repaso espaciado, Plan Allen, aventuras, biblioteca local, progreso y
Evidence of Mastery, diagnóstico inicial, Teacher Studio (PDF/TXT/Markdown → borrador → Teacher
Review → Course Quality → publicar), Question Bank, Curriculum Graph, versionado y Course Diff,
Course Packs `.allenpack`, backups cifrados y Recovery, licencias offline Ed25519 y Modo Feria.

La mascota "Allen" tiene más de 30 ilustraciones SVG en `frontend/assets/`.

- Repositorio: `github.com/abdiellzz/allen` (privado).
- Versión: la que diga `VERSION` (hoy **1.2.4**). El `README.md` aún dice 1.2.1.
- Plataforma comercial validada: Windows 10/11 x64. Android existe como demo (APK).

## Stack

- **Backend:** Python 3.13 recomendado, FastAPI + Uvicorn, SQLite (WAL). Escucha solo en
  `127.0.0.1:8787`.
- **Frontend:** HTML/CSS/JS sin framework ni build de Node. FastAPI sirve los módulos ES directamente.
- **Dependencias:** fastapi, uvicorn, httpx, qrcode, pypdf, cryptography (`requirements.txt`).
  Desarrollo: pytest, playwright, ruff, bandit, pip-audit (`requirements-dev.txt`); build:
  pyinstaller (`requirements-build.txt`).
- **CI (GitHub Actions):** pip-audit, compileall, Ruff, Bandit SAST, pytest con Playwright real y
  `node --test`. Build Windows y License Manager en workflows aparte.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `server.py` | Arranque local → `backend/app.py` (`create_app`) en `127.0.0.1:8787` |
| `backend/` | API y lógica: `database`, `migrations`, `backup`, `backup_crypto`, `recovery`, `licensing`, `security`, `course_builder`, `course_quality`, `course_versioning`, `curriculum_graph`, `question_bank`, `learning_engine`, `learning_intelligence`, `study_planner`, `tutoring`, `ai`, `local_model`, `fair`, `library`, `time_utils`, `version` |
| `frontend/` | `index.html`, `fair.html`, `app.js` (SPA, navegación por `data-page`), `components/*.js`, `styles/app.css` y `styles/v2.css` (capas v2/v3/v4), `assets/` (mascota y SVG) |
| `android/` | APK de demostración (ver abajo y `android/AGENTS.md`) |
| `distribution/` | PyInstaller, instalador Inno Setup, Portable y eliminador para Windows |
| `tools/` | License Manager (clave privada fuera del repo) |
| `public/` + `vercel.json` | Landing estática en Vercel; no contiene la app ni datos |
| `data/library/` | Biblioteca incluida |
| `config/` | Configuración pública (clave pública de licencias) |
| `tests/` | pytest, E2E con Playwright (`tests/e2e_server.py`) y pruebas JS (`*.mjs`) |
| `docs/` | Documentación oficial; empieza por `docs/INDEX.md` |

Páginas de la SPA (`data-page`): Inicio, Aprender, Cursos, Teacher Studio, Método Allen, Plan Allen,
Practicar, Aventura, Perfil, Quiz, Matemáticas, Biblioteca, Tarjetas, Progreso, Docente, Guardado,
Configuración, Privacidad. Modos de trabajo: Estudiante / Profesor (`data-workspace-mode`).

## Comandos

Windows PowerShell (no hay `.venv` versionado; créalo si falta):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe server.py --open      # abre http://127.0.0.1:8787 con token de acceso
```

`python server.py` usa la base real de `%LOCALAPPDATA%\ALLEN`, exige licencia, token de apertura de un
solo uso y PIN docente. Para pruebas o capturas usa el servidor E2E con una base temporal:

```powershell
$env:ALLEN_DB_PATH="$env:TEMP\allen-dev.sqlite3"; python -m uvicorn tests.e2e_server:app --host 127.0.0.1 --port 8787
```

Pruebas y verificaciones (las mismas que CI):

```bash
python -m pytest -q
node --test tests/*.mjs
python -m compileall -q backend tools distribution
python -m ruff check backend tools distribution tests --select E9,F63,F7,F82
python -m bandit -r backend tools distribution -ll -q
python -m pip_audit -r requirements.txt
```

Build Windows (con Inno Setup): `.\distribution\build_windows.ps1`.
APK: skill `apk-build`.

## Historial de auditorías y seguridad

| Versión | Fecha | Resumen |
| --- | --- | --- |
| 1.2.1 | 2026-10-07 | Secreto efímero por ejecución con cookie HttpOnly/SameSite=Strict, pip-audit y Dependabot, Actions fijadas por SHA, cabeceras COOP/CORP/X-Frame-Options. **Auditoría técnica** de esta versión: instalador roto por importación a un archivo eliminado, respuestas de exámenes/quizzes/simulacros expuestas por la API, restore de backup que cruzaba conversaciones entre estudiantes, bug de zona horaria en repasos, plan de estudio con fecha 9999-12-31 que bloqueaba el servidor y sin separación real de roles. |
| 1.2.2 | 2026-10-08 | Corrección de los críticos: launcher con smoke test, evaluaciones sin respuestas antes de enviar, PIN docente con scrypt + sesión HttpOnly + rate limiting, Modo Feria aislado, token de apertura de un solo uso, backups AES-256-GCM, progreso y simulacros endurecidos, backup/restore con validación de esquema y claves foráneas, UTC centralizado (`time_utils`), WAL, planes limitados a 365 días, CSP corregida. |
| 1.2.3 | 2026-10-08 | Segunda auditoría: los 5 críticos y 7 altos revalidados como corregidos (incluidos zona horaria y CSP). Caché de biblioteca y calidad pedagógica de distractores. |
| 1.2.4 | 2026-10-08 | Protección contra suplantación del puerto 8787, `/api/health` mínimo, PIN obligatorio antes del uso comercial, límites para Course Packs maliciosos, PDF cifrado rechazado, Bandit en CI. |
| 1.2.4-android-demo.1 | 2026-10-11 | **Parche de seguridad de la APK:** el APK publicado era depurable y estaba firmado con la clave de depuración (datos de niños legibles por USB); ahora es release no depurable con clave propia y rotación v3 (actualiza sin perder progreso). El APK ya no incluye Python ni el código del backend (25,6 → 3,4 MB), CSP estricta, sin copia en la nube ni transferencia entre dispositivos, WebView limitada a sus assets, textos escapados y Gradle verificado por hash. |

Pendientes estructurales reconocidos (no son fallos abiertos): dividir `backend/app.py` en routers,
modularizar `frontend/app.js`, optimizar Teacher Analytics, FTS5 para biblioteca, firma Authenticode,
lockfiles con hashes y reglas de rama/CodeQL en GitHub.

Detalle: `docs/SECURITY_AUDIT_2026-10-07.md`, `docs/SECURITY_AUDIT_2026-10-08.md`,
`docs/SECURITY_AUDIT_RECHECK_2026-10-08.md`, `docs/SECURITY_AUDIT_APK_2026-10-11.md`, `SECURITY.md` y
`CHANGELOG.md`.

Reglas de seguridad al editar:

- Nunca subir `*.sqlite3`, `*.gguf`, `.env`, `*.license`, `license_private_key.pem` ni datos reales
  de estudiantes.
- No debilitar CSP, autenticación docente, límites de importación ni el bind a loopback.
- Los informes al cliente no deben incluir rutas, nombres de funciones, ramas ni hashes (skill
  `client-report`).

## APK de Android (demo)

WebView que muestra la experiencia educativa móvil dentro del teléfono, sin servidor y sin Internet:

```text
WebView (assets del APK, https://appassets.androidplatform.net)
  └── public/mobile/ → cursos, diagnóstico, práctica, tarjetas y progreso en IndexedDB
        └── android-extras.mjs → recorrido guiado y «Actualizar ALLEN» (solo en la APK)
```

- Sin permisos de Android, sin Python ni backend, sin copia en la nube ni transferencia entre
  dispositivos. CSP estricta inyectada por el builder.
- Se publica **solo** como release no depurable: `python android/build_web_assets.py`,
  `gradlew assembleRelease` y `python android/sign_release.py` (clave de release fuera del repo con
  rotación v3 desde la clave de depuración que firmó hasta 1.2.4-android-demo).
- `android/app/src/main/assets/www/` es generado e ignorado por git. No editarlo a mano.
- APK publicado: `android/release/ALLEN-demo-android.apk` (Android 8.0+), con su SHA-256 y el del
  certificado al lado.
- Reglas y alcance: `android/AGENTS.md`. Detalle: `android/README.md`.

## Skills del repositorio

En `.agents/skills/`:

| Skill | Uso |
| --- | --- |
| `apk-build` | Regenerar assets web, compilar el APK release y firmarlo |
| `apk-review` | Capturas 375×812 claro/oscuro de la APK, desbordes y errores de CSP |
| `scope-check` | Verificar que el diff no sale de las rutas permitidas |
| `client-report` | PDF profesional para el cliente con hallazgos o correcciones |
