# ALLEN Reliability Core

Esta fase endurece ALLEN para conservar progreso y cursos durante meses de uso local.

## 1. Migraciones numeradas

ALLEN mantiene un `user_version` de SQLite y aplica migraciones numeradas desde `backend/migrations.py`.

Versión actual: **10**.

Las versiones 9 y 10 introducen:

- historial de versiones de cursos;
- historial de migraciones.

Antes de migrar una base existente, ALLEN crea automáticamente un snapshot local.

## 2. Recovery local

Los snapshots se guardan junto a la base de datos en:

```text
%LOCALAPPDATA%\ALLEN\recovery
```

o el directorio equivalente del sistema.

ALLEN conserva las 5 copias más recientes.

La recuperación usa la API de backup de SQLite en vez de copiar una base abierta de forma insegura.

Antes de restaurar un snapshot, ALLEN crea otra copia del estado actual.

El panel de Configuración puede:

- ejecutar `PRAGMA integrity_check`;
- ejecutar `PRAGMA foreign_key_check`;
- mostrar la versión del esquema;
- crear un snapshot manual;
- listar snapshots;
- restaurar una copia sana.

## 3. Versionado de cursos

Un curso conserva historial en `course_versions`.

Al importar una nueva fuente para un curso existente, ALLEN:

1. crea un snapshot de seguridad;
2. procesa el nuevo archivo con el mismo pipeline;
3. compara temas por identidad normalizada;
4. clasifica:
   - sin cambios;
   - modificados;
   - nuevos;
   - eliminados;
5. calcula cuánto progreso puede conservarse;
6. crea una nueva versión en estado `draft`;
7. conserva mastery de temas sin cambios;
8. marca temas modificados como `reviewing` para estudiantes inscritos;
9. remapea el punto de progreso cuando el mismo tema sigue existiendo;
10. obliga a pasar otra vez por Teacher Review antes de publicar.

La UI muestra un **Course Diff** antes de que el profesor publique la actualización.

## 4. Compatibilidad

Los cursos creados antes de esta fase reciben automáticamente una versión inicial al abrir la base actualizada.

Los respaldos antiguos de formato `allen-backup` que no incluían historial de versiones siguen siendo restaurables. ALLEN reconstruye una versión base desde el curso almacenado.

## 5. Alcance

Esta fase no implementa sincronización cloud ni edición colaborativa. El objetivo es que una instalación local sea segura, recuperable y actualizable.

Una nueva versión de un curso entra en estado borrador y debe revisarse/publicarse otra vez. Esto evita publicar silenciosamente cambios derivados de un documento nuevo.
