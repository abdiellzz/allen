# ALLEN: actividades contextualizadas y sendero educativo

## Cambios

Se conserva el catálogo de 14 rutas, 56 módulos y 255 lecciones. Los modelos preparados de las actividades se ajustan a sus temas: equivalencia, comparación y operaciones con fracciones; porcentajes, proporciones, ecuaciones, promedios, densidad, escala, rapidez, fuerza, conservación de masa, presupuestos y precio por unidad. Química diferencia CO₂ y H₂O; inglés usa frases correspondientes a cada lección. Los temas que no disponen de una simulación apropiada ofrecen su caso y evidencia originales, sin fingir resultados físicos. La vista Aplica propone resolver un caso antes de abrir el procedimiento preparado.

Allen revisa la elección incorrecta registrada en el perfil y utiliza su retroalimentación y primera pista. Cuando existe una explicación específica del distractor, la incorpora; cuando no existe, revisa la regla sin atribuir una confusión o una capacidad no demostradas. Las preguntas relacionadas permiten continuar la conversación. El tutor sigue preparado, local y sin modelo generativo.

Aprender permite filtrar por materia, objetivo actual (Continuar, Reforzar, Explorar) y tipo de actividad (Bases, Desarrollo, Aplicación, Proyecto). Estas categorías describen las actividades, no califican al estudiante. Cambiar de materia conserva las sesiones y el progreso anteriores. Cuatro propuestas integran al menos tres materias: biblioteca accesible, huerto con evidencia, invitación segura y recorrido con unidades. Pueden trabajarse en papel o en el cuaderno; no se califican automáticamente.

Los rangos muestran ambos requisitos pendientes y ejemplos de objetivos ya comprobados. Conservan los umbrales y las ilustraciones existentes; el juego, las notas y los clics no conceden dominio ni rangos.

## El sendero de Allen

Desde Practicar, pulsa Jugar con Allen. Tres senderos recorren orientación, fracciones equivalentes y vocabulario en inglés. Un tablero didáctico de 6 × 6 admite botones táctiles y flechas de teclado cuando tiene el foco. Recoge tres páginas en orden, rodea rocas y utiliza la pista espacial si la necesitas. No hay cronómetro, vidas, anuncios ni clasificación competitiva.

La posición, páginas y sendero se guardan por perfil en IndexedDB, se incluyen en la copia de progreso y se validan al recuperar. La partida no escribe eventos educativos ni desbloquea cursos. Volver desde Android regresa a Practicar y conserva la partida. Tanto juego como tutor funcionan con recursos incluidos en la APK; en web, espera a que termine la descarga inicial del contenido offline.

## Cristal y accesibilidad

Cristal suave utiliza transparencia, bordes y un desenfoque limitado a navegación. Los paneles de lectura mantienen fondo opaco para preservar contraste. Ajustes → Superficies permite seleccionar Sólidas sin desenfoque; la preferencia se conserva en la copia del perfil. Reducir movimiento también desactiva el desenfoque. Los temas claro y oscuro y los textos ajustables siguen disponibles. No hay animación continua ni bucle de juego que consuma batería en reposo.

## Recursos generados

Modo: herramienta integrada de generación de imágenes. Referencia para el personaje: logo raster original de Allen, que permanece intacto. Prompts:

- `public/mobile/assets/allen-explorer-game-v1.webp`: conservar el mono naranja y crema, ojos marrones y mechón, ilustración indie no realista, brújula verde, cuaderno y bandolera discreta; fondo transparente, cuerpo completo, sin texto ni logotipo.
- `public/mobile/assets/allen-forest-game-v1.webp`: claro de bosque ilustrado desde arriba, musgo verde, piedras cálidas y libros en las esquinas, centro libre para un tablero dibujado por software; sin personajes, texto, laberinto ni interfaz.

Ambos archivos son conversiones WebP sin pérdida con igualdad de píxeles RGBA comprobada. Las casillas, obstáculos y etiquetas del juego se dibujan mediante HTML/CSS determinista, separados de la decoración generada.

## Ejecutar y verificar

Web: `python -m http.server 8000 --directory public`, abrir `/mobile/`. Pruebas: `node --test tests/*.mjs` y `python -m pytest -q`. Los casos nuevos comprueban modelos temáticos, divisores cero, retroalimentación por perfil, filtros, rangos, resolución de los tres tableros, límites, recuperación y persistencia sin conexión. Las pruebas de navegador cubren teclado, cambio de perfiles, tema oscuro y botón Atrás.

Android: `python android/build_web_assets.py`, seguido de Gradle `assembleDebug lintDebug`. Esta entrega incrementa versionCode a 8, incluye imágenes, CSS y módulos en los assets generados y mantiene el escritorio y backend sin cambios. Los pagos no están activos. La revisión en un teléfono físico sigue pendiente; la compilación y las pruebas de navegador no la sustituyen.

## Distribución

La APK completa se entrega directamente en la conversación. En GitHub se publica como `android/release/ALLEN-V1-Android.apk.xz`, por el límite de 16 MiB por petición del conector. La extracción reproduce byte por byte la APK verificada, incluida su firma. Consulta el README de esa carpeta: el archivo APK antiguo y su enlace de actualización no se sustituyen en esta publicación.
