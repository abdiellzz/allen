# Arquitectura de ALLEN

## Vista general

```text
Navegador local
    |
    | HTTP 127.0.0.1:8787
    v
FastAPI
    |
    +-- SQLite
    +-- biblioteca local
    +-- cursos / Teacher Studio
    +-- Learning Intelligence
    +-- licensing
    |
    +----> llama.cpp opcional
           127.0.0.1:8080
```

ALLEN no necesita un backend cloud para su funcionamiento principal.

## Backend

Entrada principal:

`backend/app.py`

Responsabilidades destacadas:

- `database.py`: acceso a SQLite;
- `migrations.py`: evolución del esquema;
- `recovery.py` / `backup.py`: protección de datos;
- `licensing.py`: validación offline Ed25519;
- `course_builder.py`: construcción de cursos;
- `course_quality.py`: checks de publicación;
- `course_versioning.py`: versiones y diff;
- `learning_intelligence.py`: diagnóstico/mastery;
- `question_bank.py`: banco de preguntas;
- `ai.py`: conexión opcional al modelo local.

## Frontend

Entrada:

`frontend/index.html`
`frontend/app.js`

Componentes modulares en `frontend/components/`.

No existe un build de Node para ejecutar la app. Los módulos ES se sirven directamente por FastAPI.

## Datos

La base principal es SQLite.

El esquema se migra automáticamente y utiliza snapshots antes de operaciones sensibles.

Los datos de ejecución viven fuera del repositorio.

## Licenciamiento

```text
License Manager + clave privada
          |
          | firma Ed25519
          v
      archivo .license
          |
          v
ALLEN + clave pública
          |
          +-- firma válida?
          +-- Machine ID coincide?
          +-- fechas válidas?
          +-- rollback básico?
```

La clave privada nunca pertenece al producto distribuido.

## Aplicación vs landing pública

Son dos superficies distintas:

### Aplicación
`backend/` + `frontend/`

Corre localmente en `127.0.0.1`.

### Landing
`public/` + `vercel.json`

Es contenido estático para Vercel. No expone SQLite, FastAPI ni la IA local.

## Distribución

`distribution/allen.spec` empaqueta:

- frontend;
- biblioteca incluida;
- configuración pública;
- VERSION;
- runtime Python.

El paquete resultante no necesita Python instalado en el PC del cliente.
