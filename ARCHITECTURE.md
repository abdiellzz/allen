# Arquitectura de ALLEN

## Punto de partida y decisiones

El MVP original tenía `server.py` basado en `SimpleHTTPRequestHandler` e `index.html` con CSS y JavaScript incrustados. Solo existía un envío de chat sin contexto y una respuesta demo; navegación, perfiles y módulos no estaban implementados. Servir todo el directorio exponía archivos del proyecto, los errores podían revelar excepciones y el indicador offline era fijo.

La nueva versión conserva el punto de entrada `server.py`, el endpoint `/api/chat`, el concepto de modo demo y los modos educativos. La variable antigua `ALLEN_LLM_URL` se admite como valor inicial si es una URL local válida; las preferencias guardadas tienen prioridad. Los originales se conservan en `legacy/`, fuera del directorio servido.

## Flujo de datos

```text
Navegador en el dispositivo
  frontend/index.html + app.js + styles/app.css
     ↓ fetch del mismo origen + token de la instancia
FastAPI en 127.0.0.1:8787
  validación / perfiles / privacidad / reglas educativas
     ├── SQLite local: usuarios, preferencias, historial y progreso
     ├── biblioteca de archivos → ranking por palabras
     ├── ejercicios y quizzes deterministas → corrección local
     └── prompt centralizado + contexto acotado
            ↓ HTTP loopback, sin proxy ni redirecciones
          llama.cpp /v1/chat/completions
            ↓
          modelo GGUF cargado por el usuario
```

## Componentes

- `server.py`: arranque Uvicorn y apertura opcional del navegador una vez disponible el health check.
- `backend/app.py`: fábrica de la aplicación, rutas, validación de origen, errores y coordinación de servicios. `create_app(db_path, ai)` permite bases y transporte independientes para tests.
- `backend/schemas.py`: contratos Pydantic, rangos, límites, tipos y validación estrictamente local de URL.
- `backend/ai.py`: personalidad central, instrucciones por modo, detección del servidor/modelo, presupuesto de contexto y consumo SSE. Un semáforo permite una generación a la vez para reducir uso de memoria.
- `backend/security.py`: normalización y respuestas educativas de seguridad. Es una defensa básica, no un clasificador certificado.
- `backend/database.py`: conexiones SQLite por operación, transacciones, inicialización con `user_version=1`, retención, XP y borrado en cascada.
- `backend/education.py`: banco original de preguntas, plantillas matemáticas y equivalencia exacta con `Fraction`; nunca `eval` ni ejecución de código.
- `backend/library.py`: lectura acotada de paquetes, rechazo de archivos fuera de la raíz y ranking. La interfaz `search()` es el punto de sustitución para embeddings locales futuros.
- `frontend/app.js`: navegación y controladores de páginas; estado en memoria para el perfil activo y mensajes no guardados. No se necesita framework ni compilación.
- `frontend/services.js`: API del mismo origen, token y lectura incremental NDJSON, con errores comprensibles.
- `frontend/components/markdown.js`: Markdown limitado; escapa HTML, no crea enlaces ni imágenes externas. Soporta encabezados, listas, código y tablas; no implementa todo CommonMark ni LaTeX.
- `frontend/styles/app.css`: diseño responsive y accesibilidad. `frontend/assets/allen.svg`: mascota original local.

## Chat, cancelación y estado

`/api/chat?stream=true` emite NDJSON con eventos `meta`, `delta`, `done` y `error`. Entre Allen y llama.cpp se usa SSE compatible con OpenAI; no se llama a OpenAI ni se incluye su SDK. El endpoint sin `stream=true` devuelve JSON con `ok`, `answer`, `offline`, `demo` y el identificador de conversación, preservando los campos del MVP.

El frontend usa `AbortController` al detener, cambiar de página, perfil o conversación. El cliente HTTP y el semáforo se cierran/liberan al cancelar. Solo se guarda una respuesta final completada. Una generación iniciada antes de borrar datos o desactivar historial no puede volver a guardar datos después de ese cambio. La cancelación efectiva del cómputo en llama.cpp depende de cómo el servidor trate una desconexión; no se promete finalizar instantáneamente su trabajo interno.

Para filtrar antes de mostrar, la salida se acumula hasta encontrar un párrafo completo. Esto puede retrasar el primer texto de respuestas de un solo párrafo. No se muestra razonamiento interno de campos ajenos a `delta.content`. El filtro por patrones puede tener falsos positivos y omisiones.

La ventana de contexto utiliza un presupuesto conservador de bytes UTF-8 y recorta el historial más antiguo. No sustituye al tokenizador específico del GGUF y puede rechazar textos que el modelo sí podría admitir. El parámetro `context_size` no reconfigura el proceso de llama.cpp.

## Datos y retención

SQLite contiene `users`, `settings`, `conversations`, `progress`, `quiz_results`, `flashcards` y `learning_sessions`. Las relaciones de perfil tienen claves foráneas y `ON DELETE CASCADE`; las consultas usan parámetros. Las futuras migraciones deben aumentar `PRAGMA user_version` y aplicar transformaciones antes de usar las tablas.

`settings` contiene un JSON validado por `Settings`. El ejemplo de `config/` es documentación. La base predeterminada está en `%LOCALAPPDATA%/ALLEN` para no sincronizarla mediante la carpeta OneDrive de este proyecto. `secure_delete=ON` ayuda a limpiar registros borrados, sin prometer borrado forense del disco o de respaldos.

El historial caduca después de 1–90 días (30 por defecto); la limpieza sucede en arranque, lectura de historial, chat o cambio de preferencias. Sin el servidor abierto no existe una tarea de limpieza en segundo plano. Desactivar el guardado borra conversaciones de todos los perfiles. Los mensajes en pantalla son memoria de la pestaña y desaparecen al recargar o limpiar.

La aplicación es para una cuenta/dispositivo confiable: no hay autenticación entre perfiles. La vista de acompañantes muestra datos agregados; no es un rol autorizado separado.

## Endpoints principales

| Ruta | Función |
| --- | --- |
| GET `/api/bootstrap` | Token de instancia, perfiles, configuración y catálogo |
| GET `/api/health`, `/api/model/status` | Salud local y detección del modelo |
| GET/PUT `/api/settings` | Preferencias del dispositivo |
| POST `/api/profiles`; PUT/DELETE `/api/profiles/{id}` | Perfiles y eliminación en cascada |
| POST `/api/chat`, `/api/tutor`, `/api/summarize`, `/api/translate` | Motor educativo local |
| GET `/api/conversations`; GET/DELETE `/api/conversations/{id}` | Historial por perfil |
| POST `/api/quiz`, `/api/quiz/{id}/submit`; GET `/api/quiz/results` | Preguntas, corrección y resultados |
| GET/POST `/api/flashcards`; POST `/api/flashcards/generate` | Tarjetas manuales o propuestas de IA validadas |
| POST `/api/flashcards/{id}/review`; DELETE `/api/flashcards/{id}` | Repetición espaciada y eliminación |
| GET `/api/library` | Búsqueda local, sin acceso por rutas arbitrarias |
| GET `/api/progress`; POST `/api/study` | XP, rachas y sesiones |

Las escrituras requieren `X-Allen-Token`. No se habilita CORS; se comprueban Host, Origin y `Sec-Fetch-Site`. Un token CSRF protege frente a páginas externas, no frente a software malicioso ejecutándose en la misma cuenta local.

## Extensiones previstas

RAG semántico mediante embeddings y un índice local; currículo versionado; revisión pedagógica de bancos; evaluación adversarial de seguridad; perfiles con autenticación si se requiere aislamiento multiusuario; exportación/importación explícita de datos; modelos y binarios distribuidos mediante un instalador firmado. Ninguna exige servicios de IA en la nube.


## Entrenamiento opcional

`allen_training/` es un módulo aislado de creación y validación de datos. La aplicación no importa sus ejemplos ni ejecuta su script. El dataset usa `messages` y un sidecar con procedencia y grupos. `train.py` valida por defecto, puede preparar splits sin dependencias adicionales y solo inicia la ruta LoRA con `--train`. Cada respuesta se convierte en una completion con su contexto anterior como prompt. Las variantes de la misma conversación permanecen en una sola partición. No existe exportación automática a GGUF ni conexión automática de un adaptador al servidor llama.cpp.
