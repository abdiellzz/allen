# Instalación e inicio de ALLEN en Windows

## Forma simple

1. Ejecuta `Instalar_ALLEN.bat` y espera a que termine. Instala Python 3.11 o posterior antes si el instalador lo solicita. Si falta llama.cpp y `winget` está disponible, puedes aceptar su instalación desde el paquete `ggml.llamacpp`.
2. Ejecuta `Iniciar_ALLEN.bat` o el acceso directo `ALLEN` del escritorio.
3. ALLEN abre `http://127.0.0.1:8787` cuando el servidor responde. Conserva la ventana abierta. `Detener_ALLEN.bat` solo termina los procesos cuyos PID guardó el launcher.

La primera instalación crea `.venv` e instala las dependencias fijadas de `requirements.txt`; pip necesita acceso a un índice de paquetes o a un índice local. Las siguientes aperturas no reinstalan dependencias.

## Modelo local

La configuración privada se guarda en `%LOCALAPPDATA%\ALLEN\local_model.json`, con rutas `executable` y `model`. La integración actual de ALLEN usa un GGUF local y llama-server; el comando se genera desde las preferencias SQLite para usar el puerto y contexto configurados. El endpoint de estado real es `/health`.

El instalador busca el `llama-server` configurado y el modelo GGUF; para una caché local del repositorio comprueba también el modelo `ggml-org/Qwen3.5-0.8B-GGUF`. No descarga un modelo automáticamente ni supone que esa referencia sea el modelo elegido. Debes obtenerlo desde un origen de confianza y aceptar su licencia, y después configurar sus rutas. Si no hay configuración o archivo, puedes usar la experiencia local en modo demo.

La IA local y el backend usan solo loopback: `127.0.0.1:8080` y `127.0.0.1:8787` en la configuración verificada de este repositorio. El helper consulta `/health` hasta 300 segundos (configurable con `ALLEN_AI_TIMEOUT` o `--timeout`). Si el puerto está ocupado por un servicio que no responde como llama-server/ALLEN, informa el conflicto en vez de iniciar un duplicado.

Los mensajes resumidos aparecen en la terminal. Los errores y eventos técnicos del launcher se guardan en `logs/launcher.log`; no se escriben prompts ni respuestas del usuario.

## Forma desarrollador

Desde PowerShell en la carpeta del repositorio:

```powershell
python -m venv .venv
\.venv\Scripts\python.exe -m pip install -r requirements.txt
\.venv\Scripts\python.exe start_local_ai.py
\.venv\Scripts\python.exe server.py --open
```

El backend se inicia desde `server.py` y escucha en `127.0.0.1:8787`. `start_local_ai.py` lee `%LOCALAPPDATA%\ALLEN\local_model.json` y preferencias SQLite, comprueba `/health` y construye el comando local. La orden observada para este equipo usa `-m <GGUF> --host 127.0.0.1 --port 8080 -c 4096 --parallel 1 --threads 4 --reasoning off --log-disable`; el puerto y contexto se toman de la configuración.

Para validar las rutas de aprendizaje: `node --test tests/test_fair_learning.mjs`. No se requieren privilegios de administrador para instalar la app en `%LOCALAPPDATA%`.

## Qué ocurre sin Internet

Después de instalar Python, dependencias, llama.cpp y el GGUF, el launcher no descarga componentes: consulta los servicios locales e inicia ALLEN. Si falta el GGUF o llama.cpp, las actividades de ALLEN funcionan en modo demo, pero no hay respuestas del modelo local. Para instalar en una máquina nueva se requiere conexión durante la instalación de paquetes y para obtener manualmente llama.cpp/modelo.
