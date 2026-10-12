# Auditoría de seguridad de la APK — 2026-10-11

Alcance: APK de demostración publicado (`1.2.4-android-demo`, versionCode 2), su código fuente
(`android/`), la experiencia móvil que muestra (`public/mobile/`) y su proceso de compilación. La APK
la usan niños, así que el criterio principal es que su progreso no salga del teléfono ni sea
accesible para terceros.

Resultado: corregido en `1.2.4-android-demo.1` (versionCode 3).

## Hallazgos y correcciones

| # | Severidad | Hallazgo | Corrección |
| --- | --- | --- | --- |
| 1 | Alta | El APK publicado era **depurable** (`android:debuggable=true`) y estaba firmado con la **clave de depuración** (`CN=Android Debug`). Con el teléfono y un cable USB se podía leer el almacenamiento de la app (`adb run-as`) y controlar la WebView con DevTools: ver o falsificar el progreso de cualquier perfil. La clave de depuración no está protegida y solo existía en una máquina. | Release no depurable (`debuggable false`, R8). Clave de release RSA-4096 fuera del repo y de OneDrive. Rotación APK Signature Scheme v3 desde la clave anterior, sin capacidad de *rollback*. `android/sign_release.py` firma y rechaza APK depurables, con permisos o sin la rotación correcta. |
| 2 | Media | El APK incluía `allen-src.zip` con los 42 archivos del backend en texto plano (licencias, seguridad, cifrado de backups), Pyodide y la interfaz de escritorio, aunque la experiencia móvil no los usaba: unos 20 de los 25,6 MB. Código de un repositorio privado al alcance de quien recibiera el APK. | El builder solo empaqueta `public/mobile/` con una lista de tipos permitidos. Se retiró el puente Pyodide (`android/web/`). Gradle se niega a compilar si encuentra assets antiguos. APK: 3,4 MB. |
| 3 | Media | El builder descargaba los archivos principales de Pyodide sin verificar su hash. `pyodide-lock.json`, que aporta los hashes del resto, tampoco se verificaba. | Sin descargas: el builder ya no usa la red. Gradle verifica su distribución con `distributionSha256Sum`. El wrapper coincide con el oficial y lo comprueba un test. |
| 4 | Media | Publicación sin garantías: un binario compilado en local, sin CI, y una actualización sin forma de comprobar la firma. | Workflow `android-apk`: compila la release desde el código fuente y verifica el APK publicado. Se publican el SHA-256 del APK y el del certificado. La app explica que Android solo acepta actualizaciones firmadas por ALLEN. |
| 5 | Baja | La página del APK no tenía CSP: la de Vercel va en cabeceras y la WebView no envía cabeceras. Además, algunos textos de los cursos llegaban a `innerHTML` sin escapar. | CSP `default-src 'none'` inyectada por el builder antes de cualquier recurso. Los textos de los cursos y los identificadores se escapan. |
| 6 | Baja | `allowBackup="false"` no bloquea la transferencia entre dispositivos en Android 12+. | `data_extraction_rules.xml` excluye todo de la copia en la nube y de la transferencia. |
| 7 | Baja | Los enlaces externos se abrían con cualquier esquema, y las peticiones fuera de los assets se delegaban a la red. | Solo se cargan URLs `https://appassets.androidplatform.net`; el resto se responde con 403. Solo los enlaces `https` salen, y siempre al navegador. Permisos web y geolocalización denegados. |

## Verificación

- `apksigner`: esquemas v2 y v3 válidos. Firmante para Android 9+: `CN=ALLEN Android`
  (`94342140…b4729f`). Línea de rotación `Android Debug → ALLEN Android`, sin *rollback*.
- `aapt2`: sin `debuggable`, sin permisos, `allowBackup=false`, `dataExtractionRules` y
  `usesCleartextTraffic=false`.
- Emulador Android 15:
  1. Se instaló el APK anterior y se creó un perfil con progreso.
  2. Se instaló el parche encima con `adb install -r`. El progreso se conservó.
  3. `run-as` respondió `package not debuggable`.
  4. Un APK firmado solo con la clave de depuración fue rechazado
     (`INSTALL_FAILED_UPDATE_INCOMPATIBLE`).
  5. «Descargar actualización» se abrió en Chrome.
- Pruebas automáticas (`tests/test_android_demo.py`): manifiesto, release, Gradle, WebView, contenido
  del APK y CSP. La prueba E2E sirve los assets sin cabeceras, como la WebView, y comprueba que no hay
  errores de CSP, que no se hacen peticiones externas y que un nombre de perfil con HTML no se
  ejecuta.
- Revisión visual (`apk-review`): 12 vistas sin desbordes ni errores de consola.

## Riesgos residuales y decisiones

- **Android 8.x (API 26–27)** no entiende la rotación de firma: en esos teléfonos la clave de
  depuración sigue siendo válida para actualizar. Proteger `legacy-debug.keystore` igual que la clave
  de release. Cuando no queden usuarios con Android 8, subir `minSdk` a 28.
- **Material de firma:** si se pierde `%LOCALAPPDATA%\allen-android-signing`, ninguna versión futura
  podrá instalarse encima de las existentes. Necesita una copia offline.
- **Datos heredados:** quien usó la interfaz original en versiones antiguas de la APK puede conservar
  una base SQLite en el almacenamiento privado de la WebView. Ya era inaccesible desde la app antes de
  este parche. No se borra automáticamente porque no se puede recuperar; desaparece al desinstalar.
- **Demo sin PIN:** los perfiles no tienen PIN y la copia exportada es JSON sin cifrar ni firmar, así
  que puede editarse. El progreso móvil no es evidencia verificable para calificar. Firmar la copia
  con una clave guardada en el propio APK no aportaría autenticidad real.
- **Imágenes de emulador `userdebug`** activan DevTools en todas las WebViews; los teléfonos
  comerciales (`user`) no.
