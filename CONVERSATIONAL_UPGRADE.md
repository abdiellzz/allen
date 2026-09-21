# ALLEN: conversación y aprendizaje local

## Archivos
- backend/prompts.py (nuevo): identidad, enseñanza, seguridad, contexto del estudiante, acciones educativas y títulos por tema. Se combina en cada envío a llama.cpp.
- backend/tutoring.py (nuevo): operaciones aritméticas básicas verificadas, pistas, cambio de ejemplo, respuesta explícita y corrección de intentos y una introducción verificada a direcciones IP. No ejecuta código del usuario.
- backend/ai.py: integración del prompt central, reglas locales de identidad y tutor aritmético. Conserva streaming y llama.cpp para conversaciones abiertas.
- backend/schemas.py: acciones del chat y validación de memoria y guardados.
- backend/database.py: tablas student_memory y saved_answers, con eliminación en cascada por perfil; migración aditiva.
- backend/app.py: APIs de memoria y guardados, nombre declarado explícitamente, onboarding completado, títulos y temas educativos.
- frontend/components/learning.js (nuevo): bienvenida, acciones, preferencias, objetivo, continuar, guardados y temporizador.
- frontend/app.js: integra flujos, elimina materias/nivel/opciones del chat libre, mantiene esos controles en Tutor y Aprender. Conserva selección del perfil por identificador local.
- frontend/styles/app.css: presentación de bienvenida, acciones y modo estudio.
- tests/test_learning.py (nuevo): identidad, nombre y preferencias tras reapertura, contexto, acciones, aislamiento de guardados, borrado de memoria y aritmética.
- tests/test_study.mjs (nuevo): meta alcanzada sin bloquear, sin límite y reinicio del temporizador.
- tests/test_allen.py: el caso de streaming usa una explicación abierta para comprobar llama.cpp; las operaciones exactas tienen pruebas independientes.

## Primer uso y nombre
Un perfil predeterminado aún no presentado muestra “¡Hola! Soy Allen” y solicita solo nombre o apodo. El botón Continuar actualiza users.name en la SQLite local y marca onboarded en student_memory. Los perfiles existentes con un nombre personalizado se conservan. El nombre se cambia desde Perfil o con una declaración explícita completa como “Me llamo Carlos”. El nombre del asistente permanece Allen y no se toma del perfil.

## Memoria persistente
Archivo habitual: %LOCALAPPDATA%/ALLEN/allen.sqlite3; no se traslada a OneDrive.
- Nombre, nivel y avatar del perfil.
- Preferencias combinables, intereses educativos introducidos voluntariamente, últimos temas reconocidos y temas marcados como difíciles.
- Objetivo y fecha del día; las preferencias no renuevan por accidente un objetivo antiguo.
- Respuestas guardadas, hasta eliminarlas o eliminar el perfil.
- Conversaciones solo si Guardar historial está activado, con la retención configurada. Home ofrece continuar sesiones guardadas.
Los temas se reconocen mediante reglas locales limitadas; no se extrae un perfil psicológico ni se interpreta automáticamente cualquier información personal como un interés. Desde Perfil se puede borrar la memoria educativa sin borrar el nombre o las conversaciones. Eliminar el perfil borra también su memoria y guardados.

## Memoria de sesión
El historial activo, el texto aún sin enviar y el temporizador permanecen en la sesión del navegador. El modelo recibe instrucciones nuevas en cada llamada, el contexto del perfil y los mensajes recientes que caben en el presupuesto; no tiene memoria ilimitada. Si el historial está desactivado, el chat no reaparece tras recargar. El modo estudio ofrece 5, 10, 20 minutos o sin límite y nunca bloquea al terminar.

## Acciones educativas
Más fácil, Otro ejemplo, Paso a paso, Ponme a prueba, Explícalo diferente, No entiendo, Estoy perdido, Dame la respuesta y ¿Qué aprendí?, además de Guardar. Se muestran según la longitud y tipo de respuesta; las instrucciones de cada acción están centralizadas. No entiendo cambia el ejemplo; Estoy perdido vuelve a lo básico. La prueba propone de una a tres preguntas del tema y espera un intento. El resumen no afirma dominio no medido.

## Pruebas y límites
70 pruebas Python y 8 JavaScript pasadas en las ejecuciones de regresión y seguimiento. Se ejecutó el servidor y se probó en navegador con una base de prueba independiente: bienvenida y nombre Daniel, reinicio real, preferencias combinadas, chat sin materia, ejercicio 18 × 7, No entiendo, Dame la respuesta, guardar y reabrir respuesta, objetivo del día, continuar conversación y entrada/salida del modo estudio. El temporizador se verificó con reloj controlado sin bloquear el chat. Se comprobó también una conversación abierta con el modelo real.

Los casos solicitados de identidad se protegen con reglas locales y pasan las pruebas. Esto no implica una garantía absoluta sobre toda salida posible de un LLM. El modelo local pequeño puede equivocarse o seguir parcialmente las instrucciones; no se ha entrenado ni sustituido. La adaptación de dificultad en conversación abierta es cualitativa, guiada por el prompt y los intentos del historial, no una evaluación validada del nivel. La aritmética verificada se limita a expresiones sencillas de dos enteros; problemas complejos siguen utilizando el modelo. Los títulos y temas usan reconocimiento local por reglas y pueden ser genéricos fuera de los temas reconocidos. No hay servicios externos nuevos ni funciones con botones de adorno.
