# Archivos y cambios

## Archivos originales modificados

- `server.py`: punto de entrada FastAPI/Uvicorn en loopback y apertura del navegador cuando responde.
- `index.html`: página de orientación para abrir la aplicación mediante el servidor.
- `start_allen.bat`: detección de Python, entorno virtual, comprobación/instalación de dependencias y arranque.
- `README.md`: instrucciones completas, funciones, privacidad, límites, ampliación y pruebas.
- `.gitignore`: añade entorno virtual, cachés, bases y logs.

## Archivos nuevos

- `backend/__init__.py`
- `backend/app.py`
- `backend/ai.py`
- `backend/database.py`
- `backend/education.py`
- `backend/library.py`
- `backend/schemas.py`
- `backend/security.py`
- `frontend/index.html`
- `frontend/app.js`
- `frontend/services.js`
- `frontend/components/markdown.js`
- `frontend/styles/app.css`
- `frontend/assets/allen.svg`
- `data/library/math/fracciones.md`
- `data/library/math/porcentajes.json`
- `data/library/science/sistema_solar.json`
- `data/library/english/restaurant.md`
- `data/library/programming/python_basics.json`
- `data/library/technology/ia_local.md`
- `data/library/technology/cybersecurity_intro.json`
- `data/library/technology/mi_futuro.md`
- `config/settings.example.json`
- `models/.gitkeep`
- `tests/test_allen.py`
- `tests/test_markdown.mjs`
- `requirements.txt`
- `requirements-dev.txt`
- `ARCHITECTURE.md`
- `VALIDATION.md`
- `CHANGES.md`

## Copias de referencia

- `legacy/server.py.txt`: código original; extensión de texto para evitar ejecutarlo por accidente.
- `legacy/index.html`: interfaz original.

La nueva aplicación no sirve el directorio `legacy/` por HTTP. No se borraron modelos ni datos previos. El proyecto original no tenía base de datos.

## Archivos de ejecución fuera del código

- `.venv/`: entorno creado para ejecutar y verificar el proyecto.
- `%LOCALAPPDATA%/ALLEN/allen.sqlite3`: preferencias y datos educativos locales.
- `%LOCALAPPDATA%/ALLEN/allen.log`: diagnóstico técnico acotado, sin conversaciones.
- Cachés de Python/pytest: ignoradas por `.gitignore`.

No se creó un commit ni un pull request porque la carpeta no es un repositorio Git.

## Ampliación: entrenamiento local opcional (19 de septiembre)

- `allen_training/TRAINING_RULES.md`, `README.md`, `DATASET_CARD.md`, `__init__.py`.
- `allen_training/build_dataset.py`, `train.py`, `requirements-training.txt`.
- `allen_training/data/allen_dataset.jsonl`, `allen_metadata.jsonl`, `validation_report.json`.
- `allen_training/data/splits/train.jsonl`, `eval.jsonl`, `train_metadata.jsonl`, `eval_metadata.jsonl`, `manifest.json`.
- `allen_training/sources/science.tsv`, `english.tsv`, `programming.tsv`, `explanations.tsv`, `responsible_ai.tsv`, `orientation.tsv`, `personality.tsv`, `safety.tsv`.
- `allen_training/output/.gitkeep`.
- `tests/test_training.py`, `tests/test_services.mjs`.
- Se amplían `.gitignore`, `README.md` y la documentación de validación.

No se instalaron dependencias pesadas de entrenamiento ni se descargaron pesos. La ruta de SFT queda preparada, sin validación con un modelo real.

## Corrección del modo demo por servidor ausente

- Añadido `start_local_ai.py`: comprobación de salud e inicio local sin shell, sin proxies ni redirecciones; reutiliza servidor existente y respeta modo demo.
- Modificado `start_allen.bat` para iniciar el modelo configurado antes de Allen.
- Añadidos `config/local_model.example.json` y `tests/test_launcher.py`.
- Configuración específica del equipo guardada fuera del repositorio, en `%LOCALAPPDATA%\ALLEN\local_model.json`.
- Actualizados README y verificación. Se reutilizaron llama.cpp y el GGUF que ya estaban instalados.
