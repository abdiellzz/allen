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


## Tutorial operativo: emitir una licencia

### 1. Obtener Machine ID

El cliente abre ALLEN sin licencia y copia el identificador mostrado.

Ejemplo:

`ABCD-1234-EF56-7890-ABCD-1234`

### 2. Abrir License Manager

Windows:

`ALLEN-License-Manager.exe`

Linux:

```bash
export ALLEN_LICENSE_PRIVATE_KEY="/ruta/privada/license_private_key.pem"
python tools/license_manager.py
```

### 3. Completar datos

- Cliente.
- Machine ID.
- Plan.
- Duración en días.

El `license_id` se genera automáticamente.

### 4. Entregar

Envía únicamente el archivo:

`ALLEN-XXXXXXXXXXXX-R1.license`

No envíes:

- clave privada;
- License Manager con una copia accidental de la clave dentro;
- registros administrativos internos.

## Tutorial operativo: renovar

1. abre License Manager;
2. pulsa **Cargar para renovar**;
3. selecciona la licencia previa;
4. indica los días nuevos;
5. genera el archivo;
6. envíalo al cliente;
7. cliente abre **Configuración → Licencia y suscripción**;
8. importa renovación.

Si la licencia aún está activa, los días se agregan al vencimiento actual. Si expiró, la nueva vigencia comienza al emitir la renovación.

## Uso desde Linux

El generador está escrito en Python y puede usarse desde Linux.

El EXE generado por CI es para Windows; en Linux es preferible ejecutar `tools/license_manager.py` nativamente.

La licencia resultante puede activar un ALLEN en Windows porque la firma Ed25519 no depende del sistema operativo donde se generó.

## Límites del modelo offline

Un esquema 100% offline no puede consultar un servidor central para saber si un archivo se usó en otro lugar.

ALLEN resuelve esto vinculando la licencia al Machine ID.

La protección de reloj y estado local es disuasoria. Un atacante con control total del equipo y capacidad de parchear binarios siempre puede intentar evadir DRM local; el objetivo del sistema es control comercial razonable sin convertir el producto en un servicio online.
