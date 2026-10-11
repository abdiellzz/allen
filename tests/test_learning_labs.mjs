import test from 'node:test';
import assert from 'node:assert/strict';
import {courses,allTopics,questionById} from '../public/mobile/course.mjs';
import {newState,startSession,advance,submitAnswer} from '../public/mobile/engine.mjs';
import {labFor,saveLab,saveReflection,rankFor,ranks} from '../public/mobile/learning-labs.mjs';
import {validateState,parseBackup,exportBackup} from '../public/mobile/storage.mjs';
import {labView} from '../public/mobile/lab-ui.mjs';
const fresh=()=>({...newState({id:crypto.randomUUID(),name:'Ana',goal:'school',level:'bases'}),revision:1});
function finish(s){if(s.session.phase==='lesson')advance(s);while(s.session.phase==='practice'){const q=questionById(s.session.questionIds[s.session.index]);submitAnswer(s,q.answer);advance(s);}}
test('each module contains real added workshops with bounded graded procedures',()=>{
 for(const c of courses)for(const label of new Set(c.topics.map(t=>t.module))){const topics=c.topics.filter(t=>t.module===label);assert.ok(topics.length>=4);assert.equal(topics.filter(t=>t.id.includes('-workshop-')).length,2);for(const t of topics.filter(t=>t.method)){assert.equal(t.steps.length,3);assert.ok(t.case[0].length>15);assert.equal(t.questions[0].activity,'order');assert.equal(t.questions[1].activity,'match');}}
});
test('exploration persists locally and never counts as correct attempts or topic completion',()=>{
 const s=fresh(),before=structuredClone(s.events);saveLab(s,'parts',{step:1,values:[2,4,0]});saveLab(s,'parts',{step:4,note:'<svg onload=alert(1)> no código'});assert.deepEqual(s.events,before);assert.deepEqual(s.completed,[]);assert.equal(rankFor(s).current.id,'explorer');
 const copy=parseBackup(exportBackup(s));assert.deepEqual(copy.learningLabs,s.learningLabs);assert.match(labView(allTopics.find(t=>t.id==='parts'),copy),/&lt;svg/);assert.doesNotMatch(labView(allTopics.find(t=>t.id==='parts'),copy),/<svg onload/);assert.throws(()=>saveLab(s,'parts',{step:6}));assert.throws(()=>saveLab(s,'parts',{note:'x'.repeat(801)}));assert.throws(()=>saveLab(s,'parts',{built:[0,0]}));
 const extra=structuredClone(s);extra.learningLabs.parts.remoteKey='bad';assert.equal(parseBackup(exportBackup(extra)).learningLabs.parts.remoteKey,undefined);
});
test('ranks use distinct checked topics and correct explain-back evidence, not clicks or streaks',()=>{
 const s=fresh();startSession(s,'diagnostic');finish(s);startSession(s,'learn','parts');finish(s);const attempts=s.events.length;saveReflection(s,'parts','parts','parts');assert.equal(s.events.length,attempts);assert.equal(rankFor(s).reflections,1);saveReflection(s,'parts','parts','parts');assert.equal(rankFor(s).reflections,1);assert.equal(rankFor(s).current.id,'explorer');validateState(s);
 const bad=structuredClone(s);bad.reflections.parts.rule='sum';assert.throws(()=>validateState(bad));const copy=parseBackup(exportBackup(s));assert.deepEqual(copy.reflections,s.reflections);
 assert.equal(ranks.length,5);for(const rank of ranks){const sample=fresh();sample.completed=allTopics.slice(0,rank.topics).map(t=>t.id);sample.reflections=Object.fromEntries(sample.completed.slice(0,rank.reflections).map(id=>[id,{rule:id,example:id,at:new Date().toISOString()}]));assert.equal(rankFor(sample).current.id,rank.id);}
});
test('methods differ across subjects and stage rendering is authored rather than code execution',()=>{
 const types=new Set(allTopics.map(t=>labFor(t).kind));assert.ok(types.size>=12);const s=fresh();for(const t of allTopics){saveLab(s,t.id,{step:1});const html=labView(t,s);assert.ok(html.includes('lab-stage'));assert.ok(!html.includes('undefined'));}assert.equal(s.completed.length,0);
});
