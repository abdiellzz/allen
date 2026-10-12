"""Deterministic correction and locally generated exercises. Never eval code."""
import random
import re
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


# Allen Offline v2: broader reviewed educational practice banks.
BANK['Redes']={
 'IPv4 y CIDR':[
  ('¿Qué identifica una dirección IPv4 dentro de una red?','un dispositivo o interfaz',['una contraseña','un archivo','una impresora únicamente'],'Una dirección IPv4 identifica una interfaz dentro de una red IP.'),
  ('¿Qué prefijo deja 8 bits para hosts?','/24',['/16','/30','/32'],'En IPv4 hay 32 bits; /24 deja 8 bits para la parte de host.'),
  ('¿Qué dirección representa normalmente la red en 192.168.1.0/24?','192.168.1.0',['192.168.1.1','192.168.1.255','192.168.0.1'],'La primera dirección del bloque representa la dirección de red.'),
  ('¿Cuántas subredes iguales produce tomar 2 bits adicionales?','4',['2','6','8'],'Dos bits permiten 2² = 4 combinaciones, por lo que se obtienen cuatro subredes.')
 ],
 'DNS y DHCP':[
  ('¿Qué servicio traduce nombres como ejemplo.com a direcciones IP?','DNS',['DHCP','HTTP','NTP'],'DNS resuelve nombres de dominio a direcciones y otros registros.'),
  ('¿Qué servicio puede asignar automáticamente una dirección IP a un equipo?','DHCP',['DNS','HTTPS','SSH'],'DHCP entrega parámetros de red automáticamente dentro de una red administrada.'),
  ('¿Cuál es una ventaja de DHCP en una red de usuarios?','reduce configuración manual',['cifra todos los archivos','duplica el ancho de banda','elimina routers'],'DHCP evita configurar manualmente cada dirección en muchos equipos.')
 ],
 'Protocolos y puertos':[
  ('¿Qué protocolo de transporte establece una conexión antes de intercambiar datos?','TCP',['UDP','DNS','ARP'],'TCP establece una sesión y ofrece entrega ordenada.'),
  ('¿Qué protocolo de transporte prioriza baja sobrecarga sin establecer conexión?','UDP',['TCP','HTTPS','SMTP'],'UDP envía datagramas sin una sesión de transporte previa.'),
  ('¿Qué protocolo web cifra normalmente el tráfico entre navegador y sitio?','HTTPS',['HTTP sin TLS','FTP','DHCP'],'HTTPS combina HTTP con TLS para proteger el tráfico en tránsito.')
 ],
 'Dispositivos de red':[
  ('¿Qué dispositivo conecta normalmente redes distintas?','router',['switch','teclado','monitor'],'Un router reenvía paquetes entre redes diferentes.'),
  ('¿Qué dispositivo conecta equipos dentro de una LAN usando direcciones MAC?','switch',['router doméstico únicamente','impresora','modem analógico'],'Un switch Ethernet reenvía tramas dentro de la red local.')
 ]
}
BANK['Ciberseguridad']={
 'Contraseñas y MFA':[
  ('¿Cuál es una buena práctica para contraseñas?','usar una frase larga y única',['reutilizar la misma','compartirla por chat','hacerla muy corta'],'Una contraseña larga y única reduce el impacto de filtraciones y adivinación.'),
  ('¿Qué aporta MFA?','otra comprobación de identidad',['más velocidad de Internet','copias automáticas','más almacenamiento'],'MFA añade un factor adicional además de la contraseña.'),
  ('¿Qué conviene hacer si sospechas que una contraseña fue expuesta?','cambiarla y revisar accesos',['publicarla para comparar','desactivar MFA','ignorar el aviso'],'Cambiarla y revisar actividad ayuda a recuperar control de la cuenta.')
 ],
 'Phishing y privacidad':[
  ('¿Qué señal puede indicar phishing?','urgencia inesperada y enlace extraño',['un saludo normal','un documento propio','una fecha conocida'],'Los atacantes suelen usar urgencia y enlaces que imitan sitios legítimos.'),
  ('¿Qué es más seguro ante un mensaje inesperado que pide iniciar sesión?','abrir el sitio por una ruta conocida',['usar el enlace del mensaje sin revisar','enviar la contraseña por correo','desactivar alertas'],'Entrar desde un marcador o dirección conocida reduce el riesgo de páginas falsas.'),
  ('¿Qué dato conviene compartir solo cuando sea necesario?','información personal sensible',['una definición escolar','el nombre de un planeta','una operación matemática'],'Minimizar datos compartidos reduce exposición innecesaria.')
 ],
 'Backups y actualizaciones':[
  ('¿Para qué sirve una copia de seguridad?','recuperar datos ante pérdida o daño',['acelerar el procesador','aumentar la RAM','reemplazar contraseñas'],'Un backup permite restaurar información cuando el original falla o se pierde.'),
  ('¿Por qué conviene instalar actualizaciones de seguridad?','corrigen vulnerabilidades conocidas',['eliminan la necesidad de contraseñas','hacen infalible el equipo','evitan todo malware'],'Las actualizaciones corrigen fallos y vulnerabilidades conocidas.'),
  ('¿Qué hace que un backup sea realmente útil?','poder restaurarlo correctamente',['tener solo el nombre del archivo','guardarlo siempre en la misma carpeta','nunca comprobarlo'],'Una copia debe poder restaurarse cuando haga falta.')
 ],
 'Mínimo privilegio':[
  ('¿Qué significa mínimo privilegio?','dar solo los permisos necesarios',['dar permisos de administrador a todos','compartir cuentas','desactivar controles'],'Cada persona o proceso recibe únicamente los permisos que necesita.'),
  ('¿Por qué separar cuentas administrativas de cuentas normales?','reduce exposición de privilegios',['duplica archivos','mejora resolución de pantalla','evita usar contraseñas'],'Usar privilegios elevados solo cuando se necesitan reduce el impacto de errores o abuso.')
 ]
}
BANK['IA']={
 'Modelos y tokens':[
  ('¿Qué es un modelo de IA en términos simples?','un sistema que usa patrones aprendidos',['una base de datos infalible','un navegador web','un antivirus necesariamente'],'Un modelo aprende patrones de datos y los usa para producir predicciones o respuestas.'),
  ('¿Qué es un token en un modelo de lenguaje?','una unidad de texto',['una contraseña','una imagen completa','un servidor'],'Los modelos dividen el texto en unidades llamadas tokens.'),
  ('¿Puede un modelo de lenguaje equivocarse?','sí',['no','solo sin Internet','solo si usa imágenes'],'Los modelos pueden producir respuestas incorrectas o inventadas.')
 ],
 'Entrenamiento e inferencia':[
  ('¿Qué ocurre durante entrenamiento?','se ajustan parámetros usando datos',['se abre una página web','se instala un teclado','se borra la memoria RAM'],'Durante el entrenamiento se ajustan parámetros para aprender patrones.'),
  ('¿Qué ocurre durante inferencia?','se usa el modelo para generar una salida',['se cambia el sistema operativo','se compran datos','se fabrica hardware'],'Inferencia es ejecutar un modelo ya entrenado con una entrada.'),
  ('¿Entrenamiento e inferencia son lo mismo?','no',['sí','solo en modelos locales','solo en texto'],'Son fases distintas: aprender parámetros y usar el modelo.')
 ],
 'RAG y modelos locales':[
  ('¿Qué busca hacer RAG?','aportar información recuperada al modelo',['cambiar el teclado','duplicar el modelo','ocultar la pregunta'],'RAG recupera contenido relevante y lo incorpora al contexto de la generación.'),
  ('¿Qué ventaja puede tener un modelo local?','procesar contenido en el propio equipo',['garantizar precisión total','no requerir electricidad','saber todo sin datos'],'Un modelo local puede reducir el envío de contenido a servicios externos.'),
  ('¿Un modelo local elimina la necesidad de verificar información?','no',['sí','solo en matemáticas','solo si está offline'],'La verificación sigue siendo necesaria cuando la exactitud importa.')
 ],
 'Sesgo y alucinaciones':[
  ('¿Qué es una alucinación de IA?','una respuesta inventada que parece plausible',['un fallo de pantalla','un virus','una copia de seguridad'],'Un modelo puede producir información falsa con apariencia convincente.'),
  ('¿Qué ayuda a reducir el impacto de una alucinación?','verificar con fuentes confiables',['copiar sin leer','repetir la pregunta muchas veces solamente','ocultar la respuesta'],'Contrastar información importante reduce el riesgo de aceptar errores.'),
  ('¿Qué es un sesgo en un sistema de IA?','una tendencia sistemática en resultados',['un puerto de red','un tipo de archivo','un navegador'],'Los datos y decisiones de diseño pueden producir patrones de resultados desiguales o parciales.')
 ]
}
BANK['Estudio']={
 'Recuperación activa':[
  ('¿Qué es active recall?','intentar recordar sin mirar la respuesta',['releer de forma pasiva','copiar el texto entero','subrayar todo'],'Recuperar la información desde la memoria fortalece el aprendizaje.'),
  ('¿Qué pregunta favorece active recall?','¿puedo explicarlo sin mirar?',['¿cuántas veces lo releí?','¿qué color tiene la página?','¿cuánto ocupa el archivo?'],'Explicar sin consultar obliga a recuperar la idea desde la memoria.')
 ],
 'Repetición espaciada':[
  ('¿Qué propone la repetición espaciada?','repasar en intervalos separados',['estudiar todo una sola vez','repetir cada minuto para siempre','no volver a practicar'],'Distribuir repasos ayuda a reforzar recuerdos a largo plazo.'),
  ('¿Qué conviene hacer con una tarjeta difícil?','revisarla antes que una muy fácil',['eliminarla siempre','marcarla como aprendida sin verla','ignorarla'],'Una tarjeta difícil necesita un intervalo de repaso más corto.')
 ]
}
BANK['Pensamiento crítico']={
 'Fuentes y evidencia':[
  ('¿Qué conviene revisar ante una afirmación importante?','la evidencia y la fuente',['solo los likes','solo el título','solo quién la compartió'],'La calidad de la evidencia y de la fuente importa más que la popularidad.'),
  ('¿Una afirmación repetida muchas veces se vuelve verdadera?','no',['sí','solo en redes sociales','solo si es corta'],'La repetición no sustituye evidencia verificable.'),
  ('¿Qué fortalece una conclusión?','evidencia consistente de varias fuentes',['una sola opinión anónima','un rumor','un titular sin contenido'],'Varias fuentes confiables y coherentes aumentan la solidez de una conclusión.')
 ],
 'Correlación y causalidad':[
  ('¿Correlación demuestra automáticamente causalidad?','no',['sí','solo con dos variables','solo en gráficos'],'Dos variables pueden moverse juntas por otras razones; hace falta más evidencia para establecer causa.'),
  ('¿Qué pregunta ayuda a evaluar causalidad?','¿hay otras variables que expliquen el resultado?',['¿el gráfico usa colores bonitos?','¿la noticia tiene muchos comentarios?','¿el texto es corto?'],'Buscar variables de confusión ayuda a evaluar explicaciones alternativas.')
 ]
}
BANK['Inglés']['Present simple']=[
 ('Complete: She ___ Python every day.','studies',['study','studied','studying'],'Con he/she/it, muchos verbos añaden -s o cambian a -ies.'),
 ('Which sentence describes a routine?','I study every morning.',['I studied yesterday.','I will study tomorrow.','I am a book.'],'El present simple se usa para rutinas y hechos habituales.'),
 ('Choose the negative form: He works here.','He does not work here.',['He not works here.','He did not work here.','He no work here.'],'Con he/she/it se usa does not + verbo base.')
]
BANK['Inglés']['Past simple']=[
 ('Complete: Yesterday I ___ a lesson.','studied',['study','studies','studying'],'Studied es el pasado regular de study.'),
 ('Which sentence is in the past?','I learned Python last year.',['I learn Python every day.','I am learning now.','I will learn tomorrow.'],'Last year sitúa la acción en el pasado.'),
 ('What is the past of go?','went',['goed','goes','going'],'Go es irregular: go → went.')
]
BANK['Programación']['Estructuras y datos']=[
 ('¿Qué estructura guarda varios elementos en orden en Python?','list',['bool','float','if'],'Una lista almacena una secuencia de elementos.'),
 ('¿Qué estructura guarda pares clave-valor?','dict',['str','while','return'],'Un diccionario relaciona claves con valores.'),
 ('¿Qué palabra se usa para manejar una excepción en Python?','try',['loop','case','echo'],'try inicia un bloque donde una excepción puede manejarse con except.')
]
BANK['Programación']['APIs y JSON']=[
 ('¿Qué formato usa pares clave-valor y es común en APIs web?','JSON',['PNG','MP3','EXE'],'JSON representa datos estructurados mediante objetos, listas y valores.'),
 ('¿Qué hace una API en términos generales?','define una forma de comunicación entre sistemas',['aumenta la RAM','repara hardware','cifra todos los archivos'],'Una API define operaciones y datos que otro software puede utilizar.'),
 ('¿Qué método HTTP suele usarse para consultar un recurso?','GET',['POST siempre','DELETE siempre','PATCH siempre'],'GET se usa habitualmente para solicitar una representación de un recurso.')
]

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

# Plain integers, decimals or a/b fractions only: Fraction('1e10000000') would take seconds of CPU.
NUMBER=re.compile(r'\s*[+-]?\d{1,12}(?:[.,]\d{1,12})?(?:\s*/\s*[+-]?\d{1,12})?\s*')

def equivalent(given, expected):
    if NUMBER.fullmatch(given) and NUMBER.fullmatch(expected):
        try:
            return Fraction(given.replace(',','.').replace(' ','')) == Fraction(expected.replace(' ',''))
        except (ValueError, ZeroDivisionError):
            pass
    return normalized(given.strip().rstrip('.'))==normalized(expected.strip().rstrip('.'))

def grade(questions, answers):
    if len(questions)!=len(answers):
        raise ValueError('Responde todas las preguntas antes de terminar.')
    feedback=[dict(**q,given=a,correct=equivalent(a,q['answer'])) for q,a in zip(questions,answers)]
    good={f['topic'] for f in feedback if f['correct']}
    review={f['topic'] for f in feedback if not f['correct']}
    return dict(score=sum(f['correct'] for f in feedback),total=len(feedback),feedback=feedback, mastered=sorted(good-review),review=sorted(review))
