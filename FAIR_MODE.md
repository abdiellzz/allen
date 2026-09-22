# ALLEN · Modo Feria

## Abrir y preparar el stand

Ejecuta `start_allen.bat` y abre http://127.0.0.1:8787/fair. También funciona `/?mode=fair` y el enlace de Configuración. La primera instalación/actualización de dependencias necesita Internet; las actividades y el generador QR funcionan localmente después de instalarlo.

En **Presentador → Probar sistema** comprueba backend, base, modelo, reconocimiento y voces. Este panel distingue una API disponible de una captura de micrófono o reproducción realmente probada. Los botones **Probar micrófono** y **Probar voz local** permiten comprobar el hardware. **Bloquear Modo Feria** oculta la salida y redirige la aplicación habitual hacia la feria en este navegador. Desbloquear requiere confirmación deliberada; no es una barrera de seguridad frente a quien controle el navegador o el sistema operativo.

## Experiencias

- Inicio con cinco experiencias principales y estadísticas locales.
- Chat temporal con sugerencias y acciones contextuales reutilizadas. Timeout de 60 segundos y comprobación/reintento de conexión. La generación usa el mismo motor local y no guarda el texto en los perfiles.
- Retos de tres preguntas en seis categorías, evaluación en el servidor, explicación inmediata y tarjeta con nombre opcional. No hay cronómetro punitivo. El banco está preparado localmente; no depende de que el modelo invente preguntas.
- Microlecciones de tres pasos, seis categorías y preguntas comprobables. Son contenido preparado, no lecciones generadas dinámicamente por IA.
- Sorpréndeme elige una microlección distinta de la inmediatamente anterior.
- Explicación del procesamiento local, comparador educativo y Modo Jurado.
- Sonidos sintéticos opcionales, animaciones CSS con movimiento reducido y variaciones de la mascota reutilizable.
- QR local SVG mediante qrcode 8.2. Configura PROJECT_URL, GITHUB_URL o SOCIAL_URL en Presentador (almacenamiento del navegador), o como variables de entorno al iniciar el servidor. El enlace principal tiene prioridad. No se consulta la URL para generar el QR. Un repositorio privado no será accesible para visitantes sin permisos.

## Privacidad y estadísticas

Nueva persona detiene reconocimiento y reproducción, elimina nombre, conversación, estado de ejercicio, nivel y reto de la memoria del frontend, invalida la sesión del backend y vuelve al inicio. Una respuesta tardía de la sesión anterior no se muestra. Recargar la página también descarta la conversación.

Tras 120 segundos sin interacción aparece «¿Sigues ahí?». Después de 20 segundos más se limpia la sesión. Un inicio vacío entra en atracción después de 45 segundos. Constantes y decisión comprobable en `frontend/fair-content.js`.

Las tablas `fair_sessions`, `fair_questions`, `fair_quizzes` y `fair_challenges` contienen únicamente `day`, `count` y `seconds`. No hay columnas de nombre, pregunta, audio o identificador de visitante. Los identificadores de sesión aleatorios viven en memoria del servidor durante un máximo de 210 segundos sin actividad. Los contadores significan sesiones de actividad (no personas únicas), preguntas completadas, microlecciones comprobadas y retos completos. Una microlección cuenta una vez por tema y sesión. La duración es aproximada, con latidos durante la interacción y límites por intervalo; no equivale a tiempo de aprendizaje medido.

No se graba audio en ALLEN. Voz de entrada desactivada de inicio; modo local exige soporte explícito del navegador y nunca cae automáticamente a la nube. El modo navegador es opcional y está rotulado como potencialmente dependiente de Internet. TTS usa exclusivamente voces españolas marcadas como locales por el navegador, con reproducir/pausar/continuar/detener. No habla automáticamente salvo activación del presentador. La disponibilidad depende de las voces y del navegador instalados.

## Archivos y rutas

Backend: `backend/fair.py`, integración mínima en `backend/app.py`. Frontend: `frontend/fair.html`, `fair.js`, `fair.css`, `fair-content.js`, `fair-voice.js`, `components/fair-mascot.js`; entrada desde `frontend/app.js`. Dependencia QR en `requirements.txt` y comprobación actualizada en `start_allen.bat`.

Rutas: GET `/fair`, `/?mode=fair`; GET `/api/fair/token`, `/bootstrap`, `/stats`, `/links`, `/qr`; POST `/api/fair/sessions`, `/end`, `/event`, `/challenge`, `/answer`, `/chat`. Los POST usan la protección de origen y token existente. Las actividades de feria no llaman a las rutas de escritura de los perfiles habituales.

## Verificación

`python -m unittest discover -s tests -p test_fair.py -v` y `node --test tests/test_fair.mjs` comprueban rutas, token, reto completo y rechazo de repetición, chat sin persistencia, invalidación de sesión, caída/reconexión simulada del motor, contadores, generación QR, rechazo de esquemas inseguros, tiempos de inactividad y recuperación de voz. El banco y las microlecciones incluyen respuestas explicadas.

Resultado: 7 pruebas Python y 5 JavaScript aprobadas. En navegador, con una base SQLite de prueba separada: portada, reto 3/3, tarjeta, chat 18 × 7 → 126 y desaparición de la acción de revelar, Nueva persona y chat vacío, microlección completa, Modo Jurado, QR visible, estadísticas y fallos de micrófono/TTS. Se observó el aviso de inactividad y, 20 segundos después, la pantalla de atracción con la sesión limpia. Se inició el modelo real y se recibió una respuesta en el chat de feria. En el servidor principal, el panel confirmó backend, base y modelo activos; detectó una voz española local y aceptó la prueba TTS sin errores de consola. No se ha evaluado la calidad audible.

## Límites y comprobaciones pendientes para el stand

- No se apagó físicamente el Wi-Fi del equipo. La prueba de red desconectada real queda pendiente; la interfaz no afirma desconexión si el navegador indica red. No se hacen consultas externas para comprobar Internet.
- Reconocimiento real, pronunciación y calidad audible deben comprobarse en el equipo del stand con sus permisos y voces locales. El fallback a texto sí está probado.
- La respuesta del modelo real fue recibida, pero su calidad educativa necesita revisión: el modelo pequeño puede dar analogías imprecisas o repetir preguntas. Las microlecciones preparadas ofrecen una demostración estable.
- La selección de dificultad se aplica al reto mezclado; una categoría individual recorre sus tres preguntas progresivas. El banco inicial es pequeño y conviene ampliarlo antes de eventos largos.
- No hay APK ni servidor cloud en este cambio. No se altera la red ni se apaga el Wi-Fi automáticamente.
