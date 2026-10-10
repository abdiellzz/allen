---
name: apk-build
description: Regenera los assets web de la APK de Android y compila el APK debug de ALLEN. Úsala después de cambiar android/web/ o android/app/src/main/res/, antes de probar en un teléfono, o cuando pidan "compilar", "generar" o "build" de la APK. Informa la ruta del APK generado o el error exacto.
---

# apk-build

Compila la APK de demostración de ALLEN y reporta el resultado.

## Requisitos

- Python 3 (el del sistema sirve; el builder solo usa la biblioteca estándar).
- JDK 17 (`java -version` debe decir 17; si no, apunta `JAVA_HOME` a un JDK 17).
- Android SDK con platform 35 (`android/local.properties` con `sdk.dir`, o `ANDROID_HOME`).
- Internet solo la primera vez: el builder descarga Pyodide y wheels a `android/.cache` y verifica
  su SHA-256. Las siguientes ejecuciones usan la caché.

## Pasos

Ejecuta desde la raíz del repositorio.

1. Regenera los assets (borra y vuelve a crear `android/app/src/main/assets/www/`, que nunca se edita
   a mano):

   ```powershell
   python android/build_web_assets.py
   ```

   Debe terminar con `assets listos en android/app/src/main/assets/www (N MB)`. Si falla, detente y
   reporta el error (hash incorrecto, sin red, `HTML sin </head>`…). No sigas al paso 2.

2. Compila el APK debug:

   ```powershell
   Push-Location android; .\gradlew.bat assembleDebug; $code = $LASTEXITCODE; Pop-Location; exit $code
   ```

   En bash: `cd android && ./gradlew.bat assembleDebug` (Windows) o `./gradlew assembleDebug`.
   La primera compilación puede tardar varios minutos: ejecútala con un timeout amplio (10 min).

3. Comprueba el resultado:

   ```powershell
   Get-Item android/app/build/outputs/apk/debug/app-debug.apk | Select-Object FullName, Length, LastWriteTime
   ```

   Confirma que `LastWriteTime` es de esta ejecución (si no, el APK es viejo y la compilación no
   lo actualizó).

## Informe

- **Éxito:** ruta absoluta de `android/app/build/outputs/apk/debug/app-debug.apk`, tamaño en MB,
  hora de generación y tamaño de los assets reportado en el paso 1.
- **Error:** paso que falló, comando y las líneas relevantes del error (para Gradle, el bloque
  `What went wrong:`). Causas comunes: `JAVA_HOME` sin JDK 17, SDK platform 35 ausente,
  `sdk.dir` incorrecto, sin red en la primera ejecución.

## No hacer

- No copiar el APK a `android/release/ALLEN-demo-android.apk` salvo que lo pidan: ese archivo es el
  del enlace público de descarga.
- No hacer commit de `assets/www/`, `android/.cache/` ni `android/app/build/` (están ignorados).
- No editar `android/build_web_assets.py` ni Gradle para "arreglar" el build sin reportarlo antes.
