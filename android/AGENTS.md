# AGENTS.md — APK de ALLEN

Reglas para trabajar en la APK de Android. Complementan el [AGENTS.md](../AGENTS.md) de la raíz; en
caso de conflicto dentro de `android/`, prevalece este archivo.

## Qué es la APK

Una WebView que muestra la experiencia educativa móvil (`public/mobile/`) desde los assets del APK,
sin Python, sin backend y sin Internet. La usan niños: **su progreso nunca debe salir del teléfono
sin una acción explícita del usuario.** Detalle en [README.md](README.md).

## Alcance

- Diseño exclusivo de la APK: `public/mobile/android-extras.mjs` y `android-extras.css` (solo se
  cargan dentro de la APK) y `android/app/src/main/res/` (`values/themes.xml`, `drawable/`,
  `mipmap-*`).
- Cambios en el resto de `public/mobile/` afectan también a la PWA web: coordínalos.
- `android/app/src/main/assets/www/` es una **copia generada** e ignorada por git. Nunca editarla a
  mano: se regenera con `python android/build_web_assets.py`.
- El builder copia solo tipos permitidos (`.html`, `.mjs`, `.css`, `.webmanifest`, `.png`, `.svg`)
  de `public/mobile/`. Un archivo nuevo de otro tipo no llegará al APK sin cambiar el builder.

## Reglas de seguridad (no negociables)

- **Nada de permisos de Android** en el manifiesto, ni siquiera `INTERNET`.
- **Nunca publicar un APK depurable ni firmado con la clave de depuración.** Se publica solo con
  `assembleRelease` + `python android/sign_release.py`, que lo verifica.
- No volver a empaquetar Python, el backend, la interfaz de escritorio ni descargas en el APK.
- No debilitar la CSP que inyecta el builder (`default-src 'none'`, sin `'unsafe-inline'` ni
  `'unsafe-eval'`): nada de scripts en línea ni `style="…"` en HTML generado; usar clases.
- Todo texto que llegue a `innerHTML` pasa por `escape()`, aunque hoy venga del propio APK.
- No reactivar copias en la nube ni transferencia entre dispositivos
  (`res/xml/data_extraction_rules.xml`).
- La WebView solo carga `https://appassets.androidplatform.net`; los enlaces externos solo pueden
  ser `https` y salen al navegador.
- La clave de release, su contraseña y la línea de rotación viven fuera del repo
  (`%LOCALAPPDATA%\allen-android-signing`). Nunca subir `*.jks`, `*.p12`, `*.keystore` ni
  `lineage.bin`.

## Dirección visual

Patrones móviles tipo Duolingo/Headspace: una columna, acciones principales abajo y feedback claro.
Los colores son los tokens de `:root` en `public/mobile/mobile.css` (`--green`, `--orange`,
`--line`, `--muted`, `--card`, `--tint`); usa siempre el token.

- Texto mínimo 16px (también en inputs, evita zoom); área táctil mínima 48×48px; espaciado en
  múltiplos de 4px; margen lateral 16px.
- Sin desborde horizontal; respetar `env(safe-area-inset-*)` y `prefers-reduced-motion`.
- Contraste AA (4.5:1 texto, 3:1 iconos y bordes de control) en claro y oscuro.

## Verificación

1. `python -m pytest -q tests/test_android_demo.py tests/test_mobile_e2e.py`.
2. Capturas 375×812 en claro y oscuro (skill `apk-review`).
3. Compilar y firmar (skill `apk-build`); el script de firma falla si el APK es depurable, pide
   permisos o no lleva la rotación de clave correcta.
4. Antes de publicar, subir `allenApkRevision` y `allenApkVersionCode` en `gradle.properties` y
   probar la actualización encima de la versión anterior (los datos deben conservarse).
5. Skill `scope-check` antes de cada commit.
