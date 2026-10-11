# Android: entrega contextual y Sendero de Allen

La APK nueva (versionCode 8) se distribuye en `ALLEN-V1-Android.apk.xz`. Está comprimida sin alterar la APK ni su firma porque el conector de publicación limita cada petición a 16 MiB. Extrae el archivo con 7-Zip o, en Linux:

```bash
xz -dk ALLEN-V1-Android.apk.xz
sha256sum ALLEN-V1-Android.apk
```

SHA-256 de la APK extraída: `55f0bd858338357f1d8d5649a543e093e1cdf942604c7a70b6016dcc2a1faea5`.

Esta entrega añade acompañamiento contextual, actividades por tema, filtros, proyectos, cristal suave y tres senderos educativos. El chat usa respuestas preparadas y funciona sin IA generativa. Las pruebas de teléfono físico siguen pendientes.

**En GitHub, `ALLEN-demo-android.apk` conserva la entrega anterior.** El enlace Descargar actualización de las APK existentes apunta todavía a ese archivo anterior; para esta versión utiliza el archivo comprimido de arriba o la descarga directa entregada en la conversación. No reinstales una versión anterior sobre la nueva. Guarda una copia de tu progreso antes de instalar y conserva la app instalada si Android rechaza una actualización por firma.
