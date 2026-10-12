# Caminos escolares sin tiempo obligatorio

La app preparada ahora ofrece 14 rutas, 143 lecciones, 56 módulos y 471 preguntas base. El tutor local dispone de 1019 preguntas preparadas. Los contenidos son de refuerzo inicial y revisables; no representan un currículo oficial ni han recibido todavía validación docente externa.

## Materias añadidas

Cada nueva materia contiene cuatro módulos, ocho lecciones, dieciséis actividades de práctica, ocho comprobaciones y dos preguntas de diagnóstico. Cada lección incluye objetivo, explicación, ejemplo resuelto, explicación alternativa, dos pistas por actividad y tarjeta de repaso.

| Materia | Módulos |
| --- | --- |
| Geografía | Leer el espacio; Nuestro planeta; Ambiente y población; Panamá y conexiones |
| Historia | Ubicar hechos; Fuentes y explicaciones; Cambios y sociedades; Historia de Panamá |
| Biología | Células y organización; Funciones de la vida; Ecosistemas; Diversidad y adaptación |
| Física | Medir y describir; Movimiento y fuerzas; Energía; Electricidad y ondas |
| Química | Estructura de la materia; Sustancias y mezclas; Cambios; Interpretar representaciones |
| Ciudadanía | Convivir; Participar; Dialogar; Comunidad responsable |
| Técnicas de estudio | Preparar el aprendizaje; Entender información; Practicar y recordar; Trabajos escolares |
| Finanzas cotidianas | Decisiones diarias; Organizar dinero; Comparar compras; Pensar antes de decidir |

Las rutas anteriores de Matemáticas, lectura, Inglés, Ciencias, Python y Seguridad digital conservan sus identificadores, actividades y progreso. La ruta de Matemáticas tiene un nombre más amplio para incluir fracciones, decimales, porcentajes, álgebra y medidas.

Los módulos nuevos tienen entradas independientes: basta completar el diagnóstico de la materia para empezar cualquiera de sus cuatro bases. La segunda lección de cada módulo requiere comprobar la primera. Las respuestas correctas, las ayudas y las comprobaciones siguen las mismas reglas que las rutas existentes; conversar no desbloquea progreso.

## Elegir y alternar caminos

El formulario de creación de perfil permite elegir cualquiera de las catorce materias. Perfiles incluye un selector para cambiar la materia del perfil abierto. También se puede cambiar desde Aprender y desde las preferencias en Mi progreso. Hoy muestra los caminos utilizados cuando hay más de uno.

Cambiar de materia guarda la actividad pendiente en `savedSessions`, por identificador de curso, y restaura la de la materia seleccionada. El diagnóstico, los intentos, las respuestas enviadas, las pistas y la posición se conservan. Los borradores sin enviar siguen siendo temporales. No se mezcla información entre perfiles.

Las copias exportadas contienen también los caminos pendientes. Al recuperar se validan preguntas, curso, respuestas y prerrequisitos de cada sesión y se copian solo los campos permitidos. Las copias anteriores continúan siendo compatibles. Su campo histórico `minutes` puede conservarse como dato de compatibilidad, pero ya no interviene en la enseñanza ni aparece en los formularios. Los perfiles nuevos no lo almacenan.

No hay duración obligatoria por materia, contador ni elección de minutos. El camino consiste en estudiar, practicar, comprobar y repasar a ritmo propio. La hora opcional de los recordatorios sigue siendo una preferencia de notificación.

## Ejecución y verificación

```bash
python -m http.server 8080 --directory public
# Abrir http://localhost:8080/mobile/
node --test tests/*.mjs
python -m pytest -q
python android/build_web_assets.py
# Con JDK 17 y Android SDK 35:
cd android
./gradlew assembleDebug lintDebug
```

Pruebas específicas: creación de perfil sin minutos, elección inicial de Historia, cambio a Geografía con práctica pendiente, retorno al mismo ejercicio sin conexión, recarga, copia y recuperación de varios caminos, aislamiento y rechazo de sesiones con preguntas de otros cursos. La suite recorre las catorce rutas completas con el mismo motor. El diseño compacto se comprueba en Chromium. Resultado: 124 pruebas Python y 65 JavaScript aprobadas; compilación y lint Android correctos. Se comprobó también la firma del APK y que incluye el contenido y el motor actuales.

Android incluye los nuevos módulos en los assets, sin Python ni modelo generativo. Se incrementó `versionCode` a 6 y se conserva la identidad y firma de depuración existente. No se activaron cobros, telemetría ni servicios externos.

No había teléfono físico conectado: teclado, Atrás, selectores de archivos, notificaciones, batería y rendimiento Android real siguen pendientes de prueba física. Antes de actualizar, exportar una copia del progreso.

## Referencias históricas consultadas

Las fechas panameñas de las lecciones se contrastaron con fuentes institucionales:

- [Autoridad del Canal: historia en imágenes](https://pancanal.com/historia-en-imagenes-canal-de-panama/): apertura en 1914 y transferencia en 1999.
- [Ministerio de Relaciones Exteriores: contexto histórico](https://mire.gob.pa/images/PDF/Transmision_de_Mando_2019.pdf): independencia de España en 1821 y separación de Colombia en 1903.

Próximas mejoras: revisión docente de contenidos, actividades con más formatos visuales y variantes de transferencia específicas para las nuevas materias. Los intentos repetidos de estas lecciones rotan opciones, pero conservan el escenario preparado; no se presentan como problemas nuevos generados.
