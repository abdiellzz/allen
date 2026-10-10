# ALLEN

**Tutor educativo local, privado y offline.**

Release estable: **1.2.1**

ALLEN combina aprendizaje guiado, quizzes, tarjetas, planes de estudio, cursos creados por docentes, progreso local, backups, recuperación y una IA local opcional. La aplicación principal funciona en el dispositivo y no requiere una cuenta cloud.

## Primera experiencia móvil (experimental)

La rama de evolución móvil incorpora una **PWA instalable** en `public/mobile/`:
curso inicial de fracciones, diagnóstico, práctica guiada, tutor estructurado y
progreso offline por perfil. No es un APK; no incluye IA generativa móvil ni cobros.

Ejecutar `python -m http.server 8081 --bind 127.0.0.1 --directory public` y abrir
`http://localhost:8081/mobile/`. Esperar que el curso esté guardado antes de desconectar.
Para Android se requiere servir la PWA por HTTPS.

Consulta [Arquitectura, uso y límites de la PWA](docs/MOBILE.md).
La aplicación de escritorio y sus licencias continúan funcionando por separado.

## Qué contiene este repositorio

| Ruta | Propósito |
| --- | --- |
| `backend/` | FastAPI, SQLite, cursos, aprendizaje, seguridad y licencias |
| `frontend/` | Interfaz local de ALLEN |
| `data/library/` | Biblioteca incluida |
| `distribution/` | Build Windows, instalador, Portable y eliminador |
| `tools/` | Herramientas administrativas como License Manager |
| `public/` | Landing estática publicada por Vercel |
| `tests/` | Pruebas Python, E2E y JavaScript |
| `docs/` | Documentación oficial |

## Instalar ALLEN

La forma recomendada para usuarios es el instalador Windows generado por GitHub Actions:

`ALLEN-1.2.1-Setup-Windows-x64.exe`

También existe un Portable:

`ALLEN-1.2.1-Portable-Windows-x64.zip`

**Ninguno requiere Python instalado.**

Consulta [Instalación y primera ejecución](docs/INSTALLATION.md).

## Licencia offline

ALLEN 1.2.1 requiere una licencia firmada para la instalación comercial.

```text
ALLEN muestra Machine ID
        ↓
administrador genera .license
        ↓
ALLEN verifica firma + equipo + fechas
        ↓
aplicación activada
```

La cantidad de perfiles dentro de una instalación no está limitada por la licencia.

La clave privada de emisión **nunca** debe entrar al repositorio ni distribuirse con ALLEN.

Consulta [Licenciamiento offline](docs/LICENSING.md).

## Funciones principales

- Tutor y chat con modelo local opcional.
- Quizzes y ejercicios.
- Flashcards y repaso espaciado.
- Plan Allen.
- Aventuras educativas.
- Biblioteca local.
- Progreso y Evidence of Mastery.
- Teacher Studio.
- Importación PDF/TXT/Markdown.
- Course Quality.
- Question Bank.
- Curriculum Graph.
- Diagnóstico inicial.
- Versionado y Course Diff.
- Exportación/importación `.allenpack`.
- Backups y Recovery.
- Modo Feria.

Consulta [Tutorial completo de uso](docs/USAGE_GUIDE.md).

## Teacher Studio

```text
Material docente
  ↓
Borrador local
  ↓
Teacher Review
  ↓
Course Quality
  ↓
Publicar
  ↓
Curso para estudiantes
```

Consulta [Teacher Studio](docs/TEACHER_STUDIO.md).

## Desarrollo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python server.py --open
```

En Windows usa el Python de `.venv\Scripts`.

Pruebas:

```bash
python -m pytest -q
node --test tests/*.mjs
```

Consulta [Guía de desarrollo](docs/DEVELOPMENT.md).

## IA local

ALLEN puede conectarse a un servidor compatible con llama.cpp exclusivamente por loopback, por ejemplo:

`http://127.0.0.1:8080`

ALLEN no incluye modelos GGUF ni los descarga automáticamente.

## Privacidad

La aplicación principal:

- escucha en `127.0.0.1`;
- guarda SQLite localmente;
- no necesita telemetría;
- no publica conversaciones;
- mantiene el modelo local fuera del repositorio.

No subas bases SQLite, modelos, secretos, licencias emitidas o información real de estudiantes.

Consulta [Seguridad](SECURITY.md).

## Landing pública

`public/` es una página estática independiente desplegable en Vercel.

No contiene ni publica:

- FastAPI;
- SQLite;
- la IA local;
- datos de usuarios;
- la clave privada de licencias.

## Documentación

Empieza por [docs/INDEX.md](docs/INDEX.md).

Documentos clave:

- [Instalación](docs/INSTALLATION.md)
- [Tutorial de uso](docs/USAGE_GUIDE.md)
- [Arquitectura](docs/ARCHITECTURE.md)
- [Desarrollo](docs/DEVELOPMENT.md)
- [Licencias](docs/LICENSING.md)
- [Distribución Windows](docs/WINDOWS_DISTRIBUTION.md)
- [Operación y recuperación](docs/OPERATIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Teacher Studio](docs/TEACHER_STUDIO.md)
- [Learning Intelligence](docs/LEARNING_INTELLIGENCE.md)
- [Reliability Core](docs/RELIABILITY_CORE.md)
- [Modo Feria](docs/FAIR_MODE.md)
- [CHANGELOG](CHANGELOG.md)

## Estado de plataforma

Objetivo principal: **Windows 10/11 x64**.

El código fuente puede ejecutarse en Linux para desarrollo, pero la distribución comercial validada se construye para Windows.

---

ALLEN · aprendizaje local, privado y diseñado para seguir funcionando sin depender de una nube.
