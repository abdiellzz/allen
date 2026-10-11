import {schoolContent} from './school-content.mjs';
import {interactiveQuestion} from './activities.mjs';
// Share the same evaluator, tutor and backup format as the established routes.
export const schoolCourses=schoolContent.map(c=>({...c,topics:c.topics.map(t=>({...t,questions:t.questions.map((q,i)=>{
 const prepared=q.activity==='match'?{...q,...interactiveQuestion('match',q.prompt,q.pairs,q.feedback)}:{...q};
 const offset=(i+t.id.length)%prepared.options.length;
 return {...prepared,options:[...prepared.options.slice(offset),...prepared.options.slice(0,offset)]};
})}))}));
