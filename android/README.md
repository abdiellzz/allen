# ALLEN para Android (demo)

APK de demostración con la experiencia educativa móvil de ALLEN, dentro del teléfono, sin servidor y
sin Internet.

## Cómo funciona

```text
WebView (assets del APK, origen https://appassets.androidplatform.net)
  └── public/mobile/ → experiencia educativa (cursos, diagnóstico, práctica, tarjetas, progreso)
        └── android-extras.mjs → recorrido guiado y «Actualizar ALLEN» (solo en la APK)
```

- Los perfiles se guardan en IndexedDB del WebView, dentro del almacenamiento privado de la app.
- El APK no incluye Python, el backend de escritorio ni la interfaz de escritorio.

## Seguridad y privacidad

ALLEN lo usan niños; la APK está pensada para que su progreso no salga del teléfono:

- **Sin permisos de Android**, ni siquiera Internet. La WebView solo carga los archivos del APK por
  `https`; cualquier otra petición se bloquea, y los permisos web (cámara, micrófono, ubicación) se
  deniegan siempre.
- **Sin copias automáticas:** ni copia en la nube de Google ni transferencia al cambiar de teléfono
  (`res/xml/data_extraction_rules.xml`). El progreso solo sale si el usuario exporta su copia.
- **Compilación de release, no depurable:** no permite `adb run-as` ni DevTools sobre la WebView.
- **CSP estricta** en la página (`default-src 'none'`, sin scripts en línea), añadida por el builder
  porque la WebView no envía cabeceras HTTP.
- Solo los enlaces `https` (la descarga de actualizaciones) salen al navegador; otros esquemas se
  ignoran.
- Las copias de progreso importadas se validan campo a campo y se recuperan como un perfil nuevo.

Limitaciones asumidas de la demo: los perfiles no tienen PIN (cualquiera con el teléfono desbloqueado
puede abrirlos), la copia exportada es JSON sin cifrar, y el progreso del móvil no es evidencia
verificable para calificar.

## Firma y actualizaciones

| Versión | Firma |
| --- | --- |
| hasta 1.2.4-android-demo | Clave de depuración (`CN=Android Debug`, SHA-256 `a2e095c7…cc7eda4`) |
| desde 1.2.4-android-demo.1 | Clave de release (`CN=ALLEN Android`, SHA-256 en [release/signing-certificate.sha256](release/signing-certificate.sha256)) con rotación v3 desde la clave anterior |

La rotación permite instalar el parche encima de la versión anterior **sin perder el progreso** en
Android 9 o superior, y desde entonces Android rechaza actualizaciones firmadas solo con la clave de
depuración. Android 8.x no entiende la rotación: sigue verificando la clave anterior.

El SHA-256 del APK publicado está en
[release/ALLEN-demo-android.apk.sha256](release/ALLEN-demo-android.apk.sha256).

## Descargar e instalar

**[Descargar ALLEN-demo-android.apk](https://github.com/abdiellzz/allen/raw/main/android/release/ALLEN-demo-android.apk)**
(3,4 MB · Android 8.0 o superior). El repositorio es privado: el enlace funciona con una sesión de
GitHub que tenga acceso.

1. Descarga el APK en el teléfono, o en el PC y pásalo al teléfono por cable, Drive o WhatsApp.
2. Abre el archivo desde **Descargas** o **Archivos**.
3. Si Android avisa que no permite instalar apps desconocidas, pulsa **Configuración**, activa
   **Permitir de esta fuente** y vuelve atrás.
4. Pulsa **Instalar**. Si Play Protect avisa que la app no es conocida, elige
   **Más detalles → Instalar de todas formas**. Es normal: la demo no está publicada en Google Play.
5. Abre **ALLEN** y crea tu perfil.

Actualizar: instala el APK nuevo encima del anterior; los datos se conservan. Desde la app,
**Perfiles → Actualizar ALLEN** muestra la versión instalada y abre esta misma descarga en el
navegador del teléfono. La app no tiene permiso de Internet, así que no puede comprobar por sí sola
si hay una versión más reciente. Si Android dice que el paquete entra en conflicto o que la firma no
coincide, **no lo instales ni desinstales ALLEN**: ese APK no está firmado por ALLEN.

Desinstalar la app borra todos sus datos del teléfono. Antes de cambiar de teléfono, exporta la
copia de cada perfil desde **Mi progreso**.

## Qué funciona y qué no

El APK abre únicamente la experiencia educativa: seis cursos, diagnóstico, práctica, tarjetas,
tutor preparado, progreso y recuperación por perfil. Teacher Studio y el resto de ALLEN siguen en la
versión de escritorio. Ver [UI_SINGLE_HOME.md](../docs/UI_SINGLE_HOME.md).

- No hay IA generativa en el teléfono: Allen responde con explicaciones y pistas preparadas.
- La copia del progreso se exporta como texto JSON; no hay guardado nativo de archivos.

## Compilar y publicar

Requisitos: Python 3, JDK 17 y Android SDK (platform 35 y build-tools). No hace falta Internet
salvo para la primera descarga de Gradle, verificada con `distributionSha256Sum`.

```bash
python android/build_web_assets.py          # arma android/app/src/main/assets/www (sin descargas)
cd android
./gradlew assembleRelease                    # Windows: gradlew.bat assembleRelease
cd ..
python android/sign_release.py               # firma, verifica y copia a android/release/
```

`sign_release.py` falla si el APK es depurable, declara permisos o no lleva la rotación de la clave
publicada a la de release. Antes de publicar, sube `allenApkRevision` y `allenApkVersionCode` en
[gradle.properties](gradle.properties).

La clave de release vive fuera del repositorio, en `%LOCALAPPDATA%\allen-android-signing`
(`ALLEN_ANDROID_SIGNING_DIR` para otra ruta), junto con su contraseña, la clave anterior y la línea
de rotación. Solo se crea una vez (`python android/sign_release.py init`). **Guarda una copia offline
de esa carpeta:** si se pierde, ninguna versión futura podrá instalarse encima de las existentes.
Para que otra persona publique, compártele la carpeta por un canal seguro; nunca la subas al
repositorio.

Para pruebas locales sigue existiendo `assembleDebug`, pero ese APK es depurable y nunca se publica.
