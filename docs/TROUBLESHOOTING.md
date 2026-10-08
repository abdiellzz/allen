# Solución de problemas

## ALLEN pide licencia

Es normal en 1.2.0.

Copia el Machine ID y genera una licencia desde ALLEN License Manager.

## “Esta licencia pertenece a otro equipo”

El Machine ID firmado no coincide. Genera otra licencia para el Machine ID mostrado por ese ALLEN.

## “La licencia fue modificada”

El payload o la firma no coinciden. No edites `.license` manualmente. Vuelve a generarla.

## Licencia expirada

Genera una renovación. No reinstales ALLEN: reinstalar no extiende el periodo.

## Fecha del sistema retrocedió

Corrige fecha, hora y zona horaria de Windows. ALLEN bloquea el uso si detecta una fecha anterior a la última observada.

## License Manager no encuentra clave privada

El ejecutable necesita `license_private_key.pem` junto al EXE, o la variable:

`ALLEN_LICENSE_PRIVATE_KEY`

Nunca copies la clave al repositorio.

## License Manager en Linux

Puedes ejecutarlo con Python:

```bash
python -m venv .venv
source .venv/bin/activate
pip install cryptography
sudo pacman -S tk   # Arch/Garuda, si falta Tk
export ALLEN_LICENSE_PRIVATE_KEY="/ruta/license_private_key.pem"
python tools/license_manager.py
```

El `.exe` es Windows; en Linux usa Python nativo o Wine.

## Puerto 8787 ocupado

Cierra otro ALLEN o proceso que use el puerto.

## IA local desconectada

Comprueba:

- `llama-server` está ejecutándose;
- usa loopback;
- puerto correcto;
- modelo cargado;
- URL típica: `http://127.0.0.1:8080`.

## Un PDF no importa

Teacher Studio admite PDF con texto extraíble. PDF escaneado sin capa de texto requiere OCR y no está soportado actualmente.

## Base con problemas

Ve a Configuración → Protección de datos:

1. diagnosticar;
2. revisar integridad;
3. restaurar snapshot si es necesario.

## Windows SmartScreen

Un ejecutable sin firma de código comercial puede mostrar advertencia. Verifica que el archivo provenga del workflow/release oficial. La firma de licencias Ed25519 no sustituye una firma Authenticode del ejecutable.

## Portable no abre

Extrae el ZIP completo. No ejecutes solo `ALLEN.exe` separado de `_internal`.
