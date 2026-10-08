# ALLEN 1.2.4 — Exploit resistance

**Fecha:** 8 de octubre de 2026  
**Canal:** estable  
**Tipo:** patch de seguridad y robustez

## Objetivo

Endurecer ALLEN 1.2.3 frente a fallos locales, abuso de privilegios, entradas maliciosas y regresiones de seguridad.

## Cambios

- Identidad efímera por proceso para verificar que el servicio en 127.0.0.1:8787 es realmente la instancia actual de ALLEN.
- El launcher ya no confía en cualquier HTTP 200 del puerto 8787.
- /api/health expone únicamente `ok` + `instance`.
- PIN docente obligatorio en el primer uso comercial.
- Eliminación de perfiles protegida por sesión docente.
- Cambios sensibles de IA/privacidad/retención protegidos por sesión docente.
- Límites estructurales para Course Packs y cursos editados.
- PDF cifrado rechazado y texto por página acotado.
- Bandit añadido al gate de CI.
- Escaneo de secretos/material de clave privada mediante pruebas de higiene.
- SQL dinámico evitable sustituido por sentencias fijas.
- Backup mantiene SQL dinámico únicamente para identifiers cerrados por allowlist y schema real.

## Gate de release

La release no debe fusionarse si falla cualquiera de:

- pip-audit;
- compileall;
- Ruff;
- Bandit;
- pytest + E2E;
- frontend tests;
- build Windows + smoke test del ejecutable.

## Riesgos residuales

- DRM puramente offline puede parchearse con control administrativo y reverse engineering.
- Un atacante que controle completamente la sesión del sistema operativo puede leer datos locales.
- PDF sigue siendo un formato complejo: los límites reducen superficie, no prueban ausencia de futuros fallos del parser.
- Authenticode sigue siendo recomendado para distribución comercial amplia.
