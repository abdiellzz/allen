"""Reproducible original synthetic teaching corpus; not a human-review certificate."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import unicodedata

ROOT=Path(__file__).resolve().parent
TARGETS={'personalidad':200,'matematicas':500,'ciencias':300,'ingles':300,'programacion':300,
         'explicaciones':400,'quizzes':200,'seguridad':200,'orientacion':200,'ia_responsable':200}
FACT_BANKS={'ciencias':'science','ingles':'english','programacion':'programming',
            'explicaciones':'explanations','orientacion':'orientation','ia_responsable':'responsible_ai'}

def slug(text):
    plain=''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c))
    return '-'.join(''.join(c if c.isalnum() else ' ' for c in plain).split())

def load(name,fields):
    rows=[]
    for number,line in enumerate((ROOT/'sources'/f'{name}.tsv').read_text(encoding='utf-8').splitlines(),1):
        if not line.strip() or line.startswith('#'):continue
        parts=line.split('|')
        if len(parts)!=fields or any(not p.strip() for p in parts):
            raise ValueError(f'{name}:{number}: se esperaban {fields} campos no vacíos.')
        rows.append(parts)
    return rows

def messages(*turns):
    return [{'role':'user' if i%2==0 else 'assistant','content':text} for i,text in enumerate(turns)]

def fact_variants(row,area):
    topic,definition,example,question,answer,myth=row
    limits=' Es una opción para explorar, no una carrera que debas elegir obligatoriamente.' if area=='orientacion' else ''
    # Different teaching tasks, including source-grounded transformation and feedback.
    return [
      ('explicar',messages(f'No entiendo el tema «{topic}». ¿Me lo explicas?',f'{definition}{limits}\n\n{example}\n\n{question}')),
      ('ejemplo',messages(f'Dame un ejemplo de {topic.lower()} y ayúdame a entenderlo.',f'{example}\n\nLa idea que muestra es esta: {definition}\n\n{question}')),
      ('corregir_confusion',messages(f'¿Está bien esta idea? {myth}',f'Esa idea necesita una corrección: {definition}\n\n{example}\n\nPuedes comprobarlo con esta pregunta: {question}')),
      ('resumen_apunte',messages(f'Resume este apunte sin añadir datos nuevos:\n{definition}\n{example}',definition.split('. ')[0].rstrip('.')+'.')),
      ('pregunta_sin_solucion',messages(f'Estoy repasando {topic.lower()}. Hazme una pregunta y espera mi intento.',f'{question}\n\nEscribe lo que piensas; después revisamos el razonamiento juntos.')),
      ('respuesta_correcta',messages(f'Practiquemos {topic.lower()} con una pregunta.',question,answer,f'Tu respuesta coincide con la idea que estamos revisando. {definition}\n\nAhora intenta relacionarla con este caso: {example}')),
      ('respuesta_confusa',messages(f'Quiero practicar {topic.lower()}.',question,'No sé; estaba pensando esto: '+myth,f'Gracias por mostrar lo que pensabas. Revisemos esa confusión: {definition}\n\nLa respuesta a la pregunta es: {answer}\n\n{example}')),
      ('tarjeta',messages(f'Crea una tarjeta breve para repasar {topic.lower()}, con pregunta y respuesta separadas.',f'Pregunta: {question}\nRespuesta: {answer}\nRecuerda: {definition}')),
      ('guia',messages(f'Organiza una miniguía de estudio de {topic.lower()}.',f'1. Idea clave: {definition}\n2. Ejemplo: {example}\n3. Comprueba tu comprensión: {question}')),
      ('solucion_tras_intento',messages(f'Ya intenté contestar esta pregunta, pero necesito ver la respuesta explicada: {question}',f'{answer}\n\nLa razón es: {definition}\n\nRelaciona la explicación con este ejemplo: {example}')),
    ]

CONTEXTS=[
 ('fracciones','ver cómo una unidad se divide en partes iguales','Dibuja un rectángulo y divídelo en cuatro partes iguales. Sombrea una. ¿Qué parte del rectángulo quedó sombreada?'),
 ('porcentajes','relacionar una cantidad con cien','Imagina cien casillas y marca diez. Esas diez de cada cien representan 10%. ¿Cuántas casillas marcarías para representar 20%?'),
 ('lectura','identificar la idea principal de un párrafo','Elige un párrafo breve y dime con tus palabras de qué trata. No hace falta copiarlo: empecemos por una sola frase.'),
 ('inglés','practicar una petición amable','Podemos empezar con Can I have some water, please? para pedir agua con cortesía. ¿Qué parte de la frase expresa por favor?'),
 ('Python','distinguir un nombre de variable de su valor','Mira este fragmento como texto: nombre = "Ana". nombre es la variable y "Ana" es el texto asociado. ¿Cuál de los dos va entre comillas?'),
 ('ciencias','hacer una pregunta que podamos investigar','Elijamos algo observable, como cuánto crece una planta. ¿Qué condición cambiarías y cuáles intentarías mantener iguales?'),
 ('historia','ordenar hechos por fecha','Escribe dos acontecimientos de un tema que estés viendo y las fechas que tienes en tus apuntes. ¿Cuál ocurrió primero? Si falta una fecha, la marcamos como pendiente de comprobar.'),
 ('geografía','leer símbolos en un mapa','Empecemos por la leyenda: explica qué significa cada símbolo. Describe uno de los símbolos del mapa y lo interpretamos juntos.'),
 ('programación','ordenar pasos antes de escribir código','Para sumar dos números, piensa en entrada, operación y salida. ¿Qué datos tendría que recibir primero el programa? Por ahora no ejecutaremos código.'),
 ('apuntes','convertir un tema en una pregunta de repaso','Elige una idea de tus apuntes y escribe una pregunta que pueda responderse con ella. Después probamos si la respuesta está clara y es correcta.'),
]

SAFETY_CONTEXTS=[
 ('Tengo 10 años y no sé con quién hablar.','Puedes empezar buscando a una persona adulta que te haga sentir a salvo, como un familiar responsable o alguien de tu escuela.'),
 ('Tengo 15 años y me da vergüenza contarlo.','Sentir vergüenza no significa que debas quedarte sin apoyo. Puedes empezar diciendo: necesito hablar de algo que me preocupa.'),
 ('Tengo 17 años y quiero resolverlo por mi cuenta.','Pedir apoyo no te quita autonomía. Algunas situaciones requieren acompañamiento de una persona de confianza.'),
 ('Estoy en la escuela.','Si estás en la escuela, una persona docente u orientadora de confianza puede ayudarte a buscar apoyo adecuado.'),
 ('Ahora mismo no tengo conexión a Internet.','Si no tienes Internet, intenta pedir ayuda en persona o por un medio disponible. No necesitas seguir conversando conmigo para buscar apoyo.'),
 ('Me preocupa que los demás se rían.','Tu seguridad importa más que demostrar algo ante otras personas. Mereces que te escuchen sin burlas.'),
 ('No sé cómo pedir ayuda.','Una frase posible es: necesito ayuda con una situación que puede ser peligrosa; ¿puedes acompañarme?'),
 ('Quiero que sea un secreto absoluto.','No puedo prometer secreto absoluto ni ayudarte a ocultar un peligro. Es importante buscar apoyo de alguien que pueda ayudarte de verdad.'),
 ('Estoy pensando en hacerlo hoy.','No esperes a terminar esta conversación para buscar apoyo. Si hay un peligro inmediato, pide ayuda urgente local.'),
 ('¿Puedes responder sin juzgarme?','Sí: puedo tratarte con respeto sin dar instrucciones dañinas. Pedir ayuda es una acción que puede protegerte.'),
]

def math_problem(family,i):
    a,b=i+3,2+(i*7)%17
    if family=='suma':
        q=f'¿Cuánto es {a} + {b}?'; answer=a+b; hint=f'Empieza en {a} y avanza {b} unidades.'; steps=f'{a} + {b} = {answer}.'
    elif family=='resta':
        q=f'¿Cuánto es {a+b} − {b}?';answer=a;hint=f'Piensa qué número sumado a {b} da {a+b}.';steps=f'Como {a} + {b} = {a+b}, la diferencia es {a}.'
    elif family=='multiplicacion':
        q=f'¿Cuánto es {a} × {b}?';answer=a*b;hint=f'Descompón {a} en {a-1} + 1 y multiplica cada parte por {b}.';steps=f'{a-1} × {b} = {(a-1)*b}; sumamos {b} y obtenemos {answer}.'
    elif family=='division':
        q=f'Reparte {a*b} fichas en {b} grupos iguales. ¿Cuántas van en cada grupo?';answer=a;hint=f'Busca qué número multiplicado por {b} produce {a*b}.';steps=f'{a*b} ÷ {b} = {a}, porque {a} × {b} = {a*b}.'
    elif family=='fracciones_suma':
        q=f'¿Cuánto es 1/{a} + 1/{a*2}?';answer=Fraction(3,a*2);hint=f'Convierte 1/{a} en una fracción equivalente con denominador {a*2}.';steps=f'1/{a} = 2/{a*2}; al sumar 1/{a*2} obtenemos 3/{a*2}, que simplificado es {answer}.'
    elif family=='fracciones_equivalentes':
        q=f'Simplifica la fracción {a*2}/{a*6}.';answer=Fraction(1,3);hint=f'Numerador y denominador son divisibles entre {a*2}.';steps=f'Divide ambos entre {a*2}: queda 1/3. Dividir ambos por el mismo número no nulo conserva la fracción.'
    elif family=='porcentaje':
        q=f'¿Cuánto es el 20% de {a*10}?';answer=a*2;hint='Un 20% equivale a 20 de cada 100, o una quinta parte.';steps=f'{a*10} × 20 / 100 = {answer}.'
    elif family=='descuento':
        price=a*20;q=f'Un cuaderno cuesta {price} monedas y tiene 25% de descuento. ¿Cuál es el precio final?';answer=a*15;hint='Primero calcula una cuarta parte del precio: ese es el descuento. Después réstalo.';steps=f'25% de {price} es {a*5}. Precio final: {price} − {a*5} = {answer}.'
    elif family=='proporcion':
        q=f'Si {b} lápices cuestan {a*b} monedas y el precio por lápiz es constante, ¿cuánto cuestan {b+2}?';answer=a*(b+2);hint='Calcula primero el precio de un lápiz.';steps=f'{a*b} / {b} = {a} por lápiz. Luego {a} × {b+2} = {answer}.'
    elif family=='ecuacion':
        q=f'Resuelve 2x + {b} = {2*a+b}.';answer=a;hint=f'Resta {b} a los dos lados y luego divide los dos lados entre 2.';steps=f'2x = {2*a}; entonces x = {a}. Comprobación: 2 × {a} + {b} = {2*a+b}.'
    elif family=='algebra':
        q=f'Si x = {a}, calcula 3x + {b}.';answer=3*a+b;hint=f'Sustituye x por {a} y recuerda que 3x significa 3 multiplicado por x.';steps=f'3 × {a} + {b} = {3*a} + {b} = {answer}.'
    elif family=='potencias':
        q=f'¿Cuánto es {a} al cuadrado?';answer=a*a;hint=f'Al cuadrado significa multiplicar {a} por sí mismo, no por 2.';steps=f'{a}² = {a} × {a} = {answer}.'
    elif family=='perimetro':
        q=f'Un rectángulo mide {a} cm por {b} cm. ¿Cuál es su perímetro en cm?';answer=2*(a+b);hint='El perímetro recorre sus cuatro lados; hay dos lados de cada longitud.';steps=f'{a} + {b} + {a} + {b} = 2 × ({a} + {b}) = {answer} cm.'
    elif family=='area_rectangulo':
        q=f'Un rectángulo tiene base {a} cm y altura {b} cm. ¿Cuál es el área en cm²?';answer=a*b;hint='Multiplica la base por la altura y expresa el área en unidades cuadradas.';steps=f'{a} × {b} = {answer} cm². El área mide superficie, no el borde.'
    elif family=='area_triangulo':
        q=f'Un triángulo tiene base {a*2} cm y altura perpendicular {b} cm. Calcula su área en cm².';answer=a*b;hint='Multiplica base por altura perpendicular y divide entre 2.';steps=f'({a*2} × {b}) / 2 = {answer} cm².'
    elif family=='media':
        q=f'Calcula la media de {a}, {a+2} y {a+4}.';answer=a+2;hint='Suma los tres valores y divide el total entre la cantidad de valores.';steps=f'({a} + {a+2} + {a+4}) / 3 = {3*a+6} / 3 = {answer}.'
    elif family=='mediana':
        q=f'Encuentra la mediana de {a+4}, {a} y {a+2}.';answer=a+2;hint='Ordena los tres valores y busca el que queda en el centro.';steps=f'Ordenados: {a}, {a+2}, {a+4}. El valor central es {answer}.'
    elif family=='probabilidad':
        q=f'Una bolsa tiene {a} fichas rojas y {a*2} azules, todas igualmente probables al sacar una. ¿Cuál es la probabilidad de roja?';answer=Fraction(1,3);hint='Divide el número de fichas rojas entre el total de fichas.';steps=f'Hay {a*3} fichas en total. La probabilidad es {a}/{a*3} = 1/3.'
    elif family=='unidades':
        q=f'Convierte {a} metros a centímetros.';answer=a*100;hint='Cada metro equivale a cien centímetros.';steps=f'{a} × 100 = {answer} centímetros.'
    elif family=='enteros':
        q=f'¿Cuánto es −{a+b} + {b}?';answer=-a;hint=f'Parte de −{a+b} y avanza {b} unidades hacia la derecha en la recta numérica.';steps=f'−{a+b} + {b} = −{a}. Sigues a la izquierda de cero.'
    return q,str(answer),hint,steps

def corpus():
    records=[];meta=[]
    def add(area,topic,variant,turns,origin='original_sintetico',group=None):
        record={'messages':turns}
        digest=hashlib.sha256(json.dumps(record,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        records.append(record)
        meta.append({'id':digest[:16],'sha256':digest,'area':area,'topic':topic,'group':group or slug(topic),
                     'variant':variant,'origin':origin,'human_review':'pending'})
    banks={}
    for area,name in FACT_BANKS.items():
        banks[area]=load(name,6)
        for row in banks[area]:
            for variant,turns in fact_variants(row,area):
                # Preserve the user's own seed example verbatim.
                origin='original_sintetico'
                if area=='programacion' and row[0]=='Variables en Python' and variant=='explicar':
                    turns=messages('No entiendo las variables en Python',"Piensa en una variable como una caja con una etiqueta. Por ejemplo, nombre = 'Ana' significa que guardamos el texto Ana dentro de una caja llamada nombre.")
                    origin='ejemplo_aportado_por_usuario'
                add(area,row[0],variant,turns,origin)
    for scenario,response in load('personality',2):
        for subject,goal,step in CONTEXTS:
            turns=messages(f'{scenario} Estoy estudiando {subject}.',response+f' Podemos empezar por {goal}.',f'Sí, ayúdame a {goal}.',step)
            add('personalidad',scenario,'acompanamiento_'+slug(subject),turns,group='personalidad-'+slug(scenario))
    for scenario,response in load('safety',2):
        for context,extra in SAFETY_CONTEXTS:
            add('seguridad',scenario,slug(context),messages(scenario+' '+context,response+'\n\n'+extra),group='seguridad-'+slug(scenario))
    families=['suma','resta','multiplicacion','division','fracciones_suma','fracciones_equivalentes','porcentaje','descuento','proporcion','ecuacion','algebra','potencias','perimetro','area_rectangulo','area_triangulo','media','mediana','probabilidad','unidades','enteros']
    for family in families:
        for i in range(25):
            q,answer,hint,steps=math_problem(family,i)
            variant=i%5
            if variant==0:turns=messages(q,f'Vamos por un paso primero. {hint}\n\n¿Qué resultado obtienes con esa idea?')
            elif variant==1:turns=messages(q,hint,answer,f'Sí, ese resultado es correcto. {steps}\n\n¿Puedes explicar con tus palabras el paso principal?')
            elif variant==2:turns=messages(q,hint,'No sé cómo continuar.',f'Veamos el procedimiento completo: {steps}\n\nAhora vuelve al enunciado y comprueba qué representa el resultado.')
            elif variant==3:turns=messages(q+' Ya hice un intento; muéstrame cómo comprobarlo.',f'{steps}\n\nCompara cada paso con tu intento. Si alguno no coincide, dime cuál y lo revisamos.')
            else:turns=messages(q,hint,'Creo que el resultado es '+str(Fraction(answer)+1)+'.',f'Hay un paso que revisar; no pasa nada. {steps}\n\nEl resultado es {answer}. ¿En qué parte de tu procedimiento pudo aparecer la diferencia?')
            origin='original_sintetico'
            if family=='fracciones_suma' and i==0:
                turns=messages('No entiendo qué es una fracción','Claro 🐵. Imagina que tienes una pizza dividida en 4 partes iguales. Cada parte representa 1/4 de la pizza. Una fracción nos ayuda a representar partes de un todo.')
                origin='ejemplo_aportado_por_usuario'
            if family=='multiplicacion' and i==0:
                turns=messages('¿Cuánto es 18 x 7?','Vamos juntos. Primero calcula 10 × 7. Luego calcula 8 × 7. Después suma ambos resultados. ¿Quieres intentar el primer paso?')
                origin='ejemplo_aportado_por_usuario'
            add('matematicas',family,str(i),turns,origin,group='matematicas-'+family)
    # Quiz tasks reuse concepts, but share group IDs so those concepts never cross splits.
    quiz_rows=banks['ciencias'][:5]+banks['ingles'][:5]+banks['programacion'][:5]+banks['ia_responsable'][:5]
    for row in quiz_rows:
        topic,definition,example,q,answer,myth=row
        cases=[
          ('pregunta',messages(f'Hazme un quiz breve sobre {topic.lower()} sin darme aún la respuesta.',q+'\n\nEspero tu intento antes de corregirlo.')),
          ('intento_correcto',messages(f'Practiquemos {topic.lower()} en formato quiz.',q,answer,'Correcto. '+definition)),
          ('no_lo_se',messages(f'Hazme una pregunta de {topic.lower()}.',q,'No la sé.',f'Usa esta idea para pensarlo: {definition}\n\nVuelve a intentar la pregunta; no hace falta adivinar rápido.')),
          ('confusion',messages(f'Quiero un quiz de {topic.lower()}.',q,myth,f'Esa afirmación es la confusión que conviene revisar. {definition}\n\nPara la pregunta planteada: {answer}')),
          ('verdadero_falso',messages(f'Dame una pregunta de verdadero o falso sobre {topic.lower()}, sin solución todavía.',f'Verdadero o falso: {myth}\n\n¿Puedes justificar tu elección?')),
          ('vf_correcto',messages(f'Quiz de verdadero o falso: {topic.lower()}.',f'Verdadero o falso: {myth}','Falso.',f'Correcto: esa afirmación es falsa. {definition}')),
          ('vf_incorrecto',messages(f'Quiero practicar verdadero o falso sobre {topic.lower()}.',f'Verdadero o falso: {myth}','Verdadero.',f'Revisémoslo con calma: en este caso es falso. {definition}\n\n{example}')),
          ('retroalimentacion',messages(f'En un quiz escribí esto: {myth} ¿Cómo puedo corregirlo?',f'Puedes sustituir esa idea por esta: {definition}\n\nPara comprobar que se entiende: {q}')),
          ('explicar_respuesta',messages(f'Necesito la respuesta explicada de esta pregunta: {q}',f'{answer}\n\n{definition}\n\n{example}')),
          ('crear_con_clave',messages(f'Crea una pregunta de repaso de {topic.lower()} y una clave separada para corregir después.',f'Pregunta: {q}\n\nClave de corrección: {answer}\nExplicación: {definition}')),
        ]
        for variant,turns in cases:add('quizzes',topic,variant,turns)
    actual=Counter(m['area'] for m in meta)
    if actual!=Counter(TARGETS):raise ValueError(f'Distribución inesperada: {actual}')
    if len({m['sha256'] for m in meta})!=len(meta):raise ValueError('Hay conversaciones duplicadas.')
    paired=list(zip(records,meta));random.Random(42).shuffle(paired)
    return [r for r,m in paired],[m for r,m in paired]

def write_dataset(destination):
    records,metadata=corpus()
    destination.mkdir(parents=True,exist_ok=True)
    for name,rows in [('allen_dataset.jsonl',records),('allen_metadata.jsonl',metadata)]:
        (destination/name).write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows),encoding='utf-8')
    return records,metadata

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data')
    args=parser.parse_args()
    if (args.output_dir/'allen_dataset.jsonl').exists():
        parser.error('El dataset ya existe. Usa otra carpeta para comparar una regeneración sin sobrescribir tus revisiones.')
    records,_=write_dataset(args.output_dir)
    print(f'Creados {len(records)} ejemplos sintéticos. Revisión humana: pendiente.')
