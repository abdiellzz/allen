# Changelog

Todos los cambios relevantes de ALLEN se documentan aquí.

## [Unreleased]

## [1.2.1] — 2026-10-07

### Seguridad
- Protege la API local con un secreto efímero por ejecución y cookie HttpOnly/SameSite=Strict.
- Verifica criptográficamente la licencia anterior antes de renovarla en License Manager.
- Actualiza pypdf a 6.19.0 y cryptography a 50.0.2.
- Añade pip-audit a CI y Dependabot semanal.
- Fija GitHub Actions a SHAs inmutables y limita GITHUB_TOKEN a lectura.
- Endurece permisos del PEM privado en Linux/macOS.
- Añade cabeceras COOP/CORP, X-Frame-Options y Permissions-Policy.


### Repositorio y documentación
- Limpieza de scripts raíz obsoletos anteriores a la distribución 1.2.0.
- Documentación reorganizada bajo `docs/`.
- Nuevas guías de instalación, arquitectura, desarrollo, operación, releases y troubleshooting.
- Tutorial operativo ampliado para License Manager en Windows y Linux.
- Workflow de tests simplificado a `main` y pull requests.
- Reglas de higiene para impedir secretos, licencias emitidas y artefactos generados.
- Prueba automática de estructura/documentación del repositorio.

## [1.2.0] — 2026-10-07

### Licencias offline
- Activación obligatoria mediante archivo `.license` firmado con Ed25519.
- La instalación muestra un Machine ID estable y privado.
- Cada licencia queda vinculada a un Machine ID específico.
- Fechas de inicio y vencimiento firmadas: reinstalar ALLEN no reinicia la licencia.
- Renovación mediante un nuevo archivo sin reinstalar ni perder datos.
- Detección básica de retroceso del reloj del sistema.
- Perfiles, estudiantes y profesores sin límite por instalación.
- Nuevo panel de licencia en Configuración.
- Nuevo ALLEN License Manager privado para crear y renovar licencias.
- La clave privada no se incluye en ALLEN ni en el repositorio.

## [1.1.1] — 2026-10-07

### Eliminación completa
- Nuevo archivo `Eliminar ALLEN completamente.bat` incluido en el Portable y el instalador.
- Confirmación explícita escribiendo `BORRAR` antes de eliminar datos.
- Elimina instalación, perfiles, progreso, SQLite, backups, snapshots, configuración local, accesos directos y temporales propios de ALLEN.
- Ejecuta primero el desinstalador oficial cuando existe para limpiar correctamente el registro de Windows.
- El portable elimina también su propia carpeta y `ALLEN-Data`.
- No elimina modelos GGUF ni instalaciones externas de llama.cpp.


## [1.1.0] — 2026-10-07

### Distribución Windows
- Nuevo ejecutable empaquetado con runtime propio mediante PyInstaller.
- Nuevo paquete Portable para Windows x64; los datos viven en `ALLEN-Data` junto a la aplicación.
- Nuevo instalador por usuario con Inno Setup, accesos directos y desinstalador.
- El instalador conserva perfiles, progreso y backups en `%LOCALAPPDATA%\ALLEN` al desinstalar.
- Launcher gráfico con acciones para abrir y cerrar ALLEN sin depender de una consola.
- Nuevo workflow de GitHub Actions que construye y publica ambos artefactos.
- Self-test del ejecutable empaquetado antes de generar los paquetes.


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
