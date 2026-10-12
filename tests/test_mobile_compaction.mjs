import test from 'node:test';
import assert from 'node:assert/strict';
import {newState,startSession,submitAnswer,advance,requestHelp,evidence,compactEvents} from '../public/mobile/engine.mjs';
import {allTopics,questionById} from '../public/mobile/course.mjs';
import {validateState,parseBackup,exportBackup} from '../public/mobile/storage.mjs';
const now=new Date('2026-10-10T12:00:00Z');
const profile=()=>({id:crypto.randomUUID(),name:'Estudiante',goal:'school',level:'practice',minutes:10});
function finish(s,wrong){if(s.session.phase==='lesson')advance(s,now);while(s.session.phase==='practice'){const q=questionById(s.session.questionIds[s.session.index]);submitAnswer(s,wrong?q.options.find(a=>a!==q.answer):q.answer,now);advance(s,now);}}

test('profiles past 5000 events keep working and keep the same evidence',()=>{
 const s={...newState(profile()),revision:1};
 startSession(s,'diagnostic');finish(s,false);
 const topic=allTopics.find(t=>t.courseId==='fractions-v1'&&!t.prerequisite);
 // Before the fix the 5000th event threw "alcanzaste el límite local de evidencias" forever.
 let round=0;
 while(s.events.length<4990){startSession(s,'review',topic.id);if(round%3===0)requestHelp(s,'explain',now);finish(s,round%2===0);round++;}
 const before=Object.fromEntries(allTopics.map(t=>[t.id,evidence(s,t.id,now)]));
 while(s.events.length<5000||!s.events.some(e=>e.type==='summary')){startSession(s,'review',topic.id);finish(s,false);}
 assert.ok(s.events.length<=5000);
 const summary=s.events.find(e=>e.type==='summary'&&e.topicId===topic.id);
 assert.ok(summary&&summary.attempts>0);
 validateState(s);
 const restored=parseBackup(exportBackup(s));
 assert.deepEqual(evidence(restored,topic.id,now).attempts,evidence(s,topic.id,now).attempts);
 // Compacting by itself never changes mastery.
 const copy=structuredClone(s);compactEvents(copy);
 for(const t of allTopics){const a=evidence(s,t.id,now),b=evidence(copy,t.id,now);
  for(const key of ['attempts','correct','incorrect','hints','explanations','practice_count','quiz_count','score','next_review'])assert.equal(b[key],a[key],`${t.id}.${key}`);}
 assert.ok(before[topic.id].attempts<evidence(s,topic.id,now).attempts);
});

test('a summary with inconsistent counters is rejected on import',()=>{
 const s={...newState(profile()),revision:1};
 s.events.push({id:crypto.randomUUID(),type:'summary',topicId:allTopics[0].id,at:now.toISOString(),attempts:2,correct:5,incorrect:0,hints:0,explanations:0,practice:0,checks:0});
 assert.throws(()=>validateState(s));
});
