# ALLEN: refuerzo interactivo V1

La app móvil preparada incluye 79 lecciones, 24 módulos y 263 preguntas base en seis rutas. Se añadieron 48 lecciones completas; se conservaron los identificadores de los temas anteriores y sus diagnósticos para recuperar el progreso existente.

| Ruta | Módulos nuevos | Lecciones totales |
| --- | --- | --- |
| Matemáticas | Números cotidianos; Álgebra y medidas | 14 |
| Comprensión lectora | Comprender textos; Escribir con claridad | 13 |
| Inglés | Inglés cotidiano; Conversar y comprender | 13 |
| Python | Pensar con código; Organizar programas | 13 |
| Seguridad digital | Cuidar tu identidad; Usar tecnología con criterio | 13 |
| Ciencias | Materia y energía; Vida y ambiente | 13 |

Cada ruta también conserva Bases de la ruta y Aplicaciones. Aprender muestra módulos desplegables, objetivos, requisitos y botones que abren actividades reales.

## Interacciones y motor

Las nuevas actividades permiten completar respuestas, ordenar pasos mediante botones accesibles, relacionar conceptos y señalar errores. La evaluación comparte reglas entre la interfaz, el motor y la recuperación de copias: no ejecuta texto del estudiante. Las respuestas numéricas admiten coma decimal y ceros finales equivalentes. Los emparejamientos y órdenes requieren la relación o secuencia preparada correcta.

Una respuesta incorrecta sigue registrada como evidencia. La comprobación de transferencia controla la finalización del tema. Las ayudas nunca marcan una actividad como completada. Los motivos de distractores aparecen cuando existe una explicación editorial explícita; no se inventa un diagnóstico psicológico del estudiante.

Allen responde sobre la actividad actual y puede ofrecer un primer paso, un ejemplo y una explicación sencilla. El chat usa contenido preparado y reglas locales, no un modelo entrenado ni IA generativa. Incluye 571 preguntas preparadas. Las imágenes originales de Allen permanecen disponibles.

Hay representaciones de fracciones, pistas de lectura desplegables y ejemplos de programas con estados preparados por línea. Los ejemplos de código son ilustrativos y no se ejecutan. Hoy explica qué tema y actividad quedaron pendientes y permite continuar.

## Persistencia y Android

Los módulos, las imágenes y el tutor están incluidos en la APK y la caché de la PWA. El progreso confirmado, las ayudas y la sesión se guardan por perfil en IndexedDB. Los borradores de respuesta sin enviar se conservan durante cambios de vista, pero no sobreviven a cerrar o recargar la app. Exportar y recuperar utiliza los selectores nativos existentes; no modifica perfiles ajenos. No hay telemetría ni envío de respuestas a servidores.

La versión de escritorio permanece independiente. Android usa la app preparada en WebView, sin iniciar Python ni descargar un modelo. Conserva el manejo de Atrás, restauración de posición, ajuste de teclado y recordatorios locales opcionales. Se incrementó el código de versión Android a 5. No se activaron pagos.

## Ejecutar y comprobar

```bash
python -m http.server 8080 --directory public
# Abrir http://localhost:8080/mobile/
node --test tests/*.mjs
python -m pytest -q
python android/build_web_assets.py
# Con JDK 17 y Android SDK 35 configurados:
cd android
./gradlew assembleDebug lintDebug
```

Se ejecutaron 122 pruebas Python existentes, una prueba adicional de navegador para completar, relacionar y ordenar sin conexión, y 62 pruebas JavaScript. Estas verifican persistencia, contexto del tutor, retroalimentación, requisitos, validación de copias y aislamiento existente. La compilación y lint Android terminaron correctamente. La APK publicada es de depuración para probar V1.

No había teléfono ni emulador Android disponible. Siguen pendientes las pruebas físicas de teclado, Atrás, rotación, selectores de archivos, permisos y entrega de notificaciones, memoria y batería. La prueba de cambio de dimensiones en Chromium no sustituye una prueba de rotación real.

Antes de instalar o actualizar en un teléfono, exportar una copia del progreso. Revisar con docentes los contenidos y ampliar evaluaciones de transferencia con estudiantes antes de una publicación comercial.
