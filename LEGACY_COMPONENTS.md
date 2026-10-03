# Componentes antiguos conservados durante el empaquetado

Estado a 2026-09-24. No retirar estos archivos hasta que `ALLEN.exe`, `allen_backend.exe`, `ALLEN_Setup.exe`, la IA/modelo y el flujo de licencia pasen las pruebas indicadas en `DOCUMENTACION_DISTRIBUCION_AUDITORIA.md`.

| Componente | Uso actual | Destino una vez validado |
|---|---|---|
| `Iniciar_ALLEN.bat` | Entrada de inicio para usuarios actuales | Reemplazar por acceso directo a `ALLEN.exe`; conservar en rama de desarrollo si es útil |
| `start_allen.bat` | Comprueba dependencias, IA e inicia el launcher Python | Solo desarrollo hasta migración completa |
| `start_local_ai.py` | Arranca/verifica llama.cpp, `/health` e inferencia | Módulo interno de desarrollo/build; excluir fuentes del paquete |
| `scripts/allen_launcher.py` | Arranca backend Python y abre navegador | Sustituir en distribución por launcher compilado |
| `scripts/allen_stopper.py` | Detiene procesos con PID registrado | Integrar cierre en launcher compilado |
| `Detener_ALLEN.bat` | Atajo actual para detener ALLEN | Acceso desde ALLEN o desinstalador |
| `install_allen.bat` y `install_allen.ps1` | Instalación actual con Python/PowerShell | Sustituir por `ALLEN_Setup.exe` solo tras prueba de instalación real |
| `Instalar_ALLEN.bat` | Copia/alias creado por el instalador PowerShell en la carpeta instalada | Retirar junto con la ruta de instalación antigua validada |
| `server.py` | Punto de entrada Uvicorn confirmado del backend real | Mantener en repositorio; no distribuir como fuente |
| `%LOCALAPPDATA%\ALLEN\local_model.json` | Configuración de llama-server/modelo del flujo vigente | Migrar al área de datos estable y a `%PROGRAMDATA%\ALLEN` |

## Reglas de transición

- `ALLEN.exe` debe probar los binarios ubicados en `dist/ALLEN`, con working directory fuera del repositorio.
- `ALLEN_Setup.exe` debe compilarse desde `installer/ALLEN.iss`, instalarse en un destino temporal y probarse allí.
- Los BAT/PS1 anteriores solo se retiran tras superar inicio, health, inferencia, backend, licencia y persistencia offline en una instalación nueva.
- Las claves privadas del emisor quedan fuera del repositorio y de todos los paquetes. El bundle solo puede llevar clave pública.
