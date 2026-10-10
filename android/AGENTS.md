# AGENTS.md — Diseño de la APK de ALLEN

Reglas para el trabajo visual de la APK de Android. Complementan el [AGENTS.md](../AGENTS.md) de la
raíz; en caso de conflicto dentro de `android/`, prevalece este archivo.

## Alcance

**Solo se tocan:**

- `android/web/` — `allen-android.css`, `allen-android.js`, `allen-worker.js`, `allen_bridge.py`.
- `android/app/src/main/res/` — `values/themes.xml`, `values-night/`, `drawable/`, `mipmap-*`.

**No se tocan:** `frontend/`, `backend/`, `tests/`, `distribution/`, `public/`, `data/`, `config/`,
`tools/` ni `android/build_web_assets.py`. Si el diseño necesita un cambio ahí (por ejemplo, un
marcado nuevo en `frontend/app.js` o un archivo nuevo que el builder deba copiar), **no lo hagas**:
repórtalo con archivo, motivo y cambio propuesto para coordinarlo con el compañero.

- Trabajar en la rama `design/apk-mobile`, partiendo de `main` actualizada.
- `android/app/src/main/assets/www/` es una **copia generada** e ignorada por git. Nunca editarla a
  mano: se regenera con `python android/build_web_assets.py`.
- El builder solo copia `allen-android.css`, `allen-android.js` y `allen-worker.js` a
  `/static/android/`. Cualquier archivo nuevo en `android/web/` no llegará al APK sin cambiar el
  builder (fuera de alcance): mantén los estilos en `allen-android.css` y los SVG inline o en
  `frontend/assets/` existentes.
- No romper `tests/test_android_demo.py`: `PACKAGES` en `allen-worker.js` debe coincidir con el
  builder, `allen-android.js` se inyecta antes del módulo de la app y el manifiesto no declara
  permisos.

## Aislamiento de estilos

- Todo selector nuevo va prefijado con `html.allen-android` (o vive dentro de `#allen-android-boot`).
  El escritorio no debe cambiar ni un píxel.
- `allen-android.js` añade la clase `allen-android` a `<html>` (no a `<body>`, que aún no existe
  cuando el script corre en `<head>`). `body.allen-android` no funciona: no lo uses.
- **No renombrar** clases, IDs ni valores de `data-page`, `data-workspace-mode` o `data-nav-mode`
  que usa `frontend/app.js`. Se pueden ocultar o reacomodar con CSS; los nuevos elementos que cree
  `allen-android.js` (barra inferior, hoja inferior) deben reutilizar esos `data-page` y delegar el
  clic en los botones originales.
- Preferir tokens CSS definidos una vez en `html.allen-android` a colores sueltos.
- No usar estilos inline desde JS que la CSP bloquee; usar clases.

## Dirección visual

Inspiración: "Function — warm apothecary journal on parchment" (Refero Styles), adaptada a una app de
estudio: serif solo en títulos, sans redondeada en la UI, mascota visible y patrones móviles tipo
Duolingo/Headspace — barra inferior, una columna, acciones principales abajo y feedback en hoja
inferior.

### Color

Tokens definidos en `html.allen-android` dentro de `allen-android.css` (prefijo `--p-`). Usa siempre
el token, nunca el hexadecimal suelto.

| Token | Claro | Oscuro | Uso |
| --- | --- | --- | --- |
| `--p-bg` | `#fef9ef` | `#1d1712` | Fondo de la app |
| `--p-surface` | `#f5eee1` | `#2a221b` | Secciones, barra inferior |
| `--p-raised` | `#fffdf8` | `#312820` | Tarjetas |
| `--p-line` | `#d1c9bf` | `#3d3229` | Bordes y divisores |
| `--p-text` | `#2a2b2f` | `#f6eadb` | Texto principal |
| `--p-text-2` | `#515151` | `#c9b39b` | Texto secundario |
| `--p-help` | `#808988` | `#9c8a78` | Ayuda, placeholders |
| `--p-accent` | `#c8662a` | `#e08a55` | **Único** acento: botones, activo, enlaces |
| `--p-accent-press` | `#ad4c12` | `#c8662a` | Estado presionado |
| `--p-accent-soft` | `#f6e2d3` | `#3a2a1f` | Fondo de elementos activos |
| `--p-on-accent` | `#fffdf8` | `#1d1712` | Texto sobre el acento |
| `--p-success` / `--p-success-soft` | `#55796f` / `#e6f0ec` | `#8fb5a8` / `#24312c` | Correcto, completado |
| `--p-gold` | `#e8b957` | `#e8b957` | Logros, rachas, estrellas |

Otros tokens: `--p-r-card` 20px, `--p-r-btn` 14px, `--p-r-chip` 999px, `--p-nav-h` 64px (barra
inferior), `--p-top-h` 56px, `--p-sans`, `--p-serif`, `--p-shadow`, `--p-glass`. Si añades uno,
defínelo en claro y en oscuro.

Hoy conviven tres naranjas (`#c8662a`, `#f07c1a`, `#dc651f`/`#ad4c12`): en la APK todo se unifica
en `--p-accent`. `res/values/themes.xml` usa también `#c8662a`.

El modo oscuro aplica con `@media (prefers-color-scheme: dark)` (tema del teléfono) y también cuando
la app tiene `html[data-theme="dark"]` (botón de tema de ALLEN). Si el usuario eligió claro en la app
(`html[data-theme="light"]`), respetar su elección. Recursos Android equivalentes en
`res/values-night/`. Verificar contraste AA (4.5:1 texto, 3:1 iconos y bordes de control).

### Tipografía

- Títulos (`--p-serif`): serif. La dirección elegida es `"Fraunces", Georgia, serif`, pero no hay
  fuentes externas (la app es offline) y la hoja actual usa `Georgia, "Source Serif Pro",
  "Noto Serif", serif`; en Android cae en Noto Serif, y es aceptable.
- UI y texto (`--p-sans`): `ui-rounded, "Segoe UI", system-ui, sans-serif` (en Android → Roboto).

### Escala, radios y tacto

| Elemento | Tamaño |
| --- | --- |
| h1 | 28px |
| h2 | 22px |
| h3 | 18px |
| Texto | 16px (nunca menos en inputs, evita zoom) |
| Etiqueta | 12px |

- Radios: 20px tarjetas y hojas, 14px botones e inputs, 999px chips y pastillas.
- Área táctil mínima 48×48px. Espaciado en múltiplos de 4px; margen lateral 16px.
- Una sola columna en ≤640px; nada de grids de 3–4 columnas ni opciones de quiz en 2 columnas.
- Sin desborde horizontal; respetar `env(safe-area-inset-*)` y dejar espacio bajo el contenido
  para la barra inferior.
- Respetar `prefers-reduced-motion`.

## Verificación

1. `python android/build_web_assets.py` y compilar (skill `apk-build`).
2. Capturas 375×812 en claro y oscuro (skill `apk-review`): sin desbordes ni contenido tapado.
3. `python -m pytest -q tests/test_android_demo.py`.
4. Skill `scope-check` antes de cada commit.
