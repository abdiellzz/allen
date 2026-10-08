# Desarrollo de ALLEN

## Requisitos

- Python 3.13 recomendado;
- Node.js 22 para pruebas frontend;
- Git;
- Windows si vas a construir instalador/Portable localmente.

## Preparación

```bash
git clone https://github.com/abdiellzz/allen.git
cd allen
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Ejecutar

```bash
python server.py --open
```

Servidor:

`http://127.0.0.1:8787`

Modo Feria:

`http://127.0.0.1:8787/fair`

## Pruebas

Python/E2E:

```bash
python -m pytest -q
```

Frontend:

```bash
node --test tests/*.mjs
```

Antes de fusionar cambios, ambas suites deben estar verdes.

## Build Windows

En Windows con Inno Setup instalado:

```powershell
.\distribution\build_windows.ps1
```

Genera:

- `ALLEN-<version>-Portable-Windows-x64.zip`;
- `ALLEN-<version>-Setup-Windows-x64.exe`.

## Versionado

La versión se define en:

- `VERSION`;
- `backend/version.py`;
- pruebas de release.

Usa SemVer:

- MAJOR: incompatibilidad;
- MINOR: función compatible;
- PATCH: corrección.

Actualiza también `CHANGELOG.md`.

## Reglas del repositorio

No commits de:

- `.venv`;
- `*.sqlite3`;
- `*.gguf`;
- `.env`;
- `*.license`;
- `license_private_key.pem`;
- datos reales de estudiantes.

## Organización

- `backend/`: API, SQLite, lógica educativa y licencia;
- `frontend/`: aplicación web local;
- `data/library/`: contenido incluido;
- `distribution/`: empaquetado Windows;
- `tools/`: utilidades administrativas;
- `public/`: landing estática de Vercel, separada de la app;
- `tests/`: pruebas Python/E2E/JavaScript;
- `docs/`: documentación oficial.

Consulta [ARCHITECTURE.md](ARCHITECTURE.md) para dependencias y flujos internos.
