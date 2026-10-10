> Informe del segundo incremento. La integración Android y el catálogo ampliado están en [MOBILE_ANDROID_INTEGRATION.md](MOBILE_ANDROID_INTEGRATION.md).

# ALLEN móvil: catálogo y tutor contextual

Segundo incremento sobre `feature/mobile-learning-pwa`. Los pagos quedan para el
final; no hay checkout, anuncios ni desbloqueos comerciales. No se cambia `main`
ni se publica una versión comercial.

## Implementado

- Cuatro cursos utilizables: fracciones (3 lecciones), comprensión lectora (2),
  inglés inicial (2) y Python básico (2). Total: 9 lecciones y 45 preguntas.
- Diagnóstico independiente por curso, explicación, ejemplo, práctica, dos pistas,
  comprobación y repaso, usando un único motor educativo y evidencia por tema.
- Catálogo con ilustraciones de la mascota, navegación con iconos, ejemplos de
  código legibles, celebración y texto ampliable persistente.
- Historial de dificultades en Practicar con feedback y acción para reforzar.
- Copias anteriores compatibles y preferencias locales editables. Cambiar perfil
  borra ayudas, respuesta generada y conexión temporal del tutor.
- Puente opcional al modelo local existente de escritorio, con contexto acotado,
  límite de recursos, timeout, protección de acceso y respuestas identificadas.
- Paquete de escritorio incluye los recursos móviles. Teacher Studio y su flujo
  de revisión continúan disponibles en la interfaz original.

Las ilustraciones SVG derivan de las variantes oficiales de ALLEN. Se adaptaron
las de inglés y programación con marcas EN y código, sin cambiar el mono naranja
ni usar imágenes realistas. Las capturas no contienen datos reales.

## Arquitectura y ejecución

Se mantiene la PWA como primera entrega Android instalable: motor en JavaScript,
progreso en IndexedDB y los cuatro cursos en caché local. El backend Python y la
inferencia no se ejecutan en el teléfono. No se duplica `LocalAI`: el nuevo puente
reutiliza su generador y sus reglas, con contenido del mismo catálogo.

Consultar [MOBILE.md](MOBILE.md) para instalación HTTPS en Android, uso estático,
acceso autenticado desde ALLEN, límites de privacidad y estrategia de migración.
El catálogo Python se genera con `node scripts/export_mobile_catalogue.mjs`;
una prueba comprueba que coincide exactamente con los módulos editoriales.

## Verificación realizada

- Suite Python: 109 pruebas en ejecución completa; la nueva prueba integrada de
  navegador contra FastAPI añade otra prueba aprobada (110 en total).
- Suite JavaScript: 42 pruebas aprobadas, incluyendo los cuatro recorridos,
  recuperación de backups y consistencia editorial del catálogo.
- Navegador Chromium: diagnóstico y las seis lecciones nuevas completados con
  red desactivada; recarga conserva progreso. Fracciones, tarjetas, exportación,
  recuperación, perfiles, fallos de almacenamiento y pestañas simultáneas siguen
  cubiertos. Verificación de anchos móviles en las pruebas existentes.
- Tutor: UI con respuesta simulada y prueba real navegador → FastAPI → generador
  de prueba. Se verifican token, acceso local, límites de solicitudes, contexto
  permitido, pérdida del modelo y continuidad de ayuda preparada. La generación
  no altera evidencia educativa.
- Ruff con selección CI `E9,F63,F7,F82` y Bandit sin hallazgos de severidad media
  o alta. La selección completa por defecto de Ruff encuentra deuda preexistente
  de estilo; no se presenta como corregida por este incremento.

## Alcance real y pendientes

Es una PWA funcional, no un APK nativo. No se ejecutó en un Android físico ni se
midió inferencia, memoria o batería en teléfonos. No se probaron pesos de un modelo
real: la integración usa dobles de prueba. Las explicaciones preparadas funcionan
sin IA y sin red, después de descargar el contenido inicial.

No hay IA remota, sincronización de perfiles ni importación de cursos docentes en
la PWA. El contenido es revisable y requiere validación pedagógica antes de una
publicación escolar. No existe corrección automática de respuestas abiertas ni
intérprete Python. La integración de distribución Windows se añadió al spec,
pero no se produjo ni probó un ejecutable Windows en este entorno.

Siguientes mejoras útiles: revisión docente del catálogo; pruebas de usabilidad
en Android; importar paquetes revisados y firmados de Teacher Studio; ampliar
comprensión lectora y retos; evaluación del tutor con el modelo elegido. Después,
resolver sincronización opcional y distribución nativa si las pruebas lo justifican.
Los pagos se integran al final con un proveedor y validación en servidor.

## Capturas

- [Catálogo de cursos](images/mobile/catalogue.png)
- [Tutor y respuesta simulada](images/mobile/tutor-local.png)
