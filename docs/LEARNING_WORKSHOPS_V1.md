# Talleres y métodos de aprendizaje — V1

El catálogo móvil contiene 14 rutas, 56 módulos, 255 lecciones y 807 preguntas base. Se añaden 112 talleres y proyectos: dos por módulo, manteniendo los identificadores anteriores y sus variantes. Cada módulo tiene entre cuatro y seis lecciones. El tutor conserva respuestas preparadas; no requiere un modelo generativo ni un ordenador.

## Experiencia

Cada lección ofrece seis vistas: Entiende, Explora, Construye, Aplica, Explícalo y Recuerda. Trece modelos de actividad se adaptan al contenido: fracciones manipulables, cálculos, lectura con pistas, construcción de frases, seguimiento de programas, decisiones, experimentos conceptuales, procesos, mapas, líneas de tiempo, átomos, planificación y presupuestos. Los talleres incluyen procedimientos ordenados, relaciones entre pasos y un caso de aplicación con retroalimentación específica.

Las exploraciones y notas se guardan por perfil en IndexedDB y se incluyen en la exportación. No producen dominio ni corrigen automáticamente texto libre. Los modelos de experimentos son representaciones conceptuales, no mediciones; el seguimiento de programas explica pasos preparados y no ejecuta código. Las explicaciones comprobadas utilizan reglas y ejemplos seleccionables existentes.

## Rangos personales

| Rango | Temas comprobados | Explicaciones comprobadas |
| --- | ---: | ---: |
| Explorador | 0 | 0 |
| Aprendiz | 5 | 1 |
| Constructor | 15 | 3 |
| Analista | 35 | 5 |
| Mentor | 70 | 10 |

Se requieren ambos umbrales. Una explicación cuenta una vez por tema ya completado. No son certificados, clasificaciones entre estudiantes ni recompensas por clics o rachas.

## Ilustraciones

Cinco imágenes originales generadas con la herramienta integrada de generación de imágenes, usando como referencia el logo raster existente de Allen. Prompts: conservar el mono naranja y crema, proporciones e identidad, ilustración no realista, fondo transparente, sin texto; Explorador con lupa y libro, Aprendiz con lápiz y cuaderno, Constructor con bloques, Analista comparando tarjetas y Mentor explicando con libro. Los archivos `public/mobile/assets/rank-*.webp` son conversiones sin pérdida con píxeles RGBA verificados contra los originales. El logo original permanece intacto.

## Ejecución y comprobación

Vista web: `python -m http.server 8000 --directory public`; abrir `/mobile/`. El primer acceso web requiere cargar los recursos para permitir el siguiente acceso sin conexión. Android incluye los recursos desde la instalación y utiliza el almacenamiento y exportación nativos ya existentes.

Pruebas: `python -m pytest -q` y `node --test tests/*.mjs`. Los nuevos casos comprueban todos los métodos, límites y aislamiento de datos por perfil, persistencia sin conexión, notas sin calificación automática, evidencias y rangos. La selección de materias mantiene el progreso de las demás rutas.

APK: `python android/build_web_assets.py`, después Gradle `assembleDebug lintDebug` desde `android/`. Versión Android 7. No se modifican backend, escritorio, permisos remotos ni sistemas comerciales. Los pagos siguen sin estar activos. La comprobación en un teléfono Android físico sigue pendiente; las pruebas de navegador y compilación no la sustituyen.
