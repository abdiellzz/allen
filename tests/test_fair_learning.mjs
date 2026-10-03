import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {freshVisitor,readVisitor,saveVisitor,effectiveDifficulty,answerPoints,chooseQuestions,rankFor,rankProgress,award} from '../frontend/fair-session.js';
import {LearningExperiences,EXPERIENCE_GROUPS} from '../frontend/fair-learning.js';
import {gameZone,createGame} from '../frontend/game-adventure.js';
const data=Object.fromEntries(['lessons','challenges','simulations','steam_projects','tech_topics','curiosities','assessments','routes','ranks','achievements','motivational_messages'].map(key=>[key,JSON.parse(readFileSync(new URL(`../data/${key}.json`,import.meta.url),'utf8'))]));
test('all lesson areas have at least four complete six-step topics and paired assessments',()=>{
 const d=data.lessons;
 assert.equal(new Set(d.lessons.map(l=>l.id)).size,d.lessons.length);
 for(const area of d.areas)assert.ok(d.lessons.filter(l=>l.area===area).length>=4,area);
 for(const l of d.lessons){for(const field of ['concept','conceptEasy','example','altExample','howItWorks','realWorld','question','feedback','quickSummary'])assert.ok(l[field]?.length>10,l.id+': '+field);assert.ok(l.options[l.correct]);assert.equal(new Set(l.options).size,l.options.length);}
 assert.ok(d.lessons.filter(l=>l.area==='Ciberseguridad').length>=11);
 for(const l of d.lessons){assert.ok(l.practice);const a=data.assessments.topics[l.id];for(const phase of ['pre','post']){assert.equal(a[phase].length,3);for(const q of a[phase]){assert.ok(q.options[q.correct]);assert.equal(new Set(q.options).size,q.options.length);}}}
});
test('every challenge category supports five genuinely advanced questions without repetitions',()=>{
 for(const c of data.challenges.categories.filter(c=>c!=='Mixto')){
  for(const difficulty of ['Fácil','Normal','Difícil']){
   const round=chooseQuestions(data.challenges.questions,c,difficulty,5);
   assert.equal(round.length,5,c);assert.equal(new Set(round.map(q=>q.question)).size,5,c);
   if(difficulty==='Difícil')assert.ok(round.every(q=>q.difficulty==='Difícil'),c);
  }
 }
 for(const q of data.challenges.questions){assert.ok(q.options[q.correct]);assert.ok(q.hint);assert.ok(q.explanation);assert.equal(new Set(q.options).size,q.options.length);}
});
test('scoring gives exactly 100, 75, 50, or zero',()=>{
 assert.equal(answerPoints(true,1,false),100);assert.equal(answerPoints(true,1,true),75);
 assert.equal(answerPoints(true,2,false),50);assert.equal(answerPoints(true,2,true),50);assert.equal(answerPoints(false,2,true),0);
});
test('visitor session restores indefinitely without contaminating aggregate counters',()=>{
 const values=new Map(),storage={getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v)};
 const v={...freshVisitor(),name:'Daniel',difficulty:'Normal',ready:true,score:175,achievements:['Phishing']};saveVisitor(storage,v);
 assert.equal(readVisitor(storage).name,'Daniel');assert.equal(readVisitor(storage).score,175);assert.deepEqual([...values.keys()],['visitorSession']);
 values.set('visitorSession',JSON.stringify({...v,updatedAt:0,projects:{'steam:x':{status:'SUBMITTED'}},score:875}));assert.equal(readVisitor(storage).name,'Daniel');assert.equal(readVisitor(storage).score,875);assert.equal(readVisitor(storage).projects['steam:x'].status,'SUBMITTED');
 values.set('visitorSession','bad JSON');assert.equal(readVisitor(storage).ready,false);
});
test('adaptive difficulty responds to verified points and game questions change at difficult level',()=>{
 const v={...freshVisitor(),difficulty:'Sorpréndeme'};assert.equal(effectiveDifficulty(v),'Fácil');v.score=200;assert.equal(effectiveDifficulty(v),'Normal');v.score=600;assert.equal(effectiveDifficulty(v),'Difícil');
 const g=createGame(),easy=gameZone(g).question;g.level='Universidad / Técnico';assert.notEqual(gameZone(g).question,easy);
});
test('eleven experiences, local scenarios, project interests and surprises are complete',()=>{
 assert.equal(EXPERIENCE_GROUPS.flatMap(([,items])=>items).length,11);
 for(const s of data.simulations.scenarios){assert.equal(s.options.filter(o=>o.isCorrect).length,1);assert.ok(s.allenExplanation);assert.ok(s.lesson);}
 for(const interest of data.steam_projects.interests)assert.ok(data.steam_projects.projects.some(p=>p.interest.includes(interest)),interest);
 for(const p of data.steam_projects.projects){for(const field of ['name','problem','solution','difficulty','estimatedTime'])assert.ok(p[field]);for(const field of ['materials','learnings','steps'])assert.ok(p[field].length);}
 assert.equal(data.tech_topics.areas.length,12);assert.equal(new Set(data.curiosities.activities.map(a=>a.type)).size,12);
});
test('diagnostic 1/3 to 3/3 awards exact bonuses once and stores comparison',async()=>{
 let events=[];const visitor={...freshVisitor(),name:'Daniel'},host={visitor,render(){},toast(){},motivate(){},reward:(n,a,k)=>award(visitor,n,a,k),complete:(m,k,n)=>{if(award(visitor,n,'','complete:'+k)){visitor.activitiesCompleted++;visitor.metrics[m]=(visitor.metrics[m]||0)+1;}},event:(...e)=>events.push(e)};
 const ui=new LearningExperiences(host);ui.data=data;
 await ui.handle('area','Ciberseguridad');await ui.handle('lesson','ciber_phishing');
 const a=data.assessments.topics.ciber_phishing;
 for(let i=0;i<3;i++)await ui.handle('assessment-answer',String(i===0?a.pre[i].correct:(a.pre[i].correct+1)%3));
 assert.match(ui.learn(),/Paso 1 de 6/);assert.match(ui.learn(),/Daniel/);
 await ui.handle('example');assert.match(ui.learn(),/WhatsApp/);
 for(let i=0;i<4;i++)await ui.handle('continue');assert.match(ui.learn(),/Práctica/);
 await ui.handle('lesson-answer','1');await ui.handle('lesson-answer','1');assert.equal(visitor.score,125);
 await ui.handle('continue');assert.match(ui.learn(),/Paso 6 de 6/);await ui.handle('post-start');
 for(const q of a.post)await ui.handle('assessment-answer',String(q.correct));
 assert.equal(visitor.score,625);assert.equal(visitor.preAssessmentScore,1);assert.equal(visitor.postAssessmentScore,3);assert.match(ui.learn(),/Mejoraste 2 respuestas/);
 const before=visitor.score;ui.finishLesson();assert.equal(visitor.score,before);assert.equal(visitor.activitiesCompleted,1);
 assert.equal(rankFor(visitor.score,data.ranks.ranks).name,'Aprendiz Digital');
 await ui.handle('scenario','sim1');await ui.handle('sim-answer','1');await ui.handle('sim-answer','1');assert.equal(visitor.score,725);
});
test('rank boundaries, progression and idempotent rewards',()=>{
 for(const [score,name] of [[0,'Explorador'],[499,'Explorador'],[500,'Aprendiz Digital'],[1000,'Constructor'],[2000,'Innovador'],[3500,'Tecnólogo'],[5000,'Maestro Allen']])assert.equal(rankFor(score,data.ranks.ranks).name,name);
 const p=rankProgress(2450,data.ranks.ranks);assert.equal(p.remaining,1050);assert.equal(p.next.min,3500);
 const v=freshVisitor();assert.equal(award(v,200,'','route:a'),true);assert.equal(award(v,200,'','route:a'),false);assert.equal(v.score,200);
});
test('all ten roadmaps reference local lessons, expose their stages and guard locked modules',async()=>{
 const host={visitor:freshVisitor(),render(){},toast(){},reward(){},complete(){},event(){}};const ui=new LearningExperiences(host);ui.data=data;
 assert.equal(data.routes.routes.length,10);
 for(const r of data.routes.routes){assert.ok(r.modules.length>=4&&r.modules.length<=6);for(const m of r.modules)assert.ok(data.lessons.lessons.some(l=>l.id===m.lesson));assert.ok(r.finalProject.checklist.length>=3);}
 assert.deepEqual(data.routes.routes.slice(0,5).map(r=>r.name),['Fundamentos Digitales','Python desde cero','Ciberseguridad Básica','Introducción a IA','STEAM y proyectos']);
 await ui.paths.handle('path-open','digital');const r=data.routes.routes[0];
 assert.match(ui.paths.render(),/Módulos/);assert.match(ui.paths.render(),/Práctica y evaluación/);assert.match(ui.paths.render(),/Proyecto final/);
 await ui.paths.handle('path-module',r.modules[1].lesson);assert.equal(ui.lesson,null);
 await ui.paths.handle('path-module',r.modules[0].lesson);assert.equal(ui.lesson.id,r.modules[0].lesson);
 ui.paths.markLesson(r.modules[0].lesson);await ui.paths.handle('path-module',r.modules[1].lesson);assert.equal(ui.lesson.id,r.modules[1].lesson);
 await ui.paths.handle('path-challenge');assert.equal(ui.paths.challenge,null);
 for(const m of r.modules)ui.paths.markLesson(m.lesson);await ui.paths.handle('path-challenge');assert.equal(ui.paths.challenge.questions.length,3);
});
test('route final projects use the shared evaluation flow before awarding project points',async()=>{
 const visitor=freshVisitor();visitor.difficulty='Normal';let events=[];
 const host={visitor,render(){},persist(){},toast(){},motivate(){},reward:(n,a,k)=>award(visitor,n,a,k),complete:(m,k,n)=>award(visitor,n,'','complete:'+k),event:(...e)=>events.push(e),evaluateLocal:async()=>({demo:false,text:'Tu evidencia explica los pasos con claridad. Añade una segunda prueba para ampliar el proyecto.'})};
 const ui=new LearningExperiences(host);ui.data=data;await ui.paths.handle('path-open','digital');const route=data.routes.routes.find(r=>r.id==='digital');const state=ui.paths.state();state.modules=route.modules.map(m=>m.lesson);state.challenge=true;await ui.paths.handle('path-final');
 const oldDocument=globalThis.document,oldFormData=globalThis.FormData;
 try{globalThis.document={querySelector:()=>({reportValidity:()=>true,querySelectorAll:()=>[{checked:true},{checked:true},{checked:true}]})};globalThis.FormData=class{get(name){return ({description:'Preparé una maqueta y expliqué sus pasos en orden.',materials:'Papel, regla y lápiz',reflection:'Lo más difícil fue medir; aprendí a comprobar las medidas.'})[name];}};await ui.paths.handle('path-project','digital');assert.equal(state.projectSubmission.status,'COMPLETED');assert.ok(['LOCAL_EVALUATED','AI_FEEDBACK_ADDED'].includes(state.projectSubmission.evaluationStatus));assert.equal(state.complete,true);assert.equal(visitor.score,400);assert.equal(events.filter(e=>e[0]==='project_completed').length,1);}finally{globalThis.document=oldDocument;globalThis.FormData=oldFormData;}
});
