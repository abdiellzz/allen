export const lessons={
 'Matemáticas':{title:'Una fracción es una parte',concept:'Una fracción representa partes iguales de un todo.',example:'Si divides una pizza en cuatro partes iguales y tomas una, tienes 1/4.',question:'Si tomas dos de esas cuatro partes, ¿qué fracción tienes?',options:['2/4','4/2','1/4'],correct:0,feedback:'Dos partes de un total de cuatro son 2/4, lo mismo que la mitad.'},
 'Tecnología':{title:'Tu dirección en una red',concept:'Una dirección IP ayuda a dirigir datos a un dispositivo dentro de una red.',example:'Como la dirección de una casa permite entregar una carta, una IP ayuda a entregar datos.',question:'¿Para qué sirve una dirección IP?',options:['Entregar datos en una red','Medir la batería','Guardar fotos'],correct:0,feedback:'La dirección ayuda a encontrar el destino de los datos.'},
 'Inglés':{title:'Una palabra que abre puertas',concept:'Learn significa aprender. Learning significa aprendizaje o aprendiendo, según la frase.',example:'I am learning English: estoy aprendiendo inglés.',question:'¿Qué significa I learn?',options:['Yo enseño','Yo aprendo','Yo corro'],correct:1,feedback:'I significa yo; learn significa aprender: yo aprendo.'},
 'Programación':{title:'Dale nombre a un valor',concept:'Una variable es un nombre que permite usar un valor en un programa.',example:'En Python: puntos = 10. Luego puntos = puntos + 5 deja puntos en 15.',question:'Si puntos vale 10 y sumas 5, ¿qué valor queda?',options:['5','10','15'],correct:2,feedback:'El nuevo valor es 15. El nombre puntos sigue siendo el mismo.'},
 'IA':{title:'Una IA dentro de tu equipo',concept:'Un modelo de IA usa patrones aprendidos para producir una respuesta. Puede equivocarse.',example:'ALLEN usa un modelo instalado para responder preguntas sin enviar el texto a un servidor externo.',question:'¿Qué haces con un dato importante que te da una IA?',options:['Lo verifico','Siempre lo creo','Lo borro sin leer'],correct:0,feedback:'Comprueba los datos importantes. Aprender también es hacer buenas preguntas.'},
 'Curiosidades':{title:'Un byte, ocho decisiones',concept:'Un bit puede tener dos valores: 0 o 1. Ocho bits forman un byte.',example:'Cada posición duplica las combinaciones: con dos bits hay 00, 01, 10 y 11.',question:'¿Cuántas combinaciones tienen dos bits?',options:['2','4','8'],correct:1,feedback:'Hay cuatro combinaciones. Con ocho bits existen 256.'}
};

// ── «Enséñame algo»: categorías y temas sugeridos ────────────────────────────
// topic.lesson  → abre la experiencia guiada con esa microlección local
// topic.prompt  → envía la pregunta a Allen en el chat libre
export const LEARN_CATEGORIES={
 'Matemáticas':{icon:'calculator',desc:'Números, fracciones y trucos para calcular.',topics:[
  {label:'Fracciones',lesson:'Matemáticas'},
  {label:'Porcentajes',prompt:'Enséñame qué es un porcentaje con un ejemplo fácil.'},
  {label:'Multiplicación mental',prompt:'Enséñame un truco para multiplicar más rápido.'},
  {label:'Ecuaciones sencillas',prompt:'Explícame cómo resolver una ecuación como 2x + 6 = 20.'},
  {label:'Proporciones',prompt:'Explícame qué es una proporción con un ejemplo de la vida diaria.'}]},
 'Programación':{icon:'code',desc:'Ideas para crear tus propios programas.',topics:[
  {label:'Variables',lesson:'Programación'},
  {label:'Condicionales',prompt:'Explícame qué es un condicional en programación, con un ejemplo en Python.'},
  {label:'Bucles',prompt:'Explícame qué es un bucle for en Python con un ejemplo corto.'},
  {label:'Funciones',prompt:'Explícame qué es una función en programación y para qué sirve.'},
  {label:'Python básico',prompt:'Enséñame Python desde cero: mi primer programa.'}]},
 'Inglés':{icon:'languages',desc:'Palabras y frases que abren puertas.',topics:[
  {label:'Una palabra clave',lesson:'Inglés'},
  {label:'Saludos',prompt:'Enséñame saludos básicos en inglés con ejemplos.'},
  {label:'Present simple',prompt:'Explícame el present simple en inglés con ejemplos.'},
  {label:'Vocabulario diario',prompt:'Enséñame 5 palabras útiles en inglés con ejemplos.'}]},
 'Inteligencia Artificial':{icon:'sparkles',desc:'Entiende la tecnología que usas.',topics:[
  {label:'Qué es una IA',lesson:'IA'},
  {label:'Machine Learning',prompt:'Explícame qué es machine learning con una analogía sencilla.'},
  {label:'Modelos de lenguaje',prompt:'Explícame qué es un modelo de lenguaje como el que usa Allen.'},
  {label:'IA local',prompt:'Explícame qué significa que una IA funcione localmente, sin Internet.'},
  {label:'Uso responsable',prompt:'Enséñame cómo usar la inteligencia artificial de forma responsable.'}]},
 'Tecnología':{icon:'cpu',desc:'Cómo funcionan las cosas digitales.',topics:[
  {label:'Tu dirección en una red',lesson:'Tecnología'},
  {label:'Contraseñas seguras',prompt:'Enséñame cómo crear una contraseña segura y por qué importa.'},
  {label:'Hardware básico',prompt:'Explícame qué partes tiene una computadora y para qué sirven.'},
  {label:'Cómo viajan los datos',prompt:'Explícame cómo viaja un mensaje por una red.'}]},
 'Ciencia':{icon:'flask-conical',desc:'Preguntas grandes del mundo real.',topics:[
  {label:'El método científico',prompt:'Explícame qué es el método científico con un ejemplo.'},
  {label:'La célula',prompt:'Explícame qué es una célula de forma sencilla.'},
  {label:'El sistema solar',prompt:'Enséñame algo curioso del sistema solar.'},
  {label:'La energía',prompt:'Explícame qué es la energía con un ejemplo cotidiano.'}]},
 'Lógica':{icon:'compass',desc:'Entrena tu forma de razonar.',topics:[
  {label:'Bits y bytes',lesson:'Curiosidades'},
  {label:'Series y patrones',prompt:'Dame una serie numérica sencilla y explícame cómo encontrar el patrón.'},
  {label:'Deducción',prompt:'Explícame qué es deducir, con un ejemplo tipo detective.'},
  {label:'Acertijos',prompt:'Dame un acertijo de lógica y déjame intentarlo antes de la respuesta.'}]},
 'Cultura digital':{icon:'library',desc:'Moverte seguro y con criterio en línea.',topics:[
  {label:'Verificar información',prompt:'Enséñame cómo comprobar si una noticia es confiable.'},
  {label:'Privacidad en línea',prompt:'Explícame qué datos personales no debo compartir en línea.'},
  {label:'Contraseñas',prompt:'Enséñame buenas costumbres con mis contraseñas.'},
  {label:'Huella digital',prompt:'Explícame qué es la huella digital que dejamos en Internet.'}]},
 'Ciberseguridad':{icon:'shield-check',desc:'Protégete y protege a otros en el mundo digital.',topics:[
  {label:'Phishing',prompt:'Explícame qué es el phishing y cómo identificar un correo falso, con ejemplos reales.'},
  {label:'Contraseñas seguras',prompt:'Enséñame cómo crear una contraseña realmente segura y qué errores evitar.'},
  {label:'Autenticación de dos factores',prompt:'Explícame qué es la autenticación de dos factores (MFA) y por qué es importante activarla.'},
  {label:'Ingeniería social',prompt:'Explícame qué es la ingeniería social y cómo protegerme de ella.'},
  {label:'Seguridad en redes sociales',prompt:'Dame consejos prácticos para mantener mis redes sociales seguras y privadas.'},
  {label:'Malware',prompt:'Explícame qué es el malware: tipos, cómo llega y cómo protegerme.'},
  {label:'Wi-Fi pública',prompt:'Explícame los riesgos de conectarse a Wi-Fi pública y cómo protegerme.'},
  {label:'Privacidad digital',prompt:'Explícame qué es la privacidad digital y qué datos nunca debo compartir en línea.'}]},
 'Robótica':{icon:'bot',desc:'Combina electrónica y código para crear máquinas.',topics:[
  {label:'Qué es la robótica',prompt:'Explícame qué es la robótica, para qué sirve y ejemplos del mundo real.'},
  {label:'Arduino básico',prompt:'Explícame qué es Arduino y cómo funciona para principiantes.'},
  {label:'Sensores',prompt:'Explícame qué son los sensores en robótica y da ejemplos de sensores comunes.'},
  {label:'Actuadores',prompt:'Explícame qué son los actuadores en robótica: motores, servos y LEDs.'},
  {label:'Programar un robot',prompt:'Explícame los pasos básicos para programar un robot con Arduino.'}]}
};

// ── «Sorpréndeme»: actividades locales elegidas por Allen ────────────────────
// type: lesson (microlección), riddle (acertijo), fact (curiosidad comprobable),
//       tf (verdadero/falso), error (encuentra el error)
export const SURPRISES=[
 {type:'lesson',lesson:'IA'},
 {type:'lesson',lesson:'Matemáticas'},
 {type:'lesson',lesson:'Programación'},
 {type:'lesson',lesson:'Inglés'},
 {type:'lesson',lesson:'Tecnología'},
 {type:'lesson',lesson:'Curiosidades'},
 {type:'riddle',title:'Acertijo',question:'Tengo ciudades pero no casas, tengo ríos pero no agua. ¿Qué soy?',answer:'Un mapa.',explanation:'Un mapa dibuja ciudades y ríos, pero no contiene casas ni agua de verdad.'},
 {type:'riddle',title:'Acertijo',question:'Cuanto más le quitas, más grande se hace. ¿Qué es?',answer:'Un hoyo.',explanation:'Cada vez que sacas tierra, el hoyo se hace más grande.'},
 {type:'riddle',title:'Acertijo',question:'¿Qué número sigue? 3, 6, 12, 24, …',answer:'48.',explanation:'Cada número es el doble del anterior: 24 × 2 = 48.'},
 {type:'fact',title:'Curiosidad',text:'El primer "error de computadora" fue un insecto real: una polilla encontrada en un relé de la computadora Mark II en 1947. De ahí viene la palabra bug.',question:'¿De dónde viene la palabra bug en informática?',options:['De un insecto real','De un videojuego','De un tipo de cable'],correct:0,feedback:'Una polilla causó una falla en la Mark II y quedó registrada en el cuaderno de bitácora.'},
 {type:'fact',title:'Curiosidad',text:'Tu cerebro usa alrededor del 20% de la energía de tu cuerpo, aunque pesa solo cerca del 2% de tu peso.',question:'¿Cuánta energía usa aproximadamente tu cerebro?',options:['1%','20%','90%'],correct:1,feedback:'Aproximadamente el 20%: pensar también consume energía.'},
 {type:'fact',title:'Curiosidad',text:'El nombre Python no viene de la serpiente: su creador, Guido van Rossum, lo tomó del grupo de comedia Monty Python.',question:'¿De dónde viene el nombre del lenguaje Python?',options:['De una serpiente','De un grupo de comedia','De un robot'],correct:1,feedback:'Viene de Monty Python, el grupo de humor británico.'},
 {type:'tf',statement:'Una IA puede equivocarse aunque su respuesta suene convincente.',answer:true,explanation:'Los modelos generan respuestas probables, no garantizadas: por eso los datos importantes se verifican.'},
 {type:'tf',statement:'Una contraseña corta con tu nombre es segura porque es fácil de recordar.',answer:false,explanation:'Las contraseñas cortas y predecibles se adivinan rápido. Mejor largas y únicas.'},
 {type:'tf',statement:'8 bits forman un byte.',answer:true,explanation:'Un byte son 8 bits; por eso un byte puede representar 256 valores distintos.'},
 {type:'error',title:'Encuentra el error',code:'puntos = 10\npuntos = puntos + 5\nprint(punto)',question:'¿Cuál es el error de este programa?',options:['Falta un número','La variable se llama puntos, no punto','print no existe en Python'],correct:1,feedback:'Se escribió "punto" sin la s. Python no encuentra ese nombre y muestra un error.'},
 {type:'error',title:'Encuentra el error',code:'edad = 12\nsi edad > 10:\n    print("Mayor de 10")',question:'¿Qué palabra no existe en Python?',options:['print','si (debe ser if)','edad'],correct:1,feedback:'En Python las condiciones se escriben con if. "si" no es una palabra válida.'}
];


// Time without interaction before the experience view switches to AFK.
export const ATTRACT_MS = 35000;
// How long each attract message is shown (ms). Comfortable reading range: 2500–4000
export const AFK_MESSAGE_INTERVAL_MS = 3000;

// ── Attract / AFK message sequence ───────────────────────────────────────────
// Each entry: { text, cta, dest, pose }
//   text  – bold, curious & playful headline for fair visitors
//   cta   – action label of the primary button
//   dest  – target page ID to navigate on click
//   pose  – Allen mascot state (hello, challenge, thinking, teaching, celebrating, reading)
export const ATTRACT_MESSAGES = [
 {text:'¿Vienes a mirar o a jugar?',                       cta:'Jugar',           dest:'game',      pose:'celebrating'},
 {text:'Hazme una pregunta difícil.',                      cta:'Preguntar',       dest:'chat',      pose:'thinking'},
 {text:'Te apuesto que no completas 3 retos seguidos.',    cta:'Aceptar reto',    dest:'challenge', pose:'challenge'},
 {text:'Cuidado: podría hacerte pensar.',                  cta:'Probar',          dest:'compare',   pose:'teaching'},
 {text:'A ver… sorpréndeme.',                              cta:'Sorpréndeme',     dest:'game',      pose:'thinking'},
 {text:'¿Eso es todo lo que tienes?',                      cta:'Demuéstralo',     dest:'challenge', pose:'challenge'},
 {text:'Vamos, intenta impresionarme.',                    cta:'Acepto',          dest:'chat',      pose:'hello'},
 {text:'¿Quieres algo fácil o algo que de verdad te rete?',cta:'Rétame',          dest:'challenge', pose:'challenge'},
 {text:'No prometo ponértelo fácil.',                      cta:'Demuéstralo',     dest:'game',      pose:'challenge'},
 {text:'Tu turno. Haz algo interesante.',                  cta:'Empezar',         dest:'game',      pose:'celebrating'},
 {text:'Tengo un reto para ti.',                           cta:'Ver reto',        dest:'challenge', pose:'hello'},
 {text:'¿Te atreves a probar algo al azar?',               cta:'Probar al azar',  dest:'how',       pose:'thinking'},
];

export function inactivityDecision(elapsed,warningElapsed,hasVisitor,onHome){
 // An active visitor may see the attract screen, but never loses their session.
 if(elapsed>=ATTRACT_MS&&hasVisitor&&!onHome)return 'afk';
 if(elapsed>=ATTRACT_MS&&!hasVisitor&&onHome)return 'attract';
 return 'stay';
}
