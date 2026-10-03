# Validación de ALLEN

Estado registrado el 2 de octubre de 2026. Los resultados aplican al checkout local y a las pruebas indicadas; no certifican cada plataforma, instalador ni modelo.

## Pruebas automatizadas

Python:

```powershell
\.venv\Scripts\python.exe -m pytest -q
```

JavaScript (Node.js):

```powershell
node --test tests/*.mjs
```

Resultados de esta revisión:

- JavaScript: **28 aprobadas, 0 fallidas**.
- Python: **21 aprobadas, 0 fallidas** (incluye 10 subcasos aprobados; 2 warnings deprecados de Starlette/httpx).

## Análisis de los cinco fallos originales

Los cinco casos fallidos eran cinco subcasos de `tests/test_fair.py::FairTests.test_five_project_ideas_use_grounded_natural_catalog_responses`. En cada uno el error exacto fue `AssertionError: 'puedes practicar' not found in result['text']`:

| Caso | Ejemplo de proyecto | Resultado inicial | Causa |
| --- | --- | --- | --- |
| 1 | Detector de humedad para plantas | Falló | El ejemplo decía “podemos comparar”, sin invitar explícitamente a practicar |
| 2 | Semáforo con LEDs | Falló | La respuesta decía “probamos una parte pequeña”; no contenía la frase esperada |
| 3 | Alarma con sensor de movimiento | Falló | Mismo texto genérico de “probamos una parte pequeña” |
| 4 | Proyecto de Python para principiantes | Falló | Mismo texto genérico de “probamos una parte pequeña” |
| 5 | Proyecto de ciberseguridad básica | Falló | El texto sugería probar casos en el siguiente paso, pero omitía la invitación en el ejemplo |

### Comparación contra `main`

El checkout base `main` está en `97dc7c1`. Su suite Python pasa (**7 aprobadas**) y su suite JavaScript pasa (**5 aprobadas**). El test nombrado arriba, `prepared_project_idea()` y el catálogo local son adiciones sin commit que ya estaban en el árbol de trabajo antes de iniciar `repo-cleanup`; no existen en `main`, así que no se puede afirmar que el mismo test falle allí. Clasificación: **fallo preexistente en los cambios locales, no causado por repo-cleanup**; no es un fallo preexistente de `main` ni una regresión de limpieza.

### Corrección

En `backend/fair.py`, la explicación del catálogo ahora presenta un ejemplo explícito y una acción de práctica para las cinco ideas. Se conservaron selección, catálogo, fuente de respuesta y todos los asserts. El test parametrizado pasa con **5 subcasos aprobados**.

Las pruebas JavaScript cubren Feria, contenido offline, reconocimiento/voz, logros, sesiones, rúbrica, guardado de evaluación, rutas y progresión. Las pruebas Python cubren API y lógica de backend, Feria, evaluación, seguridad y licencias. No se infiere cobertura porcentual.

## Arranque integrado

Se inició `server.py` en `127.0.0.1:8787` con `ALLEN_DATA_HOME` aislado bajo una carpeta temporal. `/api/health` devolvió HTTP 200 con backend, base de datos y biblioteca disponibles. En navegador se completó el alta temporal de visitante, selección de dificultad, navegación a chat y envío de una idea de proyecto; la respuesta del catálogo se mostró correctamente. No se usó ni modificó el perfil persistente previo del navegador y el smoke test no requirió un modelo generativo.

## Lint y tipos

No hay configuración de Ruff, mypy, ESLint ni TypeScript (`package.json`/`tsconfig.json` ausentes); por tanto esos comandos no aplican al checkout actual. `git diff --check` quedó limpio después de quitar los espacios en blanco finales del CSS.

## Verificaciones que no equivalen a pruebas

- No se produjo una instalación limpia de usuario durante esta revisión.
- No se validó un release firmado de Nuitka/Inno Setup. El checkout no contiene `dist/installer/ALLEN_Setup.exe`, no tiene GGUF en el árbol y no hay clave privada de firma dentro de `tools/license_generator/private_keys/`. `ISCC.exe` no está disponible en el PATH ni se encontró una instalación en el directorio consultado; por ello no se ejecutó la compilación, que además altera temporalmente el ancla de confianza y requiere secretos/modelo explícitos.
- `dist/ALLEN/runtime/llama/` conserva los binarios de una build/prueba previa; su presencia no demuestra una build completa.
- La calidad de respuestas del GGUF y uso con estudiantes requieren evaluación humana adicional.
- Android no tiene aún una app compilable verificada.

## Estado del build

El script de build existe en `packaging/build_allen.ps1`. `DOCUMENTACION_DISTRIBUCION_AUDITORIA.md` registra que una ejecución anterior de Nuitka/Zig se detuvo antes de completar y que no se generó instalador. `build/` contiene productos intermedios generados de ese intento y debe reconstruirse si se retoma el pipeline.
