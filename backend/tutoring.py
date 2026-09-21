"""Exact, bounded arithmetic tutoring; never evaluate user code."""
import re
from fractions import Fraction
from .prompts import normalized

EXPRESSION=re.compile(r'^\s*(?:¿?cu[aá]nto es\s+)?(-?\d{1,4})\s*([x×*+÷/−-])\s*(-?\d{1,4})\s*[=?¿?]*\s*$',re.I)

def arithmetic_reply(request):
    match=EXPRESSION.fullmatch(request.message)
    current=bool(match)
    last_user=None
    controls={'mas facil','otro ejemplo','paso a paso','ponme a prueba','explicalo diferente','no entiendo','estoy perdido','dame la respuesta','¿que aprendi?','just give me the answer'}
    for message in reversed(request.history):
        if message.role!='user': continue
        if EXPRESSION.fullmatch(message.content):
            last_user=message.content;break
        if normalized(message.content).strip().rstrip('.!') not in controls and not re.fullmatch(r'-?\d+(?:/\d+)?',message.content): break

    action=request.action
    text=normalized(request.message).strip().rstrip('.!')
    explicit=text in ('just give me the answer','dame la respuesta','solo dame la respuesta','dime el resultado')
    if not match and last_user and (action or explicit or re.fullmatch(r'-?\d+(?:/\d+)?',text)):
        match=EXPRESSION.fullmatch(last_user)
    if not match and request.action and request.conversation_state and request.conversation_state.active_exercise:
        match=EXPRESSION.fullmatch(request.conversation_state.active_exercise)
    if not match:return None
    a,op,b=int(match[1]),match[2],int(match[3])
    if op in ('÷','/') and b==0:return 'No podemos dividir entre cero. Dividir busca cuántos grupos iguales hay; con grupos de tamaño cero no se obtiene un cociente definido.'
    answer=Fraction(a*b) if op in ('x','×','*') else Fraction(a+b) if op=='+' else Fraction(a-b) if op in ('−','-') else Fraction(a,b)
    expression=f'{a} {op} {b}'
    if not current and re.fullmatch(r'-?\d+(?:/\d+)?',text):
        previous=next((m.content for m in reversed(request.history) if m.role=='assistant'),'')
        questions=re.findall(r'¿Cuánto es (-?\d+) × (-?\d+)\?',previous)
        expected=Fraction(int(questions[-1][0])*int(questions[-1][1])) if questions else answer
        if '/' in text and int(text.split('/')[1])==0:return 'Una fracción no puede tener denominador cero. Escribe tu respuesta con un denominador distinto de cero.'
        if Fraction(text)==expected:return f'¡Muy bien! Ese paso da {expected}. El resultado completo es {expression} = {answer}. Ya podemos unir los pasos.'
        return f'Casi. Para ese paso necesitamos {expected}, no {text}. Revisa los grupos y cuenta cada uno una sola vez. El resultado completo de {expression} es {answer}.'
    if action=='next':
        pending=request.conversation_state.pending_question if request.conversation_state else ''
        previous=re.search(r'(-?\d+) × (-?\d+)',pending)
        first=int(previous[1])+1 if previous else (a%10 or 2)+1
        return f'Sigamos con una pregunta parecida. ¿Cuánto es {first} × {b}? Intenta separar los grupos antes de responder.' if op in ('x','×','*') else f'Prueba ahora: ¿cuánto es {a+1} {op} {b}? Esperaré tu intento.'
    if action in ('hint','explain'):
        pending=request.conversation_state.pending_question if request.conversation_state else ''
        previous=re.search(r'(-?\d+) × (-?\d+)',pending)
        first=int(previous[1]) if previous else (a%10 or a)
        if op in ('x','×','*') and first>1:
            return f'Una pista: separa {first} en {first-1} + 1. Calcula {first-1} × {b}, y después añade otro grupo de {b}. ¿Cuánto es {first} × {b}?'
    if action=='summary_learning':return f'Hoy trabajaste {expression}: separar una operación en pasos y comprobar cada parte. Siguiente paso: intenta una operación parecida y explica por qué funciona.'
    if explicit or action=='reveal_answer':
        if op in ('x','×','*') and 10<a<100:
            tens=a//10*10;rest=a-tens
            return f'El resultado es {answer}.\n\n{a} × {b} = ({tens} × {b}) + ({rest} × {b}) = {tens*b} + {rest*b} = {answer}.'
        return f'El resultado es {answer}.\n\n'+(f'Multiplicar {a} por {b} equivale a sumar {b}, {a} veces.' if op in ('x','×','*') and a>0 else f'Calculamos {expression} = {answer}. '+('Restar quita una cantidad a otra.' if op in ('−','-') else 'Sumar reúne ambas cantidades.' if op=='+' else f'Comprueba que {answer} × {b} = {a}.'))
    if action=='lost':return f'Está bien. Empecemos desde el principio.\n\nMultiplicar significa contar grupos iguales: 2 bolsas con 3 fichas tienen 3 + 3 = 6 fichas. En {expression}, identifica primero los dos números y la operación. ¿Qué parte quieres que veamos juntos?' if op in ('x','×','*') else f'Está bien. Empecemos desde el principio. En {expression}, el símbolo indica qué hacemos con los números. '+('Sumar es juntar.' if op=='+' else 'Restar es quitar.' if op in ('−','-') else 'Dividir es repartir en partes iguales.')+' Probemos primero con cantidades pequeñas.'
    if op in ('x','×','*') and 10<a<100:
        tens=a//10*10;rest=a-tens
        if action=='quiz_me':return f'Una pregunta sobre lo que estamos practicando: para resolver {a} × {b}, ya tenemos {tens} × {b} = {tens*b}. ¿Cuánto es {rest} × {b}? Esperaré tu respuesta.'
        if action in ('dont_understand','simplify','another_example','different'):
            previous=next((m.content for m in reversed(request.history) if m.role=='assistant'),'')
            struggles=sum(m.role=='user' and normalized(m.content) in ('no entiendo','mas facil','estoy perdido') for m in request.history)
            if struggles>=2 and 'Solo una idea' not in previous:
                return f'Solo una idea por ahora: multiplicar cuenta grupos iguales. Dos grupos de {b} tienen {b} + {b} elementos. ¿Cuánto es 2 × {b}? Luego volveremos a {a} × {b}.'
            if 'bolsas de fichas' in previous:
                return f'Imagina un dibujo con {a} filas de {b} puntos. Cubre las últimas {rest} filas: las primeras {tens} tienen {tens*b} puntos. Ahora descubre las filas que faltaban. ¿Cuánto es {rest} × {b}?'
            return f'Probemos con bolsas de fichas: hay {a} bolsas y cada una tiene {b} fichas. Cuenta primero {tens} bolsas: son {tens*b} fichas. Quedan {rest} bolsas.\n\n¿Cuánto es {rest} × {b}? Después juntamos las dos cantidades.'
        return f'Vamos a hacerlo juntos. Separa {a} en {tens} + {rest}.\n\nPrimero: {tens} × {b} = {tens*b}.\n\nAhora intenta: ¿Cuánto es {rest} × {b}?\n\nDespués sumamos ambos resultados.'
    if action=='quiz_me':return f'Practiquemos el tema actual: ¿cómo resolverías {expression}? Explica el primer paso; esperaré tu respuesta.'
    hint='Cuenta grupos iguales; puedes sumar uno de los números repetidamente.' if op in ('x','×','*') else 'Separa las decenas y las unidades, y reúne las cantidades.' if op=='+' else 'Parte del primer número y quita la segunda cantidad.' if op in ('−','-') else 'Busca qué número multiplicado por el divisor da el dividendo.'
    return f'Vamos paso a paso con {expression}. {hint}\n\n¿Qué resultado obtienes al intentarlo?'


def network_intro(request):
    """A vetted starter explanation; other network questions still use llama.cpp."""
    text=normalized(request.message)
    if request.action or not re.search(r'(que es|que significa|explicame|explica).*\bip\b',text): return None
    if any(word in text for word in ('publica','privada','subred','mascara','ipv6')): return None
    return ('Una dirección IP identifica una conexión de un dispositivo dentro de una red. '
            'Es parecida a una dirección postal: ayuda a que la información llegue al lugar correcto.\n\n'
            'Por ejemplo, **192.168.1.10** puede ser la IP privada de una computadora en una red local. '
            'Los cuatro números no representan ciudades, edificios ni calles; para distinguir la parte de red '
            'y la del dispositivo también necesitamos la máscara de subred.\n\n'
            '¿Quieres ver la diferencia entre una IP pública y una privada?')
