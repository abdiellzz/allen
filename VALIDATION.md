# Verificación de ALLEN

Fechas: 18–19 de septiembre de 2026. Entorno: Windows, Python 3.13.13. Se creó un entorno virtual nuevo y se instalaron las dependencias del proyecto.

## Comprobaciones automatizadas

- Suite Python: 46 casos de prueba (37 de la aplicación y 9 del dataset/entrenamiento). Incluye inicialización/persistencia SQLite, aislamiento de consultas por perfil, borrado en cascada, retención y desactivación de historial, XP idempotente, racha, repetición espaciada y rutas principales.
- Quizzes: todos los temas, tres tipos de pregunta y tres dificultades; casos matemáticos con resultados conocidos; fracciones equivalentes; rechazo de respuestas incompletas y temas inexistentes.
- IA: transporte HTTP simulado de llama.cpp, detección, modelo inexistente, modo demo, SSE incremental, contexto, prompts, endpoints tutor/resumir/traducir, regeneración, rechazo de JSON malformado y liberación del semáforo al cancelar.
- Tarjetas generadas: rechazo sin modelo; validación del JSON simulado; propuestas sin guardado automático; guardado explícito.
- Seguridad: rechazo de URL externa y redirecciones, Host/Origin/token, límites de mensajes/cuerpo, ausencia de acceso estático al backend/base, mensajes de seguridad y ejemplos benignos.
- JavaScript: 7 pruebas con Node (3 del renderizador y 4 del cliente API); escape de HTML/script, código/tablas/listas y ausencia de imágenes/enlaces remotos.
- Sintaxis Python/JavaScript y `pip check` en el entorno virtual.

Los tests usan bases temporales y transportes simulados. No necesitan Internet ni un modelo descargado. La importación del módulo de aplicación inicializa también la base predeterminada, pero los datos de cada prueba se escriben en su base temporal.

## Comprobaciones realizadas en navegador

- Inicio, identidad visual, navegación y diagnóstico de modelo desconectado.
- Chat demo: envío, estado «Allen está pensando…», respuesta claramente identificada y conversación guardada.
- Quiz del Sistema Solar: selección, corrección 1/1 y explicación de la respuesta.
- Tarjeta manual: creación, revelado de respuesta y valoración «Bien».
- Biblioteca: búsqueda «Python», lectura y bloque de código mostrado como texto.
- Configuración: selección de texto grande y alto contraste, aplicación visible de ambos ajustes.
- Vistas de escritorio (1440 × 1000), tablet (820 × 1180) y móvil (390 × 844). Tablet y móvil comprobados sin desbordamiento horizontal de la página; la navegación móvil tiene desplazamiento horizontal propio.
- Inicio real usando `cmd /c start_allen.bat`, con entorno ya instalado, servidor activo en 127.0.0.1:8787.

Las verificaciones manuales anteriores son las realizadas, no una afirmación de cobertura visual exhaustiva de todos los botones. La copia/pegado al portapapeles, cancelación de un GGUF real y revisión pedagógica de conversaciones largas requieren validación adicional.

## Límites y pendientes

1. **No había un modelo GGUF conectado.** La integración se verificó con respuestas simuladas. No se afirma haber validado calidad, velocidad, memoria, streaming ni cancelación del cómputo con llama.cpp real.
2. No se desconectó físicamente la red del equipo. Las pruebas simulan la falta del servidor de IA; el frontend y los módulos locales no requieren recursos externos. La indicación online/offline usa `navigator.onLine`, no una prueba externa de Internet.
3. Los filtros de seguridad son básicos y no constituyen una auditoría adversarial, certificación para menores ni sustituto de supervisión adulta.
4. Los bancos de contenido son pequeños. No hay embeddings, currículo completo, cuentas docentes autenticadas, instalador firmado ni una biblioteca extensa validada por docentes.
5. La instalación limpia de dependencias y el arranque del BAT con ese entorno se verificaron. No se probó el flujo de instalación en un Windows nuevo sin Python ni el camino de instalación fallida sin Internet.
6. Las dependencias de pruebas emiten advertencias de deprecación: Starlette recomienda `httpx2` para su TestClient y una API de portal de AnyIO cambió de ubicación. No fallan los tests ni afectan al arranque verificado; conviene actualizar el adaptador de pruebas en una próxima revisión.


## Dataset y entrenamiento opcional

Se validaron los 2.800 registros, la distribución en diez áreas, los hashes, ausencia de duplicados exactos, conservación de los tres ejemplos aportados, resultados matemáticos conocidos, longitud de resúmenes y división agrupada 2.530/270. Las nueve pruebas adicionales comprueban también que la validación no necesita dependencias de entrenamiento y que no comienza SFT sin modelo local y revisión. Los 2.800 registros siguen marcados como pendientes de revisión humana. No se ha entrenado, convertido ni evaluado un modelo con este dataset.

Resultado final: **46 pruebas Python y 7 pruebas JavaScript aprobadas; cero fallos.** Permanecen las dos advertencias de deprecación de las dependencias de pruebas descritas arriba. `pip check` no detectó dependencias rotas en el entorno de la aplicación. El entorno opcional SFT no se instaló.

## Verificación posterior con modelo real (19 de septiembre)

Se encontró un modelo local ya descargado y un binario de llama.cpp instalado: Qwen3.5-0.8B Q8_0, servidor build 11026. Se inició en CPU, cuatro hilos, un slot, contexto 4096 y pensamiento desactivado. `/health` pasó a disponible y `/api/model/status` devolvió `IA LOCAL ACTIVA`.

Se probó `Hola` a través de `/api/chat` usando un perfil temporal de comprobación. Se recibió una respuesta no vacía en español con `demo: false` en aproximadamente 20,7 segundos. El perfil temporal se eliminó al terminar; no se borraron conversaciones del usuario.

Esta comprobación **actualiza únicamente la limitación anterior sobre ausencia de prueba real básica**. No valida aún toda la calidad educativa, todas las modalidades, el streaming visual o la cancelación del cómputo real. Tampoco se ha entrenado el dataset.

Tres pruebas adicionales del lanzador pasaron: ruta de modelo con espacios, rechazo de dirección remota y rechazo de otro tipo de ejecutable. Se comprobó también que detecta un servidor activo sin iniciar otro.
