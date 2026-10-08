# ALLEN 1.2.0

**Fecha:** 7 de octubre de 2026  
**Canal:** estable

## Tema de la release

Licenciamiento comercial offline.

## Incluye

- archivos `.license` firmados con Ed25519;
- Machine ID por instalación;
- pantalla de activación;
- expiración y renovación;
- panel **Licencia y suscripción**;
- License Manager privado;
- perfiles ilimitados por instalación;
- build del License Manager para Windows;
- instalador y Portable de ALLEN.

## Seguridad

La aplicación contiene únicamente la clave pública.

La clave privada:

- no está en GitHub;
- no está en el instalador;
- no está en el Portable;
- no está embebida en el License Manager EXE.

## Validación

La release se valida con:

```bash
python -m pytest -q
node --test tests/*.mjs
```

y workflows separados para:

- tests;
- Windows distribution;
- License Manager Windows.

## Commit de integración original

`4b0fc618fd2c1bad08f782e3efdb0c540272de68`

Consulta [LICENSING.md](../LICENSING.md) y [WINDOWS_DISTRIBUTION.md](../WINDOWS_DISTRIBUTION.md).
