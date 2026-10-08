# ALLEN 1.2.1 — Security hardening

**Fecha:** 7 de octubre de 2026  
**Canal:** estable  
**Tipo:** patch de seguridad

## Cambios principales

- Gate de acceso local por secreto efímero por ejecución.
- Cookie de sesión HttpOnly y SameSite=Strict.
- Renovaciones de licencia verifican firma Ed25519 previa.
- pypdf 6.19.0.
- cryptography 50.0.2.
- pip-audit en CI.
- Dependabot para Python y GitHub Actions.
- GitHub Actions fijadas por SHA y permisos mínimos.
- Permisos 0600 para la clave privada en POSIX.
- Cabeceras defensivas adicionales.

## Compatibilidad

No cambia el formato de la base SQLite ni el formato actual de licencia.

Las licencias 1.2.0 válidas continúan siendo verificables por 1.2.1.

## Auditoría

Consulta [../SECURITY_AUDIT_2026-10-07.md](../SECURITY_AUDIT_2026-10-07.md).
