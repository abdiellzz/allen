# ALLEN para Android (offline)

Este directorio define la versión móvil separada de ALLEN. El APK no debe descargar ni incluir automáticamente un modelo GGUF desde GitHub.

## Arquitectura prevista

- **UI:** reutilizar los componentes visuales de `frontend/` dentro de una WebView local o migrarlos gradualmente a Jetpack Compose.
- **Datos:** SQLite/Room dentro del almacenamiento privado de la aplicación.
- **Tutor local:** `llama.cpp` compilado para `arm64-v8a`, ejecutado como proceso nativo local o mediante una biblioteca JNI.
- **Comunicación:** puente local entre la UI y el motor, sin CORS público, sin servidores externos y sin permisos de red por defecto.
- **Modelo:** el usuario selecciona un archivo `.gguf` del almacenamiento del dispositivo mediante el selector de documentos de Android. La ruta se guarda solo en preferencias privadas.

## Requisitos de compilación

- Android Studio reciente.
- Android SDK 35 y NDK compatible con el commit elegido de `llama.cpp`.
- JDK 17.
- Un dispositivo o emulador `arm64-v8a` para validar rendimiento y memoria.

## Seguridad

- No guardar modelos, tokens, historiales ni bases de datos en el repositorio.
- No pedir permisos de contactos, cámara, micrófono o ubicación.
- Mantener `android:usesCleartextTraffic="false"`; el motor local usa IPC/JNI, no HTTP público.
- Usar Android Keystore para cualquier secreto futuro.
- Firmar el APK de distribución con una clave privada fuera del repositorio.
- Probar que el modelo no se copie a almacenamiento compartido sin una acción explícita del usuario.

## Estado

La aplicación de escritorio ya está separada y probada. Este módulo es la especificación de la implementación Android; todavía requiere crear el proyecto Android Studio y compilar `llama.cpp` para ARM64. La interfaz web no se puede empaquetar sola como APK funcional porque sus rutas `/api` dependen del backend FastAPI de escritorio.

## Primer prototipo recomendado

1. Crear un proyecto Android con una sola `MainActivity` y una WebView local.
2. Copiar `frontend/` como assets y reemplazar `frontend/services.js` por un puente Android local.
3. Implementar primero biblioteca, quizzes, progreso y modo demo.
4. Integrar `llama.cpp` después de validar memoria, temperatura y consumo de batería.
5. Generar un APK firmado de prueba y evaluar respuestas con el mismo conjunto de tests del proyecto.
