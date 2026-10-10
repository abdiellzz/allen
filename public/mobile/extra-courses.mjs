// Editorial starter courses. All activities are bundled, inspectable and offline.
const question=(id,kind,prompt,options,answer,hints,feedback)=>({id,kind,prompt,options,answer,hints,feedback});
const topic=(id,title,objective,explanation,simple,example,alternative,card,questions,prerequisite=null)=>({id,title,objective,explanation,simple,example,alternative,card,questions,prerequisite});
export const extraCourses=[
 {id:'reading-v1',title:'Lee, comprende y explica',subject:'Comprensión lectora',asset:'allen-reading-official.svg',source:'ALLEN · textos originales de práctica de comprensión lectora',topics:[
  topic('reading-main','Encontrar la idea principal','Distinguir la idea principal de los detalles de un texto.',
   'La idea principal resume lo más importante del texto. Los detalles aportan ejemplos o explicaciones. Para encontrarla, pregunta: ¿de qué trata todo el texto?',
   'Busca una frase que explique el texto completo, no solo una palabra o un detalle.',
   'Texto: «El huerto escolar nos permite aprender. Sembramos semillas, observamos su crecimiento y registramos los cambios». Idea principal: el huerto ayuda a aprender. Sembrar y registrar son detalles.',
   'Texto: «Dormir ayuda al cuerpo y a la atención. Después de descansar, podemos concentrarnos mejor». La idea principal es el beneficio de dormir.',
   {front:'¿Cómo encuentras la idea principal?',back:'Busca lo que resume el texto completo y distingue los detalles que lo apoyan.'},[
    question('r-d1','diagnostic','«La biblioteca ofrece libros, talleres y espacios de lectura». ¿Qué resume el texto?',['La biblioteca ofrece recursos para aprender','Solo hay talleres','No hay libros'],'La biblioteca ofrece recursos para aprender',['Piensa en todos los elementos mencionados.','La respuesta debe incluir libros y talleres, sin excluirlos.'],'La biblioteca ofrece varios recursos; escoger solo los talleres omite parte del texto.'),
    question('r-d2','diagnostic','En «El huerto ayuda a aprender: observamos plantas», ¿qué es un detalle?',['El huerto ayuda a aprender','Observamos plantas','El texto no tiene detalles'],'Observamos plantas',['Busca el ejemplo que apoya la idea.','La observación explica cómo aprendemos.'],'Observar plantas es un detalle que apoya la idea general de aprender con el huerto.'),
    question('r-1','practice','«La bicicleta facilita desplazarse. Sirve para ir a la escuela y visitar amigos». ¿Cuál es la idea principal?',['Visitar amigos es obligatorio','La bicicleta facilita desplazarse','La bicicleta solo sirve para la escuela'],'La bicicleta facilita desplazarse',['Busca la frase más amplia.','Los viajes a la escuela y a amigos son ejemplos.'],'La idea principal es el desplazamiento; la escuela y los amigos son destinos que la apoyan.'),
    question('r-2','practice','«Leer amplía el vocabulario. En un cuento conocí palabras nuevas». ¿Qué apoya la idea principal?',['Conocer palabras nuevas en un cuento','Todos deben leer el mismo cuento','Leer nunca enseña palabras'],'Conocer palabras nuevas en un cuento',['Encuentra el ejemplo que aparece realmente.','El ejemplo habla de un cuento y palabras.'],'Las palabras nuevas del cuento son evidencia del ejemplo, no una regla sobre todos los cuentos.'),
    question('r-c','check','«Cuidamos el parque juntos: recogemos basura y protegemos las plantas». ¿Qué título resume mejor el texto?',['Una planta particular','Solo basura','Cuidar el parque en comunidad'],'Cuidar el parque en comunidad',['Incluye las dos acciones.','El texto también dice que se hace en conjunto.'],'Cuidar el parque en comunidad resume ambas acciones y el trabajo conjunto.')]),
  topic('reading-evidence','Responder con evidencia','Separar lo que dice el texto de una suposición.',
   'Una respuesta sustentada se apoya en información del texto. Una inferencia usa pistas para deducir algo, pero no debe inventar detalles que esas pistas no permiten conocer.',
   'Si el texto no lo dice ni da pistas suficientes, responde que no podemos saberlo.',
   '«Sara guardó un paraguas al ver nubes oscuras». Podemos inferir que se preparó por si llovía. No sabemos si después llovió.',
   '«Luis lleva un libro a la sala». Sabemos que lleva un libro. No sabemos su título ni si lo terminó.',
   {front:'¿Qué haces si el texto no permite responder?',back:'Reconoces que falta información en lugar de inventar un detalle.'},[
    question('re-d1','diagnostic','«Ana salió a las siete». ¿Podemos saber adónde fue?',['A la escuela','No, falta información','Al parque'],'No, falta información',['El texto solo da una hora.','No menciona un destino.'],'No podemos conocer el destino a partir de la hora de salida.'),
    question('re-d2','diagnostic','«Tomás tomó agua después de correr». ¿Qué afirma el texto?',['Tomó agua','Ganó una carrera','Corrió diez kilómetros'],'Tomó agua',['Busca una acción explícita.','La distancia y el resultado no aparecen.'],'El texto dice que tomó agua después de correr; no indica distancia ni victoria.'),
    question('re-1','practice','«Elena abrió su cuaderno y comenzó a escribir». ¿Qué está sustentado?',['Terminó un examen','Comenzó a escribir','Escribió una novela'],'Comenzó a escribir',['No inventes el tipo de actividad.','Identifica el verbo que sí aparece.'],'Comenzó a escribir es la acción explícita. No sabemos si fue un examen o una novela.'),
    question('re-2','practice','«Vimos nubes oscuras y llevamos paraguas». ¿Qué inferencia es razonable?',['Se prepararon por si llovía','Ya había una inundación','Llovió toda la noche'],'Se prepararon por si llovía',['Relaciona las nubes con el paraguas.','La preparación no demuestra que después lloviera.'],'Llevar paraguas sugiere preparación ante posible lluvia; no prueba una inundación ni la duración de la lluvia.'),
    question('re-c','check','«Diego devolvió un libro el martes». ¿Cuándo comenzó a leerlo?',['El lunes','El domingo','No se puede saber con ese texto'],'No se puede saber con ese texto',['La devolución y el inicio son momentos distintos.','Solo se conoce el día de devolución.'],'El texto no da la fecha de inicio. Una respuesta fiable reconoce esa falta de información.')],'reading-main')]
 },
 {id:'english-v1',title:'Inglés para empezar',subject:'Inglés',asset:'allen-english-book.svg',source:'ALLEN · práctica editorial de inglés inicial',topics:[
  topic('english-greetings','Saludar y presentarte','Elegir saludos y una presentación breve en inglés.',
   'Hello y Hi son saludos. Good morning se usa por la mañana. Para presentarte, puedes decir My name is… o I am… seguido de tu nombre.',
   'Hello significa hola. My name is Ana significa Me llamo Ana.',
   'A: Hello! My name is Ana. B: Hi, Ana! I am Luis.',
   'Por la mañana: Good morning! My name is Sara. Significa: ¡Buenos días! Me llamo Sara.',
   {front:'¿Cómo dices Me llamo Ana?',back:'My name is Ana. También puedes decir I am Ana.'},[
    question('en-d1','diagnostic','¿Qué significa Hello?',['Adiós','Hola','Gracias'],'Hola',['Es un saludo.','Lo usamos al comenzar una conversación.'],'Hello es un saludo: Hola.'),
    question('en-d2','diagnostic','¿Qué frase significa Me llamo Ana?',['My name is Ana','Goodbye, Ana','Thank you, Ana'],'My name is Ana',['Busca la frase sobre el nombre.','Name significa nombre.'],'My name is Ana presenta el nombre; Goodbye se usa para despedirse.'),
    question('en-1','practice','Llegas por la mañana. ¿Qué saludo corresponde?',['Good night','Good morning','Goodbye'],'Good morning',['Morning significa mañana.','Night significa noche.'],'Good morning es Buenos días. Good night suele usarse al despedirse por la noche o al ir a dormir.'),
    question('en-2','practice','Completa la presentación: «My ___ is Luis».',['name','morning','bye'],'name',['La frase comunica tu nombre.','Name es la palabra que necesitas.'],'My name is Luis significa Me llamo Luis.'),
    question('en-c','check','Conoces a alguien y quieres saludar y presentarte. ¿Qué eliges?',['Hello! My name is Sara.','Goodbye! Thank you.','Good night! Bye.'],'Hello! My name is Sara.',['Necesitas saludo y nombre.','Hello inicia la conversación.'],'Hello! My name is Sara combina un saludo con una presentación clara.')]),
  topic('english-am','Usar I am y You are','Completar oraciones sencillas con el verbo to be.',
   'Para hablar de ti, usa I am. Para dirigirte a otra persona, usa You are. Am y are son formas del verbo to be. I am a student significa Soy estudiante.',
   'I va con am. You va con are. Aprende primero esas dos combinaciones.',
   'I am a student. You are a teacher. Soy estudiante. Tú eres docente.',
   'I am happy: Estoy feliz. You are ready: Estás listo o lista.',
   {front:'¿Qué formas acompañan a I y You?',back:'I am y You are.'},[
    question('ea-d1','diagnostic','Completa: «I ___ a student».',['are','am','is'],'am',['Mira el pronombre I.','I se combina con am.'],'I am a student es la combinación correcta para hablar de ti.'),
    question('ea-d2','diagnostic','Completa: «You ___ ready».',['am','is','are'],'are',['Mira el pronombre You.','You se combina con are.'],'You are ready significa Estás listo o lista.'),
    question('ea-1','practice','¿Qué frase significa Estoy feliz?',['I am happy','You am happy','I are happy'],'I am happy',['La frase habla de ti.','I necesita am.'],'I am happy es correcto. La combinación I are no corresponde.'),
    question('ea-2','practice','Completa: «You ___ a teacher».',['is','are','am'],'are',['La frase se dirige a otra persona.','Usa You are.'],'You are a teacher significa Tú eres docente.'),
    question('ea-c','check','Quieres decir Soy estudiante en una presentación. ¿Qué dices?',['I are a student','I am a student','You am a student'],'I am a student',['Hablas de ti, así que usa I.','Combina I con am.'],'I am a student expresa correctamente que eres estudiante.')],'english-greetings')]
 },
 {id:'python-v1',title:'Tus primeros pasos en Python',subject:'Programación',asset:'allen-python.svg',source:'ALLEN · ejemplos editoriales de Python 3, sin ejecución de código',topics:[
  topic('python-values','Valores y variables','Reconocer cómo una variable guarda un valor en Python.',
   'Una variable vincula un nombre con un valor. En edad = 12, el nombre edad se vincula al número 12. El signo = asigna; no es una comparación. Los textos se escriben entre comillas.',
   'Piensa en un nombre que apunta a un dato: puntos = 5. Puedes usar puntos para recordar ese 5.',
   'puntos = 5\npuntos = puntos + 2\nAhora puntos vale 7: sumamos 2 al valor anterior y guardamos el resultado.',
   'nombre = "Ana" guarda un texto. cantidad = 3 guarda un número. Las comillas distinguen el texto.',
   {front:'¿Qué hace = en una asignación de Python?',back:'Vincula el nombre de la izquierda al valor de la derecha.'},[
    question('py-d1','diagnostic','Después de «puntos = 5», ¿qué valor tiene puntos?',['5','puntos','0'],'5',['Mira lo que está a la derecha del signo =.','El número asignado es 5.'],'puntos queda vinculado al valor 5.'),
    question('py-d2','diagnostic','¿Cuál de estos valores es texto en Python?',['12','"Ana"','3 + 2'],'"Ana"',['Busca las comillas.','Una cadena de texto se escribe entre comillas.'],'"Ana" es texto. 12 es un número y 3 + 2 es una expresión numérica.'),
    question('py-1','practice','«puntos = 5» y luego «puntos = puntos + 2». ¿Qué valor queda?',['5','2','7'],'7',['Usa el valor anterior de puntos.','Calcula 5 + 2.'],'El valor final es 7. La segunda línea suma 2 al 5 anterior y vuelve a asignar.'),
    question('py-2','practice','¿Qué línea guarda el texto Ana en nombre?',['nombre = Ana','nombre = "Ana"','"nombre" = Ana'],'nombre = "Ana"',['El texto necesita comillas.','El nombre de la variable va a la izquierda.'],'nombre = "Ana" asigna el texto. Sin comillas, Ana se interpretaría como un nombre de variable.'),
    question('py-c','check','«total = 4» y luego «total = total + 3». ¿Qué valor tiene total?',['3','4','7'],'7',['Suma al valor guardado inicialmente.','4 + 3 = 7.'],'total termina en 7. La asignación actualiza el valor anterior.')]),
  topic('python-output','Mostrar resultados con print','Predecir la salida de instrucciones básicas de Python.',
   'print muestra un resultado. print("Hola") muestra Hola, sin las comillas. print(2 + 3) calcula la expresión y muestra 5. Esto es una explicación de código, no un ejecutor.',
   'print es una instrucción para mostrar. Lo que quieres mostrar va entre paréntesis.',
   'nombre = "Ana"\nprint(nombre)\nLa salida es Ana. print usa el valor guardado en la variable.',
   'print("2 + 3") muestra el texto 2 + 3. print(2 + 3) muestra 5. Las comillas cambian cómo se interpreta el contenido.',
   {front:'¿Qué diferencia hay entre print("2 + 3") y print(2 + 3)?',back:'El primero muestra texto; el segundo calcula y muestra 5.'},[
    question('po-d1','diagnostic','¿Qué muestra print("Hola")?',['Hola','"Hola" con comillas','Nada'],'Hola',['Las comillas delimitan el texto.','No forman parte del texto mostrado.'],'print("Hola") muestra Hola; las comillas indican que es texto.'),
    question('po-d2','diagnostic','¿Qué muestra print(2 + 3)?',['2 + 3','5','23'],'5',['No hay comillas.','Se calcula la suma antes de mostrarla.'],'La expresión 2 + 3 se evalúa y print muestra 5.'),
    question('po-1','practice','«cantidad = 3» y luego «print(cantidad)». ¿Qué aparece?',['cantidad','3','0'],'3',['print consulta el valor de la variable.','cantidad guarda 3.'],'Se muestra 3, el valor guardado en cantidad, no el nombre de la variable.'),
    question('po-2','practice','¿Qué muestra print("2 + 3")?',['5','23','2 + 3'],'2 + 3',['El contenido está entre comillas.','Las comillas indican texto, no una suma para calcular.'],'Se muestra el texto 2 + 3. Para calcularlo, la expresión no debe estar entre comillas.'),
    question('po-c','check','«puntos = 4» y luego «print(puntos + 2)». ¿Qué aparece?',['4','6','puntos + 2'],'6',['Usa el valor de puntos.','Calcula 4 + 2.'],'Se muestra 6. print evalúa la expresión usando el valor de puntos.')],'python-values')]
 }
];
