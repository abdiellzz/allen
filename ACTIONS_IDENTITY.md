# Identidad y acciones contextuales de ALLEN

## Archivos modificados o añadidos
backend/prompts.py, backend/conversation.py (nuevo), backend/schemas.py, backend/tutoring.py, backend/ai.py, backend/app.py, backend/database.py; frontend/components/actions.js (nuevo), frontend/components/learning.js, frontend/components/ui.js, frontend/app.js, frontend/styles/app.css, frontend/assets/icons.svg; tests/test_actions.py y tests/test_actions.mjs (nuevos).

## Identidad
ALLEN_IDENTITY_PROMPT en backend/prompts.py define a Allen como IA educativa y personaje de mono naranja, sin afirmar ser un animal biológico. identity_reply responde de forma consistente a preguntas sobre la mascota, realidad física, nombre y estudiante. Reconoce “Yo me llamo Pedro” como nombre del estudiante. La bienvenida usa la nueva presentación del mono compañero.

## Acciones y contexto
frontend/components/actions.js contiene getAvailableActions(message, conversationState), las etiquetas, iconos y barra. Se envían acciones estructuradas como reveal_answer, simplify, another_example, quiz_me y lost. El texto visible es una etiqueta, no la única instrucción enviada al modelo. Las acciones anteriores siguen aceptándose como alias para compatibilidad.
backend/conversation.py mantiene current_topic, active_exercise, answer_revealed, mode, last_action y pending_question. Se guarda en conversation_states, relacionado por clave foránea con la conversación y se elimina junto con ella. El backend recupera el estado guardado y completa el historial cuando una acción llega sin mensajes. Sin historial persistente el estado viaja solo en la sesión activa del navegador. No se comparte entre perfiles.

## Evitar el bucle
reveal_answer incluye una instrucción explícita: responder ahora, con explicación corta, sin pedir confirmación ni reescribir el problema. Las operaciones básicas tienen una solución local exacta. Sin ejercicio pendiente devuelve un mensaje específico y no inventa uno. Tras revelar, answer_revealed queda activo y desaparece la acción de revelar, incluso al reabrir el historial. Las preguntas nuevas reemplazan el ejercicio anterior. Las respuestas antiguas ofrecen únicamente Guardar y Copiar.

## Botones
Teoría: Más fácil, Otro ejemplo, Ponme a prueba. Ejercicio pendiente: Pista, Paso a paso, Dame la respuesta. Respuesta final: Otro ejemplo, Ponme a prueba, ¿Qué aprendí? Quiz sin intento: Pista y Explicar; Siguiente aparece después de evaluar el intento. Más opciones contiene las acciones secundarias relevantes, incluyendo Guardar y Copiar. Máximo tres acciones principales y Más opciones.

## Iconos
Se incorporaron los SVG de Lucide al paquete local existente y se separaron los iconos de las etiquetas mediante span. Los SVG decorativos tienen aria-hidden, focusable=false y role=presentation. No se pudo reproducir el texto literal “svg” en la versión inspeccionada; no se atribuye una causa original no demostrada. La prueba de etiquetas y la inspección del DOM final verifican que no aparece ese texto en los botones ni SVG escapado como texto.

## Validación
87 pruebas Python y 12 JavaScript aprobadas. Incluyen los cinco casos de identidad, acciones estructuradas, respuesta con/sin ejercicio, persistencia y aislamiento, cambio de tema, quiz y siguiente pregunta, ausencia de reveal_answer tras resolver, máximo de acciones, estructura SVG y regresiones previas. En navegador se verificó la bienvenida, reconocimiento del mono, 18 × 7 → 126, desaparición del botón, quiz → intento 56 → siguiente 9 × 7 y recuperación desde el historial. Las respuestas abiertas aún dependen de la calidad del modelo local; las reglas del prompt no equivalen a una garantía absoluta sobre cualquier salida de un LLM.
