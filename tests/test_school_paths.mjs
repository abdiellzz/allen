import test from 'node:test';
import assert from 'node:assert/strict';
import {newState,chooseCourse,startSession,submitAnswer,advance,recommendation} from '../public/mobile/engine.mjs';
import {courses,questionById} from '../public/mobile/course.mjs';
import {validateState,exportBackup,parseBackup,prepareRecovery} from '../public/mobile/storage.mjs';
const fresh=()=>({...newState({id:crypto.randomUUID(),name:'Ana',goal:'school',level:'bases'}),revision:1});
test('paths can be switched mid-answer and recover independently without a time preference',()=>{
 const s=fresh();startSession(s,'diagnostic');submitAnswer(s,'1/4');advance(s);const math=structuredClone(s.session);
 chooseCourse(s,'geography-school-v1');assert.equal(s.session,null);assert.deepEqual(s.savedSessions['fractions-v1'],math);
 startSession(s,'diagnostic');let q=questionById(s.session.questionIds[0]);submitAnswer(s,q.answer);advance(s);const geography=structuredClone(s.session);
 chooseCourse(s,'study-school-v1');startSession(s,'diagnostic');const copy=prepareRecovery(exportBackup(s));assert.equal(copy.profile.minutes,undefined);assert.deepEqual(copy.savedSessions,s.savedSessions);
 chooseCourse(copy,'fractions-v1');assert.deepEqual(copy.session,math);assert.deepEqual(copy.savedSessions['geography-school-v1'],geography);assert.match(recommendation(copy).reason,/ritmo/);assert.doesNotMatch(recommendation(copy).reason,/minutos|undefined/);validateState(copy);
 const other=fresh();assert.equal(other.savedSessions,undefined);
});
test('parked sessions reject foreign course questions, forged answers and nested settings',()=>{
 const s=fresh();startSession(s,'diagnostic');chooseCourse(s,'geography-school-v1');const bad=structuredClone(s);bad.savedSessions['fractions-v1'].courseId='geography-school-v1';assert.throws(()=>validateState(bad));
 const bad2=structuredClone(s);bad2.savedSessions['fractions-v1'].questionIds[0]='geography-school-d1';assert.throws(()=>validateState(bad2));
 const extra=structuredClone(s);extra.savedSessions['fractions-v1'].remoteSecrets='not-allowed';const copy=parseBackup(exportBackup(extra));assert.equal(copy.savedSessions['fractions-v1'].remoteSecrets,undefined);
});
test('new subjects have independent module roots and real transfer checks',()=>{
 const added=courses.filter(c=>c.id.endsWith('-school-v1'));assert.equal(added.length,8);
 for(const c of added){assert.equal(c.topics.length,16);assert.equal(c.topics.filter(t=>!t.prerequisite).length,4);for(const t of c.topics){const check=t.questions.find(q=>q.kind==='check');assert.notEqual(check.prompt,t.questions.find(q=>q.kind==='practice').prompt);assert.ok(check.feedback.length>40);assert.equal(check.options.length,3);assert.equal(new Set(check.options).size,3);assert.equal(t.questions.filter(q=>q.kind==='practice').length,2);}}
});
