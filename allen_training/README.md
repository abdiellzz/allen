# Dataset y entrenamiento opcional de ALLEN

La aplicación educativa y el entrenamiento son partes separadas. Esta carpeta **no se importa al iniciar Allen**, no recoge conversaciones de estudiantes y no necesita acceso a Internet para validar o preparar los ejemplos.

## Estructura

```text
allen_training/
├── TRAINING_RULES.md              # Reglas escritas antes del dataset
├── README.md
├── DATASET_CARD.md                # Alcance, distribución y limitaciones
├── build_dataset.py               # Construcción reproducible de la base sintética
├── train.py                       # Valida por defecto; SFT solo con --train
├── requirements-training.txt      # Dependencias opcionales, separadas de Allen
├── sources/                       # Conceptos, ejemplos y situaciones originales
├── data/
│   ├── allen_dataset.jsonl        # 2.800 conversaciones, formato messages
│   ├── allen_metadata.jsonl       # Área, grupo, procedencia, hash y revisión
│   ├── validation_report.json
│   └── splits/
│       ├── train.jsonl
│       ├── eval.jsonl
│       ├── train_metadata.jsonl
│       ├── eval_metadata.jsonl
│       └── manifest.json
└── output/                       # Reservada para futuros adaptadores/checkpoints
```

## Lo que contiene

| Área | Conversaciones |
| --- | ---: |
| Personalidad de Allen | 200 |
| Matemáticas | 500 |
| Ciencias | 300 |
| Inglés | 300 |
| Programación | 300 |
| Explicaciones sencillas | 400 |
| Quizzes | 200 |
| Seguridad para menores | 200 |
| Orientación educativa | 200 |
| Uso responsable de IA | 200 |
| **Total** | **2.800** |

Se conservan los tres ejemplos aportados: fracciones, 18 × 7 y variables en Python. Hay 940 conversaciones de varios turnos. El resto combina fuentes originales con plantillas didácticas; no son 2.800 situaciones escritas y revisadas independientemente por personas. Consulta la tarjeta del dataset antes de usarlo.

Cada línea de `allen_dataset.jsonl` es un objeto JSON completo. Los saltos de línea dentro de mensajes se representan como `\n`. No se usa una lista JSON externa ni una coma entre líneas:

```json
{"messages":[{"role":"user","content":"¿Cuánto es 18 x 7?"},{"role":"assistant","content":"Vamos juntos. Primero calcula 10 × 7. Luego calcula 8 × 7. Después suma ambos resultados. ¿Quieres intentar el primer paso?"}]}
```

Los metadatos van en un archivo separado para conservar el formato conversacional de TRL. La línea N de metadatos corresponde a la línea N del dataset. Los hashes detectan cambios sin una actualización de revisión.

## Validar sin entrenar

Desde la raíz del proyecto, con Python 3.11 o superior:

```powershell
python allen_training\train.py
```

Equivale a `--validate`. Solo usa la biblioteca estándar: no descarga modelos, no importa PyTorch y no inicia entrenamiento.

Comprueba JSONL, roles alternados, contenido, límites de extensión, hashes, duplicados exactos y distribución. Informa cuántos ejemplos siguen pendientes de revisión humana. La validación **no demuestra verdad científica, calidad pedagógica ni seguridad exhaustiva**.

Los splits ya están preparados: **2.530 conversaciones de entrenamiento y 270 de evaluación**, con todos los grupos conceptuales asignados a un solo lado. La distribución busca aproximadamente 90/10; no se fuerza una división exacta que rompa grupos. Para preparar otra versión sin sobrescribir la incluida:

```powershell
python allen_training\train.py --prepare --split-dir allen_training\data\splits_v2
```

El archivo `manifest.json` registra la distribución efectiva. Aun con separación por grupos hay plantillas y estilos compartidos; esta evaluación no es un benchmark pedagógico completamente independiente.

## Revisar y mejorar

1. Usa la lista de `TRAINING_RULES.md` para revisar los ejemplos completos, incluyendo cada turno.
2. Corrige en `sources/` las ideas o formulaciones que deban cambiar. No añadas conversaciones privadas de estudiantes ni datos personales reales.
3. Genera una versión candidata en otra carpeta:

```powershell
python allen_training\build_dataset.py --output-dir allen_training\data\candidato_v2
python allen_training\train.py --dataset allen_training\data\candidato_v2\allen_dataset.jsonl --metadata allen_training\data\candidato_v2\allen_metadata.jsonl
```

4. Compara la candidata antes de sustituir una versión revisada. El constructor se niega a sobrescribir el dataset existente desde su CLI.
5. Marca `human_review` como `approved` en los metadatos solo después de revisar personalmente ese ejemplo; usa `rejected` cuando deba retirarse. Todos se entregan inicialmente como `pending`. Conserva un registro propio de quién revisó y cuándo.
6. Si editas directamente una conversación, recalcula el SHA-256 de su objeto con la función `digest()` de `train.py` y actualiza `sha256` e `id` (primeros 16 caracteres). Devuelve el estado a `pending` hasta revisar el cambio. No basta con cambiar un hash para aprobar calidad.
7. Prepara nuevamente los splits a partir de la versión revisada; los archivos incluidos no se sincronizan automáticamente con ediciones posteriores.

Prioriza situaciones nuevas y errores reales de aprendizaje frente a más paráfrasis de los mismos conceptos. Revisa especialmente la repetición de respuestas, las preguntas binarias y las metáforas.

## `train.py`: preparación para SFT local

El script incluye una ruta opcional para SFT con un adaptador LoRA. **Esa ruta no se ejecutó ni se validó con un modelo real**. Se verificaron la validación, la división y las protecciones previas al entrenamiento. Antes de un entrenamiento largo, comprueba dependencias, licencia del modelo, memoria y un ensayo pequeño en tu equipo.

Necesitas un **modelo base local en formato Transformers**: configuración, tokenizer con plantilla de chat y pesos. Un archivo GGUF de llama.cpp **no sirve como entrada directa de este script**. Tras entrenar, el adaptador no es un GGUF: fusionar, convertir, cuantizar y evaluar son etapas posteriores, no implementadas aquí.

Las dependencias opcionales se instalan en otro entorno. PyTorch debe elegirse para tu hardware según su [guía oficial](https://pytorch.org/get-started/locally/). No forman parte del arranque de Allen.

```powershell
python -m venv allen_training\.venv
# Instala primero PyTorch adecuado a tu hardware en este entorno.
allen_training\.venv\Scripts\python.exe -m pip install -r allen_training\requirements-training.txt
```

Solo cuando el dataset esté revisado y tengas el modelo adecuado:

```powershell
allen_training\.venv\Scripts\python.exe allen_training\train.py --train --model "C:\modelos\modelo-base-transformers" --output allen_training\output\allen-lora-v1
```

No ejecutes ese comando solo para comprobar las carpetas: inicia un trabajo de entrenamiento. Por defecto rechaza datos sin aprobación humana, modelos no locales, salidas no vacías y ausencia de CUDA. `--allow-unreviewed` y `--allow-cpu` permiten experimentos deliberados, pero no certifican calidad ni garantizan memoria suficiente. No se usa QLoRA ni se promete que entrenar sea viable en el mismo equipo modesto que hace inferencia GGUF.

La ruta configura modo offline, carga local, `trust_remote_code=False`, sin envío al Hub y sin servicios de seguimiento. Convierte cada respuesta del asistente en un par conversacional `prompt`/`completion` para que la pérdida se aplique a la respuesta y no a las preguntas del estudiante. Esto sigue el formato de [SFTTrainer de TRL 0.29](https://huggingface.co/docs/trl/v0.29.0/en/sft_trainer). Las variantes de una conversación se separan **después** de asignar su grupo a entrenamiento o evaluación.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_training.py -q
```

También están incluidas en la suite general. Los modelos, adaptadores y entornos de entrenamiento se ignoran en Git; no se inició ningún entrenamiento ni se descargaron pesos.
