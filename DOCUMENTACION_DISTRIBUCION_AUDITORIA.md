# Auditoría de distribución de ALLEN para Windows

Estado inicial inspeccionado el 24-09-2026. Esta auditoría precede a cualquier retirada de archivos. No se borró ni movió ningún instalador/launcher.

## Inventario solicitado

| Archivo | Función actual | Actualmente usado | Dependencias | Seguirá existiendo | Será reemplazado por | Seguro de eliminar ahora |
|---|---|---:|---|---:|---|---:|
| `Iniciar_ALLEN.bat` | Acceso de inicio visible; delega en `start_allen.bat` | Sí, flujo descrito al usuario | Windows CMD, Python venv | Sí durante transición | `ALLEN.exe` | No |
| `start_allen.bat` | Comprueba venv/dependencias; verifica IA; inicia backend | Sí, llamado por el BAT anterior | `.venv`, Python, `start_local_ai.py`, launcher Python | Sí durante transición | `ALLEN.exe` | No |
| `start_local_ai.py` | Detecta/inicia llama-server, espera `/health`, hace inferencia real; opción de descarga HF | Sí, invocado por el BAT e instalador | Python, httpx, llama.cpp, modelo | Sí como módulo de desarrollo mientras se valida el build | motor coordinador empaquetado | No |
| `scripts/allen_launcher.py` | Inicia `server.py`, espera `/api/health`, abre navegador | Sí, invocado por los BAT/instalador | Python, FastAPI/uvicorn | Sí como módulo de desarrollo | `ALLEN.exe` + backend empaquetado | No |
| `scripts/allen_stopper.py` | Detiene procesos registrados para el flujo actual | Sí, por `Detener_ALLEN.bat` | Python, archivos PID | Sí durante transición | controlador del launcher/desinstalador | No |
| `Detener_ALLEN.bat` | Acceso visible para detener ALLEN | Sí | Windows CMD, Python | Sí durante transición | cierre desde `ALLEN.exe` | No |
| `install_allen.bat` | Entrada del instalador actual; permite instalar llama.cpp por WinGet | Sí como entrada de instalación | CMD, PowerShell, WinGet | Sí durante transición | `ALLEN_Setup.exe` | No |
| `install_allen.ps1` | Copia el árbol, prepara venv, instala requisitos, detecta motor/modelo y prueba IA/backend | Sí, invocado por BAT | PowerShell, Python >=3.11, pip, Internet/WinGet según caso | Sí durante transición | proyecto Inno Setup + bootstrapper | No |
| `server.py` | Punto de entrada real de Uvicorn/FastAPI | Sí, ejecutado por launcher | Python, uvicorn, backend y recursos | Sí en el repositorio; no en entrega compilada | `allen_backend.exe` | No |
| `requirements.txt` | Requisitos runtime con versiones fijadas | Sí | pip | Sí en desarrollo/build | dependencias congeladas dentro del backend | No |
| `config/local_model.example.json` | Ejemplo del esquema `{executable, model}` | No, solo ejemplo | Ninguna | Sí en repositorio | configuración generada bajo `%ProgramData%` en distribución | No |
| `%LOCALAPPDATA%\ALLEN\local_model.json` | Configuración privada actual detectada, claves `executable` y `model` | Sí en este equipo | Rutas externas de llama.cpp y GGUF | Solo compatibilidad/migración | `%ProgramData%\ALLEN\local_model.json` | No |
| `logs/launcher.log` | Evidencia de inicio y backend | Sí | Ninguna | Sí en instalación, excluido de build | `%ProgramData%\ALLEN\logs\launcher.log` | No |
| `logs/llama-server.log` | Salida de llama-server | Sí | llama-server | Sí en instalación, excluido de build | `%ProgramData%\ALLEN\logs\llama-server.log` | No |
| `frontend/assets/allen.svg` | Logo oficial vectorial existente (Allen, mono naranja) | Sí como recurso web | Navegador SVG | Sí | ICO multirresolución generado desde este SVG para Windows | No |
| `frontend/`, `backend/`, `data/` | Interfaz, API, contenidos y rutas educativas | Sí | Navegador; Python en backend actual | Sí en desarrollo; recursos necesarios en distribución | recursos minificados y backend compilado | No |
| `*.iss`, `*.exe`, `build/`, `dist/` | No encontrados en el repositorio inspeccionado | No | — | Se crearían para distribución | Inno Setup/build de Windows | No aplica |
| `licensing/`, `license.allen`, manifest firmado | No encontrados | No | No existe aún formato, clave pública ni licencia válida | Deben añadirse antes de distribución | ver sección de brechas | No aplica |

## Arquitectura observada y pruebas existentes

- Backend real: `server.py` ejecuta `uvicorn.run('backend.app:app', host='127.0.0.1', port=8787)`.
- Health del backend: `GET http://127.0.0.1:8787/api/health`.
- Motor real: `llama-server.exe`, configurado en `%LOCALAPPDATA%\ALLEN\local_model.json`.
- GGUF configurado: `Qwen3.5-0.8B-Q8_0.gguf` en caché Hugging Face; tamaño observado anteriormente ~0,78 GiB (834 MB decimal).
- Health IA: `GET http://127.0.0.1:8080/health`.
- Chat que emplea el backend: `POST http://127.0.0.1:8080/v1/chat/completions`.
- La inferencia real de arranque está implementada en `start_local_ai.py`; el log registra una respuesta `OK` y carga observada de 13–21 s en esta máquina.
- El historial de `logs/launcher.log` registra el fallo del 24-09-2026: `UnicodeEncodeError` al imprimir `✓` bajo cp1252, antes de crear el proceso de llama-server. La impresión se cambió a marcas ASCII. El inicio exitoso subsecuente quedó registrado.
- La inspección de esta versión encontró además una indentación inválida en `start_local_ai.py` (línea 140 al inspeccionarse); se corrigió durante esta tarea y se verificará con compilación Python.
- Verificación ejecutada en esta tarea tras corregirla: `py_compile`/`compileall` de launcher/backend pasan; 12 pruebas Python pasan; 5 pruebas JS pasan.
- Se ejecutó `Iniciar_ALLEN.bat` completo: IA ya activa, inferencia mínima `OK`, backend iniciado y navegador abierto en `http://127.0.0.1:8787`.
- Respuestas en vivo: IA `GET /health` devolvió `{"status":"ok"}`; ALLEN `GET /api/health` devolvió `application=true`, `database=true`, biblioteca local con 8 documentos.
- Prueba aislada con `TestClient` contra el `LocalAI` real y el llama-server local: `POST /api/chat` HTTP 200, `demo=false`, `offline=false`; devolvió una explicación de Python generada por Qwen. El backend que estaba abierto antes del reinicio conservaba temporalmente el valor viejo `offline=true`; después de reiniciar el launcher quedó activo el código corregido.
- Esta tarea no desconectó la red ni probó una VM limpia, instalación nueva, activación, copia a otra máquina, integridad firmada ni desinstalación; todas siguen como **NO PROBADO**.

## Decisiones y límites de distribución

1. Conservar los BAT/PS1 existentes hasta que el ejecutable empaquetado y el instalador se compilen y pasen pruebas en una máquina/VM limpia.
2. El modelo no se incluye en el repositorio (`*.gguf` está excluido por `.gitignore`). Para distribución institucional offline, la vía más confiable es un paquete de modelo separado o un bundle offline versionado; descarga durante Setup requiere Internet y no satisface el estado final offline hasta completar y probarla.
3. No existe en el entorno inspeccionado un compilador Nuitka/PyInstaller, Inno Setup, un `.ico`, una clave de firma de licencias, una licencia de cliente ni una VM limpia. Por ello no se puede declarar producido o verificado `ALLEN.exe`, `ALLEN_Setup.exe`, la activación Ed25519 ni el escenario de PC limpia.
4. La clave privada de licencias debe pertenecer al sistema del proveedor y quedar fuera del repositorio, instalador cliente y equipo/artefactos de cliente. No se generó ni incrustó clave privada durante la auditoría.
5. La opción de modelo y los binarios de llama.cpp tienen licencias distintas: el repo GGUF indica Apache-2.0; llama.cpp publica MIT. El bundle debe incluir los textos/notices requeridos y validar dependencias binarias de la build concreta antes de redistribuir.

## Tabla de validación de lanzamiento solicitado

| Componente | Instalado | Verificado | Prueba real |
|---|---:|---:|---:|
| Launcher fuente Python actual | Sí | Sí | Sí, estado previo del historial/log |
| `ALLEN.exe` compilado | No | No | NO PROBADO |
| `ALLEN_Setup.exe` | No | No | NO PROBADO |
| Backend actual | Sí | Sí | Sí, `/api/health` en historial previo |
| llama-server | Sí en este PC | Sí | Sí, versión y servidor real en historial previo |
| Modelo GGUF | Sí en caché de este PC | Sí | Sí, inferencia real en historial previo |
| Installation ID/fingerprint | No implementado | No | NO PROBADO |
| Licencia Ed25519/manifest firmado | No implementado | No | NO PROBADO |
| Modo offline tras instalación | Modelo local existe; red no desconectada | Parcial | NO PROBADO sin red |
| PC limpia / copia a otro equipo / desinstalación Inno | No hay VM/instalador | No | NO PROBADO |

## Fuentes técnicas consultadas

- [Tarjeta oficial del modelo GGUF Qwen3.5-0.8B](https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF): identifica Apache-2.0 y Q8_0 (834 MB), e indica la forma de uso de llama.cpp.
- [Licencia publicada por llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE): MIT para el código del proyecto; verificar notices y licencias de cada dependencia/binario redistribuido.
- [Manual de Nuitka](https://nuitka.net/user-documentation/): fuente primaria para su compilación; compilar no equivale a protección criptográfica del código.
- [Licencia actual de Inno Setup](https://jrsoftware.org/files/is/license.txt): debe revisarse para el contexto de uso y versión exactos antes de seleccionar/redistribuir el builder.

## Continuación del trabajo de build (24-09-2026)

- Herramientas de desarrollo: Nuitka 4.2.2 y Zig 0.16.0 instalados dentro de `.venv` (`requirements-build.txt`); Inno Setup 6.7.3 instalado por WinGet ámbito usuario. `ISCC.exe`: `%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe`.
- Inno Setup 6.7.3 identifica su build gratuito como “Non-commercial use only”; el proveedor pide licencia comercial cuando la organización lo usa para un producto comercial. El uso para producción comercial debe esperar esa licencia o una decisión institucional de que el uso no es comercial. [Condiciones oficiales de Inno Setup](https://jrsoftware.org/isorder.php).
- Inno Setup compiló un script mínimo a EXE en una carpeta temporal. Nuitka compiló un script Python mínimo con `--standalone --zig`; el EXE se ejecutó con working directory `%TEMP%` e imprimió `nuitka-standalone-ok`.
- La distribución de prueba `dist/ALLEN/runtime/llama/` contiene `llama-server.exe` y DLL del paquete WinGet (89,228,061 bytes en total). Se arrancó directamente ese ejecutable en puerto 8081 con Qwen local: `/health` = 200 (`{"status":"ok"}`), inferencia = `OK`; la build no usó el llama-server global de puerto 8080. Tiempo total medido en esa prueba bajo contención de build: 66.40 s; generación del prompt mínima reportada en el log a 1.10 tokens/s, no representativa de un equipo sin compilación simultánea.
- Se añadieron verificador Ed25519, registro/fingerprint, comprobación de licencia/expiración y SHA-256 de manifest en `licensing/runtime.py`; generador de claves/licencias/manifests está en `tools/license_generator/allen_licensing.py`. El fingerprint usa `MachineGuid` y `ComputerHardwareId` leídos del registro; conserva solo su SHA-256. No usa MAC ni datos personales.
- Se generó una clave **de desarrollo sin cifrar**, fuera del repositorio, en `%LOCALAPPDATA%\ALLEN\license-keys\development-private.pem`, con ACL de usuario actual. No es clave de producción. Su clave pública de desarrollo es `licensing/development_public_key.pem`; el código fija el SHA-256 de esa clave como ancla. No se debe usar este par para licencias de clientes.
- Las verificaciones unitarias de licencia (licencia válida, vencida, alterada y archivo crítico modificado) pasan en `tests/test_licensing.py`.
- El backend standalone sin licencia fue probado desde `%TEMP%`: `/api/health`, `/`, `/api/bootstrap`, `/api/library` y `POST /api/chat` pasaron; la conversación real respondió con `demo=false`, `offline=false`. Esa build es solo un smoke test, no es el binario release.
- La segunda build standalone, ahora con auth Ed25519 y recursos adicionales, está en compilación. Aún no se ha generado ni probado el Setup/launcher final; VM limpia, instalación real y UAC siguen pendientes.

### Resultado de la continuación (24-09-2026)

- Las cinco pruebas de `tests/test_licensing.py` pasan; la compilación Python de los puntos de entrada y módulos nuevos termina correctamente. El parser de PowerShell acepta `packaging/build_allen.ps1`.
- El build de release **no terminó** y no se generó `ALLEN_Setup.exe`. Nuitka/Zig, en esta máquina, compiló los módulos C generados a una velocidad extremadamente baja: tras más de 30 minutos había 277 objetos del backend y cada objeto reciente tardaba aproximadamente 20 minutos. Se interrumpió el proceso para evitar dejar una compilación indefinida. Este comportamiento debe corregirse antes de reintentar el build; los objetos parciales de `build/` no son artefactos distribuibles.
- El proceso interrumpido no dejó alterada la clave pública fijada: `licensing/trust_anchor.py` mantiene el SHA-256 de `licensing/development_public_key.pem`. No se encontró `allen_backend.exe` final ni `ALLEN_Setup.exe` al terminar.
- Por tanto, siguen **NO PROBADOS** la ejecución final sin Python, el launcher empaquetado, la instalación del Setup, activación end-to-end y funcionamiento offline en una instalación limpia. No se retiró ningún BAT/PS1 legado.

## Sesión AFK y evaluación STEAM (24-09-2026)

- El ciclo de inactividad que borraba visitantes estaba en `frontend/fair.js`: a los 120 s abría el diálogo `#idle` y tras 20 s ejecutaba `reset(true)`. `frontend/fair-content.js` codificaba los estados `warn` y `reset`. Se quitó ese reset; tras 35 s de inactividad de una persona se muestra la vista AFK. Empezar vuelve a la experiencia anterior (o al menú si la sesión está recién creada).
- `visitorSession` vive en `localStorage`; antes estaba en `sessionStorage` y `readVisitor()` descartaba datos tras 140 s. Ahora restaura mientras exista el dato válido, incluso después de cerrar y reabrir el navegador; incluye nombre, dificultad, puntos, rango, rutas, evaluaciones/proyectos y recompensas. Los contadores generales siguen en el almacenamiento/API agregado y `reset()` no los toca. “Nueva persona” pide confirmación, elimina el visitante por completo y vuelve al nombre.
- El servidor mantiene sus sesiones de feria en memoria con expiración deslizante de 210 s. Antes el navegador solo enviaba heartbeat con actividad reciente y no en AFK; ahora manda uno cada 60 s mientras exista sesión, también en AFK. Al abrir ALLEN valida el token guardado y obtiene otro si el servidor ya lo expiró; F5/cierre no resetea al visitante.
- Antes `LearningExperiences.handle('project-finish')` guardaba una cadena de evidencia y llamaba inmediatamente a `complete('projects', ..., 200)`, sin IA ni evaluación. Los proyectos finales de ruta marcaban `project=true` con el mismo criterio. Ahora STEAM y las cinco rutas llaman al motor compartido en `frontend/fair-evaluation.js`: guarda `SUBMITTED`, ID de visitante/sesión, fechas, evidencia, contexto, dificultad y ruta; envía proyecto/evidencia/autoevaluación al endpoint real `POST /api/fair/chat`, exige respuesta no demo y JSON validado, y solo entonces cambia a `EVALUATED` y aplica la recompensa existente de 200 puntos con clave idempotente.
- Si la llamada local falla, devuelve demo o el JSON no cumple el contrato, la entrega queda `SUBMITTED`, se muestra reintento y no se asignan puntos. Una entrega evaluada se muestra desde el historial y no vuelve a llamar al modelo al abrirla. La evaluación y los puntos se guardan en `visitorSession` de esta pestaña, no en una base compartida por visitante.
- El problema corregido era la fragilidad del parser de evaluación ante formatos reales del modelo (JSON dentro de texto, comillas escapadas y feedback como lista), además de la falta de diagnóstico visible. El flujo conserva el endpoint existente `POST /api/fair/chat`; verifica respuesta no demo, valida el contenido y no recompensa respuestas malformadas o afirmaciones fuera de la evidencia. El servicio local de inferencia es `POST http://127.0.0.1:8080/v1/chat/completions`; health respondió `GET /health` HTTP 200.
- Se añadió un parser tolerante que reconoce JSON cercado/rodeado de texto, listas escapadas y campos etiquetados; estados/criterios se normalizan y los criterios ausentes quedan en cero. Si el contenido no puede validarse, la entrega conserva `SUBMITTED`, muestra opción de reintento y no suma puntos. La evaluación aceptada cambia a `EVALUATED` y el guard de estado más la clave idempotente impiden acreditar los 200 puntos por duplicado. El cliente muestra estado de carga y el backend/modelo local admiten hasta 120 s; errores y fragmentos limitados de respuesta se registran, con datos personales redactados, en `%LOCALAPPDATA%\ALLEN\logs\steam-evaluation.log`.
- Prueba end-to-end exitosa con el modelo local Qwen3.5-0.8B real: el navegador evaluador llamó al endpoint existente, el contenido de un proyecto STEAM fue interpretado, pasó validación, obtuvo `EVALUATED` con 200 puntos y generó feedback sobre fortalezas, mejora y siguiente paso. En pruebas exploratorias previas el modelo también generó una respuesta malformada o ajena al proyecto; esos casos quedan correctamente rechazados y reintentables.
- Verificación de esta corrección: 22 pruebas Node de feria/sesión/rutas/evaluación pasan; 18 pruebas Python (`tests.test_fair`, `tests.test_licensing`) pasan; `py_compile` y `node --check` de los módulos modificados pasan. `git diff --check` no reportó errores de whitespace en archivos de evaluación/backend (sí señaló una línea vacía final preexistente en `frontend/fair-experience.css`).
- Nota operativa: el backend que ya estaba escuchando en `127.0.0.1:8787` seguía siendo un proceso anterior (el health responde, pero `/api/fair/evaluation-log` devuelve 404). El cierre controlado de ese PID fue rechazado por el entorno de ejecución y no se forzó la terminación. Por ello, el endpoint de diagnóstico y timeout de 120 s quedan implementados y cubiertos en pruebas, pero requieren reiniciar ALLEN para estar activos en el proceso servido.
- Diagnóstico de seguimiento: `Habla con Allen` respondió “Hola” con HTTP 200 y `offline=false`; llama-server devolvió health/modelos HTTP 200. En la evaluación STEAM contra el proceso anterior el modelo siguió generando y la llamada se canceló; el backend anterior ocultó la excepción y devolvió HTTP 200 con “La IA local no está disponible…”, que la UI antigua clasificaba después como estado inválido. El log de llama registró la cancelación durante generación; esto corresponde al límite de tiempo del proceso viejo (el nuevo límite configurado es 120 s), no a falta de conectividad general. Una llamada directa de control a `/v1/chat/completions` devolvió HTTP 200 con JSON cercado, pero fue truncada al límite artificial de 240 tokens; su forma incluye feedback vacío como listas, ahora normalizado con valores seguros.
- Se compactó el prompt, se añadieron fallback `clave=valor` y métricas de tamaño/campos vacíos, y se diferenciaron timeout, IA no disponible, conexión y parsing en la entrega. El endpoint actualizado `/api/fair/chat` devuelve HTTP 503 para motor desconectado y HTTP 504 para timeout. Pruebas unitarias actuales: 24 Node (incluye JSON, bloque, texto, clave-valor, listas vacías, reintento/puntos) y 18 Python pasan. El proceso atendiendo el puerto todavía no carga esos cambios hasta reiniciar; el endpoint de diagnóstico en ese proceso devuelve 404.
- No se simuló una espera física de 35 s, interacción AFK en navegador real, recarga/cierre del navegador en Playwright ni la experiencia de visitante A/B manualmente. Su lógica se cubre con pruebas unitarias de decisión y persistencia. Por ello las pruebas manuales S1–S10/P1–P10 no deben describirse como completadas.

## Evaluación STEAM local por rúbrica (25-09-2026)

- La evaluación y los puntos ya no dependen de la IA. `evaluateLocalRubric()` puntúa seis criterios de 0 a 3: cumplimiento del objetivo (presencia y coincidencia de términos con el objetivo), comprensión (combinación de explicación y reflexión), pasos completados (proporción de casillas), explicación (detalle de la descripción), aplicación (descripción/materiales/pasos) y reflexión (extensión y señales de aprendizaje). Es una rúbrica determinística y reproducible, basada solo en campos de entrega; no afirma haber visto el prototipo.
- El total es sobre 18 y se convierte a porcentaje. Etiquetas: 85–100 Muy bien logrado, 65–84 Logrado, 40–64 En desarrollo, 0–39 Necesita reforzarse. El banco local elige mensajes de fortaleza y mejora según criterios con puntaje >=2 o <2, y formula el siguiente paso a partir del criterio más bajo.
- El registro persiste en `visitorSession`/localStorage con project_id, evidence/answers, `rubric_scores`, total, etiqueta, feedback local y opcional, puntos, estado, fecha de evaluación e historial de estados. SUBMITTED es transitorio; la función calcula inmediatamente `LOCAL_EVALUATED`, cambia a `COMPLETED`, persiste y asigna 200 puntos idempotentes antes de iniciar una petición IA no bloqueante.
- La IA solo redacta un comentario complementario breve. Timeout, error o IA apagada dejan `COMPLETED` intacto; la persona puede reintentar solo el feedback desde la vista evaluada, sin recalcular puntuación ni otorgar puntos otra vez. El formulario permite entregar avances parciales para que la rúbrica refleje lo que falta.
- Verificación de implementación: 23 pruebas Node de feria, aprendizaje y evaluación pasan. Cubren IA encendida, apagada y timeout; reabrir el mismo resultado; reintentar feedback sin alterar puntuación; entrega incompleta; presentación de formulario parcial y proyecto final de ruta. `node --check` también pasa. No se ejecutó una solicitud real al modelo en esta actualización: el resultado local no depende de ella y el feedback real es opcional.
