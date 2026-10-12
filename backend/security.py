"""Defense in depth, not a certified moderation system."""
import re
import unicodedata

def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))

# First-person self-harm intent as children actually write it (text is casefolded, accents removed).
# Educational questions such as "¿qué es el suicidio?" are not matched.
SELF_HARM = re.compile(r'''
    (?:quiero|quisiera|voy\s+a|como|tengo\s+ganas\s+de|ganas\s+de|pienso\s+en|pensando\s+en|deseo|me\s+gustaria|planeo)
        \s+(?:morir\w*|matarme|suicidar\w*|quitarme\s+la\s+vida|hacerme\s+dano|lastimarme|cortarme)
  | \bme\s+(?:quiero|voy\s+a|dan\s+ganas\s+de|gustaria)\s+(?:matar|morir|suicidar)
  | no\s+quiero\s+(?:vivir(?!\s+(?:en|lejos|cerca|con|junto)\b)|seguir\s+viviendo|seguir\s+viv[oa]|estar\s+viv[oa]|existir)
  | mejor\s+(?:estaria|estuviera)\s+muert[oa]
  | kill\s+myself|self.harm|want\s+to\s+die|end\s+my\s+life
''', re.X)

def safe_reply(text):
    t = normalized(text)
    if SELF_HARM.search(t):
        return 'Siento que estés pasando por algo tan difícil. Tu seguridad es lo primero. Busca ahora a una persona adulta de confianza y quédate acompañada o acompañado. Si estás en peligro inmediato, pide que contacten a los servicios de emergencia de tu localidad. Podemos hablar de lo que sientes sin instrucciones para hacerte daño.'
    if re.search(r'(?:fabricar|hacer|construir|preparar|crear|build|make).{0,50}(?:bomba|explosivo|veneno|arma casera)|(?:hackear|robar).{0,40}(?:cuenta|contrasena|password)|(?:pornograf|sexo explicito|contenido sexual explicito)|(?:producir|fabricar|consumir).{0,30}(?:cocaina|metanfetamina)|(?:reto|challenge).{0,30}(?:asfixia|desmayo)|(?:torturar|descuartizar)', t):
        return 'No puedo dar instrucciones que puedan hacer daño. Sí podemos aprender sobre prevención, seguridad y cómo pedir ayuda a una persona adulta de confianza. ¿Qué aspecto seguro del tema te gustaría entender?'
    return None
