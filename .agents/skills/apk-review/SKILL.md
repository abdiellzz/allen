---
name: apk-review
description: Revisión visual de la interfaz que muestra la APK de Android (public/mobile/ con los extras de la APK y su CSP) en tamaño de teléfono (375x812), en tema claro y oscuro. Úsala después de cambiar public/mobile/ o android-extras.*, antes de un commit de diseño, o cuando pidan capturas, "ver cómo se ve en el móvil" o revisar desbordes. Guarda capturas en .agents/review/ y reporta desbordes, contenido tapado y errores de consola o CSP.
---

# apk-review

Ensambla los assets de la APK, los sirve igual que la WebView y toma capturas en 375×812 de
**Hoy, Aprender, Practicar, Allen, Mi progreso y Perfiles**, en claro y oscuro.

## Requisitos

Dependencias de desarrollo y Chromium de Playwright:

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

## Uso

```powershell
python .agents/skills/apk-review/review.py
python .agents/skills/apk-review/review.py --pages Aprender "Mi progreso" --schemes dark
```

## Qué hace el script

1. **Ensambla la APK** con `android/build_web_assets.py` en una carpeta temporal (no toca
   `assets/www/` ni descarga nada) y la sirve **sin cabeceras HTTP**, como `WebViewAssetLoader`:
   así aplica la misma CSP que en el teléfono y cualquier violación aparece como error.
2. Emula un teléfono táctil (375×812, DPR 2) con `prefers-color-scheme` claro u oscuro, crea un
   perfil y salta el recorrido guiado.
3. Abre cada vista desde el menú de secciones (o el botón Perfiles) y guarda en `.agents/review/`:
   - `<vista>-<tema>.png`: lo que se ve al abrirla;
   - `<vista>-<tema>-full.png`: página completa;
   - `<vista>-<tema>-bottom.png`: tras desplazar todo hasta el final;
   - `report.json`: datos de cada vista.
4. Revisa cada vista:
   - **Desborde horizontal:** `document.documentElement.scrollWidth > clientWidth`, con los
     elementos que sobresalen del borde derecho.
   - **Tapado por una barra inferior:** elementos `fixed`/`sticky` pegados al borde inferior y los
     controles interactivos que quedan debajo.
   - **Errores de consola**, incluidas violaciones de CSP.

Sale con código 1 si alguna vista tiene problemas.

## Informe

Resume por vista y tema: `OK` o el problema (elementos causantes y px). Abre y mira las capturas
de las vistas con problemas, y también al menos Hoy y Mi progreso en ambos temas aunque estén OK: el
script no detecta contraste bajo, texto cortado ni jerarquía visual. Las capturas no se versionan
(`.agents/review/` está en `.gitignore`).
