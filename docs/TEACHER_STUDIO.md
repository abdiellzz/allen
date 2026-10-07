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


## Cómo usar Teacher Studio

### Crear y publicar un curso

1. Abre **Teacher Studio**.
2. Completa título, materia y nivel.
3. Importa un PDF con texto extraíble, TXT o Markdown.
4. Espera a que ALLEN construya el borrador.
5. Revisa unidades, temas, objetivos, preguntas, fuentes y examen.
6. Revisa **Course Quality** y corrige problemas bloqueantes.
7. Pulsa **Guardar revisión y aprobar**.
8. Pulsa **Publicar** cuando el curso quede listo.

La publicación nunca debe saltarse la revisión docente.

### Actualizar un curso existente

1. Localiza el curso en Teacher Studio.
2. Pulsa **Nueva versión**.
3. Selecciona el archivo actualizado.
4. ALLEN crea un snapshot antes del cambio.
5. Revisa el **Course Diff**:
   - nuevos;
   - modificados;
   - sin cambios;
   - eliminados;
   - progreso preservable.
6. La nueva versión queda como `draft`.
7. Revisa y aprueba otra vez.
8. Publícala.

Los temas sin cambios conservan progreso; los modificados pueden pasar a `reviewing` sin borrar la evidencia anterior.

### Exportar un Course Pack

Cuando un curso está publicado, usa **Exportar .allenpack**. El archivo puede moverse a otro equipo con ALLEN.

Al importarlo en otro dispositivo vuelve a `draft` y necesita Teacher Review antes de publicarse.

### Consultar el historial

Teacher Studio muestra `v1`, `v2`, etc. Cada entrada conserva estructura, estado, fecha y diff respecto a la versión anterior.

Para el recorrido completo de la interfaz consulta [USAGE_GUIDE.md](USAGE_GUIDE.md).
