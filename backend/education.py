"""Deterministic correction and locally generated exercises. Never eval code."""
import random
from fractions import Fraction
from .security import normalized

MATH_TOPICS = ['Operaciones básicas','Fracciones','Porcentajes','Regla de tres','Ecuaciones','Álgebra','Geometría','Estadística']
BANK = {
 'Ciencias': {'Sistema Solar':[
  ('¿Qué planeta es conocido como el planeta rojo?','Marte',['Venus','Júpiter','Neptuno'],'El óxido de hierro de su superficie le da su color rojizo.'),
  ('¿Cuál es la estrella del Sistema Solar?','Sol',['Luna','Tierra','Marte'],'El Sol es una estrella; los planetas orbitan a su alrededor.'),
  ('¿Cuántos planetas tiene el Sistema Solar?','8',['7','9','10'],'Son ocho. Plutón se clasifica como planeta enano.'),
  ('¿Cuál es el planeta más grande?','Júpiter',['Mercurio','Marte','Tierra'],'Júpiter es el mayor planeta del Sistema Solar.'),
  ('¿Cuál es el satélite natural de la Tierra?','Luna',['Sol','Venus','Saturno'],'La Luna orbita la Tierra.') ]},
 'Inglés': {'Vocabulario':[
  ('¿Cómo se dice libro en inglés?','book',['table','apple','chair'],'Book significa libro. I read a book: leo un libro.'),
  ('¿Cómo se dice agua en inglés?','water',['milk','bread','food'],'Water significa agua. A glass of water: un vaso de agua.'),
  ('¿Cómo se dice gracias en inglés?','thank you',['hello','goodbye','please'],'Thank you expresa agradecimiento.'),
  ('¿Cómo se dice escuela en inglés?','school',['house','park','shop'],'School significa escuela.'),
  ('¿Cómo se dice aprender en inglés?','learn',['teach','read','write'],'Learn es aprender; teach es enseñar.') ]},
 'Programación': {'Python y lógica':[
  ('¿Qué función muestra texto en Python?','print',['input','len','range'],'print muestra datos en la salida.'),
  ('¿Qué estructura repite instrucciones mientras una condición se cumple?','while',['if','return','import'],'while repite su bloque mientras la condición sea verdadera.'),
  ('¿Qué función obtiene una entrada de texto?','input',['print','int','sum'],'input devuelve el texto escrito por el usuario.'),
  ('¿Qué tipo representa verdadero o falso?','bool',['str','list','float'],'bool representa valores lógicos: True o False.'),
  ('¿Qué palabra inicia una función en Python?','def',['class','for','try'],'def define una función reutilizable.') ]},
 'Español': {'Lengua':[
  ('¿Qué clase de palabra expresa una acción?','verbo',['sustantivo','adjetivo','artículo'],'Correr y aprender son verbos.'),
  ('¿Qué signo abre una pregunta en español?','¿',['?','¡','!'],'Las preguntas llevan signo de apertura y de cierre.'),
  ('¿Cuál es el plural de lápiz?','lápices',['lápizs','lápizes','lápiz'],'Las palabras terminadas en z suelen cambiar z por c al formar el plural.') ]},
 'Tecnología': {'Privacidad e IA':[
  ('¿Qué tipo de IA procesa datos en tu dispositivo?','local',['remota','pública','social'],'La IA local puede funcionar sin enviar datos a servidores externos.'),
  ('¿Cómo se llama una respuesta inventada de una IA?','alucinación',['compresión','conexión','actualización'],'Un modelo puede producir información falsa que parece convincente.'),
  ('¿Qué conviene hacer con una afirmación importante de una IA?','verificarla',['copiarla siempre','ignorar fuentes','publicarla sin leer'],'Contrasta afirmaciones con fuentes y docentes.') ]},
 'Historia': {'Fuentes históricas':[
  ('¿Qué fuente se creó en la época del hecho estudiado?','primaria',['secundaria','ficticia','futura'],'Una carta de la época es un ejemplo de fuente primaria.'),
  ('¿Qué orden organiza acontecimientos por fecha?','cronológico',['alfabético','aleatorio','temático'],'La cronología ayuda a ubicar los hechos en el tiempo.') ]},
 'Geografía': {'Nuestro planeta':[
  ('¿Qué línea divide la Tierra en hemisferios norte y sur?','ecuador',['meridiano cero','trópico','círculo polar'],'El ecuador corresponde a la latitud 0°.'),
  ('¿Qué océano está al sur de Panamá?','Pacífico',['Ártico','Índico','Antártico'],'Panamá limita al sur con el océano Pacífico.') ]}
}

# Additional reviewed local practice questions.
BANK['Ciencias'][next(iter(BANK['Ciencias']))].extend([('¿Qué planeta está más cerca del Sol?', 'Mercurio', ['Venus', 'Tierra', 'Marte'], 'Mercurio ocupa la órbita más cercana al Sol.'), ('¿Qué planeta tiene anillos muy visibles?', 'Saturno', ['Tierra', 'Marte', 'Mercurio'], 'Saturno destaca por sus anillos de hielo y roca.'), ('¿Qué movimiento produce el día y la noche?', 'rotación', ['traslación', 'evaporación', 'erosión'], 'La Tierra gira sobre su eje.'), ('¿Qué fuerza mantiene los planetas en órbita?', 'gravedad', ['fricción', 'magnetismo', 'elasticidad'], 'La gravedad atrae los cuerpos con masa.'), ('¿Qué planeta habitamos?', 'Tierra', ['Venus', 'Urano', 'Neptuno'], 'La Tierra es el tercer planeta desde el Sol.')])
BANK['Inglés'][next(iter(BANK['Inglés']))].extend([('¿Cómo se dice rojo en inglés?', 'red', ['blue', 'green', 'yellow'], 'Red significa rojo.'), ('¿Cómo se dice gato en inglés?', 'cat', ['dog', 'bird', 'fish'], 'Cat significa gato.'), ('¿Cómo se dice hola en inglés?', 'hello', ['goodbye', 'thanks', 'sorry'], 'Hello es un saludo.'), ('¿Cómo se dice tres en inglés?', 'three', ['two', 'four', 'five'], 'Three corresponde al número tres.'), ('¿Cómo se dice escribir en inglés?', 'write', ['read', 'run', 'sleep'], 'Write significa escribir.')])
BANK['Programación'][next(iter(BANK['Programación']))].extend([('¿Qué símbolo inicia un comentario en Python?', '#', ['//', '@', '$'], 'Un comentario de una línea comienza con #.'), ('¿Qué función calcula la longitud de una lista?', 'len', ['print', 'input', 'str'], 'len devuelve la cantidad de elementos.'), ('¿Qué palabra inicia una condición en Python?', 'if', ['def', 'import', 'return'], 'if ejecuta un bloque si se cumple una condición.'), ('¿Qué tipo representa una cadena de texto?', 'str', ['int', 'bool', 'float'], 'str representa texto.'), ('¿Qué operador comprueba igualdad en Python?', '==', ['=', '!=', '**'], '== compara; = asigna un valor.')])
BANK['Español'][next(iter(BANK['Español']))].extend([('¿Qué palabra nombra personas o cosas?', 'sustantivo', ['verbo', 'adverbio', 'preposición'], 'Casa y estudiante son sustantivos.'), ('¿Qué palabra describe al sustantivo?', 'adjetivo', ['verbo', 'artículo', 'pronombre'], 'En casa grande, grande describe la casa.'), ('¿Cuál es el antónimo de alto?', 'bajo', ['grande', 'largo', 'ancho'], 'Alto y bajo expresan sentidos opuestos.'), ('¿Cuál es un sinónimo de feliz?', 'contento', ['triste', 'enojado', 'cansado'], 'Feliz y contento tienen significados cercanos.'), ('¿Qué signo termina normalmente una oración?', 'punto', ['coma', 'guion', 'tilde'], 'El punto marca el final de una oración.'), ('¿Cuál de estas palabras lleva tilde?', 'canción', ['casa', 'mesa', 'libro'], 'Canción es aguda y termina en n.'), ('¿Cuál es el singular de árboles?', 'árbol', ['árbola', 'árboles', 'arboleda'], 'Árbol nombra un solo ejemplar.')])
BANK['Tecnología'][next(iter(BANK['Tecnología']))].extend([('¿Qué protege el acceso a una cuenta?', 'contraseña', ['fondo de pantalla', 'volumen', 'brillo'], 'Una contraseña ayuda a impedir accesos sin permiso.'), ('¿Qué dato conviene mantener privado?', 'dirección de casa', ['color favorito', 'nombre de un planeta', 'tabla del dos'], 'La dirección permite localizarte.'), ('¿Qué es una copia de seguridad?', 'duplicado de datos', ['borrado de datos', 'virus', 'pantalla'], 'Permite recuperar archivos si se pierde el original.'), ('¿Qué dispositivo permite escribir?', 'teclado', ['monitor', 'altavoz', 'impresora'], 'El teclado es un dispositivo de entrada.'), ('¿Qué debes hacer antes de abrir un enlace desconocido?', 'comprobar su origen', ['dar tu clave', 'descargar todo', 'ignorar su dirección'], 'Revisar el origen ayuda a detectar engaños.'), ('¿Qué significa usar una aplicación offline?', 'sin Internet', ['sin electricidad', 'sin pantalla', 'sin archivos'], 'Offline indica que no necesita una conexión a Internet para esa función.'), ('¿Quién debe revisar una tarea creada con IA?', 'el estudiante', ['nadie', 'solo la impresora', 'el teclado'], 'La persona que usa la IA debe revisar y comprender el resultado.')])
BANK['Historia'][next(iter(BANK['Historia']))].extend([('¿Qué representa una línea del tiempo?', 'secuencia de hechos', ['mapa de calles', 'lista de colores', 'operación matemática'], 'Ordena acontecimientos según sus fechas.'), ('¿Cuántos años tiene un siglo?', '100', ['10', '50', '1000'], 'Un siglo equivale a cien años.'), ('¿Cuántos años tiene una década?', '10', ['100', '5', '1000'], 'Una década equivale a diez años.'), ('¿Cuál puede ser una fuente oral?', 'entrevista', ['moneda', 'edificio', 'cerámica'], 'Una entrevista recoge un testimonio hablado.'), ('¿Qué estudia la arqueología mediante restos materiales?', 'sociedades del pasado', ['órbitas planetarias', 'ecuaciones', 'clima futuro'], 'Los objetos y construcciones aportan pistas sobre el pasado.'), ('¿Cuál es un ejemplo de fuente escrita?', 'carta', ['vasija', 'herramienta', 'hueso'], 'Una carta conserva información mediante escritura.'), ('¿Qué ayuda a contrastar un relato histórico?', 'comparar fuentes', ['ignorar fechas', 'inventar detalles', 'leer solo un título'], 'Varias fuentes permiten encontrar coincidencias y diferencias.'), ('¿Qué es una fuente secundaria?', 'análisis posterior', ['testimonio directo de la época', 'objeto original', 'diario del protagonista'], 'Una fuente secundaria interpreta otras fuentes después de los hechos.')])
BANK['Geografía'][next(iter(BANK['Geografía']))].extend([('¿Qué instrumento indica los puntos cardinales?', 'brújula', ['termómetro', 'reloj', 'balanza'], 'La brújula orienta mediante el campo magnético terrestre.'), ('¿Qué punto cardinal indica la salida aproximada del Sol?', 'este', ['oeste', 'norte', 'sur'], 'El Sol sale aproximadamente por el este.'), ('¿Qué es una isla?', 'tierra rodeada de agua', ['agua rodeada de tierra', 'cordillera', 'desierto'], 'Una isla tiene agua a su alrededor.'), ('¿Qué representa un mapa?', 'un territorio', ['una melodía', 'una receta', 'una emoción'], 'Un mapa representa una superficie a escala.'), ('¿Qué es una cordillera?', 'conjunto de montañas', ['grupo de islas', 'río pequeño', 'llanura'], 'Una cordillera es una cadena de montañas.'), ('¿Qué es la desembocadura de un río?', 'lugar donde termina', ['lugar donde nace', 'su parte más alta', 'una nube'], 'Allí el río vierte sus aguas en otro río, lago o mar.'), ('¿Qué mide la latitud?', 'distancia angular al ecuador', ['profundidad del mar', 'temperatura', 'altura de árboles'], 'La latitud se expresa en grados al norte o al sur del ecuador.'), ('¿Qué muestra la leyenda de un mapa?', 'significado de símbolos', ['hora exacta', 'peso del papel', 'autor de un cuento'], 'La leyenda permite interpretar colores y símbolos.')])

def catalog():
    return {'Matemáticas':MATH_TOPICS, **{s:list(topics) for s,topics in BANK.items()}}

def math_question(topic, difficulty):
    cap={'Fácil':10,'Normal':30,'Difícil':100}[difficulty]
    a,b=random.randint(2,cap),random.randint(2,cap)
    if topic=='Fracciones':
        answer=Fraction(1,a)+Fraction(1,b)
        prompt=f'1/{a} + 1/{b} = ?'
        explanation=f'Usa denominador {a*b}: {b}/{a*b} + {a}/{a*b} = {a+b}/{a*b}. Simplifica: {answer}.'
    elif topic=='Porcentajes':
        p=random.choice([10,20,25,50]); base=a*20
        prompt=f'¿Cuánto es el {p}% de {base}?'; answer=Fraction(p*base,100)
        explanation=f'Divide {base} entre 100 y multiplica por {p}: {answer}.'
    elif topic=='Regla de tres':
        prompt=f'Si {a} cuadernos cuestan {a*b} monedas, ¿cuánto cuestan {a+2}?'; answer=Fraction((a+2)*b)
        explanation=f'Cada cuaderno cuesta {a*b} ÷ {a} = {b}. Multiplica {b} × {a+2} = {answer}.'
    elif topic=='Ecuaciones':
        prompt=f'Resuelve x + {a} = {a+b}. ¿Cuánto vale x?'; answer=Fraction(b)
        explanation=f'Resta {a} a ambos lados: x = {a+b} − {a} = {b}.'
    elif topic=='Álgebra':
        prompt=f'Si x = {a}, ¿cuánto es 2x + {b}?'; answer=Fraction(2*a+b)
        explanation=f'Sustituye x por {a}: 2 × {a} + {b} = {answer}.'
    elif topic=='Geometría':
        prompt=f'Un rectángulo mide {a} cm por {b} cm. ¿Cuál es su área en cm²?'; answer=Fraction(a*b)
        explanation=f'Área = base × altura = {a} × {b} = {answer} cm².'
    elif topic=='Estadística':
        prompt=f'¿Cuál es la media de {a}, {b} y {a+b}?'; answer=Fraction(2*(a+b),3)
        explanation=f'Suma los tres valores y divide entre 3: {2*(a+b)}/3 = {answer}. Puedes escribir una fracción.'
    else:
        operation=random.choice(['+','−','×','÷'])
        if operation=='+':
            prompt=f'{a} + {b} = ?'; answer=Fraction(a+b)
            explanation=f'Parte de {a} y avanza {b} unidades en la recta numérica: llegas a {answer}.'
        elif operation=='−':
            prompt=f'{a+b} − {a} = ?'; answer=Fraction(b)
            explanation=f'Busca qué número sumado a {a} da {a+b}. Como {a} + {b} = {a+b}, la diferencia es {b}.'
        elif operation=='÷':
            prompt=f'{a*b} ÷ {a} = ?'; answer=Fraction(b)
            explanation=f'Reparte {a*b} en {a} grupos iguales. Cada grupo recibe {b}, porque {a} × {b} = {a*b}.'
        else:
            prompt=f'{a} × {b} = ?'; answer=Fraction(a*b)
            explanation=f'Descompón {a} en {a-1} + 1. Calcula {a-1} × {b} = {(a-1)*b}, luego suma {b}: {answer}.'
    wrong=[str(answer+v) for v in (-2,1,3)]
    return prompt,str(answer),wrong,explanation

def generate(config):
    if config.subject not in catalog() or config.topic not in catalog()[config.subject]:
        raise ValueError('Elige uno de los temas disponibles en el banco local.')
    if config.subject=='Matemáticas':
        pool=[]
        while len(pool)<config.count:
            candidate=math_question(config.topic,config.difficulty)
            if candidate[0] not in {q[0] for q in pool}: pool.append(candidate)
    else:
        pool=list(BANK[config.subject][config.topic]); random.shuffle(pool)
        pool=pool[:config.count]
    questions=[]
    for prompt,answer,wrong,explanation in pool:
        options=[answer,*wrong]; random.shuffle(options)
        if config.kind=='boolean':
            candidate=random.choice([answer,wrong[0]])
            prompt+=f' La respuesta es «{candidate}». ¿Verdadero o falso?'
            answer='Verdadero' if candidate==answer else 'Falso'
            options=['Verdadero','Falso']
        elif config.kind=='short':
            options=[]
        questions.append(dict(prompt=prompt,answer=answer,options=options,explanation=explanation,topic=config.topic))
    return questions

def equivalent(given, expected):
    try:
        return Fraction(given.replace(',','.')) == Fraction(expected)
    except (ValueError, ZeroDivisionError):
        return normalized(given.strip().rstrip('.'))==normalized(expected.strip().rstrip('.'))

def grade(questions, answers):
    if len(questions)!=len(answers):
        raise ValueError('Responde todas las preguntas antes de terminar.')
    feedback=[dict(**q,given=a,correct=equivalent(a,q['answer'])) for q,a in zip(questions,answers)]
    good={f['topic'] for f in feedback if f['correct']}
    review={f['topic'] for f in feedback if not f['correct']}
    return dict(score=sum(f['correct'] for f in feedback),total=len(feedback),feedback=feedback, mastered=sorted(good-review),review=sorted(review))
