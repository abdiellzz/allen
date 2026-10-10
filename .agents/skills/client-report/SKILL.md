---
name: client-report
description: Genera un informe PDF profesional para el cliente de ALLEN (con reportlab) a partir de una lista de hallazgos de auditoría o de correcciones aplicadas. Úsala cuando pidan un "informe", "reporte para el cliente", "PDF de auditoría" o "informe de correcciones". Produce portada con versión y fecha, resumen ejecutivo y tarjetas por severidad, sin referencias internas.
---

# client-report

Convierte hallazgos o correcciones en un PDF listo para enviar al cliente.

## Requisitos

```powershell
python -m pip install reportlab
```

## Flujo

1. Reúne los hallazgos (auditoría) o las correcciones (informe de correcciones) y redáctalos para el
   cliente: lenguaje claro, en español, centrado en riesgo y efecto para la institución y los
   estudiantes.
2. Escribe un JSON (fuera del repo o en el scratchpad) con este formato:

   ```json
   {
     "kind": "audit",
     "title": "Auditoría técnica",
     "product": "ALLEN",
     "version": "1.2.4",
     "date": "2026-10-10",
     "client": "Nombre del cliente (opcional)",
     "author": "Sebastian (opcional)",
     "summary": "Párrafo(s) del resumen ejecutivo. Separa párrafos con una línea en blanco.",
     "items": [
       {
         "severity": "Crítica",
         "title": "Las respuestas del examen se pueden consultar antes de responder",
         "problem": "Qué ocurre.",
         "impact": "Qué riesgo tiene para el cliente.",
         "recommendation": "Qué se recomienda hacer."
       }
     ]
   }
   ```

   - `kind`: `"audit"` → tarjetas **Problema / Impacto / Recomendación**;
     `"fixes"` → tarjetas **Hallazgo / Solución** (campos `finding` y `solution`, y opcionalmente
     `status`, por ejemplo "Corregido y verificado").
   - `severity`: `Crítica`, `Alta`, `Media` o `Baja`.
3. Genera el PDF:

   ```powershell
   python .agents/skills/client-report/make_report.py hallazgos.json -o "ALLEN-informe-1.2.4.pdf"
   ```

4. Abre el PDF y revísalo antes de entregarlo.

## Estructura del PDF

- **Portada:** producto, título, versión, fecha, cliente y autor.
- **Resumen ejecutivo:** texto de `summary` y tabla con el número de elementos por severidad.
- **Tarjetas** agrupadas y ordenadas por severidad (Crítica → Alta → Media → Baja), cada una con su
  color, número correlativo (C-01, A-01…) y los campos del tipo de informe.
- Pie con nombre del informe y número de página.

## Sin referencias internas

El informe es para el cliente. **No incluir:** rutas o nombres de archivos (`backend/app.py`),
funciones, clases, endpoints, ramas, commits o hashes, nombres de tests, herramientas internas ni
personas del equipo salvo el autor. Describe el comportamiento ("al restaurar una copia de seguridad
se mezclaban conversaciones de distintos estudiantes"), no la implementación.

El script rechaza el JSON (código 2) si detecta patrones típicos de referencias internas (rutas con
extensión de código, hashes de commit, `/api/...`, nombres de rama). Reescribe esos textos; usa
`--allow-internal` solo si el usuario lo pide expresamente.
