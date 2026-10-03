# ALLEN — aprende, incluso sin Internet

> **Estado: beta funcional, con distribución empaquetada aún no validada.** El código fuente permite ejecutar la aplicación en Windows con Python. La IA requiere `llama-server` y un modelo GGUF locales. No hay un `ALLEN_Setup.exe` de lanzamiento verificado en este repositorio.

## Repositorios del proyecto

Este repositorio conserva la aplicación educativa funcional de ALLEN: su frontend local, backend, IA local, datos, instalador, pruebas y documentación técnica. La carpeta `frontend/` es parte de esa aplicación y no pertenece al sitio comercial.

El sitio comercial independiente vive en [abdiellzz/allen-website](https://github.com/abdiellzz/allen-website). Contiene la portada de ALLEN, las presentaciones comerciales de Education y Agents, recursos web locales y configuración de Vercel. No necesita que esta aplicación, Python, llama.cpp o SQLite estén ejecutándose.

## Modo Feria

Abre **http://127.0.0.1:8787/fair** para una experiencia con retos, microlecciones, chat temporal, tarjeta de logro, Modo Jurado, estadísticas anónimas y QR local. **Nueva persona** limpia la sesión del visitante; la inactividad también la reinicia. Consulta [FAIR_MODE.md](FAIR_MODE.md) para preparar el stand, configurar voz opcional y conocer las pruebas y límites.

Compañero educativo local en español, con una mascota SVG original y sin cuentas ni APIs de pago. La interfaz se sirve con HTML, CSS y JavaScript nativo; no requiere Node, compilación, fuentes externas ni CDN.

## Instalación para usuarios

No hay todavía un instalador final validado para distribución general. `install_allen.bat` y `install_allen.ps1` son instaladores desde el código fuente para Windows: requieren Python 3.11 o posterior y acceso a pip; además, el flujo normal exige encontrar llama.cpp. Si encuentra llama.cpp pero no el GGUF configurado, puede ofrecer descargar el modelo Qwen indicado en el script. Revisa el origen y licencia del modelo antes de aceptarlo.

La compilación Nuitka/Inno Setup está implementada en `packaging/` e `installer/`, pero la compilación previa quedó incompleta y no existe `dist/installer/ALLEN_Setup.exe` validado. Consulta [REPO_AUDIT.md](REPO_AUDIT.md) y [DOCUMENTACION_DISTRIBUCION_AUDITORIA.md](DOCUMENTACION_DISTRIBUCION_AUDITORIA.md) antes de distribuir builds.

## Instalación para desarrollo

Requisitos: Windows, Python 3.11 o posterior, pip y conexión a un índice de paquetes para la primera instalación. El instalador comprueba al menos 1 GB libre antes de copiar la aplicación; instalar además dependencias, llama.cpp y un modelo requiere espacio adicional (el Qwen indicado ocupa alrededor de 0,78 GiB). Node.js solo es necesario para ejecutar las pruebas JavaScript. llama.cpp y un modelo GGUF local son necesarios para respuestas generativas; las actividades deterministas se pueden ejecutar sin IA desde el arranque de desarrollo. El proyecto no fija mínimos de CPU, RAM o GPU: el consumo y la velocidad dependen del modelo, cuantización, contexto y backend disponibles.

```powershell
python -m venv .venv
\.venv\Scripts\python.exe -m pip install -r requirements.txt
\.venv\Scripts\python.exe server.py --open
```

Abre `http://127.0.0.1:8787`. Configura el modelo fuera del repositorio en `%LOCALAPPDATA%\ALLEN\local_model.json` usando como referencia `config/local_model.example.json`. Para iniciar también la IA y comprobar su disponibilidad, configura llama.cpp y usa `start_allen.bat`; `Iniciar_ALLEN.bat` es el alias de inicio para usuarios que genera el instalador. Para cerrar los procesos lanzados por el launcher, ejecuta `Detener_ALLEN.bat`.

Las dependencias Python están fijadas en `requirements.txt`; para pruebas instala `requirements-dev.txt`. Las herramientas Nuitka/Zig están separadas en `requirements-build.txt` y no forman parte del entorno normal. Consulta [GUIA_INSTALACION_ALLEN.md](GUIA_INSTALACION_ALLEN.md) y [DOCUMENTACION_TECNICA_ALLEN.md](DOCUMENTACION_TECNICA_ALLEN.md).

## IA local

ALLEN integra un servidor compatible con la API local de llama.cpp y modelos GGUF. El nombre usado actualmente por el pipeline de distribución es `Qwen3.5-0.8B-Q8_0.gguf`, pero el repositorio no incluye los pesos y la configuración privada del equipo no se versiona. `start_local_ai.py` lee la configuración y preferencias, inicia o comprueba el servidor en loopback y valida inferencia. La configuración de ejemplo y el código usan como puertos habituales 8080 para llama.cpp y 8787 para ALLEN; ambos deben estar disponibles. No hay integración de IA en la nube implementada.

Sin motor/modelo, el modo de demostración depende de la configuración explícita y ofrece las actividades deterministas. No atribuyas respuestas generativas a la IA cuando el modelo no está activo. Revisa [SECURITY.md](SECURITY.md) antes de usar datos reales.

## Datos, privacidad y registros

La base SQLite de desarrollo usa `%LOCALAPPDATA%\ALLEN\allen.sqlite3` en Windows (o `~/.local/share/ALLEN` en otros sistemas), salvo que `ALLEN_DB_PATH` o `ALLEN_DATA_HOME` definan otra ruta. La configuración privada del modelo se ubica en `%LOCALAPPDATA%\ALLEN\local_model.json`. No guardes GGUF, bases de datos, tokens ni claves privadas en el repositorio. No se implementa sincronización de cuentas ni telemetría de producto. Los logs técnicos dependen del modo de ejecución y pueden estar bajo `logs/` durante desarrollo o bajo el directorio de datos en ejecución; revisa y redacta cualquier log antes de compartirlo.

## Desinstalación y actualización

El instalador de desarrollo copia ALLEN a `%LOCALAPPDATA%\ALLEN\app`; la desinstalación normal consiste en detener ALLEN y retirar esa carpeta. La base de datos/configuración puede quedar en `%LOCALAPPDATA%\ALLEN`; respáldala antes de eliminarla si quieres conservar progreso. El script Inno Setup, aún no validado como release, ofrece eliminar también los datos bajo `%ProgramData%\ALLEN` al desinstalar. No hay actualizador automático verificado: instala una copia nueva después de respaldar los datos y revisa las notas técnicas para cambios de esquema.

## Android

La aplicación Android está planeada, pero `android/` está vacío en este checkout: no hay todavía proyecto compilable, APK, puente ARM64 ni guía de compilación.

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
2. Obtén un modelo **instruct/chat en formato GGUF** de una fuente de confianza, con licencia que permita tu uso y soporte de español. Descarga el archivo completo antes de desconectarte. Para empezar en hardware modesto, prueba un modelo cuantizado pequeño; velocidad y memoria dependen del equipo y del modelo. El repositorio no incluye los pesos. `install_allen.ps1` puede iniciar una descarga de Qwen si se detecta llama.cpp y la persona acepta expresamente el prompt; fuera de ese flujo, configura manualmente un GGUF.
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
| Feria educativa | Microlecciones offline, retos graduados, rutas, simulaciones, proyectos STEAM, sesión de visitante y evaluación local con feedback IA opcional |
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
- El log principal rotativo registra clases de error. El diagnóstico opcional de Feria escribe métricas de evaluación y hasta 2.000 caracteres de respuesta del modelo en `logs/steam-evaluation.log` bajo el directorio de datos; filtra correos y teléfonos reconocibles, pero no debe asumirse que elimina todo dato personal. Los logs rotan. La aplicación no implementa telemetría de producto.
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

Si tienes Node, ejecuta las pruebas de frontend (Node no es necesario para usar ALLEN):

```powershell
node --test tests/*.mjs
```

Consulta [VALIDATION.md](VALIDATION.md) para resultados y límites de la verificación, [ARCHITECTURE.md](ARCHITECTURE.md) para el diseño, y [REPO_AUDIT.md](REPO_AUDIT.md) para la clasificación y limpieza del repositorio.

## Solución de problemas

- **Puerto ocupado:** cierra la otra ventana de Allen. No ejecutes dos servidores en 8787.
- **Dependencias sin Internet:** la primera instalación necesita descargar paquetes. Después puedes desconectarte. Para distribuir en un lugar sin red, prepara previamente el entorno o un repositorio de ruedas compatible con la misma versión de Python y Windows.
- **Modelo desconectado:** abre llama.cpp, espera que cargue y comprueba puerto/nombre. Se conserva acceso a todos los recursos deterministas.
- **Texto demasiado largo:** envía secciones menores o amplía el contexto tanto en Allen como en el servidor, teniendo en cuenta la memoria disponible.
- **Respuesta interrumpida:** puedes regenerarla; las respuestas incompletas no se guardan como conversación final.

## Beta y limitaciones

La experiencia de Feria, las rutas, microlecciones y evaluación local tienen pruebas automatizadas. El tutor clásico y la IA local dependen de la configuración del equipo y el modelo; su calidad educativa requiere evaluación con GGUF reales. No existe certificación curricular, multiusuario con aislamiento, autenticación docente ni validación de seguridad para uso institucional con menores. El empaquetado Windows no se encuentra validado y Android contiene únicamente preparación/documentación.

## Roadmap

**Hecho en el código:** actividades de Feria offline, rutas y microlecciones locales, evaluación rubricada determinista y feedback IA opcional; interfaz web local y tutor clásico.

**En desarrollo / pendiente de validar:** build firmado Windows, instalador Inno Setup, instalación/desinstalación en máquinas limpias y evaluación pedagógica con modelos concretos.

**Planeado:** embeddings y RAG semántico local, contenidos curriculares revisados por docentes, exportación/sincronización manual, roles docentes con aislamiento real, y aplicación Android funcional.

## Licencia y contacto

No se encontró un archivo `LICENSE` que defina la licencia del código de ALLEN; el estado de la licencia del proyecto está **pendiente de definición**. Los avisos dentro de `licenses/` se refieren a componentes de terceros y no otorgan por sí solos una licencia al repositorio completo. Para asuntos de seguridad, sigue el canal privado descrito en [SECURITY.md](SECURITY.md). Para consultas generales, contacta al propietario del repositorio desde su plataforma de alojamiento.

## Preguntas frecuentes

- **¿ALLEN necesita Internet?** Para instalar dependencias Python y obtener llama.cpp/modelos puede hacer falta conexión. Ya instalado, la interfaz, los datos y el motor configurado trabajan en el equipo; no se requiere una API de IA en la nube.
- **¿Puedo cambiar el modelo?** Sí. Configura otra ruta GGUF y un `llama-server` compatible en `%LOCALAPPDATA%\ALLEN\local_model.json`; consulta la licencia del modelo que elijas.
- **¿Dónde queda mi progreso?** En la base SQLite local. En desarrollo Windows se guarda normalmente bajo `%LOCALAPPDATA%\ALLEN`.
- **¿ALLEN envía conversaciones a Internet?** El código revisado apunta la IA a loopback y no implementa telemetría. El comportamiento de herramientas/servicios externos que el usuario instale queda fuera de ALLEN.
- **¿Está terminado?** No. Es una beta funcional; el instalador final, validación institucional y app Android siguen pendientes.
- **¿Cómo reporto un problema?** Incluye versión, pasos para reproducir y mensajes relevantes; elimina rutas personales, conversaciones, tokens y otros datos privados antes de compartir logs.

## Contribuciones

El estado público y la política de contribuciones de este repositorio no están documentados. Antes de preparar un cambio externo, confirma con el propietario si acepta contribuciones. Para trabajo local, crea una rama, conserva cambios ajenos, ejecuta las pruebas Python y JavaScript, y documenta límites reproducibles.

## Dataset y entrenamiento opcional

Se añadió `allen_training/` con reglas, un dataset conversacional sintético de 2.800 ejemplos por áreas, metadatos, validación, splits por grupos y un script SFT LoRA opcional. La aplicación no depende de esta carpeta. No se entrenó ningún modelo. Consulta `allen_training/README.md` y `allen_training/DATASET_CARD.md` para conocer la revisión pendiente y sus límites.

Para validar sin entrenar: `python allen_training/train.py`.

## Inicio con IA local

`start_allen.bat` comprueba dependencias y ejecuta `start_local_ai.py` antes de iniciar el backend. Si la IA no está disponible, el inicio continúa solo cuando el modo demo se habilitó explícitamente en las preferencias. Configura el GGUF y `llama-server.exe` en `%LOCALAPPDATA%\ALLEN\local_model.json`, usando `config/local_model.example.json` como guía. El proceso de llama.cpp puede permanecer activo después de cerrar la interfaz; utiliza `Detener_ALLEN.bat` para detener los procesos del launcher y revisa el Administrador de tareas si el motor continúa activo.
