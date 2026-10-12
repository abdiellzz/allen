import {workshopContent} from './workshop-content.mjs';
import {interactiveQuestion} from './activities.mjs';
export function addWorkshops(courses){
 for(const row of workshopContent){
  const c=courses.find(c=>c.id===row.courseId);
  const [prompt,options,feedback]=row.case;
  const descriptions=row.steps.map((step,i)=>[String(i+1),step]);
  const prepared=[interactiveQuestion('order','Construye el procedimiento de este taller.',row.steps,`El orden acordado es: ${row.steps.join(' → ')}.`),interactiveQuestion('match','Relaciona cada posición con su función en el procedimiento.',descriptions,row.steps.join('. ')),interactiveQuestion('choice',prompt,options,feedback)];
  c.topics.push({...row,card:{front:`¿Cómo aplicarías ${row.title.toLowerCase()}?`,back:feedback},questions:prepared.map((q,i)=>({...q,id:`${row.id}-${i}`,kind:i===2?'check':'practice',options:[...q.options.slice(1),q.options[0]],hints:[`Primero: ${row.steps[0]}.`,`Comprueba el procedimiento: ${row.steps.join(' → ')}.`]}))});
 }
 return courses;
}
