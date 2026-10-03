# ALLEN
## Documentación técnica, arquitectura e implementación

**Versión documentada:** estado del repositorio inspeccionado el 24 de septiembre de 2026.\
**Idioma:** español.\
**Alcance:** aplicación web local para Windows, modo Feria actual y tutor clásico que se conserva en `/study`.

> Esta guía describe el código y configuración inspeccionados. Distingue funcionalidades verificadas, configuración local de este equipo y propuestas. No es una certificación de seguridad ni una evaluación pedagógica formal.

## 1. Introducción

ALLEN es un tutor educativo que funciona como aplicación web servida en el equipo del usuario. El repositorio ofrece una interfaz de feria con experiencias breves y un tutor clásico con perfiles, biblioteca, ejercicios y progreso. El backend está escrito en Python/FastAPI; la interfaz usa HTML, CSS y JavaScript nativo. Se puede conectar a un servidor compatible con la API local de llama.cpp para generar respuestas abiertas. Varias actividades y contenidos se preparan en archivos JSON locales y siguen disponibles sin el modelo.

El proyecto busca hacer más accesible la práctica de habilidades digitales, programación, ciberseguridad, pensamiento lógico y actividades STEAM cuando la conectividad es limitada. Su enfoque educativo es convertir preguntas y temas en explicaciones, ejemplos, práctica y reflexión. La IA apoya la conversación; no reemplaza al docente ni valida por sí sola el dominio de un tema.

**ALLEN transforma la inteligencia artificial de una herramienta que responde en una herramienta que enseña, guía y permite practicar.**

## 2. Objetivo del sistema

El sistema ofrece acompañamiento con experiencias locales, niveles, microlecciones y retos. En la versión de Feria actual hay evaluación breve antes/después de algunas lecciones, diez mapas de ruta con módulos secuenciales, simulaciones de decisión, exploración tecnológica, proyectos STEAM y una aventura. El progreso lúdico da puntos y rangos; los resultados de autoevaluación no equivalen a certificación.

El contenido determinista reduce la dependencia de Internet y del modelo. El servidor solo acepta como motor de texto una URL HTTP loopback configurada; la aplicación no intenta conectarse a una API de IA en la nube. El modo offline completo debe probarse en el equipo de implementación: instalar dependencias por primera vez sí requiere preparar paquetes con anticipación o disponer de conexión durante la instalación.

## 3. Arquitectura general

```text
Navegador local
  ├─ /fair (predeterminado): feria, conversación efímera y recursos locales
  └─ /study: tutor clásico, perfiles e historial opcional
          │ fetch same-origin /api/* (token local; JSON/SSE)
          ▼
FastAPI (127.0.0.1:8787)
  ├─ API educativa clásica ── SQLite (perfiles, progreso, preferencias…)
  ├─ API Feria ─────────────── SQLite (contadores anónimos agregados)
  ├─ datasets educativos ───── data/*.json y data/library/*
  └─ LocalAI ── HTTP loopback ── llama-server (si está configurado)
                                      └─ GGUF local (este equipo: Qwen3.5-0.8B-Q8_0)
```

**Observación:** no son instalaciones equivalentes. El repositorio contiene el código de integración de llama.cpp, pero no el ejecutable `llama-server` ni los pesos. En el equipo inspeccionado, la configuración privada bajo `%LOCALAPPDATA%\ALLEN\local_model.json`, el ejecutable y el GGUF configurado existen; la configuración no se incluyó ni sus rutas privadas se reproducen aquí. En esta auditoría, las comprobaciones HTTP al puerto 8080 excedieron el tiempo límite: no afirmo que el modelo estuviese activo en ese momento. El archivo de configuración de ejemplo usa nombres genéricos.

## 4. Componentes del sistema

### Frontend

HTML y CSS con JavaScript ES modules nativo; no hay `package.json`, Node ni paso de compilación requerido para ejecutar la aplicación. `frontend/index.html` es la interfaz del tutor clásico y `frontend/fair.html` la feria. `frontend/fair.js` conecta experiencia, conversación, juego y API; `fair-learning.js`, `fair-paths.js` y `fair-session.js` separan actividades, rutas y estado de visitante. `frontend/app.js` y `frontend/components/` implementan la interfaz clásica y utilidades reutilizadas. `services.js` concentra las peticiones locales.

CSS está en `frontend/styles/app.css`, `fair.css`, `fair-brand.css`, `fair-experience.css`, `fair-unified.css` y `game-adventure.css`. Hay iconos SVG locales en `frontend/assets/icons.svg`, marca/mascota original en `allen.svg` y `components/fair-mascot.js`. Los archivos de versión/licencia Lucide acompañan los iconos. No se cargan fuentes ni scripts desde CDN en la interfaz local.

### Backend y rutas

Python 3.11+ y FastAPI (versiones fijadas en `requirements.txt`). `server.py` inicia Uvicorn solo en `127.0.0.1:8787`. `backend/app.py` construye la aplicación, middleware, API clásica y páginas. `backend/fair.py` registra rutas `/api/fair/*`. `schemas.py` valida modelos Pydantic; `database.py` inicializa SQLite; `ai.py` habla con la API compatible con llama.cpp; `prompts.py`, `tutoring.py`, `conversation.py`, `education.py` y `library.py` contienen lógica de tutoría, prompts, generación acotada y biblioteca. `security.py` contiene saneamiento de respuestas.

Rutas principales observadas en FastAPI:

| Ruta | Uso |
|---|---|
| `GET /` | Feria por defecto; `/?mode=study` sirve interfaz clásica |
| `GET /fair` | Feria |
| `GET /study` | Tutor clásico |
| `GET /api/health`, `/api/model/status` | Estado del backend y motor |
| `/api/chat`, `/api/tutor`, `/api/summarize`, `/api/translate` | Conversación y tutor clásico |
| `/api/library/*`, `/api/quiz/*`, `/api/flashcards/*`, `/api/profiles/*` | Biblioteca y funciones clásicas |
| `/api/fair/token`, `/sessions`, `/end`, `/event`, `/stats`, `/chat`, `/challenge`, `/answer` | Sesiones temporales, interacción y métricas de Feria |
| `GET /api/fair/data/{dataset}` | Lista permitida de JSON educativo local |
| `GET /api/fair/qr`, `/links` | QR local y enlaces opcionales del proyecto |

FastAPI desactiva sus páginas públicas OpenAPI/Swagger. Las rutas `GET` no requieren token; operaciones de escritura requieren `X-Allen-Token` emitido por `/api/fair/token`. Los endpoints `/api/*` son específicos de la aplicación local; Vercel configura cabeceras para su sitio, no despliega este backend.

### Motor educativo, Feria y scoring

Los ficheros JSON son la fuente de lecciones, evaluaciones, retos, simulaciones, rutas, proyectos, curiosidades, rangos, logros y mensajes motivacionales. La feria usa sus propios componentes cliente para navegación, selección y presentación; el backend sirve una lista permitida de datasets, administra sesiones temporales, valida acciones del reto del endpoint clásico de Feria y agrega eventos. Los puntos de la nueva capa educativa se calculan en el navegador y se guardan en `sessionStorage`; no son una puntuación firmada por servidor ni una medida invulnerable a manipulación.

Una visita conserva apodo temporal, nivel, logros, recompensas, evaluaciones y avance durante esa pestaña. El visitante se reinicia con “Nueva persona” y caduca tras 140 segundos sin actualización local; la sesión de API caduca a los 210 segundos. La dificultad “Sorpréndeme” se deriva de los puntos: Fácil por debajo de 200, Normal desde 200 y Difícil desde 600. Hay otros ajustes de nivel por experiencia.

El helper de retos asigna 100 puntos por respuesta correcta al primer intento, 75 con pista, 50 en segundo intento y 0 por respuesta incorrecta. Las recompensas identificadas se aplican una sola vez por clave dentro de esa visita. Seis rangos definidos en `data/ranks.json` y ocho logros en `data/achievements.json` alimentan la interfaz. La evaluación compara tres preguntas de entrada y tres de salida; el resultado y puntos adicionales se guardan en sesión. No es evaluación psicométrica.

### IA local

`backend/ai.py` consulta `/health`, `/v1/models` y `/v1/chat/completions`, procesa respuesta progresiva y limita el tamaño. La configuración valida direcciones locales, rechaza proxies del entorno/redirecciones y restringe formato/contexto. `start_local_ai.py` lee `%LOCALAPPDATA%\ALLEN\local_model.json`, consulta preferencias SQLite y solo arranca un ejecutable local llamado `llama-server`/`llama-server.exe` con modelo `.gguf` existente y host loopback. No descarga modelos. `start_allen.bat` llama este helper antes de `server.py`.

El modelo detectado en la configuración privada de este equipo es **Qwen3.5-0.8B-Q8_0.gguf**. No está distribuido con el repo. GGUF es un formato de almacenamiento/cuanti­zación de modelos utilizado por llama.cpp; la cuantización Q8 almacena pesos en una representación de aproximadamente 8 bits, además de metadatos y escalas. El sufijo `0.8B` indica la clase de tamaño anunciada, no el uso total de RAM. No calculo memoria necesaria porque el repositorio no proporciona una medición por máquina y el uso total depende del contexto, runtime y hardware.

`backend/prompts.py` define instrucciones educativas. `backend/fair.py` ofrece una respuesta revisada para algunas introducciones exactamente reconocidas y contenido de lección en el fallback; no convierte toda respuesta generativa en contenido verificado. La indisponibilidad del modelo no debe presentarse como respuesta generada por IA.

### Persistencia

SQLite guarda la aplicación clásica en `%LOCALAPPDATA%\ALLEN\allen.sqlite3` en Windows (`~/.local/share/ALLEN` como alternativa). `ALLEN_DB_PATH` permite definir una ruta específica. Esquema en `backend/database.py`: `users`, `settings`, `conversations`, `progress`, `quiz_results`, `flashcards`, `learning_sessions`, `library_packs`, `student_memory`, `saved_answers`, `conversation_states`. Las relaciones usan claves foráneas y borrado en cascada para los registros vinculados al perfil.

El subsistema Feria agrega tablas por día —visitas/sesiones, preguntas, retos, simulaciones, juegos, proyectos y actividades/rutas— y no escribe apodo ni contenido del chat. La clave de visitante y su estado se guardan en memoria Python por proceso; la conversación de feria se mantiene en la pestaña. El agregado SQLite y estado efímero no deben confundirse con un historial de visitantes.

## 5. Flujo completo de funcionamiento

1. `start_allen.bat` valida Python 3.11, crea/reutiliza `.venv`, comprueba o instala paquetes, intenta levantar IA configurada y ejecuta `server.py --open`.
2. FastAPI escucha en loopback puerto 8787 y abre el navegador. `/` muestra Feria; `/study` conserva el tutor clásico.
3. Feria: atracción → apodo opcional → nivel → menú por tipo de experiencia. Se crea sesión backend y se cargan JSON locales mediante el endpoint de datos.
4. El visitante practica; recompensas/avance se reflejan en `sessionStorage`. Eventos agregados se envían a la API y SQLite.
5. Chat: interfaz envía mensaje, historial temporal, acción didáctica y nivel a `/api/fair/chat`. Backend puede usar respuesta local revisada, modelo local o fallback de contenido preparado. No se persiste el texto en SQLite de Feria.
6. “Nueva persona”, caducidad o fin de visita limpia identidad y estado de la pestaña. No borra los agregados anónimos diarios.

## 6. Funciones principales

El tutor clásico incluye chat, tutoría, biblioteca local, ejercicios y quizzes, resúmenes/traducción, tarjetas de estudio, perfiles y vista de progreso. La Feria agrega bienvenida, microlecciones, reto con pistas, simulador, proyectos STEAM, exploración tecnológica, sorpresa, juego, rangos, logros, estadísticas agregadas y chat temporal. Las funciones de voz dependen del navegador y son opcionales.

## 7. Sistema de aprendizaje

El contenido local preparado guía con conceptos y ejemplos, práctica y comprobación. Las evaluaciones comparan tres respuestas previas y tres posteriores; las rutas ordenan módulos, reto y evidencia de proyecto. Sirven para orientar la práctica, no prueban retención ni certifican dominio. El contenido y la adecuación curricular necesitan revisión docente.

## 8. Sistema de puntos y rangos

Nombres y umbrales viven en `data/ranks.json`; logros en `data/achievements.json`. `frontend/fair-session.js` gestiona score, rango, progreso, selección de preguntas y recompensas idempotentes en `sessionStorage`. El reto concede 100 puntos por acierto inicial, 75 con pista, 50 por acierto en segundo intento y 0 por error. No es puntuación firmada ni resistente a manipulación desde el cliente.

## 9. Funcionamiento offline

Una vez instaladas las dependencias, la interfaz, los JSON y actividades deterministas se sirven localmente. El modelo generativo requiere que llama.cpp y los pesos estén ya instalados y cargados localmente. Sin modelo, el tutor clásico indica modo demo y la Feria recurre a contenido preparado/fallback, además de retos, lecciones y simulaciones. Un dispositivo desconectado no puede completar la primera descarga de dependencias/modelo si estos no se prepararon antes.

El indicador de red consulta `navigator.onLine`; el código aclara que no verifica acceso a Internet. Durante esta documentación no se apagó la red ni se ejecutó una prueba física sin conectividad, así que la operación totalmente desconectada en hardware de destino queda por validar.

## 10. Privacidad y datos

En Feria, apodo, chat, evaluaciones, puntos y avance viven principalmente en `sessionStorage`; las sesiones API viven en memoria. SQLite de Feria conserva contadores diarios agregados sin nombre ni texto de chat. En `/study`, perfiles, preferencias e historial opcional se guardan en SQLite según la retención. Las bases y copias requieren protección local.

## Auditoría e inventario de archivos

### Árbol de primer nivel y módulos relevantes

```text
allen_offline_ai/
├── backend/                 FastAPI, IA local, SQLite, educación y seguridad
├── config/                  JSON de ejemplo (no secretos ni configuración activa)
├── data/                    bancos JSON y biblioteca Markdown/JSON
│   └── library/              material de referencia del tutor clásico
├── frontend/                dos interfaces, módulos JS, CSS y SVG locales
│   ├── assets/               iconos, marca y licencias
│   ├── components/           interfaz/utilidades del tutor y mascota
│   └── styles/               estilos del tutor clásico
├── tests/                    pruebas Python y Node
├── models/                   placeholder `.gitkeep`; pesos excluidos/no distribuidos
├── android/                  directorio vacío en el árbol auditado
├── legacy/                   directorio vacío en el árbol auditado
├── allen_training/           placeholders y archivos de documentación; ver advertencia
├── server.py                 entrada Uvicorn loopback
├── start_local_ai.py         arranque controlado de llama.cpp local
├── start_allen.bat           lanzador Windows
├── install_allen.bat/.ps1    instalador Windows
├── requirements*.txt         versiones del entorno Python
├── README.md                 instrucciones y descripción existentes
├── FAIR_MODE.md              guía previa de feria
├── SECURITY.md               orientación de seguridad
├── vercel.json               despliegue/cabeceras del sitio estático
└── DOCUMENTACION_TECNICA_ALLEN.md
```

Inventario de datasets en el commit/árbol inspeccionado: `lessons.json` (83 lecciones, 13 áreas), `challenges.json` (144 preguntas, 11 categorías), `simulations.json` (10 escenarios), `steam_projects.json` (13 proyectos, 9 intereses), `tech_topics.json` (12 áreas), `curiosities.json` (12 actividades), `routes.json` (10 rutas), `ranks.json` (6 rangos), `achievements.json` (8 logros), `assessments.json` (evaluaciones por tema), `motivational_messages.json` (mensajes). `data/library/` contiene material clásico de matemáticas, tecnología, inglés, programación y ciencia; `library-example.json` es un ejemplo de formato.

### Clasificación del inventario

El inventario cubrió los archivos visibles del repositorio, imports, referencias, rutas FastAPI, configuración, instaladores, pruebas, directorios de modelo y entrenamiento. Se excluyó contenido interno de `.git`, `.venv` y caches al contar archivos del proyecto. El inventario reproducible encontró **78 archivos visibles/no ignorados y 977 862 bytes**, incluyendo documentos existentes; es una medida del árbol local inspeccionado, no del tamaño de instalación. No se calculó delta antes/después porque no se eliminó nada ni había una medición previa fiable.

Clasificación funcional representativa (no una lista de cada fichero):

| Grupo/archivo | Clasificación | Evidencia/uso |
|---|---|---|
| `server.py`, `backend/*.py`, `frontend/fair.html`, `frontend/fair.js`, `frontend/index.html`, `frontend/app.js` | Necesario | Servidor, API, tutor/feria y frontend servido |
| `frontend/components/*`, hojas CSS, `frontend/assets/*` | Necesario | Importadas/servidas por interfaces activas |
| `data/*.json`, `data/library/*` | Necesario | Datos consultados por API, motor o interfaz |
| `start_allen.bat`, `start_local_ai.py`, `install_allen.bat/.ps1`, `requirements.txt`, `config/*.example.json` | Necesario/operativo | Arranque, instalación y configuración modelo |
| `tests/*`, `README.md`, `FAIR_MODE.md`, `SECURITY.md` | Opcional para ejecución; recomendados para mantenimiento | Pruebas y documentación; no son import de runtime |
| `vercel.json` | Opcional según despliegue | Solo aplica al publicar sitio estático; no ejecuta API local |
| `models/.gitkeep`, carpetas vacías `android/`, `legacy/`, training `data/`, `sources/`, `output/` | Placeholder/opcional | No contienen el modelo ni código Android/legacy activo |
| `.venv/`, `__pycache__/**`, `.pytest_cache/**`, `allen_training/__pycache__/**` | Generado automáticamente | Entorno, bytecode y caché ignorados por Git; conservar, no forman entrega fuente |
| `.git/` | Metadatos de control de versiones | Necesario para historial Git; no es runtime |
| `frontend/fair-world.js` | Posiblemente innecesario/obsoleto | Contiene renderizadores de mundo/ruleta, pero no hay imports o llamadas a sus exports en frontend, backend o pruebas. No se eliminó sin una confirmación completa de dependencias |
| Copias duplicadas/obsoletas confirmadas | Ninguna identificada y eliminada | `frontend/index.html` es el tutor clásico vigente servido en `/study`, no se clasifica como copia muerta |
| Código aparentemente muerto | Sin eliminación en esta auditoría | El análisis estático no prueba que un handler, ruta dinámica o script de instalador sea prescindible |

**Hallazgo documental:** `README.md` menciona `android/README.md`, `allen_training/README.md`, `DATASET_CARD.md`, scripts/dataset de entrenamiento; esos archivos no aparecen en el árbol visible inspeccionado. `android/` y `legacy/` no contienen fuentes. En `allen_training/` solo se encontraron `.pyc` en `__pycache__` y subdirectorios vacíos. Por eso no se atribuye a este checkout un APK, fuentes de entrenamiento o proceso SFT reproducible. La caché no se borró; los `.pyc` no sustituyen fuentes. También la guía `FAIR_MODE.md` describe un panel “Presentador” y experiencia previa que no coincide enteramente con la interfaz de feria actual; debe tratarse como documento pendiente de sincronización.

**Hallazgo de instalador comprobado:** ejecuté `install_allen.ps1` con `-SkipDependencies` en una carpeta temporal desechable y sin usar la base de datos del proyecto. Copió `frontend/fair.html`, `fair-learning.js` y los CSS nuevos, pero omitió `data/lessons.json` y los demás JSON raíz (solo copia `data/library`); así, el backend instalado no puede servir datasets que la Feria requiere. También omitió `frontend/fair-world.js`, pero el rastreo de imports/consumidores no encontró una referencia activa a ese módulo, por lo que esto no bloquea el runtime actual y se clasifica como código posiblemente obsoleto. Esta instalación independiente de Feria no está lista para entrega hasta corregir la copia de datos y repetir la prueba. La carpeta temporal de auditoría se conserva fuera del repositorio.

No se borraron archivos. Motivo: el requerimiento daba prioridad a no eliminar recursos sin verificar todas las dependencias y el espacio ahorrable no justifica riesgo. Los `.venv`/caches están ignorados por Git y se clasifican como generados; su eliminación puede hacerse por separado tras confirmar que se quiere recuperar espacio.

## 11. Requisitos del equipo

- Windows es la plataforma del lanzador e instalador comprobados. Python 3.11 o superior.
- Dependencias fijadas: FastAPI 0.136.3, Uvicorn 0.49.0, HTTPX 0.28.1 y qrcode 8.2. `requirements-dev.txt` añade pytest 9.1.1.
- Navegador moderno con módulos ES, `fetch`, SQLite local disponible mediante Python.
- Feria no requiere Node, bundler ni CDN para el runtime. Node se usa solo para la suite `.mjs`.
- Puerto ALLEN 8787; modelo por defecto de ejemplo 8080. Ambos deben estar libres y distintos.
- Base Windows `%LOCALAPPDATA%\ALLEN\allen.sqlite3`. `ALLEN_DB_PATH` puede sobreescribirla. Logs rotativos, `allen.log`, en el directorio de datos local.
- Configuración de ejemplo `config/settings.example.json` documenta propiedades; el backend guarda ajustes reales en SQLite. `config/local_model.example.json` solo enseña la forma del objeto de ejecutable/modelo; la configuración activa de este equipo se encuentra fuera del repo.
- `vercel.json` solo especifica rewrites/cabeceras para el despliegue definido; README indica que el servicio completo FastAPI/modelo no se publica en Vercel.

## 12. Instalación de ALLEN desde cero

### Inicio recomendado en Windows

```powershell
.\start_allen.bat
```

El `.bat` usa Python 3.11+, crea `.venv`, valida las versiones fijadas e instala `requirements.txt` si faltan. La primera instalación requiere Internet o una fuente de ruedas preparada. Inicia `start_local_ai.py` y después `server.py --open`. Para detener el backend, usa `Ctrl+C` en su ventana. Navegación: `http://127.0.0.1:8787/` (Feria), `/study` (tutor clásico), `/fair` (Feria explícita).

### Inicio manual / pruebas

```powershell
.\.venv\Scripts\python.exe server.py --open
```

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_fair -v
node --test tests/test_fair_learning.mjs tests/test_fair.mjs
```

Suite completa del repositorio (pytest si está instalado):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests/*.mjs
```

Las dos últimas órdenes son instrucciones de mantenimiento; no se afirma que se hayan ejecutado todas las pruebas de cualquier archivo ajeno a `test_fair*.mjs`.

### Modelo local separado

Instala llama.cpp y descarga un modelo GGUF de fuente/licencia apropiada por separado. Configura rutas locales en `%LOCALAPPDATA%\ALLEN\local_model.json`. La forma de la orden del README para iniciarlo manualmente es:

```powershell
& 'C:\ruta\a\llama-server.exe' -m 'C:\ruta\a\modelo.gguf' --host 127.0.0.1 --port 8080 -c 4096
```

El helper `start_local_ai.py` puede arrancarlo si la configuración privada existe, es válida y el puerto está libre. El consumo depende del GGUF, contexto, llama.cpp, cuantización y hardware; este documento no da un mínimo RAM no medido.

El instalador copia los datasets `data/*.json`, la biblioteca y la aplicación a `%LOCALAPPDATA%\ALLEN\app`; genera `Iniciar ALLEN.bat` usando el mismo lanzador probado por el repositorio. Con Python y dependencias instaladas, basta con abrir ese archivo. La primera ejecución instala dependencias y requiere Internet; después el servidor y el modelo local ya configurado se inician automáticamente, y el navegador se abre al responder el servidor.

## 13. Cómo iniciar ALLEN desde Visual Studio Code

Abre la carpeta del proyecto en VS Code y usa la terminal PowerShell integrada para ejecutar `start_allen.bat`, o inicia `python server.py --open` desde el entorno virtual. Deja la ventana abierta mientras uses ALLEN. Si hay un modelo local configurado, el lanzador lo inicia antes del backend; si no, ALLEN abre en modo demo. No expongas el backend a la red.

## 14. Arranque rápido

1. En Windows, ejecuta `start_allen.bat`.
2. Espera a que el backend inicie y abra el navegador.
3. Abre `/` o `/fair` para Feria y `/study` para el tutor clásico.
4. Si configuraste llama.cpp y un modelo GGUF local, el lanzador los inicia automáticamente. De lo contrario, ALLEN funciona en modo demo con herramientas educativas locales.

## 15. Solución de problemas

- **Puerto 8787 ocupado:** cierra el servidor Allen duplicado.
- **No inicia:** revisa Python 3.11+, `.venv`, dependencias y salida de consola.
- **Sin Internet al instalar:** prepara previamente ruedas/dependencias para ese equipo.
- **IA lenta/desconectada:** verifica proceso, puerto 8080, ruta/compatibilidad GGUF, contexto y recursos del equipo.
- **Feria sin datos en copia instalada:** limitación comprobada del instalador actual; corregir antes de distribuir.
- **Android:** no hay fuentes ni APK en el `android/` vacío de este checkout.

## 16. Estructura de carpetas

```text
allen_offline_ai/
├── backend/                 FastAPI, IA, persistencia y motor educativo
├── config/                  JSON de ejemplo
├── data/                    datasets locales y biblioteca
├── frontend/                tutor clásico y Feria; assets, components, styles
├── tests/                   suites Python y Node
├── models/                  solo placeholder; pesos externos al repo
├── android/ legacy/          directorios vacíos en el checkout
├── allen_training/          placeholders/caché; fuentes citadas ausentes
├── server.py                Uvicorn loopback
├── start_local_ai.py        arranque llama.cpp
├── start_allen.bat          lanzador Windows
└── install_allen.bat/.ps1   instalador Windows
```

El inventario anterior contiene el detalle por carpetas y JSON.

## 17. Configuración

- `config/settings.example.json` documenta ajustes; los valores activos del tutor clásico se guardan en SQLite.
- `config/local_model.example.json` muestra formato de rutas; configuración privada activa en `%LOCALAPPDATA%\ALLEN\local_model.json` en este equipo.
- Backend loopback 8787; modelo ejemplo 8080; `ALLEN_DB_PATH` cambia ubicación SQLite.
- El puerto/contexto configurado en ALLEN debe coincidir con llama.cpp; no guardar GGUF o secretos en Git.
- Feria almacena nivel/puntos en `sessionStorage`; algunos enlaces pueden usar `localStorage`.

## 18. Desarrollo

Modifica módulos Python/FastAPI y frontend ES/CSS local manteniendo imports, CSP y peticiones same-origin. Revisa ejemplos vecinos antes de cambiar esquemas; valida datos, agrega pruebas unitarias y comprueba ambos modos en navegador. El árbol no requiere Node/bundler para ejecutar la aplicación.

## 19. Cómo agregar una lección

1. En `data/lessons.json`, agrega un ID único/estable y completa `area`, `topic`, `concept`, `conceptEasy`, `example`, `realWorld`, `practice`, `question`, `options`, `correct`, `feedback`, `altExample`, `howItWorks` y `advanced`, según los registros actuales.
2. En `data/assessments.json`, crea para el mismo ID listas `pre` y `post` de tres preguntas cada una, opciones, índice correcto y explicación.
3. Si el área es nueva, actualiza el catálogo/representación correspondiente. No cambies IDs ya referenciados por rutas.
4. Valida JSON y ejecuta pruebas de cobertura/opciones. Pide revisión docente de exactitud y nivel.

## 20. Cómo agregar una ruta

Agrega un objeto a `routes` en `data/routes.json`, con ID, nombre, objetivo, nivel/duración, lista ordenada `modules` con IDs de lección reales y `finalProject` con tarea/checklist. Prueba estados bloqueado, disponible, módulo terminado, reto y proyecto final en `frontend/fair-paths.js` y su suite.

## 21. Cómo agregar un reto

Agrega preguntas a `questions` en `data/challenges.json` con categoría, dificultad, texto, opciones, índice `correct`, explicación y pista siguiendo registros vecinos. Mantén claves únicas por opciones y suficiente cobertura por categoría/nivel para no repetir preguntas; valida el banco con `tests/test_fair_learning.mjs`.

Los escenarios se añaden en `simulations.json`, proyectos/intereses en `steam_projects.json`, áreas en `tech_topics.json` y sorpresas en `curiosities.json`. Toda nueva experiencia debe probarse con caso correcto, incorrecto y pantallas estrechas.

## 22. Modelo de negocio

El modelo indicado para la propuesta de ALLEN es: licencia institucional; servicios de implementación/instalación y capacitación; soporte/mantenimiento; personalización y módulos educativos a medida. Licencia y soporte pueden ser ingresos recurrentes, e implementación/personalización servicios adicionales. El repositorio inspeccionado no contiene código de licenciamiento, control de activaciones, facturación o soporte contractual; no hay precios documentados y esta guía no los inventa.

## 23. Implementación en una institución

1. Acordar propósito, dispositivos, grupos de edad, conectividad, custodia y retención de datos.
2. Medir en el hardware objetivo: Windows/Python, RAM libre, almacenamiento, CPU/GPU, espacios, resolución y periféricos. No reutilizar estimaciones genéricas como garantía.
3. Seleccionar modelo local compatible y licencia; verificar calidad, seguridad, privacidad y rendimiento con docentes antes de despliegue estudiantil.
4. Preparar instalador, dependencias y modelo con licencias aprobadas. Confirmar capacidad de instalación totalmente offline y copias de respaldo.
5. Instalar, configurar loopback/puerto/base y probar `/api/health`, estado de motor, rutas Feria y `/study`.
6. Revisar contenido curricular, lenguaje, edad y adecuación con educadores. Capacitar en límites de IA y privacidad.
7. Ensayar desconexión real del Wi-Fi, reinicio, reinicio de servidor/modelo y recuperación de backup en un equipo de prueba.
8. Entregar guía, responsable técnico, canal/alcance de soporte y plan de actualizaciones.

## 24. Escenario de implementación

```text
Institución → equipo local con ALLEN → estudiantes
                                ├→ lecciones y rutas
                                ├→ retos y simulaciones
                                └→ conversación local opcional con modelo
```

## 25. Mantenimiento

- Respaldar SQLite con la app detenida o mediante snapshot coherente; proteger la copia como dato personal. Probar restauración periódicamente.
- Conservar fuera del repo la base, GGUF, `local_model.json` y logs. No versionar `.env`, secretos o pesos.
- Al actualizar el código, revisar migraciones SQLite y cambios de esquema JSON; ejecutar pruebas, probar `/` y `/study` y respaldar antes del despliegue.
- La base clásica purga conversaciones según los ajustes de retención. Datos de perfil/progreso se conservan hasta borrarlos. La feria conserva agregados diarios; acordar política institucional y retención antes de su uso.
- `allen.log` es rotativo en `%LOCALAPPDATA%\ALLEN`; esta auditoría no atribuye monitorización remota ni envío de telemetría.
- Actualiza el modelo únicamente tras comprobar origen, licencia, compatibilidad y evaluación local. No existe actualización automática de GGUF.

## 26. Seguridad

El servidor escucha solo en loopback; Host/Origin y `Sec-Fetch-Site` se comprueban, las mutaciones requieren token aleatorio, se limita el cuerpo y se configuran CSP/cabeceras. La URL del modelo se restringe a loopback, sin proxies/redirecciones. SQLite usa consultas parametrizadas, claves foráneas y `secure_delete`; logs rotativos.

Son mitigaciones, no garantía: el proceso no autentica usuarios del sistema operativo; los perfiles clásicos no tienen contraseña y los datos cliente de Feria se pueden alterar localmente. La salida del modelo puede ser errónea o inadecuada. No hay evidencia de pentest, análisis completo de dependencias o certificación de privacidad en este checkout.

## 27. Limitaciones actuales

- Modelo de 0.8B es pequeño y puede inventar, simplificar en exceso o fallar; una respuesta local revisada existe solo para intents educativos acotados.
- El proceso de aprendizaje/puntuación de Feria vive en el cliente y sus pre/post de tres ítems son señales de práctica, no un instrumento validado ni certificación.
- El contenido estructurado es sustancial (83 lecciones, 144 retos y 10 rutas observadas), pero aún requiere validación curricular y ampliación por docentes.
- La feria tiene frontend/interfaz local y métricas anónimas agregadas; no es un sistema multiusuario institucional autenticado. Datos de pestaña expiran y no proporcionan progreso duradero entre visitas.
- Estado de red solo refleja el navegador. No se verificó corte físico de Internet durante esta auditoría.
- `android/` está vacío; no existe APK observado. `allen_training/` no tiene fuentes de entrenamiento visibles pese a afirmaciones del README.
- La calidad audible/voz y el funcionamiento real del modelo no se confirmaron en esta sesión; en la inspección el endpoint local 8080 excedió el timeout.
- La distribución del instalador excluye varios directorios raíz por reglas explícitas y copia selectivamente `data/library`; el nuevo modo Feria/data debe validarse en la copia instalada antes de distribuir, ya que el instalador se escribió para una estructura anterior.

## 28. Roadmap técnico

**Propuesta, no funcionalidad ya implementada:**

1. Alinear README, FAIR_MODE.md, instalador y docs con la experiencia/JSON actual; verificar instalación copiada y añadir prueba de humo del artefacto.
2. Recuperar o retirar de forma revisada las afirmaciones y referencias a fuentes de entrenamiento/Android faltantes.
3. Ejecutar revisión docente por contenido/edad, construir pruebas de regresión sobre rutas completas y evaluar resultados con estudiantes bajo consentimiento institucional.
4. Robustecer persistencia/exportación de avance con controles de privacidad y evitar puntajes de confianza exclusiva en frontend.
5. Crear perfil de configuración institucional, políticas de retención y respaldos con restauración ensayada; sin presentar roles actuales como aislamiento seguro.
6. Fijar versión/hash/licencia de llama.cpp y modelo por despliegue y evaluación reproducible de calidad/rendimiento en equipos objetivo.
7. Ampliar cobertura de pruebas de instalación offline, accesibilidad, navegador y degradación con modelo apagado.
8. Considerar APK/roles/sincronización únicamente tras definir arquitectura, permisos, soporte y revisión de riesgos.

## 29. Checklist de instalación

- [ ] Python 3.11+ presente.
- [ ] Dependencias fijadas instaladas/preparadas sin red para el entorno destino.
- [ ] `start_allen.bat` abre el servidor en loopback 8787.
- [ ] Interfaz `/`, Feria `/fair` y tutor `/study` responden.
- [ ] Base SQLite local se crea en la ubicación elegida y backup probado.
- [ ] Si aplica, llama.cpp/GGUF/licencia configurados y `/api/model/status` verificado.
- [ ] Chat con modelo apagado se identifica honestamente como contenido local/demo.
- [ ] Prueba de desconexión física completada en hardware destino.

## 30. Checklist para entrega a cliente

- [ ] Equipo y rendimiento validados en las condiciones de aula.
- [ ] Modelo, software y contenido tienen licencia/revisión correspondiente.
- [ ] Retención, copias y responsable institucional definidos.
- [ ] Pruebas de reinicio, red desconectada y restauración ejecutadas.
- [ ] Docentes y soporte capacitados en límites de IA y privacidad.
- [ ] Checklist, guía y versión exacta entregados.

## 31. Limpieza realizada

**Archivos eliminados: ninguno.** No se cambiaron ni purgaron base SQLite, modelo, caches, assets, instaladores, código o contenido durante la fase de inventario. Los archivos temporales/cachés identificados (`.venv`, `.pytest_cache`, `__pycache__`) son generados e ignorados por Git, pero no los eliminé por el riesgo y por no ser necesario para el documento.

**Documento nuevo:** `DOCUMENTACION_TECNICA_ALLEN.md`.\
**Otros archivos del repositorio modificados por esta tarea:** ninguno. El resto de cambios ya existían en el árbol antes de iniciar esta tarea y se conservaron.

**Arquitectura observada:** interfaz HTML/JS local → FastAPI loopback → SQLite/JSON; generación opcional por llama.cpp compatible OpenAI local → GGUF externo al repositorio.\
**Modelo configurado en este equipo:** `Qwen3.5-0.8B-Q8_0.gguf`, existe en la ruta local configurada; la API de inferencia no respondió dentro del timeout de esta auditoría.\
**Dependencias declaradas:** Python/FastAPI/Uvicorn/HTTPX/qrcode y pytest para desarrollo; Node solo para tests JS.\
**Problemas documentales/de distribución:** referencias a fuentes Android/training ausentes; guía de feria previa desincronizada; instalador probado pero omite datasets requeridos; `fair-world.js` podría ser obsoleto; faltan prueba de desconexión física y confirmación de modelo activo.\
**Resultado de pruebas ejecutadas durante la ronda previa de cambios:** `python -m unittest tests.test_fair -q` (11 OK); `node --test tests/test_fair_learning.mjs tests/test_fair.mjs` (14 OK); `git diff --check` limpio para los archivos elegidos. Esta es una captura de la verificación existente de la ronda previa, no una afirmación de que esas pruebas se hayan repetido como parte de la auditoría documental actual.

## 32. Reporte final

- Documento principal: `DOCUMENTACION_TECNICA_ALLEN.md`; exportación PDF complementaria en `output/pdf/DOCUMENTACION_TECNICA_ALLEN.pdf`.
- Archivos eliminados durante la auditoría: ninguno.
- La lista de cambios previos al documento, arquitectura, comandos, requisitos y resultados está registrada en “31. Limpieza realizada” y las secciones precedentes.
- Hallazgos prioritarios: el instalador omite datasets requeridos; `fair-world.js` parece código sin referencias activas; faltan fuentes Android/entrenamiento citadas por otros documentos; modelo instalado no equivale a servicio activo; no se verificó desconexión física.
- Mejoras recomendadas están marcadas como propuesta en “28. Roadmap técnico”.
