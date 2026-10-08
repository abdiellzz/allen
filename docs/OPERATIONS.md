# Operación y mantenimiento

## Rutina recomendada

Antes de una actualización importante:

1. abre ALLEN;
2. comprueba **Configuración → Protección de datos**;
3. crea un snapshot;
4. exporta un backup si el equipo contiene datos importantes;
5. actualiza la aplicación.

## Backups

El backup exportable incluye datos funcionales del usuario y cursos. No incluye secretos.

Para restaurar:

1. Configuración;
2. Importar respaldo;
3. validar resumen;
4. confirmar;
5. ALLEN crea un snapshot previo;
6. restaura y valida.

## Recovery

ALLEN conserva hasta cinco snapshots recientes.

Usa Recovery cuando:

- una actualización falla;
- una migración produce un estado extraño;
- se necesita volver a un punto anterior;
- antes de probar una operación destructiva.

## Integridad

El diagnóstico ejecuta:

- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- lectura de versión de esquema.

## Cursos

Antes de actualizar material docente usa **Nueva versión**, no elimines el curso.

ALLEN crea snapshot, Course Diff y preserva progreso equivalente cuando es posible.

## Licencias

Para renovar una instalación:

1. abre el License Manager;
2. carga la licencia actual;
3. elige duración;
4. genera renovación;
5. entrega solo el nuevo `.license`;
6. el cliente lo importa en Configuración.

Nunca envíes la clave privada.

## Cambio de equipo

Una licencia está vinculada al Machine ID. Si cambia el equipo:

1. obtén el nuevo Machine ID;
2. reemite una licencia para el nuevo equipo;
3. conserva tus propios registros comerciales fuera de ALLEN.

## Logs

ALLEN rota logs locales y evita registrar contenido de conversaciones.

## Eliminación completa

Usa el eliminador incluido únicamente cuando se quiera borrar también los datos locales. Para una actualización normal no es necesario.
