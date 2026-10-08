# Licencias offline de ALLEN

ALLEN 1.2.0 utiliza licencias firmadas con Ed25519 para mantener el producto offline y permitir renovaciones periódicas.

## Principio de seguridad

Hay dos claves:

- **Clave privada:** solo existe en el entorno privado del propietario de ALLEN y se usa para emitir licencias.
- **Clave pública:** se distribuye dentro de ALLEN y solo sirve para verificar firmas.

Conocer la clave pública no permite crear una licencia válida.

## Flujo de activación

1. Se instala ALLEN.
2. En la primera ejecución aparece la pantalla **Activar ALLEN**.
3. ALLEN muestra un Machine ID derivado de forma irreversible de identificadores locales del equipo.
4. El cliente envía ese código al proveedor.
5. El proveedor abre ALLEN License Manager y genera un archivo `.license`.
6. ALLEN verifica:
   - formato;
   - firma Ed25519;
   - Machine ID;
   - fecha de inicio;
   - fecha de vencimiento;
   - retroceso básico del reloj.
7. Si todo es válido, habilita la aplicación.

No se necesita conexión a Internet para esta verificación.

## Contenido firmado

Una licencia contiene:

- `license_id`;
- cliente;
- plan;
- Machine ID;
- `valid_from`;
- `valid_until`;
- fecha de emisión;
- número de renovación;
- indicador de perfiles ilimitados.

Modificar cualquiera de estos campos invalida la firma.

## Renovación

La renovación conserva:

- `license_id`;
- cliente;
- Machine ID.

Si la licencia sigue vigente, los días nuevos se agregan al vencimiento existente. Si ya expiró, la nueva licencia comienza el día de la renovación.

El cliente solo importa el nuevo archivo desde **Configuración → Licencia y suscripción**.

## Reinstalación

Reinstalar ALLEN no concede un periodo nuevo. La fecha de vencimiento está firmada en el propio archivo de licencia y el Machine ID permanece estable mientras siga siendo la misma instalación de Windows.

## Perfiles

La licencia no limita perfiles. ALLEN 1.2.0 elimina el límite técnico anterior de 20 perfiles por dispositivo.

## Machine ID

En Windows se usa `MachineGuid` como fuente local, pero ALLEN no expone ese valor. Genera un hash SHA-256 con dominio propio y muestra únicamente un identificador derivado como:

`ABCD-1234-EF56-7890-ABCD-1234`

## Retroceso del reloj

ALLEN guarda la última fecha observada. Si Windows informa después una fecha anterior, la licencia se bloquea hasta corregir el reloj.

Esta protección es disuasoria, no un DRM infalible. Un producto completamente offline no puede impedir todos los ataques de manipulación local.

## ALLEN License Manager

El generador privado está en:

`tools/license_manager.py`

El ejecutable se construye mediante:

`.github/workflows/license-manager-windows.yml`

El ejecutable **no contiene la clave privada**. Debe existir un archivo:

`license_private_key.pem`

junto al ejecutable, o definirse mediante `ALLEN_LICENSE_PRIVATE_KEY`.

Nunca se debe subir esa clave al repositorio ni entregarla a clientes.
