# Instalación y primera ejecución

ALLEN 1.2.1 está orientado primero a Windows 10/11 x64.

## Opción recomendada: instalador

Descarga el artefacto `allen-installer` generado por GitHub Actions y ejecuta:

`ALLEN-1.2.1-Setup-Windows-x64.exe`

No necesitas instalar Python.

El instalador:

- instala ALLEN por usuario;
- usa `%LOCALAPPDATA%\Programs\ALLEN`;
- crea acceso en Inicio;
- puede crear acceso directo;
- guarda datos en `%LOCALAPPDATA%\ALLEN`.

## Opción Portable

Descarga `allen-portable`, extrae todo el ZIP y ejecuta `ALLEN.exe`.

No muevas solo el EXE. La carpeta `_internal` forma parte del programa.

En Portable los datos quedan en:

`ALLEN-Data`

junto a la aplicación.

## Primera apertura

ALLEN mostrará una pantalla de activación con un Machine ID.

1. Copia el Machine ID.
2. Envíalo al administrador de licencias.
3. Recibe un archivo `.license`.
4. En ALLEN pulsa **Seleccionar archivo .license**.
5. Si firma, equipo y fechas son válidos, ALLEN se desbloquea.

No se necesita Internet para validar la licencia.

## IA local

ALLEN funciona sin modelo generativo para sus funciones deterministas. Para respuestas abiertas puedes conectar `llama.cpp` en loopback.

Configuración típica:

`http://127.0.0.1:8080`

El modelo GGUF y `llama.cpp` no vienen incluidos.

## Datos

Instalación normal:

`%LOCALAPPDATA%\ALLEN\allen.sqlite3`

Portable:

`ALLEN-Data\allen.sqlite3`

No guardes una base real dentro del repositorio.

## Desinstalación normal

Usa el desinstalador de Windows. Conserva los datos del usuario.

## Eliminación completa

Los paquetes incluyen **Eliminar ALLEN completamente.bat**.

Exige escribir `BORRAR` y elimina aplicación, datos locales, snapshots, backups internos y accesos directos. No elimina modelos GGUF ni instalaciones externas de llama.cpp.

## Ejecutar desde código fuente

Esto es para desarrollo, no para clientes.

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe server.py --open
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
python server.py --open
```

La ejecución desde código también exige licencia cuando usa la app comercial normal.
