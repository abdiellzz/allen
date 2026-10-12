# Android V1: páginas legales y errores

Esta compilación (versionCode 9) incluye las páginas de privacidad, términos, contacto, 404 y ayuda dentro de la APK, junto con metadatos por sección, errores recuperables y estilos responsive. No necesita conexión para leer estas páginas. Enviar correo o abrir las fuentes externas requiere una aplicación y conexión apropiadas.

La entrada educativa utiliza el nuevo cargador y mantiene los cursos, el tutor preparado, el juego, los perfiles y las copias de progreso. El botón Atrás desde las páginas legales vuelve por el historial de WebView; las acciones nativas de aprendizaje solo están habilitadas en la entrada educativa. Una navegación interna inexistente recibe la página 404 local con rutas de recursos correctas y una CSP que no permite scripts. No se cambia el permiso de Internet ni los datos del estudiante.

## Firma e instalación

La clave utilizada para la APK anterior no está disponible en este entorno. Esta entrega usa una nueva clave de demostración. Mantiene el identificador de la app, pero Android no permite actualizar directamente la instalación con firma anterior. Exporta el progreso desde Mi progreso y conserva esa copia antes de desinstalar o reinstalar. Si Android rechaza la instalación, conserva la app anterior hasta tener la copia. Después puedes recuperar la copia en la nueva instalación; se crea un perfil nuevo.

Se entrega una copia privada de la nueva clave fuera del repositorio. No debe publicarse. En próximas compilaciones utiliza `ALLEN_ANDROID_DEBUG_KEYSTORE` con la ruta absoluta de ese keystore para conservar esta firma. El alias y las contraseñas son los habituales de la clave Android de demostración; no es una firma comercial definitiva. Sin la variable, Gradle conserva su comportamiento debug estándar.

## Compilar y probar

Con JDK 17, Gradle 8.11.1, Android SDK 35 y build-tools 34:

```bash
python android/build_web_assets.py
# Define ALLEN_ANDROID_DEBUG_KEYSTORE fuera del repositorio antes de compilar.
cd android
gradle assembleDebug lintDebug
```

Las páginas y la copia de assets se verifican con las pruebas de navegador y de paridad. La comprobación de la APK compara todos los assets empaquetados con los generados y verifica la firma y la versión. El funcionamiento físico de Android, incluida la instalación, el correo y Atrás, sigue pendiente de prueba en un teléfono. La APK completa se entrega directamente; en GitHub se distribuye comprimida sin alterar sus bytes por el límite del conector. El enlace antiguo de Descargar actualización sigue apuntando a la APK anterior.
