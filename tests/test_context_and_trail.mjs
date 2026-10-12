import test from 'node:test';
import assert from 'node:assert/strict';
import {allTopics,courses,topicById,questionById} from '../public/mobile/course.mjs';
import {newState,startSession,submitAnswer,chooseCourse,advance} from '../public/mobile/engine.mjs';
import {labFor,freshLab} from '../public/mobile/learning-labs.mjs';
import {labView,rankPanel} from '../public/mobile/lab-ui.mjs';
import {numericResult} from '../public/mobile/topic-models.mjs';
import {freshTrail,moveTrail,saveTrail,trailLevels,trailDirections,trailBlocked,validateTrail,trailView} from '../public/mobile/allen-trail.mjs';
import {validateState,exportBackup,parseBackup} from '../public/mobile/storage.mjs';
import {errorCoach} from '../public/mobile/learning-coach.mjs';
import {routeMatches,lessonStage,crossProjects} from '../public/mobile/route-discovery.mjs';
import {answerPrepared} from '../public/mobile/guided-tutor.mjs';
const fresh=()=>({...newState({id:crypto.randomUUID(),name:'Ana',goal:'school',level:'bases'}),revision:1});
function path(start,end){const queue=[[start,[]]],visited=new Set();while(queue.length){const [p,steps]=queue.shift(),key=`${p.x},${p.y}`;if(visited.has(key))continue;visited.add(key);if(p.x===end.x&&p.y===end.y)return steps;for(const [d,[dx,dy]] of Object.entries(trailDirections)){const n={x:p.x+dx,y:p.y+dy};if(!trailBlocked(n.x,n.y))queue.push([n,[...steps,d]]);}}throw Error('Unreachable target');}
test('topic models use exact authored operations rather than a subject-wide unrelated calculator',()=>{
 const checks=[['math-percent',/Precio final: 40/],['math-ratio',/9 unidades/],['math-integers',/-3 \+ 5 = 2/],['math-equation',/x = 5/],['geography-school-6',/20 habitantes/],['physics-school-workshop-2-1',/3 m\/s/],['chemistry-school-7',/10 g/],['money-school-4',/Saldo previsto: 5/],['money-school-6',/Precio final: 40/],['money-school-5',/Precio por unidad: 2/]];
 for(const [id,expected] of checks){const t=topicById(id),m=labFor(t);assert.match(numericResult(m,freshLab(t).values),expected);assert.equal(labFor(courses.find(c=>c.id===t.courseId).topics.find(t=>t.id===id)).kind,m.kind);}
 assert.match(numericResult(labFor(topicById('physics-school-3')),[60,0,0]),/no puede ser cero/);
 assert.equal(labFor(topicById('geography-school-4')).kind,'case');
 assert.deepEqual(labFor(topicById('chemistry-school-2')).molecule.counts,[['C',1],['O',2]]);
 assert.equal(labFor(topicById('chemistry-school-workshop-4-2')).kind,'number');
 assert.equal(labFor(topicById('english-workshop-3-2')).sentence.join(' '),'The book is under the table.');
 assert.equal(labFor(topicById('english-articles')).sentence.join(' '),'An apple.');
 assert.deepEqual(labFor(topicById('history-school-1')).timeline.map(p=>p[0]),[1820,1830]);
});
test('all exploration views are tied to each lesson objective and retain valid model parameters',()=>{
 const s=fresh();for(const t of allTopics){s.learningLabs={[t.id]:{...freshLab(t),step:1}};const html=labView(t,s);assert.ok(html.includes(t.objective.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))));assert.doesNotMatch(html,/undefined|NaN|Infinity/);}
});
test('error coaching uses actual wrong choices, concrete first steps and selected profile/topic',()=>{
 const a=fresh(),b=fresh();startSession(a,'diagnostic');const q=questionById(a.session.questionIds[0]),wrong=q.options.find(o=>o!==q.answer);submitAnswer(a,wrong);const before=JSON.stringify(a),c=errorCoach(a,q.topicId);assert.equal(c.answer,wrong);assert.ok(c.reason.includes(q.feedback));assert.equal(c.firstStep,q.hints[0]);assert.equal(errorCoach(b),null);assert.equal(errorCoach(a,'python-loop'),null);assert.ok(answerPrepared(a,'context:error-next').text.includes(q.hints[0]));assert.equal(JSON.stringify(a),before);
});
test('route filters distinguish pending work, observed errors and new paths without modifying sessions',()=>{
 const s=fresh(),math=courses[0],english=courses.find(c=>c.id==='english-v1');assert.equal(routeMatches(math,s,'continue'),false);startSession(s,'diagnostic');const q=questionById(s.session.questionIds[0]);submitAnswer(s,q.options.find(o=>o!==q.answer));assert.equal(routeMatches(math,s,'continue'),true);assert.equal(routeMatches(math,s,'reinforce'),true);chooseCourse(s,english.id);assert.equal(routeMatches(math,s,'continue'),true);assert.equal(routeMatches(english,s,'explore'),true);const before=JSON.stringify(s);for(const c of courses)routeMatches(c,s,'reinforce','project');assert.equal(JSON.stringify(s),before);assert.equal(lessonStage(topicById('english-workshop-1-2')),'project');assert.ok(crossProjects.every(p=>p.courses.length>=3&&p.steps.length===3));
});
test('every trail stage is solvable with touch/keyboard directions and never grants educational mastery',()=>{
 const s=fresh(),before=JSON.stringify({events:s.events,completed:s.completed});for(let level=0;level<trailLevels.length;level++){let t=freshTrail(level);for(const goal of trailLevels[level].targets){for(const d of path(t,goal))t=moveTrail(t,d).trail;}assert.deepEqual(t.collected,[0,1,2]);saveTrail(s,t);validateState(s);assert.equal(moveTrail(t,'north').trail.moves,t.moves);assert.match(trailView(s),/Páginas recuperadas/);}assert.equal(JSON.stringify({events:s.events,completed:s.completed}),before);assert.equal(fresh().allenTrail,undefined);assert.deepEqual(parseBackup(exportBackup(s)).allenTrail,s.allenTrail);
});
test('trail boundaries, rocks, future page order and malicious backup payloads are bounded',()=>{
 assert.match(moveTrail(freshTrail(),'west').message,/borde/);assert.throws(()=>moveTrail(freshTrail(),'teleport'));assert.throws(()=>validateTrail({...freshTrail(),x:1,y:1}));assert.throws(()=>validateTrail({...freshTrail(),collected:[2]}));assert.throws(()=>validateTrail({...freshTrail(),level:3}));const s=fresh();saveTrail(s,freshTrail());s.allenTrail.inject='<script>';const clean=parseBackup(exportBackup(s));assert.equal(clean.allenTrail.inject,undefined);const bad=structuredClone(s);bad.allenTrail.moves=10001;assert.throws(()=>validateState(bad));
});
test('glass preference survives backup and rejects unsupported surfaces',()=>{
 const s=fresh();s.preferences={textSize:'normal',surface:'solid'};assert.equal(parseBackup(exportBackup(s)).preferences.surface,'solid');s.preferences.surface='external';assert.throws(()=>validateState(s));
});
test('rank evidence describes checked objectives and both next thresholds',()=>{
 const s=fresh();assert.match(rankPanel(s),/Temas para Aprendiz/);assert.match(rankPanel(s),/Explicaciones para Aprendiz/);assert.match(rankPanel(s),/primer objetivo comprobado/);startSession(s,'diagnostic');while(s.session.phase!=='complete'){submitAnswer(s,questionById(s.session.questionIds[s.session.index]).answer);advance(s);}startSession(s,'learn','parts');advance(s);while(s.session.phase!=='complete'){submitAnswer(s,questionById(s.session.questionIds[s.session.index]).answer);advance(s);}assert.match(rankPanel(s),/Objetivo comprobado: Partes de un entero/);
});
