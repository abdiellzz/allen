---
name: apk-build
description: Regenera los assets web de la APK de Android, compila el APK release no depurable y lo firma con la clave de ALLEN. Úsala después de cambiar public/mobile/ o android/, antes de probar en un teléfono, o cuando pidan "compilar", "generar", "build" o "publicar" la APK. Informa la ruta del APK, su versión y SHA-256, o el error exacto.
---

# apk-build

Compila y firma la APK de demostración de ALLEN y reporta el resultado.

## Requisitos

- Python 3 (el builder solo usa la biblioteca estándar y no descarga nada).
- JDK 17 (`JAVA_HOME` apuntando a un JDK 17; lo usan Gradle, `keytool` y `apksigner`).
- Android SDK con platform 35 y build-tools (`android/local.properties` con `sdk.dir`, o
  `ANDROID_HOME`).
- Material de firma en `%LOCALAPPDATA%\allen-android-signing` (o `ALLEN_ANDROID_SIGNING_DIR`). Si no
  existe, **detente y avisa**: solo se crea una vez con `python android/sign_release.py init` y
  crear otro en una máquina distinta rompería las actualizaciones de todos los usuarios.

## Pasos

Ejecuta desde la raíz del repositorio.

1. Regenera los assets (borra y vuelve a crear `android/app/src/main/assets/www/`, que nunca se edita
   a mano):

   ```powershell
   python android/build_web_assets.py
   ```

   Debe terminar con `assets listos en android/app/src/main/assets/www (N MB)`.

2. Compila el APK release (sin firmar; nunca depurable):

   ```powershell
   Push-Location android; .\gradlew.bat assembleRelease; $code = $LASTEXITCODE; Pop-Location; exit $code
   ```

   La primera compilación puede tardar varios minutos: ejecútala con un timeout amplio (10 min).

3. Firma y verifica. Copia el resultado a `android/release/ALLEN-demo-android.apk` y escribe su
   `.sha256`:

   ```powershell
   python android/sign_release.py
   ```

   Falla si el APK es depurable, declara permisos o la línea de rotación no va de la clave
   publicada (`a2e095c7…`) a la de `android/release/signing-certificate.sha256`.

Para una versión que se va a publicar, antes del paso 2 sube `allenApkRevision` y
`allenApkVersionCode` en `android/gradle.properties`.

## Informe

- **Éxito:** versión (`1.2.4-android-demo.N`), tamaño en MB y SHA-256 que imprime el paso 3.
- **Error:** paso que falló, comando y líneas relevantes (para Gradle, el bloque
  `What went wrong:`). Causas comunes: `JAVA_HOME` sin JDK 17, SDK platform 35 ausente,
  `sdk.dir` incorrecto, falta el material de firma.

## No hacer

- No publicar ni copiar a `android/release/` un APK de `assembleDebug`: es depurable.
- No hacer commit de `assets/www/`, `android/app/build/` ni de nada de la carpeta de firma.
- No ejecutar `sign_release.py init` si ya existe material de firma en otra máquina.
- No editar `android/build_web_assets.py`, `sign_release.py` ni Gradle para "arreglar" el build sin
  reportarlo antes.
