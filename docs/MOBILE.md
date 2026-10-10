# ALLEN móvil: primera entrega PWA

Estado: **PWA experimental instalable**, con un curso completo y progreso offline.
No es un APK, no incorpora IA generativa y no tiene cobros activos. La versión de
escritorio continúa funcionando con sus bases y licencias actuales.

## Ejecutar y probar

Desde la raíz del repositorio, sin instalar dependencias nuevas de la app:

```bash
python -m http.server 8081 --bind 127.0.0.1 --directory public
```

Abrir `http://localhost:8081/mobile/`. Crear un perfil con apodo, objetivo, nivel
inicial y tiempo. Esperar **Curso guardado · listo sin conexión** antes de cortar
la conexión. La primera visita necesita descargar el contenido.

En Android se debe servir `public/` en **HTTPS**. Abrir `/mobile/` en Chrome y usar
**Instalar** cuando el navegador lo permita, o su menú de instalación. Una IP LAN
por HTTP no permite probar correctamente el service worker. `localhost` en el
celular es el propio celular, no la computadora.

El `vercel.json` actual puede servir este directorio sin publicar FastAPI, SQLite,
modelos o secretos. No se ha desplegado ni modificado el enlace de producción.

## Arquitectura elegida

| Opción | Reutilización y offline | Decisión |
| --- | --- | --- |
| PWA con lógica educativa local | Reutiliza ES modules, mascota y reglas; IndexedDB y cache del curso funcionan en el navegador | Primera entrega: menor superficie de cambio y pruebas reales sin servidor Python móvil |
| Contenedor Android/WebView | Puede reutilizar la UI, pero necesita resolver almacenamiento, distribución, integración nativa e inferencia | Posterior; envolver la UI no ejecuta FastAPI ni llama.cpp |
| Cliente móvil independiente | Permite integración nativa más profunda, con mayor costo de migración de UI y reglas | Evaluar después de validar aprendizaje y dispositivos objetivo |

La PWA está en `public/mobile/`, separada de `frontend/` y de la landing. No altera
las rutas, controles de acceso ni distribución de escritorio. Su service worker
solo controla `/mobile/` y solo cachea una lista explícita de archivos estáticos.

| Componente | Dónde se ejecuta en esta entrega |
| --- | --- |
| Motor educativo | `engine.mjs`, en el navegador; reglas deterministas |
| Perfiles, sesiones y evidencia | IndexedDB local `allen-mobile-v1`; sin sincronización |
| Curso descargado y UI | Cache Storage mediante `sw.js`; instalación inicial atómica |
| Tutor | Explicaciones, ejemplos y pistas editoriales de `course.mjs`; sin LLM |
| IA local o remota | No conectada; `capabilities.mjs` informa indisponibilidad |
| Derechos comerciales | Solo funciones gratuitas; Premium e Instituciones informativos |
| Teacher Studio, importación PDF y `.allenpack` | Siguen en escritorio; no hay importación de cursos en móvil todavía |
| Backups | Exportación JSON del perfil activo y recuperación como perfil nuevo |

### Reutilización con límites explícitos

La inspección encontró implementaciones reales en `backend/learning_engine.py`,
`learning_intelligence.py`, `recommendations.py`, `course_builder.py`,
`question_bank.py`, `backup.py`, `recovery.py` y `licensing.py`. La interfaz de
Teacher Studio está en `frontend/components/course-studio.js`. Las pruebas
existentes cubren diagnóstico, dominio, cursos, aislamiento y licencias.

El README enumera funciones disponibles de escritorio; no demuestra una
implementación Android. No existía una app móvil independiente en el árbol
inspeccionado. La documentación raíz de release también conserva referencias a
1.2.1 mientras el código estable y sus pruebas indican 1.2.4; este trabajo no
cambia la versión comercial.

`engine.mjs` es una **proyección acotada** de `compute_mastery`,
`recommend_for_state` y la agenda de repaso del motor Python. Las pruebas de paridad
comparan resultados de ambos, incluyendo redondeo. No hay dos fuentes autorizadas
para las reglas: cambios al cálculo de escritorio deben actualizar la proyección
y aprobar `test_mobile_parity.py`. La selección del recorrido escolar y sus
prerrequisitos editoriales son nuevos en esta PWA.

No se copia ni migra SQLite. El progreso móvil y el de escritorio **no se
sincronizan ni comparten perfiles**. Un contrato de cursos revisados y un adaptador
de evidencia serán necesarios antes de interoperar; no se afirma compatibilidad
con `.allenpack` en esta entrega.

## Recorrido educativo implementado

1. Elegir Apoyo escolar o Aprender algo nuevo, nivel y 5/10/15 minutos.
2. Completar seis preguntas de diagnóstico. Añaden evidencia sin omitir la
   comprobación con situaciones nuevas.
3. Estudiar **Partes de un entero**, **Fracciones equivalentes** y **Sumar partes
   del mismo tamaño**. Los prerrequisitos desbloquean los temas en orden.
4. Leer una explicación con apoyo cuando el nivel o la evidencia lo requiere,
   ver un ejemplo y una representación de partes iguales.
5. Resolver dos prácticas y una comprobación contextual por tema.
6. Pedir pistas progresivas, otro ejemplo o una explicación sencilla. Las ayudas
   quedan registradas; una pregunta ya respondida no vuelve a sumar evidencia
   dentro de la misma sesión.
7. Superar al menos dos respuestas y la comprobación final para completar el tema.
   Un error final mantiene el objetivo pendiente.
8. Recibir una recomendación con razón y fecha de repaso; continuar una sesión
   incompleta antes de comenzar otra.
9. Repasar temas y tarjetas sin conexión, exportar, recuperar o eliminar perfiles.

El tiempo influye en la recomendación y permite pausas con posición guardada;
no hay temporizador obligatorio ni promesa de duración exacta. El nivel elegido
ajusta apoyo, no crea preguntas difíciles inventadas. Las dos rutas de entrada
usan este mismo curso inicial; el catálogo general aún no está implementado.

El contenido amplía `data/library/math/fracciones.md` con ejemplos de fracciones
elementales. Su autoría es editorial, no generativa. Las pruebas verifican
consistencia de respuestas y se revisaron los cálculos. Requiere revisión pedagógica
por docentes antes de presentarse como currículo escolar validado.

## Privacidad, recuperación y límites

- No pide edad, correo, escuela, ubicación ni cuenta. Se recomienda un apodo.
- No utiliza analytics, telemetría, anuncios ni servicios externos.
- Todo acceso a evidencia parte del ID del perfil activo. Cambiar de perfil limpia
  la ayuda y la tarjeta visible. Las escrituras usan revisión optimista para que
  una pestaña antigua no sobrescriba el estado reciente.
- Los perfiles **no son cuentas autenticadas**. Cualquier persona con acceso al
  mismo navegador puede abrirlos. No almacenar información sensible ni usar como
  sistema de expedientes escolares. El aislamiento lógico no es cifrado.
- Una copia JSON contiene solo el perfil elegido y **no está cifrada**. Debe
  conservarse de forma privada. Recuperar nunca reemplaza perfiles existentes.
- El importador limita tamaño, estructura, versión, IDs y respuestas. Solo acepta
  progreso del curso incluido; descarta privilegios, ajustes de IA y otros campos
  no autorizados. El texto se escapa al renderizar; no se ejecutan cursos ni
  instrucciones de archivos. No hay pipeline móvil de documentos no confiables.
- Los puntajes locales pueden ser manipulados por el dueño del navegador. No son
  credenciales, notas oficiales ni evidencia para conceder derechos comerciales.
- El navegador puede expulsar almacenamiento; exportar copias es la protección
  disponible. No se promete durabilidad ilimitada. Límite: 5,000 eventos por perfil.
- Eliminar un perfil borra sus datos de IndexedDB; conserva el curso gratuito
  cacheado y no puede eliminar copias descargadas fuera del navegador.
- IndexedDB está versionado. Una futura migración debe conservar los perfiles,
  probar backups anteriores y explicar incompatibilidades; versiones desconocidas
  se rechazan, no se reinterpretan silenciosamente.

## IA y monetización: contratos pendientes

`capabilities.mjs` es la frontera de capacidades. El tutor estructurado funciona
siempre con el curso. `requestGenerativeTutor()` falla de forma explícita y no
realiza solicitudes. La indisponibilidad se muestra en la UI.

Antes de conectar un proveedor generativo se necesitan:

- consentimiento claro y configuración opcional para datos que salen del dispositivo;
- contexto limitado al perfil y materiales revisados, separado de las instrucciones;
- verificación de fidelidad, lenguaje, ayuda pedagógica y resistencia a instrucciones
  maliciosas del material importado;
- límites configurables de solicitudes/tokens, timeout y costo por sesión;
- uso de secretos únicamente en servidor, nunca en el frontend;
- mediciones de memoria, latencia y batería para IA local en Android, con fallback.

No se promete inferencia móvil universal. No se reutiliza Machine ID ni se
modifica Ed25519 del escritorio. Gratis funciona sin permisos comerciales.
`hasAccess()` no acepta derechos enviados por un perfil y `paidEntitlement()`
permanece inactivo hasta incorporar un verificador real.

La integración comercial posterior necesita un adaptador que **verifique**
compras con el proveedor en un backend, vincule derechos a una identidad y emita
una prueba verificable con alcance, expiración y revocación. El cliente no puede
concederse Premium. Debe definirse cómo caducan derechos offline y cómo se recuperan
al cambiar de dispositivo. No hay checkout, precio, suscripción ni cobro simulado.

## Pruebas

Con las dependencias de desarrollo del repositorio y Node.js 22 o posterior:

```bash
python -m playwright install chromium
python -m pytest -q
node --test tests/*.mjs
```

`test_mobile.mjs`: ciclo educativo, pistas acotadas, prerrequisitos, respuestas
únicas por sesión, fallo de comprobación, recuperación, validación y capacidades.

`test_mobile_parity.py`: resultados del motor Python y la proyección JS.

`test_mobile_e2e.py`: navegador real, CSP de producción, los tres temas, service
worker, recarga offline, persistencia, perfiles, backup, importación no ejecutable,
conflictos entre pestañas y error de almacenamiento. Capturas en
`artifacts/mobile/` (no se suben datos reales).

Resultados y límites de la ejecución: [MOBILE_VERIFICATION.md](MOBILE_VERIFICATION.md).

## Siguiente incremento

Validar esta PWA en un teléfono Android físico antes de elegir distribución
nativa. Priorizar revisión docente y observación de aprendizaje con usuarios,
después interoperabilidad de cursos revisados, contenido de comprensión lectora
e inglés y una integración comercial verificable. La IA generativa se añade
cuando mejore el aprendizaje con calidad y costos medidos.
