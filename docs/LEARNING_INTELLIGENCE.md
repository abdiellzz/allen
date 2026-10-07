# ALLEN Learning Intelligence

Esta capa convierte el progreso de ALLEN en decisiones educativas interpretables y locales.

## Objetivos

- explicar por qué un tema tiene cierto mastery;
- representar relaciones entre conceptos;
- hacer un diagnóstico antes de iniciar un curso;
- evitar repetir temas ya dominados;
- programar repasos de temas completos;
- medir la calidad de un curso antes de publicarlo;
- separar y observar el banco de preguntas;
- dar al profesor métricas locales sin telemetría externa.

## Curriculum Graph

Cada tema de un curso se representa como un nodo:

```text
u0:t0  CIDR
u0:t1  Subnetting
u1:t0  DNS
```

Relaciones iniciales:

- `prerequisite`
- `builds_on`
- `related_to`

Las relaciones se derivan de la estructura del material y se guardan en `curriculum_edges`. No son una afirmación universal sobre la materia: describen el curso importado y revisado.

## Course Quality

El score de calidad no sale de una opinión del modelo. Se calcula con checks visibles:

- existencia de unidades y temas;
- fuente verificable;
- objetivo medible;
- preguntas de comprobación;
- extractos de tamaño razonable;
- preguntas duplicadas o ambiguas;
- balance básico entre unidades;
- examen final.

Un error bloqueante impide publicar. El profesor recibe razones concretas.

## Diagnóstico

Antes de empezar un curso, ALLEN usa de 5 a 10 preguntas cuando el banco disponible lo permite.

El resultado clasifica temas como:

- strong
- developing
- weak

Los temas con >=80% pueden omitirse de la ruta. El estudiante comienza en el primer tema que todavía necesita desarrollar.

El diagnóstico no borra mastery previo. Añade evidencia.

## Evidence of Mastery

La UI no muestra solamente un porcentaje. También puede explicar:

- respuestas correctas / intentos;
- errores;
- pistas;
- prácticas;
- quizzes;
- último resultado de examen disponible;
- próxima revisión.

## Spaced Topic Review

`topic_mastery.next_review` funciona como agenda central de revisión. Home puede mostrar temas vencidos aunque no sean flashcards.

## Question Bank

Las preguntas del curso se normalizan en `question_bank` con:

- materia;
- tema;
- objetivo;
- prompt;
- respuesta;
- opciones;
- dificultad;
- tipo;
- página fuente;
- estado;
- origen;
- intentos;
- correctas;
- incorrectas.

Después del Teacher Review Gate pasan a `approved`.

Cuando una pregunta acumula suficiente uso, una tasa de aciertos extrema puede marcarla para revisión docente. Esto es una señal, no prueba de que la pregunta sea mala.

## Teacher Analytics

El dashboard local muestra por curso:

- score de calidad;
- inscripciones;
- finalizaciones;
- solicitudes de “No entendí”;
- tamaño del banco de preguntas;
- preguntas con estadísticas sospechosas;
- temas con mastery bajo;
- posiciones activas del aprendizaje;
- hotspots de solicitudes de ayuda.

No se envían datos fuera del dispositivo.


## Cómo usar Learning Intelligence

### Diagnóstico inicial

Desde **Cursos**, abre un curso publicado y comienza el diagnóstico. ALLEN clasifica la evidencia por tema como `strong`, `developing` o `weak` y recomienda dónde iniciar.

El diagnóstico no sustituye una calificación oficial y no borra evidencia previa.

### Leer Evidence of Mastery

En Inicio y vistas de progreso, el porcentaje de mastery debe leerse junto con su evidencia: intentos, aciertos, errores, pistas, prácticas, quizzes, examen y próxima revisión.

El objetivo es poder responder “¿por qué tengo este porcentaje?” sin depender de una explicación opaca de IA.

### Usar el repaso espaciado

Cuando `next_review` vence, Inicio puede recomendar repasar el tema antes de avanzar. Completar nueva práctica añade evidencia y permite actualizar la planificación posterior.

### Revisar Course Quality

En Teacher Studio, usa el desglose del score para identificar fuentes faltantes, objetivos poco medibles, preguntas ambiguas o duplicadas, temas sin evaluación y problemas del examen final.

Los bloqueos deben corregirse antes de publicar.

### Revisar Question Bank

Desde Teacher Studio consulta las preguntas normalizadas del curso. Las tasas extremas de acierto con suficiente uso son señales para revisar redacción, distractores o dificultad; no prueban por sí solas que la pregunta sea incorrecta.

### Usar Teacher Analytics

Teacher Analytics sirve para observar calidad, inscripciones, finalizaciones, “No entendí”, temas débiles, hotspots y estado del banco de preguntas. Los datos permanecen locales.

Para instrucciones paso a paso de todas las áreas consulta [USAGE_GUIDE.md](USAGE_GUIDE.md).
