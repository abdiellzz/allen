---
name: apk-review
description: Revisión visual de la interfaz de ALLEN en tamaño de teléfono (375x812) con los estilos de la APK aplicados, en tema claro y oscuro. Úsala después de cambiar android/web/allen-android.css o allen-android.js, antes de un commit de diseño, o cuando pidan capturas, "ver cómo se ve en el móvil" o revisar desbordes. Guarda capturas en .agents/review/ y reporta desbordes horizontales y contenido tapado por la barra inferior.
---

# apk-review

Levanta el frontend de ALLEN, aplica la hoja de la APK y toma capturas en 375×812 de **Inicio,
Cursos, Quiz, Tarjetas, Progreso y Configuración**, en claro y oscuro.

## Requisitos

Dependencias de desarrollo y Chromium de Playwright:

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

## Uso

```powershell
python .agents/skills/apk-review/review.py
python .agents/skills/apk-review/review.py --pages Quiz Tarjetas --schemes dark
```

## Qué hace el script

1. **Levanta el frontend** con FastAPI. No usa `python server.py` directamente porque ese arranque
   abre la base real de `%LOCALAPPDATA%\ALLEN`, exige licencia, token de acceso de un solo uso y PIN
   docente, y las capturas saldrían en la pantalla de licencia. En su lugar ejecuta
   `uvicorn tests.e2e_server:app` (la misma `create_app` que `server.py`, sin licencia) en un puerto
   libre, con una base SQLite temporal y el onboarding marcado como hecho.
2. **Reproduce la APK**: inyecta `<link href="/static/android/allen-android.css">` antes de `</head>`
   igual que `android/build_web_assets.py`, sirve ese archivo desde `android/web/` (sin necesidad de
   regenerar assets) y añade la clase `allen-android` a `<html>`, igual que `allen-android.js`. No carga `allen-android.js` porque
   arrancaría Pyodide; si un cambio de diseño depende de marcado creado por ese script, verifícalo
   también en el APK real.
3. Emula un teléfono táctil (375×812, DPR 2) con `prefers-color-scheme` claro u oscuro y
   `localStorage['allen-theme']` igual al esquema, en modo Estudiante.
4. Navega a cada página haciendo clic en su `[data-page]` y guarda en `.agents/review/`:
   - `<pagina>-<tema>.png`: lo que se ve al abrir la página;
   - `<pagina>-<tema>-full.png`: página completa;
   - `<pagina>-<tema>-bottom.png`: tras desplazar todo hasta el final (para ver la barra inferior);
   - `report.json`: datos de cada vista.
5. Revisa cada vista:
   - **Desborde horizontal:** `document.documentElement.scrollWidth > clientWidth`, con los
     elementos que sobresalen del borde derecho.
   - **Tapado por la barra inferior:** detecta elementos `fixed`/`sticky` pegados al borde inferior
     (≥60% del ancho, <30% del alto) y, con todo desplazado al final, lista los controles interactivos
     que quedan debajo de ella.
   - Errores de consola (por ejemplo, CSP).

Sale con código 1 si alguna vista tiene problemas.

## Informe

Resume por página y tema: `OK` o el problema (elementos causantes y px). Abre y mira las capturas
de las vistas con problemas, y también al menos Inicio y Quiz en ambos temas aunque estén OK: el
script no detecta contraste bajo, texto cortado ni jerarquía visual. Las capturas no se versionan
(`.agents/review/` está en `.gitignore`).
