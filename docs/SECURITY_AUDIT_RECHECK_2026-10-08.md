# Segunda auditoría técnica — ALLEN 1.2.3

**Fecha:** 8 de octubre de 2026  
**Base revisada:** ALLEN 1.2.2  
**Fuente:** informe técnico de ALLEN 1.2.1 y revisión adicional de código/CI.

## Resultado

Los cinco hallazgos críticos y los siete hallazgos altos del informe original fueron revalidados contra `main` 1.2.2.

### Críticos

| Hallazgo | Estado |
| --- | --- |
| Launcher roto por `start_local_ai` eliminado | Corregido |
| Respuestas de examen/diagnóstico expuestas | Corregido |
| Simulacros exponen respuestas | Corregido |
| Backup puede mezclar conversaciones | Corregido |
| Deadline puede generar millones de días | Corregido |

### Altos

| Hallazgo | Estado |
| --- | --- |
| Mezcla de UTC/hora local | Corregido |
| Progreso falsificable / simulacro no idempotente | Corregido |
| Falta de transacciones y WAL | Corregido en operaciones críticas |
| Sin rol real docente/estudiante | Corregido con PIN + sesión servidor |
| Modo Feria comparte API/token | Corregido |
| CSP rompe estilos inline | Corregido y cubierto por navegador real |
| Error visible de Tarjetas | Corregido y cubierto por navegador real |

## Medios revalidados

- Caché de licencia: corregida.
- Límite de request condicionado a licensing: corregido.
- Simulacros con temas inválidos/solo primer tema: corregido.
- Moderación por fragmentos: corregida con contexto acumulado.
- Inflado de tiempo de estudio: corregido con deduplicación/rate limit.
- Backups: exportación cifrada AES-256-GCM disponible y flujo UI cifrado por defecto.
- Clave privada de licencias: el generador exige PEM cifrado para firmar.
- Machine ID: reforzado con segundo factor cuando está disponible y compatibilidad con licencias 1.2.x.
- Build Windows: ejecuta self-test de imports y smoke test real del servidor empaquetado.
- CI: compileall, Ruff, pip-audit y Playwright real.

## Correcciones de esta segunda pasada

### Biblioteca

`Library.documents()` ya no recorre y relee toda la biblioteca en cada búsqueda. Mantiene caché y solo recalcula al cambiar fingerprint de archivos.

### Calidad pedagógica

Course Quality ahora marca:

- objetivos que siguen usando la plantilla genérica;
- opciones inválidas/duplicadas;
- distractores que coinciden con respuestas correctas de otras preguntas.

El generador dejó de usar fragmentos reales de otros temas como distractores.

## Pendientes estructurales honestos

No se consideran “corregidos” porque requieren una fase de arquitectura propia:

1. dividir `backend/app.py` en routers/repositorios;
2. modularizar `frontend/app.js` y unificar helpers de escape;
3. optimizar Teacher Analytics para reducir consultas por curso;
4. migrar búsqueda de biblioteca a SQLite FTS5 si el catálogo crece mucho;
5. añadir firma Authenticode del ejecutable/instalador;
6. generar lockfiles con hashes para dependencias;
7. habilitar/proteger reglas de rama, CodeQL y secret scanning desde la configuración de GitHub cuando estén disponibles.

Estos puntos son deuda técnica o hardening de distribución; no invalidan las remediaciones críticas anteriores.
