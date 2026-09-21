# ALLEN — aprende, incluso sin Internet

Compañero educativo local en español, con una mascota original SVG y sin cuentas ni APIs de pago. Trabaja sobre el MVP original, conservado como referencia en `legacy/`. La interfaz nueva no requiere Node, compilación, fuentes externas ni CDN.

## Empezar en Windows

1. Instala **Python 3.11 o superior** desde https://www.python.org/downloads/windows/ y marca **Add Python to PATH**. Se verificó con Python 3.13.
2. Abre esta carpeta y haz doble clic en **start_allen.bat**.
3. La primera vez se crea `.venv` y se instalan las dependencias de `requirements.txt`; esta instalación necesita Internet. Los siguientes arranques omiten la instalación si las versiones ya están presentes.
4. El lanzador inicia el servidor y abre **http://127.0.0.1:8787** cuando responde. Conserva la ventana abierta; para cerrar Allen usa Ctrl+C.

Sin modelo puedes usar quizzes, ejercicios, biblioteca, perfiles, tarjetas manuales y progreso. Las respuestas abiertas muestran **MODO DEMO** y nunca fingen ser una IA conectada.

## Instalar en otro equipo

Descarga el repositorio como ZIP, extrae la carpeta y ejecuta `install_allen.bat`. El instalador comprueba Python 3.11+, copia la aplicación a `%LOCALAPPDATA%\ALLEN\app`, crea un entorno aislado e instala las dependencias. Luego usa el archivo `Iniciar ALLEN.bat` creado en esa carpeta.

El instalador no descarga modelos ni ejecutables de IA. Para activar respuestas abiertas, instala una versión confiable de llama.cpp, coloca un modelo GGUF con licencia adecuada y crea `%LOCALAPPDATA%\ALLEN\local_model.json` siguiendo `config/local_model.example.json`. Sin ese paso, ALLEN funciona en modo demo con sus actividades locales.

## Publicación segura

El repositorio puede alojarse en GitHub. Mantén fuera del repositorio `.venv/`, bases SQLite, modelos GGUF, `.env` y cualquier token; las reglas de `.gitignore` ya los excluyen. Consulta [SECURITY.md](SECURITY.md) antes de hacer público el proyecto.

Vercel sirve la página de entrada y aplica cabeceras de seguridad mediante `vercel.json`. El tutor completo no se despliega como servicio público: el modelo, el historial y el servidor FastAPI permanecen en el equipo del estudiante para conservar el modo offline y evitar exponer el modelo local.

Alternativa manual (PowerShell, desde esta carpeta):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py --open
```

No es necesario activar el entorno ni cambiar la política de ejecución de PowerShell. Si instalaste las dependencias en tu Python habitual, `python server.py` también funciona.

## Conectar llama.cpp y un modelo GGUF

1. Descarga una versión de **llama.cpp** apropiada para Windows desde sus [versiones oficiales](https://github.com/ggml-org/llama.cpp/releases). Extrae los archivos completos en una carpeta, por ejemplo `C:\allen-tools\llama`.
2. Obtén un modelo **instruct/chat en formato GGUF** de una fuente de confianza, con licencia que permita tu uso y soporte de español. Descarga el archivo completo antes de desconectarte. Para empezar en hardware modesto, prueba un modelo cuantizado pequeño; velocidad y memoria dependen del equipo y del modelo. Allen no incluye ni descarga un modelo automáticamente.
3. Guarda el GGUF, por ejemplo en `C:\allen-models\modelo.gguf`. No necesitas ponerlo en OneDrive.
4. En PowerShell inicia el servidor local:

```powershell
& "C:\allen-tools\llama\llama-server.exe" -m "C:\allen-models\modelo.gguf" --host 127.0.0.1 --port 8080 -c 4096
```

5. Espera a que termine de cargar. En Allen abre **Configuración → Inteligencia Artificial**, deja `http://127.0.0.1:8080`, y pulsa **Comprobar conexión**. Un nombre de modelo vacío selecciona el primer modelo anunciado por `/v1/models`.
6. El estado debe pasar a **IA LOCAL ACTIVA**. Si figura **IA LOCAL DESCONECTADA**, comprueba el servidor, el puerto y el nombre de modelo. **Usar siempre modo demo** fuerza el modo de demostración.

El administrador detecta modelos cargados mediante el servidor; no inspecciona archivos GGUF ni lanza llama.cpp. Cambiar el nombre en Allen no carga un archivo nuevo. Ajusta el contexto tanto en Allen como con `-c` al iniciar llama.cpp. La respuesta máxima no puede superar la mitad del contexto configurado. Se aplica un presupuesto conservador de bytes UTF-8: textos largos pueden necesitar dividirse.

La conexión usa `/health`, `/v1/models` y `/v1/chat/completions` con streaming SSE conforme a la [documentación oficial del servidor llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md). No se siguen redirecciones ni proxies del entorno. Solo se aceptan direcciones loopback HTTP con puerto explícito.

## Qué puedes hacer

| Área | Implementación de esta versión |
| --- | --- |
| Inicio | Mascota naranja original, tarjetas, navegación responsive y métricas locales |
| Chat | Contexto de conversación, historial, nueva/limpiar, copiar, regenerar, detener y Markdown seguro básico |
| IA local | Estado, detección de modelo cargado, temperatura, contexto, tokens y modo demo explícito |
| Tutor | Materia, nivel y método didáctico en prompt centralizado; conversación con retroalimentación del modelo |
| Matemáticas | Generador local de operaciones, fracciones, porcentajes, proporciones, ecuaciones sencillas, álgebra, rectángulos y medias |
| Quizzes | Banco local en ocho materias; selección múltiple, verdadero/falso y respuesta corta; corrección, explicación y resultados |
| Explicar / Resumir | Opciones didácticas, analogía, guía de estudio y preguntas mediante el modelo local |
| Idiomas | Español ↔ inglés, vocabulario, pronunciación aproximada y conversación simulada mediante el modelo |
| Programación | Lógica, Python, HTML, CSS y JavaScript como texto; pistas, revisión y desafíos. **No ejecuta código** |
| Futuro / Aprende IA | Modos de conversación específicos y lecturas offline de apoyo |
| Tarjetas | Creación manual, propuestas del modelo revisables antes de guardar, cuatro valoraciones y repetición espaciada sencilla |
| Biblioteca / RAG | JSON, Markdown y TXT, ranking por palabras y contexto opcional para el chat con títulos de referencia |
| Progreso | XP, racha, ejercicios, quizzes, tarjetas y estimación de tiempo activo; vista agregada para acompañantes |
| Perfiles | Apodo, edad opcional, avatar, nivel, edición, selección y borrado en cascada |
| Accesibilidad | Tamaño de texto, contraste, labels, foco visible, teclado y respeto de movimiento reducido |

### Alcance educativo real

Los ejercicios matemáticos son plantillas acotadas, no un sistema simbólico universal. La dificultad cambia los números en matemáticas. Las demás materias tienen bancos pequeños de 2–5 preguntas por tema: al pedir más se entregan las disponibles, sin inventar preguntas. Las respuestas cortas aceptan fracciones equivalentes, decimales exactos, mayúsculas y acentos; no califican ensayos ni aproximaciones numéricas arbitrarias.

Un quiz de una pregunta cuenta como ejercicio (+10 XP); los demás como quiz (+30 XP). Estudiar suma +5 XP una vez por día, y cada tarjeta suma +5 XP una vez por día. No hay rankings. La tarjeta se considera aprendida en el panel cuando su intervalo es de al menos tres días. El tiempo es una estimación: se registra en bloques de 30 segundos mientras hay actividad reciente y la pestaña está visible.

El tutor no tiene una secuencia curricular certificada ni calificación automática confiable de respuestas abiertas: su calidad depende del modelo. Resúmenes, traducciones, orientación, generación de tarjetas y tutor se integraron y probaron con un servidor simulado; se requiere probar su calidad con tu GGUF real.

## Privacidad y seguridad

- Datos de ejecución en **`%LOCALAPPDATA%\ALLEN\allen.sqlite3`** en Windows, fuera de la carpeta de OneDrive de este proyecto. En otros sistemas: `~/.local/share/ALLEN`. `ALLEN_DB_PATH` permite una ruta alternativa; si eliges una carpeta sincronizada, puede ser copiada por ese servicio.
- Preferencias en la tabla `settings` de SQLite. `config/settings.example.json` documenta los valores; **no se carga automáticamente**.
- Los perfiles comparten el dispositivo y no tienen contraseña. No son una barrera de seguridad frente a otros usuarios de la misma cuenta de Windows. La vista docente muestra solo métricas, pero no es una cuenta con permisos restringidos.
- Conversaciones: retención predeterminada de 30 días, configurable de 1 a 90; limpieza al arrancar, consultar o enviar mensajes. Desactivar historial borra lo guardado en todos los perfiles. Los datos de progreso y tarjetas se conservan hasta borrarlos.
- **Tu privacidad → Eliminar todos mis datos de este perfil** elimina perfil, mensajes, resultados, tarjetas y progreso. Las copias de seguridad externas quedan fuera del control de Allen.
- Solo el frontend se sirve como archivos estáticos. La base, el código Python y la biblioteca no se exponen como directorio web.
- SQL parametrizado, entradas acotadas, comprobación de Host y Origin, token contra peticiones cruzadas, sin CORS abierto, CSP, sin ejecución de código, Markdown sin HTML activo ni imágenes remotas.
- El prompt y filtros básicos intentan mantener conversaciones educativas y seguras. **No garantizan detectar todo contenido dañino**; se requiere supervisión y evaluación del modelo antes de usarlo con menores. No son un servicio de emergencias.
- Los logs rotan y contienen clases de error, sin conversaciones ni respuestas. La aplicación no envía telemetría.
- La indicación de red proviene del navegador; no prueba conectividad a Internet. No se realizan llamadas externas para comprobarla.

## Ampliar la biblioteca

Copia archivos `.md`, `.txt` o `.json` en una subcarpeta de `data/library/`. Se leen al buscar; no requiere reiniciar. Un JSON puede ser un objeto o una lista:

```json
{"title":"Mi lección","subject":"Ciencias","content":"# Mi lección\nContenido educativo…"}
```

Archivos máximos de 300 KB, contenido visible limitado a 20 000 caracteres por documento. Los paquetes malformados se omiten; los enlaces simbólicos a archivos externos no se leen. No se ejecuta HTML. Revisa exactitud y derechos de los contenidos que incorpores. Las lecturas incluidas se escribieron para este proyecto.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Si tienes Node, también puedes comprobar el renderizador de Markdown (Node no es necesario para usar Allen):

```powershell
node --test tests/test_markdown.mjs
```

Consulta `VALIDATION.md` para resultados y límites de la verificación, `ARCHITECTURE.md` para el diseño, y `CHANGES.md` para la lista de archivos.

## Solución de problemas

- **Puerto ocupado:** cierra la otra ventana de Allen. No ejecutes dos servidores en 8787.
- **Dependencias sin Internet:** la primera instalación necesita descargar paquetes. Después puedes desconectarte. Para distribuir en un lugar sin red, prepara previamente el entorno o un repositorio de ruedas compatible con la misma versión de Python y Windows.
- **Modelo desconectado:** abre llama.cpp, espera que cargue y comprueba puerto/nombre. Se conserva acceso a todos los recursos deterministas.
- **Texto demasiado largo:** envía secciones menores o amplía el contexto tanto en Allen como en el servidor, teniendo en cuenta la memoria disponible.
- **Respuesta interrumpida:** puedes regenerarla; las respuestas incompletas no se guardan como conversación final.

## Próximas fases

Embeddings y RAG semántico local; bancos curriculares más amplios y revisados por docentes; evaluación de calidad y seguridad de modelos concretos; empaquetado instalable; sincronización manual/exportación de paquetes; roles docentes autenticados si se requieren varios usuarios con aislamiento real. Las expresiones animadas de la mascota, más allá del saludo actual, también quedan para una fase posterior.

## Dataset y entrenamiento opcional

Se añadió `allen_training/` con reglas, un dataset conversacional sintético de 2.800 ejemplos por áreas, metadatos, validación, splits por grupos y un script SFT LoRA opcional. La aplicación no depende de esta carpeta. No se entrenó ningún modelo. Consulta `allen_training/README.md` y `allen_training/DATASET_CARD.md` para conocer la revisión pendiente y sus límites.

Para validar sin entrenar: `python allen_training/train.py`.

## Arranque automático del modelo en este equipo

Se encontró llama.cpp instalado mediante WinGet y el modelo `Qwen3.5-0.8B-Q8_0.gguf` ya descargado. Sus rutas se guardaron en `%LOCALAPPDATA%\ALLEN\local_model.json`, fuera del código. No se descargaron pesos nuevos.

`start_allen.bat` ahora ejecuta `start_local_ai.py` antes de abrir la aplicación. Comprueba si el servidor ya responde y, si no, inicia el binario configurado en segundo plano, solo en loopback, con el contexto indicado en Configuración. No duplica un servidor activo y respeta el modo demo explícito. Si no hay configuración o falla el modelo, la aplicación sigue abriendo en modo demo.

Para otro equipo, adapta `config/local_model.example.json` y guárdalo como `%LOCALAPPDATA%\ALLEN\local_model.json`. Requiere una versión de llama.cpp compatible con `--reasoning off`. El proceso del modelo permanece en segundo plano al cerrar la ventana de Allen; puedes finalizar `llama-server.exe` desde el Administrador de tareas cuando no lo necesites.
