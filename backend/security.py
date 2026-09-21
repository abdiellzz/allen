"""Defense in depth, not a certified moderation system."""
import re
import unicodedata

def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))

def safe_reply(text):
    t = normalized(text)
    if re.search(r'(?:(?:quiero|voy a|como|me quiero)\s+(?:suicidar\w*|matarme|hacerme dano|cortarme)|no quiero vivir|kill myself|self.harm)', t):
        return 'Siento que estés pasando por algo tan difícil. Tu seguridad es lo primero. Busca ahora a una persona adulta de confianza y quédate acompañada o acompañado. Si estás en peligro inmediato, pide que contacten a los servicios de emergencia de tu localidad. Podemos hablar de lo que sientes sin instrucciones para hacerte daño.'
    if re.search(r'(?:fabricar|hacer|construir|preparar|crear|build|make).{0,50}(?:bomba|explosivo|veneno|arma casera)|(?:hackear|robar).{0,40}(?:cuenta|contrasena|password)|(?:pornograf|sexo explicito|contenido sexual explicito)|(?:producir|fabricar|consumir).{0,30}(?:cocaina|metanfetamina)|(?:reto|challenge).{0,30}(?:asfixia|desmayo)|(?:torturar|descuartizar)', t):
        return 'No puedo dar instrucciones que puedan hacer daño. Sí podemos aprender sobre prevención, seguridad y cómo pedir ayuda a una persona adulta de confianza. ¿Qué aspecto seguro del tema te gustaría entender?'
    return None
