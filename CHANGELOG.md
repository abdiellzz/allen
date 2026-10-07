# Changelog

Todos los cambios relevantes de ALLEN se documentan aquí.

## [1.0.0] — 2026-10-07

Primera versión estable de ALLEN.

### Experiencia de aprendizaje
- Tutor educativo local y privado en español.
- Plan Allen, Aventuras, Quizzes, Flashcards, Biblioteca y Simulacro.
- Continuidad de aprendizaje y recomendaciones locales.
- Cursos con diagnóstico inicial, rutas guiadas y Evidence of Mastery.
- Repaso espaciado por tema y progreso persistente.
- Learning Journey gráfico por unidad.
- Dashboard de progreso con mastery, tiempo activo, materias y actividad reciente.

### Teacher Studio
- Importación de PDF, TXT y Markdown.
- Revisión explícita antes de publicar.
- Course Quality, Curriculum Graph y Question Bank.
- Teacher Analytics.
- Course Packs portables.
- Versionado de cursos, historial y Course Diff con conservación de progreso.

### Fiabilidad y privacidad
- SQLite local con migraciones versionadas.
- Snapshots rotativos y Recovery local.
- Backups exportables e importables.
- Sin cuentas obligatorias ni APIs de pago.
- Modelo local opcional mediante llama.cpp/GGUF.
- CSP, TrustedHost, protección de acciones con token local y límites de tamaño.

### Interfaz
- Modos Estudiante y Profesor.
- Home con continuidad, recomendaciones y mastery explicable.
- Command Palette con Ctrl/Cmd + K.
- Dark mode persistente.
- Responsive verificado en 1920×1080, 1440×900, 1366×768, 900×800, 640×900 y 390×844.
- Estados de carga con skeletons, errores recuperables, empty states y focus-visible.
- Respeto a prefers-reduced-motion.

### Calidad
- Suite frontend con Node test.
- Suite Python y pruebas E2E con Playwright.
- Flujos E2E de cursos, Teacher Studio, versionado, diagnóstico, Recovery, búsqueda y tema.
