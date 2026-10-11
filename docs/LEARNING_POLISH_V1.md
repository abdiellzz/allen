# ALLEN V1: práctica, comprensión y accesibilidad

## Qué incluye

- Repetir una lección alterna cuatro conjuntos finitos: original y tres variantes. En los seis temas de fracciones cambian números y situaciones, con respuestas, pistas y procedimientos derivados de los mismos parámetros. En las otras rutas cambia el orden de las opciones; todavía no hay situaciones nuevas para todas ellas. Los 119 identificadores originales y el diagnóstico permanecen compatibles.
- Tras dos errores recientes en un tema aparece ayuda contextual: explicación sencilla, otro ejemplo, recuperación de la base y un ensayo con apoyo. Este ensayo no desbloquea temas ni aumenta el dominio automáticamente. La actividad original permanece guardada.
- **Explícamelo tú**, al completar una lección, pide relacionar una explicación con su ejemplo justificativo. La reflexión no cambia la evaluación automáticamente; el estudiante puede escribir su propia explicación en el cuaderno.
- **Cuaderno de descubrimientos**, desde Mi progreso o la lección: una nota de hasta 800 caracteres por tema y una marca opcional de error comprendido. Se guarda por perfil y viaja en la copia JSON. Las notas se muestran como texto, nunca como HTML ni instrucciones del tutor.
- **Repaso combinado**, desde Practicar: hasta tres temas comprobados de la ruta activa, empezando por menor dominio estimado. Registra intentos y nuevas fechas de repaso; no añade comprobaciones ni desbloquea temas nuevos.
- Ajustes: tema claro/oscuro/del dispositivo, texto grande y menos movimiento. Lectura opcional de lecciones solo cuando existe una voz española identificada por el dispositivo como local; nunca se elige una voz remota como alternativa. La lectura se detiene al cambiar de pantalla, salir a perfiles o poner la app en segundo plano.
- Android: exportación mediante `ACTION_CREATE_DOCUMENT`, recuperación mediante el selector de documentos sin permiso general de almacenamiento. Solo se confirma una exportación después de escribir el archivo; cancelar o fallar conserva el progreso local. La copia es privada pero **no cifrada**. Android Atrás vuelve primero a la pantalla de origen general (actividad → Aprender, cuaderno → actividad cuando hay una pendiente; otras → Hoy); desde Hoy ofrece el cierre y luego permite salir.
- Menú accesible durante el desplazamiento; posición recuperada al regresar a una sección en la misma sesión y paneles abiertos conservados durante las actualizaciones de contenido. La posición no se promete tras cerrar el proceso.
- Dos ilustraciones nuevas: Allen pensando y Allen explicando. El logo original, lectura y celebración se conservan. Las ilustraciones nuevas se usan según el contexto, también offline.

## Compatibilidad y privacidad

Los nuevos campos son opcionales: copias anteriores siguen siendo válidas. Los identificadores de variantes permanecen resolubles, incluso en intentos históricos y sesiones a medio terminar. Las importaciones validan el conjunto de preguntas esperado, opciones, respuestas, temas, límites y preferencias antes de crear un perfil independiente. Las notas se limitan a campos conocidos. No hay telemetría, entrenamiento, modelos externos ni envío de preguntas; sigue funcionando el tutor con contenido preparado.

Exportar desde Android abre el selector del sistema: el usuario decide el destino. Elegir allí un proveedor de nube puede sacar la copia del dispositivo por decisión del usuario. ALLEN no la sube por su cuenta. No hay nuevos permisos en el manifiesto. Conserva una copia antes de cambiar de firma o desinstalar la APK.

## Ejecutar y verificar

```bash
node --test tests/*.mjs
python -m pytest -q
python android/build_web_assets.py
# JDK 17 completo, Android SDK 35 y Gradle 8.11.1
gradle -p android assembleDebug lintDebug
```

La vista web puede servirse desde `public/` con un servidor en localhost. PWA: primera descarga con conexión; después puede recargarse offline. APK: contenido incluido desde el inicio, sin servidor ni Python.

Validación realizada: pruebas de variantes y aritmética, recuperación a mitad de sesión, límites y aislamiento del cuaderno, rescate, repaso combinado, reflexión sin alterar dominio y dos flujos de navegador con IndexedDB y PWA offline. Revisión visual en 320, 375, 768 y 1440 px, incluyendo oscuro/texto grande. Compilación y lint de Android. El puente de exportación se verifica en navegador con un sustituto del contrato nativo; no equivale a una prueba física del selector Android.

Pendiente en teléfono real: escritura/recuperación con distintos proveedores de archivos, voces TTS, botón Atrás del sistema y entrega de recordatorios bajo restricciones de batería. Variantes de situaciones para inglés, lectura, tecnología y ciencias quedan para la siguiente expansión editorial.

## Ilustraciones

Generadas con la herramienta integrada de imágenes usando `public/mobile/assets/allen-reading.png` como referencia de identidad. Nuevos archivos: `public/mobile/assets/allen-thinking-v1.png` y `public/mobile/assets/allen-explaining-v1.png`. Fondo transparente; sin sustituir el logo.

Prompts: conservar el mismo mono naranja, rostro crema en forma de corazón, orejas redondas, ojos marrones ovalados, rubor, mechón y cola curva. Mismo estilo de caricatura con sombreado limpio, cuerpo completo centrado, sin realismo, texto ni marcas. Para **pensando**: sentado, mano en el mentón, cuaderno turquesa y sonrisa pensativa. Para **explicando**: libro turquesa abierto, mano en gesto de guía y sonrisa alentadora mirando al estudiante.
