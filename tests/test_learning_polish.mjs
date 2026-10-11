import test from 'node:test';
import assert from 'node:assert/strict';
import {newState,startSession,advance,submitAnswer,startMixedReview,rescueFor,requestHelp} from '../public/mobile/engine.mjs';
import {questionById,questions,allTopics,sessionQuestions} from '../public/mobile/course.mjs';
import {validateState,exportBackup,parseBackup,prepareRecovery} from '../public/mobile/storage.mjs';
import {checkExplanation,saveDiscovery} from '../public/mobile/learning-tools.mjs';
const fresh=()=>({...newState({id:crypto.randomUUID(),name:'Ana',goal:'school',level:'bases',minutes:5}),revision:1,diagnosticComplete:true});
function finish(s,wrong=false){if(s.session.phase==='lesson')advance(s);while(s.session.phase==='practice'){const q=questionById(s.session.questionIds[s.session.index]);if(!s.session.answers.some(a=>a.questionId===q.id))submitAnswer(s,wrong?q.options.find(o=>o!==q.answer):q.answer);advance(s);}}

test('repeated fraction sessions have new parameters, durable identifiers and distinct choices',()=>{
 const s=fresh();startSession(s,'learn','parts');finish(s);
 const original=[...s.session.questionIds];startSession(s,'review','parts');
 assert.equal(s.session.round,1);assert.notDeepEqual(s.session.questionIds,original);
 const active=questionById(s.session.questionIds[0]);assert.notEqual(active.prompt,questionById(original[0]).prompt);
 advance(s);submitAnswer(s,active.answer);const restored=parseBackup(exportBackup(s));assert.deepEqual(restored.session,s.session);finish(restored);validateState(restored);
 const prompts=s.session.questionIds.map(id=>questionById(id).prompt);assert.equal(new Set(prompts).size,3);
 for(const q of questions.filter(q=>q.kind!=='diagnostic'))for(let round=1;round<=3;round++){const v=questionById(`${q.id}~v${round}`);assert.equal(v.options.length,new Set(v.options).size);assert.equal(v.options.filter(o=>o===v.answer).length,1);assert.ok(v.feedback&&v.hints.length===2);}
});
test('fraction arithmetic variants are computed correctly rather than plausible strings',()=>{
 for(const topic of allTopics.filter(t=>t.courseId==='fractions-v1'))for(let round=1;round<=3;round++)for(const id of sessionQuestions(topic,round)){
  const q=questionById(id),values=q.prompt.match(/\d+/g).map(Number);
  if(topic.id==='parts')assert.equal(q.answer,`${values[1]}/${values[0]}`);
  if(topic.id==='sum')assert.equal(q.answer,`${values[0]+values[2]}/${values[1]}`);
  if(topic.id==='fraction-amount')assert.equal(Number(q.answer),values[0]*values[1]/values[2]);
  if(topic.id==='fraction-unlike'){const [num,den]=q.answer.split('/').map(Number);assert.ok(Math.abs(num/den-(1/values[1]+1/values[3]))<1e-12);}
 }
});
test('rescue responds to two recent topic errors and never completes a topic',()=>{
 const s=fresh();startSession(s,'learn','parts');advance(s);let q=questionById(s.session.questionIds[0]);submitAnswer(s,q.options.find(o=>o!==q.answer));advance(s);assert.equal(rescueFor(s),null);
 q=questionById(s.session.questionIds[1]);submitAnswer(s,q.options.find(o=>o!==q.answer));assert.equal(rescueFor(s).base.id,'parts');const before=[...s.completed];requestHelp(s,'simple');assert.deepEqual(s.completed,before);assert.equal(s.session.index,1);
});
test('mixed review enforces prerequisites, records each topic and does not claim a new check',()=>{
 const s=fresh();assert.throws(()=>startMixedReview(s),/dos temas/);startSession(s,'learn','parts');finish(s);startSession(s,'learn','equivalent');finish(s);
 const before=[...s.completed],checks=s.events.filter(e=>e.type==='check_complete').length;startMixedReview(s);assert.equal(s.session.questionIds.length,2);assert.equal(questionById(s.session.questionIds[1]).topicId,'equivalent');requestHelp(s,'hint');assert.equal(s.events.at(-1).topicId,'parts');
 const copy=parseBackup(exportBackup(s));finish(copy);assert.deepEqual(copy.completed,before);assert.equal(copy.events.filter(e=>e.type==='check_complete').length,checks);validateState(copy);
 const tampered=structuredClone(s);tampered.session.topicIds=['parts','sum'];assert.throws(()=>validateState(tampered));
});
test('explain-back requires the matching rule and example; notebook is local and exportable',()=>{
 const s=fresh();const count=s.events.length;assert.equal(checkExplanation('parts','parts','equivalent').correct,false);assert.equal(checkExplanation('parts','parts','parts').correct,true);assert.equal(s.events.length,count);
 saveDiscovery(s,'parts','<script>texto, nunca código</script>',true);s.preferences={textSize:'large',theme:'dark',reduceMotion:true};const copy=prepareRecovery(exportBackup(s));assert.deepEqual(copy.notebook,s.notebook);assert.deepEqual(copy.preferences,s.preferences);assert.notEqual(copy.profile.id,s.profile.id);assert.equal(fresh().notebook,undefined);
 assert.throws(()=>saveDiscovery(s,'parts','x'.repeat(801)));const bad=structuredClone(s);bad.preferences.theme='remote';assert.throws(()=>validateState(bad));
});
