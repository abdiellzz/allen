import test from 'node:test';
import assert from 'node:assert/strict';
import {newState,startSession,submitAnswer,advance,requestHelp,evidence,recommendation,reviewCard,localDay,nextReviewDate,computeMastery,chooseCourse} from '../public/mobile/engine.mjs';
import {course,courses,allTopics,questionById} from '../public/mobile/course.mjs';
import {validateState,parseBackup,exportBackup,prepareRecovery} from '../public/mobile/storage.mjs';
import {hasAccess,paidEntitlement,requestGenerativeTutor} from '../public/mobile/capabilities.mjs';
const now=new Date('2026-10-10T12:00:00Z');
const profile=()=>({id:crypto.randomUUID(),name:'Estudiante',goal:'school',level:'practice',minutes:10});
const state=()=>({...newState(profile()),revision:1});
function finish(s,wrong=false){if(s.session.phase==='lesson')advance(s,now);while(s.session.phase==='practice'){const q=questionById(s.session.questionIds[s.session.index]);submitAnswer(s,wrong?q.options.find(a=>a!==q.answer):q.answer,now);advance(s,now);}}
function diagnosed(){const s=state();startSession(s,'diagnostic');finish(s);return s;}

test('diagnosis, hints, checks and due reviews form a complete learning cycle',()=>{
 const s=state();assert.equal(recommendation(s,now).kind,'diagnostic');startSession(s,'diagnostic');finish(s);
 assert.equal(s.diagnosticComplete,true);assert.equal(s.events.filter(e=>e.type==='answer').length,6);assert.equal(s.completed.length,0);
 assert.equal(recommendation(s,now).topicId,'parts');startSession(s,'learn','parts');advance(s,now);
 assert.match(requestHelp(s,'hint',now).text,/numerador/);assert.equal(evidence(s,'parts',now).hints,1);
 finish(s);assert.deepEqual(s.completed,['parts']);assert.equal(recommendation(s,now).topicId,'equivalent');
 const due=evidence(s,'parts',now).next_review;assert.ok(due);const r=recommendation(s,new Date(`${due}T12:00:00Z`));assert.equal(r.kind,'review');assert.equal(r.topicId,'parts');
 reviewCard(s,'parts',false,now);assert.equal(s.cards.parts.due,nextReviewDate(20,now));validateState(s);
});

test('questions cannot be submitted twice or skipped and prerequisites cannot be bypassed',()=>{
 const s=diagnosed();assert.throws(()=>startSession(s,'learn','sum'),/Primero/);startSession(s,'learn','parts');assert.throws(()=>startSession(s,'learn','parts'),/Continúa/);advance(s,now);
 assert.throws(()=>advance(s,now),/Responde/);const q=questionById(s.session.questionIds[0]);submitAnswer(s,q.answer,now);assert.throws(()=>submitAnswer(s,q.answer,now),/registrada/);assert.throws(()=>requestHelp(s,'hint',now),/antes/);
 assert.equal(evidence(s,'parts',now).attempts,3); // two diagnostic answers + one practice
});

test('failed transfer check keeps topic incomplete and recommendation explains reinforcement',()=>{
 const s=diagnosed();startSession(s,'learn','parts');finish(s,true);assert.equal(s.completed.length,0);assert.equal(recommendation(s,now).topicId,'parts');assert.match(recommendation(s,now).reason,/práctica|reconstruir/);
});

test('hint budget is bounded and help does not reveal a solution to an unanswered exercise',()=>{
 const s=diagnosed();startSession(s,'learn','parts');advance(s,now);requestHelp(s,'hint',now);requestHelp(s,'hint',now);requestHelp(s,'hint',now);assert.equal(s.session.hints.length,2);assert.equal(s.session.answers.length,0);
});

test('all fraction lessons can be completed and backup restores resume position',()=>{
 const s=diagnosed();for(const t of course.topics){startSession(s,'learn',t.id);finish(s);}assert.equal(s.completed.length,course.topics.length);
 const copy=parseBackup(exportBackup(s));assert.deepEqual(copy.completed,s.completed);assert.equal(copy.session.phase,'complete');
 startSession(s,'review','parts');advance(s,now);const q=questionById(s.session.questionIds[0]);submitAnswer(s,q.answer,now);const resumed=parseBackup(exportBackup(s));assert.equal(resumed.session.answers.length,1);assert.throws(()=>submitAnswer(resumed,q.answer),/registrada/);
});

test('invalid backup data is rejected and arbitrary settings cannot enable paid features or AI',async()=>{
 const s=diagnosed();const bad=structuredClone(s);bad.events[0].correct=false;assert.throws(()=>validateState(bad));
 const oversized=structuredClone(s);oversized.profile.minutes=99;assert.throws(()=>validateState(oversized));
 assert.throws(()=>parseBackup('x'.repeat(2_000_001)));assert.throws(()=>parseBackup('{}'));
 const payload=JSON.parse(exportBackup(s));payload.state.entitlements={premium:true};payload.state.remoteAI='https://attacker.invalid';const cleaned=parseBackup(JSON.stringify(payload));assert.equal(cleaned.entitlements,undefined);assert.equal(cleaned.remoteAI,undefined);
 assert.equal(hasAccess('premium'),false);assert.equal(paidEntitlement().active,false);await assert.rejects(()=>requestGenerativeTutor());
});

test('profiles hold independent evidence and review dates follow device calendar',()=>{
 const a=diagnosed(),b=state();startSession(a,'learn','parts');finish(a);assert.equal(evidence(b,'parts',now).attempts,0);assert.equal(b.completed.length,0);
 const edge=new Date(2026,11,31,23,55);assert.equal(localDay(edge),'2026-12-31');assert.equal(nextReviewDate(0,edge),'2027-01-01');
 assert.deepEqual(computeMastery({},now),{score:0,confidence:0,status:'new'});
});

test('every editorial question has valid answers, feedback, sources and bounded hints',()=>{
 const ids=new Set();for(const t of course.topics){assert.ok(t.objective&&t.explanation&&t.simple&&t.example&&t.alternative&&t.card.front&&t.card.back);for(const q of t.questions){assert.ok(!ids.has(q.id));ids.add(q.id);assert.ok(q.options.includes(q.answer));assert.equal(new Set(q.options).size,q.options.length);assert.equal(q.hints.length,2);assert.ok(q.feedback.length>30);}}
});

test('recovery preserves valid maximum-length names without overwriting profile identity',()=>{
 const s=diagnosed();s.profile.name='a'.repeat(40);const copy=prepareRecovery(exportBackup(s));assert.equal(copy.profile.name.length,40);assert.notEqual(copy.profile.id,s.profile.id);validateState(copy);
});


test('all school and skill courses diagnose, teach, validate and review through one engine',()=>{
 const s=state();for(const c of courses){chooseCourse(s,c.id);assert.equal(recommendation(s,now).kind,'diagnostic');startSession(s,'diagnostic');assert.equal(s.session.questionIds.length,c.topics.flatMap(t=>t.questions).filter(q=>q.kind==='diagnostic').length);finish(s);for(const t of c.topics){startSession(s,'learn',t.id);requestHelp(s,'simple',now);finish(s);assert.ok(s.completed.includes(t.id));}validateState(s);}
 assert.equal(s.completed.length,143);assert.equal(allTopics.length,143);assert.equal(s.events.filter(e=>e.type==='answer').length,471);const copy=parseBackup(exportBackup(s));assert.deepEqual(copy.completed,s.completed);assert.deepEqual(copy.diagnosticCourses,s.diagnosticCourses);assert.equal(copy.activeCourse,'money-school-v1');
});

test('catalogue snapshot stays aligned with course source and editorial identifiers',async()=>{
 const {readFile}=await import('node:fs/promises');const json=JSON.parse(await readFile(new URL('../public/mobile/catalogue.json',import.meta.url),'utf8'));assert.deepEqual(json,courses);
 const ids=new Set();for(const c of courses){assert.ok(c.source);for(const t of c.topics){assert.ok(t.simple&&t.alternative&&t.card.back);if(t.prerequisite)assert.ok(c.topics.some(p=>p.id===t.prerequisite));for(const q of t.questions){assert.ok(!ids.has(q.id));ids.add(q.id);assert.ok(q.options.includes(q.answer));assert.equal(q.hints.length,2);assert.ok(q.feedback);}}}assert.equal(ids.size,471);
});

test('old backups migrate additively; course switching cannot discard a session',()=>{
 const s=diagnosed();delete s.activeCourse;const old=parseBackup(exportBackup(s));assert.equal(recommendation(old,now).topicId,'parts');chooseCourse(old,'reading-v1');startSession(old,'diagnostic');const pending=structuredClone(old.session);chooseCourse(old,'python-v1');assert.deepEqual(old.savedSessions['reading-v1'],pending);chooseCourse(old,'reading-v1');assert.deepEqual(old.session,pending);finish(old);old.preferences={textSize:'large'};const restored=parseBackup(exportBackup(old));assert.equal(restored.preferences.textSize,'large');const invalid=structuredClone(restored);invalid.session.courseId='english-v1';assert.throws(()=>validateState(invalid));assert.equal(restored.diagnosticComplete,true);assert.equal(restored.events.filter(e=>e.topicId==='parts').length,2);
});
