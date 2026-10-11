// Prepared, bounded exploration models. None executes student code or grants mastery.
import {allTopics,topicById} from './course.mjs';
import {checkExplanation} from './learning-tools.mjs';
export const labMethods={fraction:'Representar y comparar',number:'Manipular cantidades',reading:'Leer y señalar pistas',sentence:'Construir frases',trace:'Seguir un programa',decision:'Explorar consecuencias',experiment:'Cambiar una condición',process:'Conectar funciones',map:'Recorrer un mapa',timeline:'Ordenar acontecimientos',atoms:'Construir moléculas',plan:'Organizar un proyecto',budget:'Probar un presupuesto'};
export function labFor(t){
 const kinds={'fractions-v1':t.id.startsWith('math-')?'number':'fraction','reading-v1':'reading','english-v1':'sentence','python-v1':'trace','digital-safety-v1':'decision','science-v1':'experiment','geography-school-v1':'map','history-school-v1':'timeline','biology-school-v1':'process','physics-school-v1':/energía|calor|circuit|onda/i.test(t.title)?'experiment':'number','chemistry-school-v1':/school-[3-6]$/.test(t.id)?'process':'atoms','citizenship-school-v1':'decision','study-school-v1':'plan','money-school-v1':'budget'};
 const kind=t.method??kinds[t.courseId]??'process';
 const steps=t.steps??t.guide?.lines?.map(([line,explain])=>`${line}: ${explain}`)??[t.simple,t.example,t.alternative];
 const pairs=t.questions.find(q=>q.pairs)?.pairs??steps.slice(0,3).map((step,i)=>[`Idea ${i+1}`,step]);
 const timeline=kind==='timeline'?/canal/i.test(t.title)?[[1914,'Apertura del Canal'],[1977,'Tratados Torrijos-Carter'],[1999,'Transferencia de administración']]:/independencia|comparar dos etapas/i.test(t.title)?[[1821,'Independencia de España'],[1903,'Separación de Colombia']]:[[1840,'Registro del ejemplo'],[1850,'Otro registro del ejemplo'],[2020,'Análisis posterior del ejemplo']]:null;
 return {kind,timeline,steps:steps.slice(0,6),pairs:pairs.slice(0,3),sentence:t.courseId==='english-v1'?englishSentence(t):null};
}
function englishSentence(t){
 if(/\bcan\b|habilidad|ability/i.test(t.id+' '+t.title+' '+t.example))return ['I','can','swim.'];
 if(/there|salón|plurals/i.test(t.id+' '+t.title))return ['There','are','two','books.'];
 if(/where|wh-question/i.test(t.id))return ['Where','is','the','library?'];
 if(/have|tienes/i.test(t.id+' '+t.title))return ['I','have','a','book.'];
 if(/routine|rutina/i.test(t.id+' '+t.title))return ['She','studies','every','day.'];
 if(/connectors/i.test(t.id))return ['I','read','and','I','write.'];
 if(/english-reading|invitación/i.test(t.id+' '+t.title))return ['Meet','me','at','the','library.'];
 if(/question/i.test(t.id))return ['Do','you','read?'];
 if(/place|preposition/i.test(t.id+' '+t.title))return ['The','book','is','under','the','table.'];
 return ['I','am','a','student.'];
}
export function freshLab(t){const kind=t?labFor(t).kind:'fraction';const defaults={map:[0,0,0],budget:[20,8,0],atoms:[1,0,0],number:[6,3,0]};return {step:0,values:defaults[kind]??[3,8,0],built:[],note:'',at:new Date().toISOString()};}
export function saveLab(state,id,patch){
 if(!topicById(id))throw Error('Abre una lección válida.');
 const next={...(state.learningLabs?.[id]??freshLab(topicById(id))),...patch,at:new Date().toISOString()};
 validateLab(next);state.learningLabs??={};state.learningLabs[id]=next;return next;
}
export function validateLab(lab){
 if(!lab||!Number.isInteger(lab.step)||lab.step<0||lab.step>5||!Array.isArray(lab.values)||lab.values.length!==3||lab.values.some(n=>!Number.isFinite(n)||n< -1000||n>1000)||!Array.isArray(lab.built)||lab.built.length>12||lab.built.some(n=>!Number.isInteger(n)||n<0||n>11)||new Set(lab.built).size!==lab.built.length||typeof lab.note!=='string'||lab.note.length>800||typeof lab.at!=='string'||lab.at.length>30||!Number.isFinite(Date.parse(lab.at)))throw Error('Exploración no válida.');
 return lab;
}
export function saveReflection(state,id,rule,example){
 const result=checkExplanation(id,rule,example);
 if(result.correct&&state.completed.includes(id)){state.reflections??={};state.reflections[id]={rule,example,at:new Date().toISOString()};}
 return result;
}
export const ranks=[
 {id:'explorer',title:'Explorador',topics:0,reflections:0,description:'Empiezas a descubrir cómo aprender.'},
 {id:'apprentice',title:'Aprendiz',topics:5,reflections:1,description:'Compruebas ideas y explicas una de ellas.'},
 {id:'builder',title:'Constructor',topics:15,reflections:3,description:'Conectas lo aprendido y lo aplicas.'},
 {id:'analyst',title:'Analista',topics:35,reflections:5,description:'Revisas evidencia y justificas tus respuestas.'},
 {id:'mentor',title:'Mentor',topics:70,reflections:10,description:'Practicas explicar con claridad lo aprendido.'}
];
export function rankFor(state){
 const topics=new Set(state.completed).size,reflections=Object.entries(state.reflections??{}).filter(([id,r])=>state.completed.includes(id)&&validReflection(id,r)).length;
 const current=ranks.findLast(r=>topics>=r.topics&&reflections>=r.reflections)??ranks[0],next=ranks[ranks.indexOf(current)+1]??null;
 return {current,next,topics,reflections,remainingTopics:next?Math.max(0,next.topics-topics):0,remainingReflections:next?Math.max(0,next.reflections-reflections):0};
}
export function validReflection(id,value){return allTopics.some(t=>t.id===id)&&value&&value.rule===id&&value.example===id&&typeof value.at==='string'&&value.at.length<=30&&Number.isFinite(Date.parse(value.at));}
