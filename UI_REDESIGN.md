# Rediseño de ALLEN

Navegación: Inicio, Aprender, Practicar, Biblioteca, Progreso, Perfil y Configuración. Programación e Idiomas dejan de ser pestañas independientes; sus contenidos siguen disponibles por materia.

Componentes reutilizables: iconos Lucide locales, AllenMascot (saludo, lectura, estudio, pensamiento, celebración, error y sueño), AllenLoader, FeatureCard y EmptyState en frontend/components/ui.js. Sin CDN ni fuentes externas. Licencia y versión de Lucide en frontend/assets.

Bibliotecas propias: Biblioteca > Añadir mi biblioteca. JSON (objeto o lista con title, subject y content), Markdown o TXT, UTF-8, hasta 90 KB en la interfaz y 20.000 caracteres por lectura. Ejemplo en data/library-example.json. Se guardan en SQLite por perfil y se pueden eliminar desde la interfaz. La opción de consultar la biblioteca en el chat incluye las lecturas importadas.

Práctica: 10 preguntas distintas en cada tema no matemático; matemáticas genera preguntas sin repetir en el mismo quiz. Retroalimentación por pregunta y corrección final autoritativa en servidor; no se duplica XP al enviar un resultado dos veces. El quiz en curso dura durante la sesión de la página; recargar reinicia la interfaz.

Validación: 49 pruebas Python previas y 12 pruebas nuevas de cantidades, importación, aislamiento, rechazo de archivos inválidos y corrección. 7 pruebas JavaScript de Markdown y streaming. Verificación manual en navegador: inicio, navegación, configuración, quiz de Historia 5 preguntas, corrección inmediata, siguiente pregunta, importación JSON, búsqueda y lectura.
