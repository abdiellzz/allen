> Integración de la rama móvil: el código abre ahora `mobile/index.html`, con seis
> cursos y ayuda preparada. La demo publicada en `main` no se ha reemplazado:
> necesita recompilación para incluir estos cambios. Ver
> [MOBILE_ANDROID_INTEGRATION.md](../docs/MOBILE_ANDROID_INTEGRATION.md).

# ALLEN para Android (demo)

APK de demostración que ejecuta ALLEN completo dentro del teléfono, sin servidor y sin Internet.

## Cómo funciona

```text
WebView (assets del APK)
  ├── public/mobile/ → experiencia educativa inicial
  ├── frontend/ de ALLEN → interfaz original accesible desde Perfiles
  ├── allen-android.js  → intercepta fetch('/api/...')
  └── allen-worker.js   → Web Worker con Pyodide (Python 3.13 en WebAssembly)
        └── allen_bridge.py → backend/app.py real (FastAPI + SQLite)
```

- Python corre en un Web Worker para que la interfaz siga respondiendo mientras arranca.
- Los perfiles móviles se guardan directamente en IndexedDB. La interfaz original conserva SQLite sobre IDBFS del WebView; ambos almacenes son independientes. Los datos sobreviven al cerrar la app.
- La app no declara ningún permiso de Android, ni siquiera Internet.
- El backend arranca en modo demo: sin licencia, sin PIN de profesor y con la IA local desconectada.

## Descargar e instalar

**[Descargar ALLEN-demo-android.apk](https://github.com/abdiellzz/allen/raw/main/android/release/ALLEN-demo-android.apk)**
(21 MB · Android 8.0 o superior). El repositorio es privado: el enlace funciona con una sesión de
GitHub que tenga acceso.

1. Descarga el APK en el teléfono, o en el PC y pásalo al teléfono por cable, Drive o WhatsApp.
2. Abre el archivo desde **Descargas** o **Archivos**.
3. Si Android avisa que no permite instalar apps desconocidas, pulsa **Configuración**, activa
   **Permitir de esta fuente** y vuelve atrás.
4. Pulsa **Instalar**. Si Play Protect avisa que la app no es conocida, elige
   **Más detalles → Instalar de todas formas**. Es normal: la demo no está publicada en Google Play.
5. Abre **ALLEN**. La primera vez tarda unos segundos mientras prepara Python.

Actualizar: instala el APK nuevo encima del anterior; los datos se conservan. Si Android dice que
el paquete entra en conflicto, el APK se firmó en otro equipo: desinstala la versión anterior
(esto borra sus datos) e instala la nueva.

Desinstalar la app borra todos sus datos del teléfono.

## Qué funciona y qué no

Funciona: perfiles, quizzes, simulacros, tarjetas, Plan Allen, aventuras, biblioteca,
cursos, Teacher Studio (importar PDF/TXT/Markdown), progreso, recuperación y Modo Feria.

Limitaciones de la demo:

- El chat con IA generativa responde en modo demo (no hay llama.cpp en el teléfono).
  El tutor de aritmética sí responde.
- La pantalla móvil permite exportar manualmente el JSON del perfil; no hay guardado nativo de archivos. Course Packs y descargas de la interfaz original siguen pendientes.
- La interfaz educativa móvil no inicia Python. Python se carga al abrir la interfaz original.

## Compilar

Requisitos: Python 3, JDK 17 y Android SDK (platform 35).

```bash
python android/build_web_assets.py          # arma android/app/src/main/assets/www
cd android
./gradlew assembleDebug                      # Windows: gradlew.bat assembleDebug
```

El APK queda en `android/app/build/outputs/apk/debug/app-debug.apk`. Para publicar una versión nueva,
cópialo a `android/release/ALLEN-demo-android.apk`, que es el archivo del enlace de descarga.

`build_web_assets.py` descarga Pyodide 0.29.5 y los paquetes necesarios, y verifica cada
archivo con el SHA-256 de `pyodide-lock.json` o de PyPI. Los archivos generados no se suben al repositorio.
