import {reinforcementContent} from './reinforcement-content.mjs';
import {interactiveQuestion} from './activities.mjs';
export function addReinforcement(courses){
 for(const course of courses){
  course.topics.forEach((topic,i)=>{topic.module??=i<course.topics.length-3?'Bases de la ruta':'Aplicaciones';});
 }
 for(const row of reinforcementContent){
  const course=courses.find(c=>c.id===row.courseId);
  if(!course)throw Error('Curso de refuerzo desconocido.');
  course.topics.push({id:row.id,title:row.title,module:row.module,prerequisite:row.prerequisite,objective:`Aplicar ${row.title.toLowerCase()} en un caso concreto.`,explanation:row.explanation,simple:row.explanation.split('. ')[0]+'.',example:row.example,alternative:row.alternative,guide:row.guide??null,card:{front:`¿Qué recuerdas sobre ${row.title.toLowerCase()}?`,back:row.explanation},questions:row.items.map(([type,prompt,values,feedback,extra],i)=>{
   const q=interactiveQuestion(type,prompt,values,feedback,extra);
   const offset=(row.id.length+i)%q.options.length;
   return {...q,id:`${row.id}-${i}`,kind:i===2?'check':'practice',options:[...q.options.slice(offset),...q.options.slice(0,offset)],hints:[`Busca qué pide la actividad. ${row.explanation.split('. ')[0]}.`,type==='order'?'Usa los botones para mover los pasos; verifica qué debe suceder antes.':type==='match'?'Relaciona cada concepto con su función; cada descripción se usa una vez.':`Revisa esta idea con otro caso: ${row.alternative}`]};
  })});
 }
 return courses;
}
