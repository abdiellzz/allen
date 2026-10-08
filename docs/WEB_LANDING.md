# Landing pública

La landing de ALLEN es independiente de la aplicación local.

## Archivos

`public/`

Vercel usa:

`vercel.json`

y publica únicamente el contenido estático configurado.

## Qué sí puede estar en public/

- textos comerciales;
- CSS/JavaScript estático;
- imágenes de marca;
- enlaces de contacto.

## Qué nunca debe estar en public/

- SQLite;
- FastAPI;
- claves;
- licencias;
- Machine IDs de clientes;
- backups;
- documentos educativos privados;
- modelos;
- datos de estudiantes.

## Relación con ALLEN Education

La landing puede explicar el producto, pero no ejecuta el tutor local.

El producto real corre en el dispositivo del usuario.

## Antes de desplegar

Revisa:

- enlaces;
- datos de contacto;
- CSP y cabeceras;
- que no existan secretos en `public/`;
- que `.vercelignore` siga excluyendo la aplicación local y herramientas privadas.
