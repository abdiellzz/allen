# Android: entrega V1 con páginas legales (versionCode 9)

La nueva APK incluye privacidad, términos, contacto, metadatos, errores personalizados, adaptación móvil y los cursos, tutor preparado y Sendero de Allen. Se distribuye en `ALLEN-V1-Android.apk.xz` por el límite de 16 MiB del conector de publicación. Extrae con 7-Zip o, en Linux:

```bash
xz -dk ALLEN-V1-Android.apk.xz
sha256sum ALLEN-V1-Android.apk
```

SHA-256 de la APK extraída: `6755cd43c6bdedeed2954c171690ce8f9bd130973ef7af401e109c178a78116e`.

**Esta entrega tiene una firma nueva.** La clave anterior no está disponible en el entorno; Android no permite actualizar directamente aquella instalación. Exporta y conserva tu progreso desde Mi progreso antes de desinstalar o reinstalar. La nueva app puede recuperar la copia. Conserva la app anterior si todavía no tienes una copia.

La nueva clave de demostración se guarda privadamente fuera de GitHub. Para futuras compilaciones configura `ALLEN_ANDROID_DEBUG_KEYSTORE` con su ruta absoluta y conserva la firma. No es una firma comercial definitiva.

**En GitHub, `ALLEN-demo-android.apk` conserva la entrega anterior.** El botón Descargar actualización sigue apuntando a ese archivo anterior; utiliza el comprimido de arriba o la descarga directa de la conversación para instalar esta entrega. No instales una versión anterior sobre la nueva.

Compilación y lint completos, firma verificada y todos los assets comprobados byte por byte. El funcionamiento físico en Android sigue pendiente. Más detalles en la documentación de la entrega Android legal.
