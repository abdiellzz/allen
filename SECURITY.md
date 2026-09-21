# Seguridad y privacidad

ALLEN está diseñado para uso local. El servidor escucha en `127.0.0.1` y el modelo GGUF debe permanecer en el equipo del usuario. No subas modelos, bases SQLite, tokens, archivos `.env` ni credenciales al repositorio.

## Antes de publicar

- Revisa `git diff --cached` y confirma que no contiene secretos ni datos personales.
- Usa un repositorio privado si el código o los datos todavía no deben ser públicos.
- Configura los secretos de despliegue únicamente en GitHub/Vercel; nunca los escribas en el código.
- Rota cualquier credencial que haya sido pegada en un commit o en una incidencia.

## Vercel

La configuración de Vercel publica únicamente la página de entrada. No expone el servidor FastAPI, SQLite ni el modelo local. Para usar el tutor completo, ejecuta ALLEN en el dispositivo con `start_allen.bat`.

Para reportar un problema de seguridad, no publiques detalles sensibles en una incidencia. Contacta al propietario del repositorio de forma privada.
