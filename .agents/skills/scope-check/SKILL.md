---
name: scope-check
description: Verifica que los cambios de la rama actual (commits y archivos sin commitear) no salen de las rutas permitidas para la tarea. Úsala antes de cada commit, antes de pedir un push o PR, y siempre que se trabaje en paralelo con otra persona. Falla (código de salida 1) si algún archivo cambiado está fuera del alcance.
---

# scope-check

Comprueba que el diff contra `main` solo toca rutas permitidas, para no pisar el trabajo del compañero.

## Uso

```powershell
python .agents/skills/scope-check/scope_check.py                 # perfil "design" por defecto
python .agents/skills/scope-check/scope_check.py --profile design --allow .gitignore
python .agents/skills/scope-check/scope_check.py --only backend/ tests/   # alcance a medida
```

El script ejecuta y muestra:

- `git diff --stat <base>` y `git diff --name-only <base>`, donde `<base>` es
  `git merge-base main HEAD`. Así se comparan los commits de la rama más los cambios sin commitear
  contra el punto donde la rama salió de `main`, sin que aparezcan como "cambios" los commits nuevos
  que entren a `main` después.
- Archivos nuevos sin seguimiento (`git ls-files --others --exclude-standard`).

Sale con **0** si todo está dentro del alcance y con **1** listando cada archivo fuera de él.

## Perfiles

| Perfil | Rutas permitidas |
| --- | --- |
| `design` (defecto) | `android/web/`, `android/app/src/main/res/`, `.agents/`, `AGENTS.md`, `android/AGENTS.md` |

Una ruta que termina en `/` permite todo lo que hay debajo; si no, debe coincidir exactamente.
`--allow RUTA...` añade rutas al perfil para una tarea concreta (solo si la tarea las pide
explícitamente). `--only RUTA...` sustituye el perfil. `--base RAMA` cambia `main` por otra rama.

## Si falla

1. No hagas commit.
2. Para cada archivo fuera de alcance: si lo cambiaste por error, revierte solo ese archivo
   (`git restore --source=<base> -- <archivo>` o `git checkout <base> -- <archivo>`, confirmando antes
   con el usuario). Si es necesario para la tarea, explícalo y pide coordinación; no amplíes el
   alcance por tu cuenta.
3. Vuelve a ejecutar la skill hasta que pase.
