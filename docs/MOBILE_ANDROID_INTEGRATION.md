# Integración Android y ampliación educativa

Se integran las aportaciones de Sebastián de `main` en la rama
`feature/mobile-learning-pwa`: demo Android, Pyodide, constructor de recursos,
APK publicado y correcciones de iconos. Base revisada:
`74a5ce94471cfd693817cacc501a41cda790fdf4`; trabajo móvil previo:
`31a2f6f11df49ac41138c830508c693d12246048`.

## Cambios funcionales

- Seis cursos gratuitos: fracciones, lectura, inglés, Python, seguridad digital
  y ciencias. Trece lecciones y 65 preguntas editoriales con diagnósticos,
  explicación, ejemplo, práctica, feedback, comprobación y repasos.
- Buscador por objetivo y filtros por área, con estado sin resultados.
- Misiones de aplicación en Practicar. Cada misión abre una práctica del último
  tema del curso; se respetan diagnóstico y prerrequisitos. No es un motor nuevo
  ni una simulación libre: mantiene el mismo registro de evidencia.
- Mapa de aprendizaje con temas comprobados y bases pendientes.
- Código Android inicia directamente la interfaz educativa móvil. La interfaz
  original se conserva para administración en escritorio (`/teacher`); ya no
  se ofrece desde Perfiles. Ver [UI_SINGLE_HOME.md](UI_SINGLE_HOME.md).
- La pantalla móvil no inicia Pyodide: cursos y progreso funcionan con assets
  empaquetados e IndexedDB. No necesita service worker dentro del APK.
- El worker de la interfaz original serializa solicitudes y confirma escrituras
  después de completar `syncfs`. Los errores de guardado se informan al cliente
  en vez de ocultarse y anunciar éxito antes de persistir.
- Exportación móvil en Android mediante JSON seleccionable para copia manual;
  no se presenta como descarga nativa. La PWA sigue descargando un archivo JSON.

No se implementaron pagos. No se cambiaron guardas de seguridad o licencias del
escritorio. Se conserva la configuración **demo** de Android aportada por
Sebastián: sin licencia, sin PIN docente y sin IA generativa. Esta demo no debe
presentarse como distribución comercial ni como espacio docente protegido.

## Datos y compatibilidad

| Interfaz | Motor | Almacenamiento | Inferencia |
| --- | --- | --- | --- |
| PWA web | Proyección JS de reglas educativas | IndexedDB y caché estática | Modelo local de escritorio solo con conexión explícita |
| Móvil en APK | Mismo motor JS y cursos empaquetados | IndexedDB del WebView | Ayuda editorial; sin modelo |
| Interfaz original en APK | Backend existente en Pyodide | SQLite sobre IDBFS | Modo demo |
| Escritorio | FastAPI y motor Python existentes | SQLite original | IA local opcional |

Los perfiles móviles y los de la interfaz original son independientes; no se
migran, sincronizan ni mezclan automáticamente. El ID de la aplicación Android
se conserva. Para actualizar manteniendo datos hace falta la misma firma del APK;
no desinstales antes de guardar una copia. No hay sincronización cloud ni
telemetría añadida.

Las copias previas de fracciones y de los cuatro cursos siguen aceptadas. El
catálogo es ampliable mediante módulos editoriales; después de modificarlo,
ejecutar `node scripts/export_mobile_catalogue.mjs`. El backend recibe ese mismo
snapshot en `allen-src.zip`, sin duplicar lógica de evaluación.

## Ejecutar

PWA, desde la raíz:

```bash
python -m http.server 8081 --bind 127.0.0.1 --directory public
```

Abrir `http://localhost:8081/mobile/`. Esperar la descarga completa antes de
cortar la red. Para instalación PWA en un teléfono, usar HTTPS.

Recompilación Android con Python, JDK 17 y Android SDK platform 35:

```bash
node scripts/export_mobile_catalogue.mjs
python android/build_web_assets.py
cd android
./gradlew assembleDebug
```

El APK generado queda en `android/app/build/outputs/apk/debug/app-debug.apk`.
No se reemplazó `android/release/ALLEN-demo-android.apk`: ese binario sigue siendo
la demo anterior de Sebastián, conservada sin cambios. No incluye automáticamente
los cursos e interfaz nuevos por subir estos archivos fuente.

## Verificación y límites

- 116 pruebas Python y 43 JavaScript aprobadas.
- Los cinco cursos posteriores a fracciones se completan en Chromium sin red:
  10 lecciones; progreso conservado después de recargar. Fracciones y repasos
  mantienen las pruebas anteriores.
- Se comprueban búsqueda, filtros, misiones, mapa, backup manual y ausencia de
  solicitudes al backend en el modo empaquetado, simulando su marcador en un
  navegador. También se prueba el empaquetado de ambas interfaces sin descargas.
- Prueba del worker con filesystem simulado: orden de solicitudes, espera de
  sincronización y propagación de errores. No sustituye una prueba real de IDBFS
  bajo Pyodide/WebView.
- Paridad del motor Python/JS, aislamiento de perfiles, recuperación, pérdida de
  almacenamiento, integración del tutor y límites de acceso siguen aprobados.
- Ruff con reglas CI y Bandit sin hallazgos de severidad media o alta.

No hay SDK Android en este entorno: **no se recompiló ni ejecutó un APK nuevo**.
Tampoco se probó Pyodide/WebView en un dispositivo, inferencia real o batería.
El contenido está preparado para revisión docente, no certificado como currículo.
Teacher Studio continúa siendo preferible desde computadora. No se añadió
importación de cursos al motor móvil, corrección de texto libre ni ejecución de
Python del estudiante.

## Capturas

- [Catálogo ampliado](images/mobile/catalogue.png)
- [Misiones](images/mobile/missions.png)
- [Tutor contextual con respuesta de prueba](images/mobile/tutor-local.png)

Siguiente paso práctico: recompilar con la firma existente, probar la actualización
sin borrar datos en un Android real y revisar los cursos con un docente. Después,
importación de paquetes docentes revisados y misiones con producciones del alumno.
