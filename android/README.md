# ALLEN para Android (demo)

APK de demostración que ejecuta ALLEN completo dentro del teléfono, sin servidor y sin Internet.

## Cómo funciona

```text
WebView (assets del APK)
  ├── frontend/ de ALLEN, sin cambios
  ├── allen-android.js  → intercepta fetch('/api/...')
  └── allen-worker.js   → Web Worker con Pyodide (Python 3.13 en WebAssembly)
        └── allen_bridge.py → backend/app.py real (FastAPI + SQLite)
```

- Python corre en un Web Worker para que la interfaz siga respondiendo mientras arranca.

- Los datos se guardan en el almacenamiento del WebView (IndexedDB) y sobreviven al cerrar la app.
- La app no declara ningún permiso de Android, ni siquiera Internet.
- El backend arranca en modo demo: sin licencia, sin PIN de profesor y con la IA local desconectada.

## Qué funciona y qué no

Funciona: perfiles, quizzes, simulacros, tarjetas, Plan Allen, aventuras, biblioteca,
cursos, Teacher Studio (importar PDF/TXT/Markdown), progreso, recuperación y Modo Feria.

Limitaciones de la demo:

- El chat con IA generativa responde en modo demo (no hay llama.cpp en el teléfono).
  El tutor de aritmética sí responde.
- Exportar respaldos o Course Packs (descargas) no está conectado todavía.
- El primer arranque tarda unos segundos mientras se carga Python.

## Compilar

Requisitos: Python 3, JDK 17 y Android SDK (platform 35).

```bash
python android/build_web_assets.py          # arma android/app/src/main/assets/www
cd android
./gradlew assembleDebug                      # Windows: gradlew.bat assembleDebug
```

El APK queda en `android/app/build/outputs/apk/debug/app-debug.apk`.

`build_web_assets.py` descarga Pyodide 0.29.5 y los paquetes necesarios, y verifica cada
archivo con el SHA-256 de `pyodide-lock.json` o de PyPI. Los archivos generados no se suben al repositorio.
