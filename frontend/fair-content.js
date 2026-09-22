export const lessons={
 'Matemáticas':{title:'Una fracción es una parte',concept:'Una fracción representa partes iguales de un todo.',example:'Si divides una pizza en cuatro partes iguales y tomas una, tienes 1/4.',question:'Si tomas dos de esas cuatro partes, ¿qué fracción tienes?',options:['2/4','4/2','1/4'],correct:0,feedback:'Dos partes de un total de cuatro son 2/4, lo mismo que la mitad.'},
 'Tecnología':{title:'Tu dirección en una red',concept:'Una dirección IP ayuda a dirigir datos a un dispositivo dentro de una red.',example:'Como la dirección de una casa permite entregar una carta, una IP ayuda a entregar datos.',question:'¿Para qué sirve una dirección IP?',options:['Entregar datos en una red','Medir la batería','Guardar fotos'],correct:0,feedback:'La dirección ayuda a encontrar el destino de los datos.'},
 'Inglés':{title:'Una palabra que abre puertas',concept:'Learn significa aprender. Learning significa aprendizaje o aprendiendo, según la frase.',example:'I am learning English: estoy aprendiendo inglés.',question:'¿Qué significa I learn?',options:['Yo enseño','Yo aprendo','Yo corro'],correct:1,feedback:'I significa yo; learn significa aprender: yo aprendo.'},
 'Programación':{title:'Dale nombre a un valor',concept:'Una variable es un nombre que permite usar un valor en un programa.',example:'En Python: puntos = 10. Luego puntos = puntos + 5 deja puntos en 15.',question:'Si puntos vale 10 y sumas 5, ¿qué valor queda?',options:['5','10','15'],correct:2,feedback:'El nuevo valor es 15. El nombre puntos sigue siendo el mismo.'},
 'IA':{title:'Una IA dentro de tu equipo',concept:'Un modelo de IA usa patrones aprendidos para producir una respuesta. Puede equivocarse.',example:'ALLEN usa un modelo instalado para responder preguntas sin enviar el texto a un servidor externo.',question:'¿Qué haces con un dato importante que te da una IA?',options:['Lo verifico','Siempre lo creo','Lo borro sin leer'],correct:0,feedback:'Comprueba los datos importantes. Aprender también es hacer buenas preguntas.'},
 'Curiosidades':{title:'Un byte, ocho decisiones',concept:'Un bit puede tener dos valores: 0 o 1. Ocho bits forman un byte.',example:'Cada posición duplica las combinaciones: con dos bits hay 00, 01, 10 y 11.',question:'¿Cuántas combinaciones tienen dos bits?',options:['2','4','8'],correct:1,feedback:'Hay cuatro combinaciones. Con ocho bits existen 256.'}
};
export const FAIR_IDLE_MS=120000, FAIR_WARNING_MS=20000, ATTRACT_MS=45000;
export function inactivityDecision(elapsed,warningElapsed,hasVisitor,onHome){
 if(warningElapsed>=FAIR_WARNING_MS)return 'reset';
 if(elapsed>=FAIR_IDLE_MS&&warningElapsed<0&&hasVisitor)return 'warn';
 if(elapsed>=ATTRACT_MS&&!hasVisitor&&onHome)return 'attract';
 return 'stay';
}
