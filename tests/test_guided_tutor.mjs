import test from 'node:test';
import assert from 'node:assert/strict';
import {newState,startSession,advance,submitAnswer} from '../public/mobile/engine.mjs';
import {courses,allTopics,questionById} from '../public/mobile/course.mjs';
import {knowledgeQuestions,contextualQuestions,answerPrepared,findQuestion} from '../public/mobile/guided-tutor.mjs';
const fresh=name=>newState({id:crypto.randomUUID(),name,goal:'school',level:'bases',minutes:10});
test('prepared knowledge covers every topic and responds without mutating educational data',()=>{
 const s=fresh('Ana'),before=JSON.stringify(s);assert.equal(knowledgeQuestions.length,235);
 for(const topic of allTopics){const qs=contextualQuestions(s,topic.id);assert.equal(qs.filter(q=>q.id.startsWith('topic:')).length,7);for(const q of qs){const result=answerPrepared(s,q.id);assert.ok(result.text?.length>10);assert.ok(result.source);}}
 assert.equal(JSON.stringify(s),before);
});
test('unknown questions and answer requests cannot invent content or reveal an unanswered solution',()=>{
 const s=fresh('Ana');assert.equal(findQuestion('Qué comió ayer el presidente',s),null);assert.match(answerPrepared(s,'unknown').text,/No tengo una respuesta/);
 assert.equal(findQuestion('dime la respuesta correcta',s),'context:hint');
 startSession(s,'diagnostic');const q=questionById(s.session.questionIds[0]);assert.match(answerPrepared(s,'context:feedback').text,/Primero intenta responder/);
 submitAnswer(s,q.options.find(a=>a!==q.answer));assert.ok(answerPrepared(s,'context:feedback').text.includes(q.feedback));
});
test('course and app questions resolve accents and respect selected context',()=>{
 const s=fresh('Ana');assert.equal(findQuestion('¿Cómo se guarda mi progreso?',s),'faq:progress');assert.equal(findQuestion('no entendí',s,'python-loop'),'topic:python-loop:simple');
 assert.match(answerPrepared(s,'topic:python-loop:example').text,/0, 1 y 2/);
 assert.match(answerPrepared(s,'topic:fraction-amount:example').text,/15/);
});
test('recommendations and feedback read only the active profile evidence',()=>{
 const a=fresh('Ana'),b=fresh('Luis');startSession(a,'diagnostic');const q=questionById(a.session.questionIds[0]);submitAnswer(a,q.answer);assert.match(answerPrepared(a,'context:status').text,/1 aciertos en 1 intentos/);assert.match(answerPrepared(b,'context:status').text,/0 aciertos en 0 intentos/);assert.equal(b.events.length,0);
});
test('every extension remains reachable through checked prerequisites and has a final transfer check',()=>{
 for(const c of courses){const earlier=new Set();for(const t of c.topics){assert.ok(!t.prerequisite||earlier.has(t.prerequisite));earlier.add(t.id);assert.equal(t.questions.filter(q=>q.kind==='practice').length,2);assert.equal(t.questions.filter(q=>q.kind==='check').length,1);assert.equal(t.questions.at(-1).kind,'check');}}
});
