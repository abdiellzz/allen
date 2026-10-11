import test from 'node:test';
import assert from 'node:assert/strict';
import {recap,companionTip,followUpQuestions,shortMissions,missionReadiness} from '../public/mobile/companion.mjs';
import {newState,startSession,submitAnswer,advance,chooseCourse} from '../public/mobile/engine.mjs';
import {questionById,topicById} from '../public/mobile/course.mjs';
import {answerPrepared,findQuestion} from '../public/mobile/guided-tutor.mjs';
const now=new Date('2026-10-11T14:00:00');
const fresh=()=>newState({id:crypto.randomUUID(),name:'Ana',goal:'school',level:'bases',minutes:5});
const finish=s=>{if(s.session.phase==='lesson')advance(s,now);while(s.session.phase!=='complete'){submitAnswer(s,questionById(s.session.questionIds[s.session.index]).answer,now);advance(s,now);}};
test('closing recap reports only real current-day evidence, per profile',()=>{
 const a=fresh(),b=fresh();startSession(a,'diagnostic');submitAnswer(a,'4/1',now);advance(a,now);submitAnswer(a,'8',now);
 const before=JSON.stringify(a),r=recap(a,now);assert.equal(r.attempts,2);assert.equal(r.correct,1);assert.deepEqual(r.reinforce,['Partes de un entero']);assert.equal(r.checked.length,0);assert.equal(recap(b,now).attempts,0);assert.equal(recap(a,new Date('2026-10-12T14:00:00')).attempts,0);assert.equal(JSON.stringify(a),before);
});
test('companion responds to actual errors, support and session completion',()=>{
 const s=fresh();startSession(s,'diagnostic');assert.equal(companionTip(s,'session').title,'Un paso cada vez');submitAnswer(s,'4/1',now);assert.equal(companionTip(s,'session').title,'Vamos a revisar la idea');advance(s,now);finish(s);assert.equal(companionTip(s,'session').asset,'allen-celebrate.png');
});
test('follow-up questions remain valid and preserve the selected topic',()=>{
 const s=fresh();for(const id of ['topic:python-loop:simple','topic:python-loop:example','context:hint','context:status','faq:privacy'])for(const q of followUpQuestions(id,'python-loop')){assert.ok(answerPrepared(s,q.id).text);assert.ok(!q.id.includes('unknown'));}
 assert.equal(findQuestion('¿Cómo voy?',s),'context:status');assert.equal(findQuestion('¿Qué hago después?',s),'context:recommend');
});
test('short missions are ordinary learning activities and cannot bypass prerequisites',()=>{
 const s=fresh();for(const m of shortMissions){assert.ok(topicById(m.topicId));assert.equal(missionReadiness(s,m),false);assert.throws(()=>startSession(s,'learn',m.topicId));}
 chooseCourse(s,'digital-safety-v1');startSession(s,'diagnostic');finish(s);const mission=shortMissions.find(m=>m.id==='message');assert.equal(missionReadiness(s,mission),false);startSession(s,'learn','safe-accounts');finish(s);assert.equal(missionReadiness(s,mission),true);startSession(s,'learn',mission.topicId);finish(s);assert.ok(s.completed.includes('spot-phishing'));
});
test('a failed review is not presented as a newly demonstrated achievement',()=>{
 const s=fresh();startSession(s,'diagnostic');finish(s);startSession(s,'learn','parts');finish(s);
 const tomorrow=new Date('2026-10-12T14:00:00');startSession(s,'review','parts');advance(s,tomorrow);
 while(s.session.phase!=='complete'){const q=questionById(s.session.questionIds[s.session.index]);submitAnswer(s,q.options.find(o=>o!==q.answer),tomorrow);advance(s,tomorrow);}
 assert.ok(s.completed.includes('parts'));assert.equal(recap(s,tomorrow).checked.length,0);assert.equal(recap(s,tomorrow).correct,0);
});
test('progress questions use the selected chat topic without changing the active activity',()=>{
 const s=fresh();startSession(s,'diagnostic');submitAnswer(s,'1/4',now);
 const result=answerPrepared(s,'context:status','python-loop');assert.match(result.text,/Repetir con bucles/);assert.match(result.text,/0 aciertos en 0 intentos/);
 const reply=answerPrepared(s,'topic:python-loop:simple','python-loop');assert.equal(reply.action,undefined);assert.equal(s.events.length,1);
});
