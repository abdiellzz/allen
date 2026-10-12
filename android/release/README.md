# APK publicada de ALLEN

`ALLEN-demo-android.apk` es la única descarga oficial: compilación release **no depurable**, firmada
con la clave de release de ALLEN. Incluye la experiencia completa (cursos, tutor preparado, Sendero de
Allen, páginas legales, exportación del progreso y recordatorios opcionales).

- SHA-256 del APK: [ALLEN-demo-android.apk.sha256](ALLEN-demo-android.apk.sha256).
- SHA-256 del certificado de firma: [signing-certificate.sha256](signing-certificate.sha256).

## Actualizar sin perder el progreso

| Versión instalada | Qué hacer |
| --- | --- |
| Hasta `1.2.4-android-demo` (firma original) | Instala encima: Android 9+ acepta la nueva firma por rotación y conserva los datos |
| `1.2.4-android-demo.1` o posterior | Instala encima |
| Entregas «guided» o «V1» de prueba (versionCode 7–9, otra clave de depuración) | Android no permite instalar encima: en **Mi progreso**, exporta la copia, desinstala, instala esta APK y recupera la copia |

Si Android avisa de un conflicto o de una firma distinta con otra versión, no instales ese archivo.

## Permisos

Solo dos, ambos para los recordatorios opcionales y locales: notificaciones (se piden al activarlos)
y volver a programarlos tras reiniciar el teléfono. La app no tiene acceso a Internet.
