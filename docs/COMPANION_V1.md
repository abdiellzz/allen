# Acompañamiento de Allen y cierre de V1

El chat propone dos preguntas relacionadas después de cada respuesta. Reconoce «No entendí», «Dame un ejemplo», «¿Cómo voy?» y «¿Qué hago después?». Las sugerencias se mantienen en el tema elegido. Las decisiones sobre evaluación siguen en el motor educativo; conversar no desbloquea cursos.

Allen aparece en una tarjeta dentro de cada pantalla de estudio. Su consejo responde al estado real: inicio, pista utilizada, respuesta correcta, error o actividad terminada. Se puede minimizar por perfil; no hay animaciones permanentes, temporizadores de motivación ni mensajes que interrumpan una respuesta. Se usan las imágenes originales existentes.

Practicar ofrece tres misiones de aproximadamente cinco minutos: medidas de una receta, mensajes sospechosos y condiciones de un programa. Abren una lección de la ruta correspondiente, con sus dos prácticas y comprobación. La duración depende del ritmo del estudiante; no existe un contador que lo presione. Los diagnósticos y prerrequisitos siguen siendo obligatorios. «Preparar esta misión» abre sus bases; nunca descarta una sesión pendiente.

«Terminar por hoy» presenta actividades y aciertos del día, comprobaciones superadas, dificultades recientes y el siguiente paso con su razón. Solo usa evidencia guardada del perfil activo. El diagnóstico no se presenta como dominio y un repaso fallido no se cuenta como logro. El botón Atrás de Android muestra este cierre; pulsarlo otra vez permite salir. Al pasar al fondo se conserva un resumen para el próximo recordatorio, si fue autorizado. No se puede garantizar que Android ejecute JavaScript si termina abruptamente el proceso; cada respuesta educativa ya está guardada antes de ello.

## Recordatorios de Android

Ajustes → Recordatorios → elegir hora → Activar. Android 13 o posterior solicita `POST_NOTIFICATIONS` al pulsar Activar. Rechazarlo no afecta al aprendizaje. Desactivar cancela tanto el aviso visible como la siguiente alarma. Son preferencias del dispositivo, no del progreso de un curso.

Se programa una alarma inexacta diaria local, con `setAndAllowWhileIdle`, sin permisos de alarma exacta, conexión a Internet ni servidor. Los horarios siguen la zona horaria del teléfono y se reprograman tras reiniciar o cambiar hora/zona. Se evita avisar mientras ALLEN está abierto y no se envía más de un recordatorio diario. Android puede retrasar la entrega por ahorro de batería; forzar la detención impide recibirlo hasta volver a abrir la app. La entrega con el teléfono bloqueado, después de reiniciar y bajo restricciones de distintos fabricantes requiere prueba física.

El aviso usa la imagen original de Allen. El texto incluye un consejo preparado y, cuando existe, el cierre anterior sin nombre. La pantalla bloqueada usa una versión pública genérica, sin detalles de aprendizaje. Cambiar, importar o borrar perfiles limpia el resumen nativo. Desactivar también lo elimina. No hay seguimiento externo. La vista web explica el alcance y no promete notificaciones con el navegador cerrado.

## Compilación

JDK 17 completo, SDK Android 35 y Gradle 8.11.1. Ejecutar `python android/build_web_assets.py` y `cd android && ./gradlew assembleDebug lintDebug`. La compilación educativa predeterminada empaqueta contenido preparado sin descargar Pyodide. `python android/build_web_assets.py --legacy-runtime` conserva el ensamblado del runtime de demostración anterior. No se editan los assets generados a mano.

APK de pruebas: paquete `com.allen.tutor.demo`, versión interna 3. No es una publicación comercial. Para actualizar una instalación anterior Android exige la misma firma. La clave privada de otra persona no está disponible en este entorno; no se garantiza que esta firma de pruebas coincida con su APK. Exportar una copia antes de cambiar de instalación evita depender de esa coincidencia. No desinstalar una app con progreso sin una copia recuperable.

## Verificación

Pruebas del motor y del tutor, cierre por perfil y día, bloqueo de misiones, continuación del chat, IndexedDB, navegación móvil y funcionamiento offline. La interfaz de consentimiento nativo se comprueba desde el navegador con un puente simulado; esa prueba no demuestra entrega real de notificaciones. Compilar y analizar Android no sustituye probar en un dispositivo físico.
