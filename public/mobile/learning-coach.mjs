import {questionById,topicById} from './course.mjs';
import {feedbackFor} from './activities.mjs';
// Describe only observable choices. No diagnosis of a student's ability or intentions.
export function errorCoach(state,selectedTopicId=null){
 const s=state.session,q=questionById(s?.questionIds[s?.index]),current=s?.answers.find(a=>a.questionId===q?.id);
 const event=state.events.findLast(e=>e.type==='answer'&&!e.correct&&(!selectedTopicId||e.topicId===selectedTopicId));
 const question=current&&!current.correct&&(!selectedTopicId||q.topicId===selectedTopicId)?q:questionById(event?.questionId);
 const answer=question===q&&current&&!current.correct?current.answer:event?.answer;
 if(!question||answer===undefined)return null;
 const topic=topicById(question.topicId),specific=question.feedbackByAnswer?.[answer];
 return {topicId:topic.id,questionId:question.id,answer,title:specific?'Revisemos lo que cambió':'Vamos a revisar la idea',reason:specific?`${specific} ${question.feedback}`:feedbackFor(question,answer).text,firstStep:question.hints[0]??topic.simple,source:topic.source,followUps:[{id:'context:error-next',label:'Veamos el primer paso juntos'},{id:`topic:${topic.id}:alternative`,label:'Dame otro ejemplo'}]};
}
