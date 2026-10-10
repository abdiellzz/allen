# ALLEN: identidad y un solo inicio educativo

## Qué cambió

- El encabezado utiliza el PNG original del usuario, sin reconstruirlo con formas. El encuadre del mono se hace con CSS; el archivo conserva sus bytes originales. También se usa en favicon, manifest y recurso de icono Android.
- Las cinco secciones están en un menú desplegable: Hoy, Aprender, Practicar, Allen y Mi progreso. Se cierra al elegir una opción, al tocar fuera o con Escape. Mantiene controles de al menos 44 px y foco visible.
- Contenedor de hasta 1200 px, títulos e ilustraciones centrados, inicio compacto y tarjetas menos altas. En teléfono los seis cursos se exploran horizontalmente, con flechas y desplazamiento táctil. Las lecciones, misiones y evidencia detallada se despliegan a petición.
- Tocar ALLEN muestra una orientación basada en la siguiente actividad y una pequeña animación. No modifica aciertos ni dominio; respeta la preferencia de movimiento reducido. La ayuda editorial y el tutor conservan su contexto educativo.
- `/`, `/index.html`, `/fair` y los HTML antiguos de inicio redirigen a `/mobile/`. Android inicia la misma experiencia y sus alias de inicio también la abren. Se retiraron Inicio del menú administrativo, Modo Feria de Ajustes y el enlace a la interfaz alternativa en Perfiles.
- Los datos y APIs heredados no se eliminan. Teacher Studio y las herramientas de escritorio se mantienen en `/teacher`, con los permisos existentes. No se fusionan automáticamente sus perfiles SQLite con los perfiles IndexedDB móviles.

## Imágenes y procedencia

Original: `public/mobile/assets/allen-user-logo.png`, `frontend/assets/allen-user-logo.png` y `android/app/src/main/res/drawable/allen_logo_original.png`. SHA-256 de las tres copias: `c502f657fde9d854cf98cdec8b03b1c031ed7c296fd7869fb0d71d61bd3794e1`.

Las siguientes ilustraciones se generaron con la herramienta integrada **ImageGen**, tomando el logo adjunto como referencia. Fondo transparente y estilo 2D; son poses complementarias, no sustituciones del logo.

### ALLEN leyendo

Archivo: `public/mobile/assets/allen-reading.png`.

Prompt usado:

> Use case: identity-preserve illustration-story. Reference image is the user's official ALLEN orange monkey logo. Create one high quality 2D cartoon illustration asset for an educational app. Preserve this exact monkey's visual identity: orange rounded head, cream heart-like face, oval dark brown eyes, small dark nose, smile, peach cheeks, cream round belly, ears and single swept orange tuft, curled tail. Do not replace with generic SVG shapes or a different monkey. The monkey is sitting comfortably reading a small open teal book, looking warmly at the viewer, one hand holding the book. Friendly clean cartoon shading like reference, not photorealistic, no 3D, no overly childish accessories. Full body centered with compact composition, transparent background, no text, no wordmark, no business branding, no border, no panel, no decorative gradients. This is a companion illustration only: the original user-provided file will remain the actual app logo.

### ALLEN celebrando

Archivo: `public/mobile/assets/allen-celebrate.png`.

Prompt usado:

> Use case: identity-preserve illustration-story. The reference is the official ALLEN mascot. Generate one isolated 2D cartoon educational app illustration of this exact orange monkey celebrating a learner's progress with a small friendly raised hand and warm smile. Preserve the identity precisely: orange body, cream heart-like face, cream round belly, peach cheeks, dark brown oval eyes and nose, single swept orange tuft, same rounded ears, curled tail. Match the clean soft 2D shading of the reference. Full body centered, compact pose, transparent background. No words, logo text, slogan, business typography, confetti, costume, photorealism, 3D, invented characters or exaggerated features. The original logo remains unchanged; this is a separate interactive companion pose.

## Ejecutar y comprobar

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m http.server 8081 --directory public
```

Abrir `http://localhost:8081/mobile/`. Crear un perfil, esperar «Curso guardado · listo sin conexión», hacer el diagnóstico y probar los repasos con la red desactivada. La caché v4 instala también las imágenes; el progreso conserva el esquema anterior.

Para escritorio usar el lanzador habitual de ALLEN: `/` abre la experiencia educativa y `/teacher` mantiene las herramientas administrativas. Para preparar Android:

```bash
python android/build_web_assets.py
cd android
./gradlew assembleDebug
```

## Verificación y límites reales

- Suite Python: **118 pruebas aprobadas**; JavaScript: **43 aprobadas**. Ruff y Bandit según los comandos de CI sin errores bloqueantes. La prueba visual y de navegación se repitió tras ajustar la posición del desplegable.
- Chromium: ciclo educativo, persistencia, aislamiento de perfiles, caché offline, ayuda sin modelo, menú con Escape, mascota sin alteración del progreso y ausencia de desbordamiento horizontal a 320, 390, 768 y 1440 px.
- Capturas: [inicio](images/mobile/home-compact.png), [menú](images/mobile/menu-compact.png), [catálogo escritorio](images/mobile/catalogue-desktop.png), [catálogo móvil](images/mobile/catalogue.png), [tutor](images/mobile/tutor-local.png).
- No hay Android SDK en este entorno: no se compiló ni probó un APK nuevo, ni se reemplazó el APK publicado. El icono Android queda pendiente de inspección real en dispositivo.
- IA generativa en Android: no disponible; la ayuda preparada sigue funcionando. La conexión al modelo local del escritorio continúa siendo opcional y explícita. Sin pagos, telemetría externa ni despliegue comercial nuevos.
- Próxima comprobación: compilar y probar instalación/actualización con la misma firma, verificar icono de launcher, persistencia y memoria en teléfonos reales.
