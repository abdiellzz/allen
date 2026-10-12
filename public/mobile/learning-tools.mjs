import {allTopics,topicById} from './course.mjs';
export function explanationChoices(topicId){
 const topic=topicById(topicId);if(!topic)throw Error('Tema no válido.');
 const others=allTopics.filter(t=>t.courseId===topic.courseId&&t.id!==topicId).slice(0,2);
 const choices=[topic,...others].map(t=>({id:t.id,text:t.simple,example:t.example}));
 const offset=allTopics.indexOf(topic)%choices.length;
 return [...choices.slice(offset),...choices.slice(0,offset)];
}
export function checkExplanation(topicId,ruleId,exampleId){
 const choices=explanationChoices(topicId);if(!choices.some(c=>c.id===ruleId)||!choices.some(c=>c.id===exampleId))throw Error('Elige una explicación y un ejemplo.');
 return {correct:ruleId===topicId&&exampleId===topicId,text:ruleId===topicId&&exampleId===topicId?'Relacionaste la regla con un ejemplo que la aplica. Ahora intenta explicarla con tus palabras.':`Revisemos el objetivo. ${topicById(topicId).simple} Un ejemplo que lo apoya: ${topicById(topicId).example}`};
}
export function saveDiscovery(state,topicId,text,understood=false,now=new Date()){
 if(!topicById(topicId)||typeof text!=='string'||text.trim().length>800||typeof understood!=='boolean')throw Error('Escribe una nota de hasta 800 caracteres.');
 state.notebook??={};state.notebook[topicId]={text:text.trim(),understood,at:now.toISOString()};
}
