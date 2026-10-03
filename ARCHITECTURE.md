# Arquitectura de ALLEN

Documento basado en el código del repositorio inspeccionado el 2 de octubre de 2026. Distingue el runtime de desarrollo del pipeline de distribución, que todavía no está validado como release.

## Componentes

```text
Navegador local
  ├─ frontend/                 HTML, CSS y JavaScript ES modules
  └─ HTTP same-origin /api/*
          │
          ▼
FastAPI (server.py, backend/)
  ├─ tutor y actividades      SQLite y data/*.json
  ├─ experiencia Feria        módulos frontend/fair-*.js y API Feria
  └─ IA opcional               HTTP loopback → llama-server → GGUF local
```

El servidor web usa `127.0.0.1:8787`. La integración local de llama.cpp suele usar `127.0.0.1:8080`; el host y puerto se validan como loopback. No se encontró cliente de IA remota en la configuración revisada.

## Estructura

| Ruta | Responsabilidad |
| --- | --- |
| `backend/` | API, base SQLite, tutor, contenidos, seguridad y experiencia Feria |
| `frontend/` | Interfaz clásica y Feria; no requiere bundler para ejecutarse desde fuente |
| `data/` | Catálogos JSON y biblioteca educativa local |
| `config/` | Ejemplos de configuración; no contienen la configuración privada del equipo |
| `scripts/` | Launcher y parada de procesos de desarrollo |
| `packaging/`, `installer/` | Fuentes del launcher compilado y receta Inno Setup; distribución pendiente de validación |
| `licensing/`, `tools/license_generator/` | Verificación y generación de licencias; proteger cualquier clave privada de firma |
| `tests/` | Pruebas Python y JavaScript |
| `public/`, `vercel.json` | Sitio estático público independiente del tutor local |
| `allen_training/` | Dataset y herramientas de entrenamiento opcionales; no necesarios para ejecutar ALLEN |
| `android/` | Preparación documental, sin aplicación Android construible identificada |
| `legacy/` | Directorio de referencia vacío en el checkout auditado |

## Datos y configuración

La aplicación fuente persiste perfiles, preferencias y progreso en SQLite. En Windows la ruta base habitual es `%LOCALAPPDATA%\ALLEN`; `ALLEN_DATA_HOME` y `ALLEN_DB_PATH` permiten cambiarla. La configuración local de llama.cpp se guarda fuera del repositorio en `%LOCALAPPDATA%\ALLEN\local_model.json` y toma como referencia `config/local_model.example.json`.

Los datasets se cargan desde `data/`; la biblioteca admite archivos locales descritos en el README. Los GGUF, bases de datos de usuario, modelos de entrenamiento y credenciales no deben versionarse.

## Inicio

- Desarrollo: crea `.venv`, instala `requirements.txt` y ejecuta `python server.py --open`.
- Launcher Windows: `start_allen.bat` comprueba dependencias, el estado de IA y luego delega en `scripts/allen_launcher.py`.
- IA local: `start_local_ai.py` lee la configuración, comprueba/inicia llama-server y realiza una comprobación de inferencia.
- Build compilado: `packaging/build_allen.ps1` produce componentes Nuitka y llama a Inno Setup. Necesita claves de firma proporcionadas explícitamente y un GGUF específico. El intento registrado quedó incompleto; no está listo para release.

## Límites

El modelo genera texto localmente, pero no valida por sí solo la exactitud curricular. La rúbrica de proyectos es determinista y se basa en la evidencia escrita, no inspecciona prototipos. La interfaz no es un sistema de cuentas con separación segura entre usuarios del mismo dispositivo. La verificación de seguridad y privacidad no constituye certificación institucional.
