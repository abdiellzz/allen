# Proceso de release

## 1. Preparación

Confirma que `main` está verde.

Ejecuta localmente:

```bash
python -m pytest -q
node --test tests/*.mjs
```

## 2. Versión

Actualiza de forma coherente:

- `VERSION`;
- `backend/version.py`;
- `tests/test_release_version.py`;
- `CHANGELOG.md`;
- documento de release si es una release significativa.

## 3. Documentación

Revisa:

- README;
- docs/INDEX.md;
- instalación;
- licensing;
- distribución;
- troubleshooting.

No publiques instrucciones de una versión anterior como si fueran actuales.

## 4. Seguridad

Comprueba que no existan:

- `license_private_key.pem`;
- `*.license`;
- SQLite reales;
- GGUF;
- tokens;
- backups;
- documentos privados.

## 5. PR

Usa una rama de release o feature. No mezcles hasta que CI esté verde.

## 6. Workflows

La release de Windows debe pasar:

- `tests`;
- `windows-distribution`;
- `license-manager-windows` cuando cambie licensing/tools.

## 7. Artefactos

Windows Distribution produce:

- `allen-installer`;
- `allen-portable`.

License Manager produce:

- `allen-license-manager`.

Comprueba que los artefactos correspondan al commit final de `main`, no solo al commit del PR.

## 8. Smoke test

En una VM Windows limpia:

1. instala ALLEN;
2. abre;
3. copia Machine ID;
4. genera licencia;
5. activa;
6. crea perfil;
7. prueba quiz;
8. prueba Teacher Studio;
9. exporta backup;
10. renueva licencia;
11. desinstala;
12. prueba eliminador completo en una VM desechable.

## 9. Publicación

Distribuye el instalador/Portable oficial.

No distribuyas:

- repositorio completo a clientes que solo necesitan la app;
- clave privada;
- License Manager a clientes;
- datos internos.
