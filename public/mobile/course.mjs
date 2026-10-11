import {addReinforcement} from './reinforcement.mjs';
import {variantsFor} from './variants.mjs';
import {extendCourses} from './course-extensions.mjs';
import {scenarioCourses} from './scenario-courses.mjs';
import {extraCourses} from './extra-courses.mjs';
// Bundled editorial content. No model-generated questions or executable imports.
// Source: data/library/math/fracciones.md; expanded worked examples checked by tests.
export const course = {
  id: 'fractions-v1', version: 1, title: 'Fracciones, paso a paso', subject: 'Matemáticas',
  source: 'Biblioteca ALLEN · Fracciones · contenido inicial revisable',
  topics: [
    {
      id: 'parts', title: 'Partes de un entero', prerequisite: null,
      objective: 'Representar partes iguales de un entero con una fracción.',
      explanation: 'Una fracción expresa cuántas partes iguales tomas de un entero. El denominador indica en cuántas partes iguales se divide. El numerador indica cuántas tomas.',
      simple: 'Divide una pizza en 4 partes iguales. Si tomas 1, tienes 1/4. Abajo va el total de partes; arriba, las que tomas.',
      example: 'Una barra tiene 8 partes iguales. Comes 3. La fracción que comiste es 3/8: numerador 3, denominador 8.',
      alternative: 'Un dibujo tiene 6 regiones del mismo tamaño. Coloreas 2: has coloreado 2/6 del dibujo.',
      visual: {total: 8, selected: 3},
      card: {front: '¿Qué indica el denominador?', back: 'El número de partes iguales en que se divide un entero.'},
      questions: [
        {id:'p-d1',kind:'diagnostic',prompt:'Una pizza tiene 4 partes iguales y tomas 1. ¿Qué fracción tomaste?', options:['1/4','4/1','1/3'],answer:'1/4',hints:['El total de partes va abajo.','Tomaste 1 de 4 partes.'],feedback:'Tomaste 1 parte de un total de 4: 1/4. Invertir los números cambia el significado.'},
        {id:'p-d2',kind:'diagnostic',prompt:'En 3/8, ¿cuál es el denominador?',options:['3','8','11'],answer:'8',hints:['Busca el número de abajo.','Ese número indica el total de partes iguales.'],feedback:'El denominador es 8. El 3 es el numerador: las partes tomadas.'},
        {id:'p-1',kind:'practice',prompt:'Una barra tiene 8 partes iguales. Comes 3. ¿Qué fracción comiste?',options:['8/3','3/8','5/8'],answer:'3/8',hints:['El numerador cuenta lo que comiste.','Comiste 3 y había 8 partes.'],feedback:'Comiste 3/8. La fracción 5/8 representa lo que queda, no lo que comiste.'},
        {id:'p-2',kind:'practice',prompt:'Coloreas 2 de 6 regiones iguales. ¿Qué fracción está coloreada?',options:['2/6','6/2','4/6'],answer:'2/6',hints:['Cuenta las regiones coloreadas.','Pon 2 arriba y 6 abajo.'],feedback:'Son 2 de 6 regiones: 2/6. Las 4 regiones restantes representan 4/6.'},
        {id:'p-c',kind:'check',prompt:'Un jardín está dividido en 5 parcelas iguales. Sembraste 4. ¿Qué fracción sembraste?',options:['1/5','5/4','4/5'],answer:'4/5',hints:['El entero es el jardín completo.','Sembraste 4 de 5 parcelas.'],feedback:'Sembraste 4/5 del jardín. La parcela sin sembrar representa 1/5.'}
      ]
    },
    {
      id:'equivalent',title:'Fracciones equivalentes',prerequisite:'parts',
      objective:'Reconocer fracciones que representan la misma cantidad.',
      explanation:'Dos fracciones son equivalentes cuando representan la misma cantidad. Multiplica o divide numerador y denominador por el mismo número distinto de cero para conservar esa cantidad.',
      simple:'La mitad sigue siendo la mitad aunque cortes cada parte en pedazos más pequeños: 1/2 y 2/4 ocupan lo mismo.',
      example:'1/2 = 2/4. Multiplicamos arriba y abajo por 2: (1 × 2)/(2 × 2) = 2/4.',
      alternative:'2/3 = 4/6. Cada tercio se divide en dos. Ahora tomas 4 de 6 partes, la misma cantidad.',
      visual:{total:4,selected:2},
      card:{front:'¿Cómo obtienes una fracción equivalente?',back:'Multiplica o divide ambos números por el mismo número distinto de cero.'},
      questions:[
        {id:'e-d1',kind:'diagnostic',prompt:'¿Qué fracción equivale a 1/2?',options:['1/4','2/4','2/3'],answer:'2/4',hints:['Multiplica ambos números por 2.','1 × 2 = 2 y 2 × 2 = 4.'],feedback:'2/4 es equivalente a 1/2. Multiplicar solo uno de los números cambia la cantidad.'},
        {id:'e-d2',kind:'diagnostic',prompt:'¿Qué fracción equivale a 2/3?',options:['4/6','2/6','3/4'],answer:'4/6',hints:['Multiplica arriba y abajo por el mismo número.','Prueba multiplicar ambos por 2.'],feedback:'2/3 = 4/6 porque ambos números se multiplicaron por 2.'},
        {id:'e-1',kind:'practice',prompt:'Completa: 1/2 = ?/6',options:['1','3','6'],answer:'3',hints:['De 2 a 6 multiplicas por 3.','Haz lo mismo con el numerador: 1 × 3.'],feedback:'1/2 = 3/6. Multiplicamos numerador y denominador por 3.'},
        {id:'e-2',kind:'practice',prompt:'¿Qué fracción equivale a 3/4?',options:['3/8','6/8','4/6'],answer:'6/8',hints:['La misma operación debe aplicarse a ambos números.','Multiplica 3 y 4 por 2.'],feedback:'3/4 = 6/8. Cambiar solo el denominador a 8 daría una cantidad diferente.'},
        {id:'e-c',kind:'check',prompt:'Una receta usa 2/5 de taza. ¿Qué medida representa la misma cantidad?',options:['2/10','5/2','4/10'],answer:'4/10',hints:['Busca una fracción equivalente.','Multiplica 2 y 5 por 2.'],feedback:'2/5 = 4/10. Ambas medidas representan la misma cantidad de taza.'}
      ]
    },
    {
      id:'sum',title:'Sumar partes del mismo tamaño',prerequisite:'equivalent',
      objective:'Sumar fracciones con el mismo denominador y explicar el resultado.',
      explanation:'Si las partes son del mismo tamaño, suma los numeradores y conserva el denominador. El denominador no se suma porque el tamaño de las partes no cambió.',
      simple:'Un cuarto más dos cuartos son tres cuartos. Sigues contando cuartos: 1/4 + 2/4 = 3/4.',
      example:'2/8 + 3/8 = 5/8. Sumamos las partes tomadas: 2 + 3 = 5. Cada parte sigue siendo un octavo.',
      alternative:'Estudiaste 1/5 de un libro y después 2/5 más. En total estudiaste 3/5 del libro.',
      visual:{total:8,selected:5},
      card:{front:'¿Sumas los denominadores si son iguales?',back:'No. Sumas los numeradores y conservas el denominador, pues el tamaño de las partes no cambia.'},
      questions:[
        {id:'s-d1',kind:'diagnostic',prompt:'¿Cuánto es 1/4 + 2/4?',options:['3/8','3/4','2/4'],answer:'3/4',hints:['Ambas fracciones cuentan cuartos.','Suma 1 + 2 y conserva el 4.'],feedback:'1/4 + 2/4 = 3/4. Sumar los denominadores cambiaría el tamaño de las partes.'},
        {id:'s-d2',kind:'diagnostic',prompt:'¿Cuánto es 2/8 + 3/8?',options:['5/16','6/8','5/8'],answer:'5/8',hints:['Las partes son octavos en ambas fracciones.','Suma 2 + 3.'],feedback:'Son 5 octavos: 5/8. El denominador permanece en 8.'},
        {id:'s-1',kind:'practice',prompt:'¿Cuánto es 1/6 + 2/6?',options:['3/12','3/6','2/6'],answer:'3/6',hints:['Conserva el denominador.','1 + 2 = 3.'],feedback:'El resultado es 3/6, equivalente a 1/2. Sigues sumando sextos.'},
        {id:'s-2',kind:'practice',prompt:'¿Cuánto es 2/7 + 3/7?',options:['5/7','5/14','6/7'],answer:'5/7',hints:['Ambas fracciones tienen denominador 7.','Suma los numeradores: 2 + 3.'],feedback:'2/7 + 3/7 = 5/7. Cada parte sigue siendo un séptimo.'},
        {id:'s-c',kind:'check',prompt:'Caminaste 2/9 de una ruta y luego 4/9 más. ¿Qué fracción recorriste?',options:['6/18','6/9','8/9'],answer:'6/9',hints:['Suma las partes recorridas, del mismo tamaño.','2 + 4 = 6; conserva el 9.'],feedback:'Recorriste 6/9 de la ruta, equivalente a 2/3. Sumar 9 + 9 no corresponde.'}
      ]
    }
  ]
};
export const courses = addReinforcement(extendCourses([course,...extraCourses,...scenarioCourses]));
export const allTopics = courses.flatMap(c=>c.topics.map(t=>({...t,courseId:c.id,source:c.source,subject:c.subject})));
export const getCourse = id => courses.find(c=>c.id===id);
export const questions = allTopics.flatMap(t => t.questions.map(q => ({...q,topicId:t.id,courseId:t.courseId})));
const variantQuestions=questions.flatMap(variantsFor);
export const questionById = id => questions.find(q => q.id === id)??variantQuestions.find(q=>q.id===id);
export const sessionQuestions = (topic,round=0) => topic.questions.filter(q=>q.kind!=='diagnostic').map(q=>round?`${q.id}~v${round}`:q.id);
export const topicById = id => allTopics.find(t => t.id === id);
