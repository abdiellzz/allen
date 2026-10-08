# Distribución de ALLEN para Windows

ALLEN 1.2.0 produce dos artefactos para Windows x64 a partir del mismo build congelado.

## 1. Portable

Archivo esperado:

\`ALLEN-1.2.0-Portable-Windows-x64.zip\`

Características:

- no requiere Python instalado;
- no instala nada en Windows;
- se puede extraer en una carpeta o memoria USB;
- ejecuta \`ALLEN.exe\`;
- crea \`ALLEN-Data\` junto a la aplicación;
- perfiles, progreso, SQLite, backups y configuración permanecen dentro de esa carpeta;
- mover la carpeta completa conserva los datos;
- no incluye modelos GGUF ni llama.cpp.

El archivo \`portable.flag\` activa este comportamiento. No debe eliminarse del paquete portable.

## 2. Instalador

Archivo esperado:

\`ALLEN-1.2.0-Setup-Windows-x64.exe\`

Características:

- no requiere Python instalado;
- instalación por usuario, sin permisos de administrador;
- instala en \`%LOCALAPPDATA%\Programs\ALLEN\`;
- crea acceso en el menú Inicio;
- el acceso directo del escritorio es opcional;
- los datos de usuario siguen en \`%LOCALAPPDATA%\ALLEN\`;
- el desinstalador elimina la aplicación pero conserva perfiles, progreso y backups.

## Launcher

\`ALLEN.exe\` abre un launcher pequeño de Windows con:

- estado de inicio;
- botón **Abrir ALLEN**;
- botón **Cerrar ALLEN**.

El servidor sigue escuchando solo en \`127.0.0.1:8787\`.

## Construcción

La construcción se realiza en Windows:

\`\`\`powershell
.\distribution\build_windows.ps1
\`\`\`

El script:

1. lee \`VERSION\`;
2. instala dependencias de ejecución y build;
3. crea un bundle \`onedir\` con PyInstaller;
4. ejecuta \`ALLEN.exe --self-test\`;
5. crea el ZIP portable;
6. compila el instalador con Inno Setup.

## GitHub Actions

\`.github/workflows/windows-distribution.yml\` construye ambos artefactos en:

- pull requests que cambian archivos relacionados con la distribución;
- pushes a \`main\` con esos cambios;
- ejecución manual mediante \`workflow_dispatch\`.

Los artefactos se guardan durante 30 días en GitHub Actions.

## Seguridad y datos

El portable usa \`ALLEN_DATA_ROOT\` internamente para apuntar a \`ALLEN-Data\`.

La instalación normal no define esa variable y conserva el comportamiento estable:

\`%LOCALAPPDATA%\ALLEN\`

Los modelos GGUF, bases SQLite, logs y datos personales continúan fuera del repositorio.


## Eliminación completa

Ambos paquetes incluyen:

- `Eliminar ALLEN completamente.bat`
- `remove_allen.ps1`

El flujo copia el script PowerShell a `%TEMP%`, por lo que puede eliminar la propia carpeta desde la que se ejecutó. Antes de borrar nada exige escribir exactamente `BORRAR`.

Elimina:

- `%LOCALAPPDATA%\ALLEN`;
- `%LOCALAPPDATA%\Programs\ALLEN`;
- instalaciones heredadas en `%LOCALAPPDATA%\ALLEN\app`;
- `ALLEN-Data` del Portable;
- accesos directos de ALLEN;
- temporales cuyo nombre pertenece a ALLEN.

Cuando existe `unins000.exe`, se ejecuta primero de forma silenciosa para retirar correctamente la entrada de desinstalación de Windows.

No elimina automáticamente modelos `.gguf` ni llama.cpp externos.
