# Herramientas administrativas

Este directorio no forma parte de la experiencia normal del estudiante.

## ALLEN License Manager

`license_manager.py` crea y renueva licencias offline firmadas.

### Regla principal

**Nunca coloques `license_private_key.pem` en Git.**

El generador necesita esa clave para firmar, pero el archivo debe vivir únicamente en tu almacenamiento privado.

### Windows

El workflow `.github/workflows/license-manager-windows.yml` crea:

`ALLEN-License-Manager.exe`

Coloca junto al ejecutable:

`license_private_key.pem`

y abre el EXE.

### Linux

Puedes ejecutarlo nativamente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install cryptography
# Instala Tk si tu distro no lo trae.
export ALLEN_LICENSE_PRIVATE_KEY="/ruta/privada/license_private_key.pem"
python tools/license_manager.py
```

En Arch/Garuda, Tk normalmente se instala con:

```bash
sudo pacman -S tk
```

### Crear licencia

1. Cliente instala ALLEN.
2. Copia su Machine ID.
3. Abre License Manager.
4. Introduce cliente, Machine ID, plan y días.
5. Genera el archivo `.license`.
6. Entrega únicamente ese archivo.

### Renovar

1. Pulsa **Cargar para renovar**.
2. Abre la licencia vigente.
3. Define los días adicionales.
4. Genera la renovación.
5. El `license_id` y Machine ID se conservan.

Consulta [docs/LICENSING.md](../docs/LICENSING.md) para arquitectura, límites y seguridad.
