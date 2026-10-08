# Contribuir a ALLEN

## Antes de cambiar código

1. crea una rama desde `main`;
2. evita trabajar directamente sobre `main`;
3. lee [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md);
4. no uses datos reales ni secretos como fixtures.

## Convención de ramas

Ejemplos:

- `feature/nombre`
- `fix/nombre`
- `chore/nombre`
- `docs/nombre`

## Antes del PR

Ejecuta:

```bash
python -m pytest -q
node --test tests/*.mjs
```

Verifica:

- versión si corresponde;
- CHANGELOG;
- documentación;
- migraciones si cambió SQLite;
- no hay secretos;
- no hay `.license` reales;
- no hay modelos o bases.

## Cambios de base de datos

No edites silenciosamente una base existente.

Añade una migración numerada en `backend/migrations.py` y pruebas de compatibilidad.

## Cambios de licencia

Nunca introduzcas la clave privada en código, tests, workflows o fixtures.

Las pruebas criptográficas deben generar claves temporales durante el test.

## Pull request

Explica:

- qué problema resuelve;
- qué archivos principales cambia;
- riesgos;
- cómo se probó;
- si cambia datos, licencias, distribución o interfaz.

No mezcles una refactorización masiva con una nueva función si se pueden revisar por separado.
