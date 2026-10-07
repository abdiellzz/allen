# Guía de uso de ALLEN

Esta guía explica cómo usar las funciones principales de ALLEN desde la interfaz. ALLEN está diseñado para funcionar de forma local y offline; el modelo de IA local es opcional para las funciones abiertas del tutor.

## 1. Iniciar ALLEN

### Windows

1. Ejecuta `start_allen.bat`.
2. Mantén abierta la ventana del servidor.
3. ALLEN abre `http://127.0.0.1:8787`.
4. Para cerrar el servidor usa `Ctrl+C`.

La primera instalación puede necesitar Internet para instalar dependencias. Después, las funciones locales pueden utilizarse sin conexión.

## 2. Perfiles

Los perfiles separan el progreso educativo de cada persona en el mismo dispositivo.

### Crear un perfil

1. Abre ALLEN.
2. Entra a **Perfiles**.
3. Crea un perfil con nombre o apodo, nivel y datos opcionales.
4. Selecciona ese perfil antes de estudiar.

### Qué se guarda por perfil

- progreso;
- quizzes;
- flashcards;
- planes de estudio;
- aventuras;
- simulacros;
- cursos inscritos;
- mastery por tema;
- diagnósticos;
- actividad actual.

Los perfiles no son cuentas de seguridad y no tienen contraseña.

## 3. Inicio

La página **Inicio** resume qué conviene hacer a continuación.

Puede mostrar:

- actividad que dejaste a medias;
- curso activo;
- Plan Allen;
- aventura en progreso;
- repasos vencidos;
- temas con mastery;
- siguiente mejor acción.

Cuando existe una revisión pendiente de un tema, ALLEN puede priorizarla antes de continuar contenido nuevo.

## 4. Tutor y chat

El Tutor sirve para explicar, practicar y resolver dudas.

1. Selecciona tu perfil.
2. Entra a **Tutor** o abre el chat desde una actividad.
3. Escribe qué quieres aprender o qué no entendiste.
4. Si existe un modelo local conectado, ALLEN usa ese modelo.
5. Si no existe modelo, las funciones deterministas siguen disponibles y el chat no pretende estar conectado a una IA.

Dentro de un curso, cuando se abre el Tutor desde una actividad, puede recibir como contexto el fragmento fuente del tema.

## 5. IA local con llama.cpp

ALLEN no incluye un modelo automáticamente.

### Conectar un modelo

1. Inicia `llama-server` en `127.0.0.1`.
2. En ALLEN abre **Configuración → Inteligencia Artificial**.
3. Indica la URL local, normalmente `http://127.0.0.1:8080`.
4. Pulsa **Comprobar conexión**.
5. Comprueba que aparezca **IA LOCAL ACTIVA**.

El servidor solo debe exponerse en loopback para este uso local.

## 6. Plan Allen

**Plan Allen** organiza una meta de estudio en sesiones.

1. Abre **Plan Allen**.
2. Indica materia, objetivo, fecha, tiempo disponible y temas.
3. Crea el plan.
4. Inicia una sesión.
5. Marca actividades como entendidas, usa pistas o continúa al siguiente paso.
6. Si cierras ALLEN, la sesión puede retomarse.

Las prioridades pueden utilizar errores previos, flashcards pendientes y mastery.

## 7. Aventuras

Las Aventuras convierten el estudio en una secuencia de misiones.

1. Abre **Aventuras**.
2. Elige una aventura disponible.
3. Iníciala.
4. Completa cada misión.
5. El progreso se guarda localmente.
6. Si cierras la aplicación, puedes continuar desde el punto guardado.

Solo se mantiene una aventura activa por perfil.

## 8. Quizzes

1. Abre **Quizzes**.
2. Escoge materia, tema y cantidad de preguntas disponible.
3. Responde.
4. Envía el quiz.
5. Revisa explicación, errores y resultado.

Los resultados pueden alimentar el mastery del tema y el banco de estadísticas local.

## 9. Flashcards

1. Abre **Tarjetas**.
2. Crea tarjetas manuales o revisa propuestas antes de guardarlas.
3. Durante el repaso selecciona:
   - Otra vez;
   - Difícil;
   - Bien;
   - Fácil.
4. ALLEN calcula cuándo conviene volver a mostrarlas.

Las flashcards tienen repetición espaciada propia y no sustituyen la revisión de temas completos.

## 10. Simulacro

El simulacro sirve para practicar en condiciones más parecidas a una evaluación.

1. Abre **Simulacro**.
2. Selecciona materia, temas y configuración.
3. Empieza.
4. Responde sin pistas.
5. Finaliza para obtener puntaje y temas a reforzar.

Las respuestas y el tiempo restante se conservan para permitir reanudar una sesión interrumpida.

## 11. Biblioteca

La Biblioteca utiliza contenido local.

Puedes incorporar archivos compatibles dentro de `data/library/`.

Formatos soportados:

- Markdown;
- TXT;
- JSON.

La búsqueda actual usa ranking local por términos. El contenido puede utilizarse como referencia para el Tutor.

## 12. Cursos

Los cursos son experiencias guiadas creadas desde Teacher Studio.

### Empezar un curso

1. Abre **Cursos**.
2. Selecciona un curso publicado.
3. Pulsa la opción para iniciar o realizar el diagnóstico.
4. Completa el diagnóstico inicial cuando esté disponible.
5. ALLEN calcula el punto recomendado de inicio.
6. Sigue la ruta:
   **Descubre → Ejemplo → Recupera → Practica → Comprueba → Revisa**.

El progreso se guarda automáticamente.

## 13. Diagnóstico inicial

El diagnóstico intenta evitar que el estudiante repita contenido que ya domina.

Después de responder, los temas pueden quedar como:

- **strong**;
- **developing**;
- **weak**.

Los temas con evidencia suficiente de dominio pueden omitirse de la ruta inicial. El diagnóstico añade evidencia; no borra mastery previo.

## 14. Mastery y Evidence of Mastery

El porcentaje de mastery no debe interpretarse como una nota aislada.

ALLEN puede justificarlo usando:

- respuestas correctas;
- intentos;
- errores;
- pistas;
- prácticas;
- quizzes;
- examen;
- próxima revisión.

Ejemplo:

```text
CIDR — 64%

4/5 respuestas correctas
2 prácticas
1 pista utilizada
Próxima revisión: hoy
```

## 15. Repaso espaciado por tema

Además de flashcards, ALLEN programa revisión de temas completos.

Cuando un tema llega a su fecha de `next_review`, Inicio puede mostrarlo como pendiente. La recomendación puede colocarlo por delante de contenido nuevo.

## 16. Teacher Studio

Teacher Studio convierte material docente en un curso local.

### Crear un curso

1. Abre **Teacher Studio**.
2. Indica título, materia y nivel.
3. Importa un archivo:
   - PDF con texto extraíble;
   - TXT;
   - Markdown.
4. ALLEN crea un borrador.
5. Revisa unidades, temas, objetivos, preguntas, fuentes y examen.
6. Revisa el **Course Quality**.
7. Pulsa **Guardar revisión y aprobar**.
8. Cuando no existan bloqueos, pulsa **Publicar**.

Un borrador no debe publicarse sin pasar por Teacher Review.

## 17. Course Quality

Course Quality mide checks concretos del curso.

Puede revisar:

- cobertura de fuentes;
- objetivos medibles;
- temas evaluados;
- preguntas ambiguas;
- preguntas duplicadas;
- temas sin práctica;
- examen final;
- balance de unidades.

Un score alto no reemplaza la revisión humana. Los bloqueos sí pueden impedir publicación.

## 18. Curriculum Graph

ALLEN representa relaciones entre temas del curso, por ejemplo:

- `prerequisite`;
- `builds_on`;
- `related_to`.

El grafo ayuda a explicar por qué un tema anterior podría necesitar refuerzo.

Estas relaciones describen el curso importado; no deben interpretarse como una ontología universal de la materia.

## 19. Question Bank

Teacher Studio normaliza las preguntas del curso en un banco local.

Cada pregunta puede almacenar:

- tema;
- objetivo;
- dificultad;
- tipo;
- página fuente;
- respuesta;
- opciones;
- origen;
- estado;
- intentos;
- aciertos;
- errores.

Después de Teacher Review las preguntas pasan a `approved`.

Una tasa de aciertos demasiado alta o baja con suficiente uso puede servir como señal para que el profesor revise la pregunta.

## 20. Teacher Analytics

Dentro del área docente se pueden consultar métricas locales como:

- calidad del curso;
- inscripciones;
- finalizaciones;
- solicitudes de “No entendí”;
- temas débiles;
- hotspots de ayuda;
- posición actual de los estudiantes;
- tamaño y estado del Question Bank.

No se envía telemetría a servicios externos.

## 21. Versionado de cursos

No es necesario eliminar un curso para actualizar su material.

### Crear una nueva versión

1. Abre **Teacher Studio**.
2. Busca un curso existente.
3. Pulsa **Nueva versión**.
4. Selecciona el nuevo PDF, TXT o Markdown.
5. ALLEN crea automáticamente un snapshot.
6. Se genera un **Course Diff**.
7. La nueva versión queda en `draft`.
8. Revísala.
9. Apruébala.
10. Publícala.

### Course Diff

El diff separa:

- temas nuevos;
- temas modificados;
- temas sin cambios;
- temas eliminados.

También muestra un porcentaje estimado de progreso preservable.

Los temas sin cambios conservan progreso. Los temas modificados pueden pasar a `reviewing` sin borrar el mastery anterior.

## 22. Historial de versiones

Teacher Studio muestra versiones como `v1`, `v2`, etc.

Cada versión conserva:

- estructura;
- estado;
- fecha;
- diff respecto a la versión anterior.

Una actualización publicada no elimina automáticamente el historial previo.

## 23. Course Packs

Un curso publicado puede exportarse como `.allenpack`.

### Exportar

1. Abre Teacher Studio.
2. Busca un curso publicado.
3. Pulsa **Exportar .allenpack**.
4. Guarda el archivo.

### Importar

Al importar un Course Pack en otro ALLEN, entra nuevamente como `draft` y debe pasar por Teacher Review antes de publicarse.

## 24. Backups

El backup de ALLEN permite exportar y restaurar datos locales de la aplicación.

Incluye, entre otros:

- perfiles;
- progreso;
- planes;
- aventuras;
- mastery;
- cursos;
- diagnósticos;
- Question Bank;
- Course Quality;
- historial de versiones.

Antes de restaurar un backup, ALLEN crea un snapshot de seguridad del estado actual.

## 25. Recovery local

Recovery protege la base SQLite frente a actualizaciones o errores.

Abre **Configuración → Recovery local**.

Desde ahí puedes:

- diagnosticar la base;
- crear un snapshot;
- listar snapshots;
- restaurar uno.

ALLEN conserva hasta 5 snapshots recientes.

### Cuándo se crea un snapshot automáticamente

- antes de una migración;
- antes de crear una nueva versión de curso;
- antes de restaurar un backup;
- antes de restaurar otro snapshot.

## 26. Diagnosticar la base

En **Recovery local**, pulsa **Diagnosticar base**.

ALLEN ejecuta:

- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- lectura de schema version;
- estado de snapshots.

Si aparece **Base íntegra**, SQLite no reportó problemas en esas comprobaciones.

## 27. Migraciones SQLite

Las migraciones son automáticas al abrir una base antigua con una versión nueva de ALLEN.

El usuario normal no necesita ejecutarlas manualmente.

Antes de migrar:

1. ALLEN detecta la versión anterior.
2. Crea un snapshot.
3. Ejecuta las migraciones pendientes.
4. Registra las versiones aplicadas.
5. Conserva los datos existentes.

El esquema actual de Reliability Core es v10.

## 28. Privacidad

ALLEN está pensado para funcionar localmente.

Por defecto, la base vive fuera del repositorio, por ejemplo en Windows:

```text
%LOCALAPPDATA%\ALLEN\allen.sqlite3
```

No subas al repositorio:

- bases SQLite reales;
- modelos GGUF;
- tokens;
- archivos `.env`;
- datos personales de estudiantes.

## 29. Qué funciona sin IA

Aunque llama.cpp esté apagado, siguen disponibles muchas funciones:

- perfiles;
- cursos;
- rutas guiadas;
- quizzes;
- flashcards;
- Plan Allen;
- aventuras;
- simulacros;
- biblioteca;
- progreso;
- mastery;
- diagnosis;
- Course Quality;
- versionado;
- backups;
- recovery.

La IA local complementa el producto; no es la fuente única de funcionalidad.

## 30. Pruebas para desarrolladores

Python:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
node --test tests/*.mjs
```

La rama Reliability Core también incluye pruebas de migración, recuperación, Course Diff, versionado y flujo E2E de navegador.

## Documentación relacionada

- `README.md`: instalación, alcance y visión general.
- `docs/TEACHER_STUDIO.md`: arquitectura y flujo docente.
- `docs/LEARNING_INTELLIGENCE.md`: mastery, diagnóstico, grafo, preguntas y analytics.
- `docs/RELIABILITY_CORE.md`: migraciones, snapshots, recovery y versionado.
- `ARCHITECTURE.md`: arquitectura general.
- `SECURITY.md`: seguridad y privacidad.
