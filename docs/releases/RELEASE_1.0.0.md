# ALLEN 1.0.0 — Release estable

**Fecha:** 7 de octubre de 2026  
**Canal:** estable  
**Versión:** 1.0.0

## Qué representa esta versión

ALLEN 1.0.0 es la primera versión que se considera estable para uso local de escritorio y laptop. La release consolida la experiencia educativa, Teacher Studio, Learning Intelligence, Reliability Core y el sistema visual final.

## Requisitos

- Windows 10/11 recomendado.
- Python 3.11 o superior.
- Aproximadamente 1 GB libre para la aplicación, entorno y datos; los modelos GGUF requieren espacio adicional.
- Internet solo para la instalación inicial de dependencias. El uso normal puede ser local.
- llama.cpp y un modelo GGUF son opcionales; sin ellos, las actividades deterministas y el modo demo siguen disponibles.

## Instalación recomendada

1. Descarga el código de esta versión.
2. Ejecuta `install_allen.bat` para una instalación local o `start_allen.bat` para iniciar desde el repositorio.
3. Abre `http://127.0.0.1:8787`.
4. Si quieres IA generativa local, configura `%LOCALAPPDATA%\ALLEN\local_model.json` a partir de `config/local_model.example.json`.

## Garantías de datos

- La base de datos principal permanece local.
- Las migraciones crean una copia previa cuando corresponde.
- Recovery permite crear y restaurar snapshots.
- Los backups pueden exportarse manualmente.
- Los documentos del usuario, conversaciones y modelos no deben subirse al repositorio.

## Compatibilidad visual validada

- 1920×1080
- 1440×900
- 1366×768
- 900×800
- 640×900
- 390×844

La experiencia principal sigue orientada a escritorio/laptop; las pantallas pequeñas están soportadas para que la interfaz no se rompa y los flujos esenciales sigan siendo utilizables.

## Validación antes de publicar

La release debe cumplir:

- `node --test tests/*.mjs`
- `python -m pytest -q`
- sin overflow horizontal en los viewports cubiertos por E2E;
- flujo de Teacher Studio completo;
- publicación y nueva versión de un curso;
- diagnóstico y ruta del estudiante;
- Recovery local;
- Ctrl/Cmd + K;
- cambio de tema claro/oscuro.

## Archivos de referencia

- `README.md`
- `docs/USAGE_GUIDE.md`
- `docs/TEACHER_STUDIO.md`
- `docs/LEARNING_INTELLIGENCE.md`
- `docs/RELIABILITY_CORE.md`
- `SECURITY.md`
- `CHANGELOG.md`

## Política de versión

ALLEN usa Semantic Versioning:

- **MAJOR**: cambios incompatibles en datos, flujos o contratos.
- **MINOR**: nuevas capacidades compatibles.
- **PATCH**: correcciones y pulido sin romper compatibilidad.
