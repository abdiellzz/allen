# Auditoría y limpieza del repositorio

Auditoría realizada el 2 de octubre de 2026 sobre la rama `maintenance/repo-cleanup`. El árbol ya contenía cambios locales staged/unstaged y archivos nuevos del trabajo en curso; se conservaron sin sobrescribirlos.

## Clasificación

| Clase | Rutas / hallazgos | Decisión |
| --- | --- | --- |
| Necesarios | `backend/`, `frontend/`, `data/`, `config/`, launchers, `requirements*.txt`, `tests/`, `installer/`, `packaging/`, `licensing/`, `tools/`, `licenses/` | Conservar; contienen código, dependencias o soporte activo |
| Reutilizables | `DOCUMENTACION_TECNICA_ALLEN.md`, `DOCUMENTACION_DISTRIBUCION_AUDITORIA.md`, guías, `FAIR_MODE.md`, `SECURITY.md`, `SPEECH_CHALLENGE_ALLEN.md` | Conservar y enlazar como documentación especializada |
| Generados | `build/` (aprox. 499 MB; objetos Nuitka de intento abortado), `dist/` (aprox. 85 MB; runtime llama.cpp), `__pycache__/`, `.pytest_cache/`, `logs/` | `build/` está documentado como incompleto; las carpetas de caché son regenerables. La eliminación física fue rechazada por la política automática de ejecución, por lo que se conservaron. Se ampliaron reglas de ignore. `dist/` y logs se conservan por su valor en diagnóstico y distribución de prueba. |
| Temporales / desconocidos | `tmp/` (aprox. 14 MB; contiene evaluaciones, logs y renders), `.codex-finalizer/`, `.codex-pitch-build/` | Conservar; incluyen fuentes/resultados no versionados y no se determinó que sean prescindibles |
| Entregables | `output/` con PDF técnico y cuatro presentaciones | Conservar; no son basura de build de la aplicación |
| Vacíos / exploratorios | `android/`, `legacy/` | Mantener sus ubicaciones; Android no tiene archivos y `legacy/` no contiene implementación en este checkout |
| Modelos | `models/.gitkeep`; no se encontraron GGUF en el repositorio | Mantener placeholder; pesos excluidos por `.gitignore` |

## Ramas y preservación

La rama histórica `backup/pre-website-split-20260927` ya existía. Git no incorpora cambios sin commit en una rama de respaldo; por eso no se creó una rama de respaldo que aparentara incluirlos. Se creó `maintenance/repo-cleanup` y no se hizo commit ni push.

## Duplicados y dependencias

No se eliminaron dependencias. Se confirmó un asset idéntico por SHA-256: `frontend/assets/allen.svg` y `public/assets/allen.svg`; se conserva porque la app y el sitio estático lo consumen en despliegues distintos. No se confirmó otro duplicado entre fuentes/datos (se excluyeron artefactos de build, cachés y salida). Las dependencias activas están fijadas en `requirements.txt`; las de pruebas y build están separadas. No existe `package.json`; Node solo se necesita para tests y utilidades.

## Secretos

La búsqueda superficial de nombres y patrones comunes no encontró archivos `.env` ni claves privadas en las rutas revisadas. `licensing/development_public_key.pem` es una clave pública. `tools/license_generator/private_keys/` y `*.private.pem` están ignorados. No se ejecutó Gitleaks ni un escáner especializado, y esta revisión no certifica todo el historial Git: revisar el historial con un detector de secretos antes de publicar.

## Documentación y distribución

Se completaron los enlaces locales del README para arquitectura, validación y auditoría. La fuente actual de instalación es `install_allen.ps1`; no está validada como instalador de distribución final y el flujo normal puede requerir llama.cpp/modelo. El script `packaging/build_allen.ps1` e Inno Setup existen, pero el reporte anterior registra un build detenido y no hay `ALLEN_Setup.exe` en `dist/installer/`.

## Validación ejecutada

- JavaScript: 28 pruebas aprobadas, 0 fallidas (`node --test tests/*.mjs`).
- Python: 21 aprobadas, 0 fallidas y 10 subcasos aprobados; 2 warnings deprecados. El historial de los cinco subcasos iniciales y su comparación con `main` está en [VALIDATION.md](VALIDATION.md).
- Flujo básico: servidor, health check, frontend Feria y chat local verificados; ver [VALIDATION.md](VALIDATION.md).
- No se relanzó el launcher, instalador ni modelo para evitar interferir con servicios ya iniciados por el usuario.
