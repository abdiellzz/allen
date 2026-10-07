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
