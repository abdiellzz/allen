# Allen: tutor guiado y ampliación de cursos

El tutor móvil funciona con conocimiento editorial y reglas verificables. No es un modelo entrenado ni genera respuestas nuevas. Incluye 235 preguntas guiadas: siete por cada uno de los 31 temas, más 18 preguntas de orientación sobre la app. Hay preguntas adicionales sobre pistas, retroalimentación, progreso y recomendaciones. El texto libre reconoce preguntas cubiertas; ante una duda fuera del contenido ofrece opciones y reconoce el límite.

Las seis rutas contienen 31 lecciones y 119 preguntas evaluables. Se añadieron comparación, suma heterogénea y cantidades con fracciones; resumen, intención y argumentos; posesión, rutinas y preguntas en inglés; condiciones, bucles y depuración en Python; privacidad, verificación y copias; medidas, datos y conclusiones en ciencias. El diagnóstico conserva las preguntas originales para no invalidar sesiones y copias previas. Los temas nuevos se comprueban dentro de la ruta.

No hay conexión a un modelo, descarga de IA ni dependencia de una computadora en el chat móvil. El contenido, las preguntas sugeridas y las respuestas se empaquetan como módulos estáticos. La PWA los descarga mediante el service worker; Android los incluye al regenerar sus assets. El escritorio mantiene sus capacidades independientes.

## Privacidad y reglas

La conversación es temporal y se limpia al cambiar de perfil, importar, borrar o crear perfiles. No se envía a servicios externos. Las preguntas del chat nunca califican, completan ni desbloquean temas. Las pistas y explicaciones de una sesión activa pasan por el motor educativo existente y se guardan como evidencia. La retroalimentación del ejercicio se ofrece después de responder. Los perfiles locales son separación de datos, no autenticación: otras personas con acceso al dispositivo pueden seleccionarlos.

## Ejecutar y verificar

Desde la raíz: `python -m http.server 8081 --directory public`; abrir `http://localhost:8081/mobile/`. Crear un perfil, seleccionar una ruta y completar diagnóstico, lección y comprobación. Abrir Allen: elegir otro tema, preguntar con botones y escribir una pregunta cubierta. Pedir la respuesta antes de contestar devuelve orientación hacia pistas. Consultar un tema no conocido reconoce el límite. Cambiar de perfil limpia la conversación.

Pruebas: `node --test tests/test_mobile.mjs tests/test_guided_tutor.mjs`; `python -m pytest -q`. La actualización de la PWA necesita cerrar las pestañas anteriores para activar la nueva caché. El APK de esta entrega incluye el tutor preparado y el acompañamiento, sin cargar Python. Los recordatorios se activan desde Ajustes, de forma opcional. Véase [COMPANION_V1.md](COMPANION_V1.md). No se ha ejecutado esta versión en un teléfono Android físico.

El contenido es preparado y revisable; no se afirma certificación docente ni dominio de cualquier pregunta del mundo. Próximos pasos: revisión pedagógica externa, más variantes de evaluación para evitar memorización y mejor reconocimiento de formulaciones libres.
