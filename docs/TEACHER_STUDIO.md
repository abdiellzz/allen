# ALLEN Teacher Studio — arquitectura local

Teacher Studio convierte material docente en una experiencia de aprendizaje sin depender de una nube.

## Principios

1. **La fuente manda.** Cada tema, tarjeta y pregunta conserva referencia a la página o fragmento local del documento.
2. **La IA no publica.** El contenido generado o estructurado permanece como borrador hasta revisión del profesor.
3. **Offline primero.** PDF, TXT, Markdown, SQLite, rutas, progreso y Course Packs funcionan localmente.
4. **Contenido y progreso se separan.** Un curso puede actualizarse sin convertir el historial del estudiante en parte del documento.
5. **El estudiante aprende por pasos.** Descubre → ejemplo → recuperación → práctica → comprobación → revisión.
6. **Allen guía, no sustituye al estudiante.** La mascota explica qué toca hacer, ofrece ayuda progresiva y señala el siguiente paso.

## Pipeline actual

```text
Documento
  ↓
Extracción local
  ↓
Páginas + texto
  ↓
Detección de unidades / conceptos
  ↓
Borrador estructurado
  ↓
Objetivos + rutas + preguntas + flashcards + examen
  ↓
Teacher Review Gate
  ↓
Curso publicado
  ↓
Inscripción del estudiante
  ↓
Ruta guiada y persistente
  ↓
Examen final
  ↓
Mastery / refuerzo
```

## Source map

Los temas incluyen:

- página de origen;
- extracto que sustenta el concepto;
- preguntas con referencia;
- examen final con referencia.

Esto permite mostrar al estudiante y al profesor de dónde sale una actividad y evita presentar como fuente una respuesta inventada por el modelo.

## Course Pack

Un curso publicado puede exportarse como `.allenpack`. El formato contiene versión y estructura del curso, pero al importarlo vuelve a estado **draft**. Debe revisarse antes de publicarse en el nuevo dispositivo.

Esto permite compartir contenido sin crear una cuenta cloud ni sincronización externa.

## Persistencia

SQLite conserva por separado:

- `teacher_documents`
- `courses`
- `course_enrollments`
- `course_exam_results`
- `topic_mastery`
- `learning_events`
- `profile_current_activity`

Cerrar ALLEN no borra la ruta actual.

## Formatos

Implementados:

- PDF con texto extraíble;
- TXT;
- Markdown;
- `.allenpack`.

Planeados, pero **no implementados todavía**:

- DOCX;
- PPTX;
- PDF escaneado mediante OCR.

No se debe afirmar que un PDF escaneado está soportado hasta añadir OCR local y pruebas específicas.

## Evolución segura

Una futura versión puede añadir enriquecimiento opcional con el modelo GGUF local para proponer mejores explicaciones o distractores. La propuesta del modelo nunca debe reemplazar silenciosamente el texto fuente ni saltarse la revisión docente.

DOCX y PPTX deberían entrar al mismo pipeline normalizado:

```text
archivo → páginas/secciones → chunks con origen → curriculum graph → review gate
```

No crear una arquitectura distinta por formato.
