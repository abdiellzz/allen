# ALLEN Dataset · base sintética v1

## Propósito y procedencia

Ejemplos de tutoría breve y respetuosa en español, dirigidos a apoyar un futuro ajuste de comportamiento de ALLEN. Contenido creado para este proyecto a partir de conceptos educativos generales, fuentes TSV originales y tres ejemplos proporcionados por el usuario. No se extrajeron chats privados, perfiles ni resultados de la aplicación.

Fecha: 19 de septiembre de 2026. Formato UTF-8 JSONL conversacional: `messages`, `role`, `content`. El archivo principal contiene únicamente conversaciones; el sidecar contiene su procedencia y estado de revisión.

## Composición

2.800 conversaciones en diez áreas según la distribución solicitada; 940 tienen varios turnos. Se construyen a partir de **229 grupos identificados** de conceptos/situaciones y variantes didácticas, incluidas 20 familias matemáticas parametrizadas. Los grupos no representan una medición automática de diversidad semántica completa.

Se incluyen explicaciones, ejemplos, corrección de ideas equivocadas, respuestas correctas e incorrectas del estudiante, preguntas con espera, tarjetas, guías, resúmenes, pistas y resolución después de un intento. Las respuestas más largas tienen 76 palabras en esta versión. La mayoría no lleva emojis.

**Estado de revisión humana: 0 aprobados; 2.800 pendientes.** Se validó automáticamente todo el formato y se revisaron las fuentes y una muestra de 20 conversaciones durante la creación por el asistente. Esto no equivale a revisión docente ni humana del corpus completo.

## Validación realizada

- Cada línea es JSON válido con mensajes alternados user/assistant y termina en assistant.
- No hay conversaciones exactamente duplicadas.
- Los hashes coinciden con los registros y el conteo por área coincide con el objetivo.
- Se comprobaron resultados conocidos de las 20 familias matemáticas y equivalencia de fracciones.
- Los resúmenes son más cortos que su texto fuente.
- Separación reproducible: 2.530 registros de entrenamiento, 270 de evaluación; cero identificadores de grupo compartidos.
- Se preservan los tres ejemplos originales del usuario.

Los detalles legibles por máquina están en `data/validation_report.json` y `data/splits/manifest.json`.

## Limitaciones conocidas

- Hay **plantillas y mensajes de apoyo repetidos**; no deben confundirse 2.800 registros con 2.800 situaciones independientes. La estructura puede hacer que un modelo repita fórmulas de respuesta.
- Muchas comprobaciones conceptuales son binarias. Faltan más preguntas abiertas, problemas de transferencia, diálogos prolongados, contextos regionales y niveles avanzados.
- El contenido inglés es introductorio y las explicaciones científicas simplifican. El corpus no constituye un currículo completo ni una fuente única de verdad.
- Las respuestas de seguridad son ejemplos de orientación general; no constituyen protocolos profesionales, asesoramiento clínico personalizado ni garantía de comportamiento seguro.
- La agrupación reduce filtraciones entre particiones, pero las plantillas, métodos y algunos temas relacionados siguen apareciendo en ambas. Se necesita un conjunto independiente escrito por revisores para evaluar calidad real.
- No hay datos de entrenamiento universitario especializado, multilingüismo amplio ni evaluación adversarial exhaustiva.
- La validación no detecta todos los errores factuales ni todas las paráfrasis cercanas; el informe no contiene una puntuación de calidad inventada.

## Uso recomendado

Punto de partida para revisión y pequeños experimentos, no un corpus certificado para desplegar un modelo con menores. Antes de entrenar, revisar y ampliar diversidad. Antes de desplegar, comparar con el modelo base y evaluar exactitud, seguridad, privacidad y utilidad pedagógica con situaciones nuevas.

No se afirma que este dataset mejore un modelo: no se ha entrenado ni medido ningún modelo con él. No se asigna una licencia nueva al conjunto sin la decisión del propietario del proyecto.
