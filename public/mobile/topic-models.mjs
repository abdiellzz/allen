// Prepared activity metadata. Unsupported simulations use the actual authored case.
const number=(mode,labels,values)=>({kind:'number',numeric:{mode,labels},values});
const numeric={
 'math-decimal-add':number('sum',['Primer decimal','Segundo decimal'],[2.3,1.45,0]),
 'math-percent':number('discount',['Porcentaje','Precio original'],[20,50,0]),
 'math-ratio':number('ratio',['Personas del ejemplo','Personas nuevas'],[2,6,3]),
 'math-integers':number('sum',['Punto inicial','Avance'],[-3,5,0]),
 'math-equation':number('equation',['Resultado','Cantidad sumada a x'],[9,4,0]),
 'math-area':number('area',['Largo en cm','Ancho en cm'],[5,3,0]),
 'math-average':number('average',['Primer dato','Segundo dato','Tercer dato'],[4,6,8]),
 'fractions-workshop-3-1':number('percent',['Porcentaje','Materiales'],[10,80,0]),
 'fractions-workshop-3-2':number('ratio',['Personas del ejemplo','Personas nuevas'],[3,5,6]),
 'fractions-workshop-4-1':number('area',['Largo en m','Ancho en m'],[8,3,0]),
 'fractions-workshop-4-2':number('area',['Largo en m','Ancho en m'],[5,4,0]),
 'geography-school-2':number('scale',['Kilómetros por cm','Distancia en cm'],[2,3,0]),
 'geography-school-workshop-1-2':number('scale',['Kilómetros por cm','Distancia en cm'],[3,5,0]),
 'geography-school-6':number('density',['Habitantes','Superficie en km²'],[200,10,0]),
 'geography-school-workshop-3-1':number('density',['Habitantes','Superficie en km²'],[400,20,0]),
 'geography-school-workshop-3-2':number('density',['Habitantes','Superficie en km²'],[400,10,0]),
 'science-measure':number('metres',['Longitud en metros'],[1.2,0,0]),
 'science-data':number('changes',['Primer registro en cm','Segundo registro en cm','Tercer registro en cm'],[5,7,9]),
 'science-workshop-2-1':number('metres',['Longitud en metros'],[1,0,0]),
 'physics-school-1':number('metres',['Longitud en metros'],[1.2,0,0]),
 'physics-school-2':number('metres',['Longitud en metros'],[2.5,0,0]),
 'physics-school-4':number('force',['Fuerza hacia el este en N','Fuerza hacia el oeste en N'],[5,5,0]),
 'physics-school-workshop-1-1':number('metres',['Longitud en metros'],[1.8,0,0]),
 'physics-school-workshop-1-2':number('metres',['Longitud en metros'],[2,0,0]),
 'physics-school-workshop-2-1':number('speed',['Distancia en m','Tiempo en s'],[90,30,0]),
 'physics-school-workshop-2-2':number('force',['Fuerza hacia el este en N','Fuerza hacia el oeste en N'],[10,6,0]),
 'chemistry-school-7':number('mass',['Masa inicial A en g','Masa inicial B en g'],[4,6,0]),
 'chemistry-school-workshop-4-2':number('mass',['Masa inicial A en g','Masa inicial B en g'],[5,8,0]),
 'money-school-3':number('balance',['Recursos iniciales','Ingreso','Gasto'],[5,3,2]),
 'money-school-4':{kind:'budget',numeric:{mode:'budget',labels:['Ingresos previstos','Gasto en transporte','Gasto en materiales']},values:[20,8,7]},
 'money-school-workshop-2-1':{kind:'budget',numeric:{mode:'budget',labels:['Recursos','Primer gasto','Segundo gasto']},values:[25,9,6]},
 'money-school-workshop-2-2':{kind:'budget',numeric:{mode:'budget',labels:['Ingresos previstos','Gastos previstos']},values:[20,24,0]},
 'money-school-5':number('unit',['Precio total','Cantidad de cuadernos'],[8,4,0]),
 'money-school-workshop-3-1':number('unit',['Precio total','Cantidad de cuadernos'],[18,6,0]),
 'money-school-6':number('discount',['Porcentaje de descuento','Precio original'],[20,50,0]),
 'money-school-workshop-3-2':number('discount',['Porcentaje de descuento','Precio original'],[10,60,0]),
 'money-school-7':number('goal',['Meta','Recursos reunidos'],[24,9,0]),
 'money-school-workshop-4-1':number('goal',['Meta','Recursos reunidos'],[45,28,0])
};
const fractions={parts:['parts',3,8,0],equivalent:['equivalent',1,2,0],sum:['sum',2,8,3],'fraction-compare':['compare',3,8,1],'fraction-unlike':['unlike',1,2,1,4],'fraction-amount':['quantity',3,4,20],'math-decimal':['decimal',3,4,0],'fractions-workshop-1-1':['parts',5,12,0],'fractions-workshop-1-2':['parts',7,10,0],'fractions-workshop-2-1':['unlike',1,3,1,6],'fractions-workshop-2-2':['unlike',1,4,3,8]};
const sentences={
 'english-greetings':'Hello! My name is Ana.', 'english-am':'I am a student.', 'english-has':'She has a pen.',
 'english-routine':'She reads every day.', 'english-questions':'Do you read?', 'english-articles':'An apple.',
 'english-plurals':'Two boxes.', 'english-there':'There are two books on the desk.', 'english-place':'The book is on the desk.',
 'english-can':'I can swim.', 'english-wh-questions':'Where is the library?', 'english-connectors':'I rest because I am tired.',
 'english-reading':'Meet me at the library at three.', 'english-workshop-1-1':'I am Ana.', 'english-workshop-1-2':'You are my friend.',
 'english-workshop-2-1':'Do you read?', 'english-workshop-2-2':'She studies every day.', 'english-workshop-3-1':'There are two books.',
 'english-workshop-3-2':'The book is under the table.', 'english-workshop-4-1':'Meet me at the library to study.', 'english-workshop-4-2':'I can swim.'
};
export function topicModel(t){
 if(numeric[t.id])return numeric[t.id];
 if(fractions[t.id]){const [mode,a,b,c,denominatorB]=fractions[t.id];return {kind:'fraction',fraction:{mode,denominatorB},values:[a,b,c]};}
 if(sentences[t.id])return {kind:'sentence',sentence:sentences[t.id].split(' ')};
 if(t.courseId==='geography-school-v1')return ['geography-school-1','geography-school-workshop-1-1'].includes(t.id)?{kind:'map',values:[0,0,0]}:{kind:'case'};
 if(t.courseId==='history-school-v1'){
  if(/canal/i.test(t.title))return {kind:'timeline',timeline:[[1914,'Apertura del Canal'],[1977,'Tratados Torrijos-Carter'],[1999,'Transferencia de administración']]};
  if(/independencia|comparar dos etapas/i.test(t.title))return {kind:'timeline',timeline:[[1821,'Independencia de España'],[1903,'Separación de Colombia']]};
  if(t.id==='history-school-1')return {kind:'timeline',timeline:[[1820,'Carta del ejemplo'],[1830,'Noticia del ejemplo']]};
  return {kind:'case'};
 }
 if(t.courseId==='chemistry-school-v1'){
  if(['chemistry-school-1','chemistry-school-2','chemistry-school-8','chemistry-school-workshop-1-1','chemistry-school-workshop-1-2','chemistry-school-workshop-4-1'].includes(t.id))return {kind:'atoms',molecule:/CO₂/.test(t.example)?{formula:'CO₂',symbols:['O','C','O'],counts:[['C',1],['O',2]]}:{formula:'H₂O',symbols:['H','O','H'],counts:[['H',2],['O',1]]},values:[t.id==='chemistry-school-8'?2:t.id==='chemistry-school-workshop-4-1'?4:1,0,0]};
  return {kind:'process'};
 }
 if(t.courseId==='money-school-v1')return {kind:'decision'};
 if(t.courseId==='physics-school-v1'){
  if(/rapidez/i.test(t.title))return {...number('speed',['Distancia en m','Tiempo en s'],[60,20,0])};
  if(/fuerza/i.test(t.title))return {...number('force',['Fuerza hacia el este en N','Fuerza hacia el oeste en N'],[10,6,0])};
  return {kind:'experiment'};
 }
 if(t.courseId==='science-v1'&&/célula|cadena|ciclo|red de vida/i.test(t.title))return {kind:'process'};
 return {};
}
const fmt=n=>Number.isFinite(n)?Number(n.toFixed(3)).toString():'Sin resultado';
export function numericResult(model,values){const [a,b,c]=values,mode=model.numeric?.mode;
 if(['ratio','speed','density','unit'].includes(mode)&&(mode==='ratio'?a:b)===0)return 'El divisor no puede ser cero. Cambia esa cantidad para comparar.';
 return ({changes:()=>`Cambios: ${fmt(b-a)} cm y ${fmt(c-b)} cm. Un patrón no demuestra por sí solo su causa.`,sum:()=>`${fmt(a)} + ${fmt(b)} = ${fmt(a+b)}`,equation:()=>`x + ${fmt(b)} = ${fmt(a)} → x = ${fmt(a-b)}`,area:()=>`Área: ${fmt(a*b)} unidades² · Perímetro: ${fmt(2*(a+b))} unidades`,percent:()=>`${fmt(a)}% de ${fmt(b)} = ${fmt(a*b/100)}`,discount:()=>`Descuento: ${fmt(a*b/100)} · Precio final: ${fmt(b-a*b/100)}`,ratio:()=>`${fmt(c)} ÷ ${fmt(a)} × ${fmt(b)} = ${fmt(c/a*b)} unidades para ${fmt(b)} personas`,average:()=>`Promedio: (${fmt(a)} + ${fmt(b)} + ${fmt(c)}) ÷ 3 = ${fmt((a+b+c)/3)}`,metres:()=>`${fmt(a)} m = ${fmt(a*100)} cm`,speed:()=>`Rapidez media: ${fmt(a)} ÷ ${fmt(b)} = ${fmt(a/b)} m/s`,force:()=>`Fuerza neta: ${fmt(Math.abs(a-b))} N ${a===b?'· equilibrio en este modelo':a>b?'hacia el este':'hacia el oeste'}`,mass:()=>`Masa final del sistema cerrado: ${fmt(a+b)} g`,scale:()=>`Distancia representada: ${fmt(a*b)} km`,density:()=>`Densidad: ${fmt(a/b)} habitantes/km²`,unit:()=>`Precio por unidad: ${fmt(a/b)}`,goal:()=>`Faltan: ${fmt(Math.max(0,a-b))} · ${a<=b?'Meta cubierta':'Puedes planear cómo reunirlos'}`,balance:()=>`Saldo: ${fmt(a+b-c)}`,budget:()=>`Saldo previsto: ${fmt(a-b-c)}`}[mode]??(()=> 'Relaciona el ejemplo con la regla de la lección.'))();
}
