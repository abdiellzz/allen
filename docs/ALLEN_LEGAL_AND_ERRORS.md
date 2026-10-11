# Páginas legales, contacto y errores

El sitio y la PWA incluyen privacidad, términos, contacto, error general y 404 personalizados. Correo de contacto indicado por el propietario: iallenbussinesss@gmail.com. Los textos describen la versión educativa preparada actual; no afirman que el tutor sea generativo, que los perfiles tengan autenticación o que las copias estén cifradas.

Se distinguen datos locales, alojamiento web, enlaces externos y correo Gmail. Referencia oficial consultada para derechos de protección de datos en Panamá: https://antai.gob.pa/preguntas-frecuentes-de-proteccion-de-datos-personales/. No se añade una sociedad, domicilio o condiciones comerciales no proporcionados por el propietario.

Las páginas están disponibles en la raíz de la web y en /mobile/, donde se incluyen en la caché offline y en los assets de una próxima compilación Android. Vercel sirve public/404.html automáticamente para rutas inexistentes. public/error.html es una página de ayuda; no se afirma que sustituya los errores 5xx de la infraestructura de Vercel. Dentro de la PWA, navegaciones móviles no disponibles usan el fallback 404/503 del service worker; no se cachean APIs o archivos privados.

Cada página HTML tiene título y metadatos propios. Las secciones de la app actualizan título, descripción y metadatos sociales sin incluir nombres o datos de estudiantes. Un fallo de módulos o almacenamiento ofrece una pantalla con reintento explícito. Los errores de acciones permanecen visibles hasta que se descartan, con ayuda y sin repetir automáticamente operaciones de escritura.

Se refuerzan breakpoints de 480 y 768 px y el rango tablet. Los enlaces de contacto permiten partir líneas para evitar desbordes. No se añaden scripts ni estilos inline ni se debilita CSP. La aplicación de correo solo se abre al pulsar el enlace mailto; no se envían mensajes automáticamente.

Para revisar: servir public/ con python -m http.server 8000 --directory public. Abrir /privacidad.html, /terminos.html, /contacto.html y /404.html; en /mobile/ revisar los enlaces del pie, títulos al navegar y disponibilidad offline tras completar la preparación. La APK de la entrega anterior no se modifica: estas páginas llegarán a Android al regenerar los assets y recompilar con la misma clave de firma.
