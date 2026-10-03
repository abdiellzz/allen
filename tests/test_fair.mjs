import test from 'node:test';
import assert from 'node:assert/strict';
import {SpeechRecognitionService,TextToSpeechService} from '../frontend/fair-voice.js';
import {inactivityDecision,lessons} from '../frontend/fair-content.js';
import {freshVisitor,award,markAchievementViewed,buildSessionSummary,saveSessionSummary,readVisitor,saveVisitor} from '../frontend/fair-session.js';
import {AchievementCard,AchievementModal} from '../frontend/components/achievements.js';
import {GameResult} from '../frontend/game-adventure.js';
import {getAllenPose,AllenPose} from '../frontend/components/fair-mascot.js';
test('inactive visitor enters AFK without resetting; empty home attracts',()=>{
 assert.equal(inactivityDecision(119999,-1,true,false),'afk');
 assert.equal(inactivityDecision(120000,-1,true,false),'afk');
 assert.equal(inactivityDecision(140000,20000,true,false),'afk');
 assert.equal(inactivityDecision(45000,-1,false,true),'attract');
 assert.equal(inactivityDecision(45000,-1,true,true),'stay');
});
test('every offline micro lesson includes a valid answer and feedback',()=>{
 assert.equal(Object.keys(lessons).length,6);
 for(const lesson of Object.values(lessons)){assert.equal(lesson.options.length,3);assert.ok(lesson.options[lesson.correct]);assert.ok(lesson.feedback.length>20);}
});
test('speech defaults off and local mode never silently switches to cloud',async()=>{
 globalThis.window={SpeechRecognition:class{start(){throw new Error('must not start cloud recognition');}}};
 const speech=new SpeechRecognitionService();
 await assert.rejects(speech.listen(()=>{},()=>{}),/Puedes escribirme/);
 speech.mode='local';await assert.rejects(speech.listen(()=>{},()=>{}),/no ofrece reconocimiento local/);
});
test('cancelled recognition cannot deliver an old visitor transcript',async()=>{
 let instance,received=false;
 globalThis.window={SpeechRecognition:class{constructor(){instance=this;this.processLocally=false;}start(){}abort(){}}};
 const speech=new SpeechRecognitionService();speech.mode='local';
 await speech.listen(()=>received=true,()=>{});assert.equal(instance.processLocally,true);
 speech.cancel();instance.onresult({results:[[{transcript:'private'}]]});assert.equal(received,false);
});
test('TTS rejects remote voices and handles absent browser audio',()=>{
 globalThis.window={};const tts=new TextToSpeechService();tts.enabled=true;
 assert.throws(()=>tts.play('hello'),/No hay una voz/);tts.pause();tts.resume();tts.stop();
 globalThis.window={speechSynthesis:{getVoices:()=>[{lang:'es-ES',localService:false}],cancel(){}}};
 assert.throws(()=>tts.play('hello'),/No hay una voz/);
});
test('game result only offers an unlocked achievement and includes actual score and duration',()=>{
 const g={mode:'quick',level:'Premedia',index:2,score:220,pointsEarned:220,elapsedSeconds:83,correct:2,totalHints:1,collected:['Llave'],name:'',newAchievement:null};
 const without=GameResult(g);assert.doesNotMatch(without,/Mostrar logro/);assert.match(without,/220 puntos ganados/);assert.match(without,/1:23 tiempo/);
 g.newAchievement={id:'first_game',name:'Primera aventura',icon:'gamepad-2'};
 const withAchievement=GameResult(g);assert.match(withAchievement,/Mostrar logro/);assert.match(withAchievement,/data-achievement-open="first_game"/);
});
test('opening an achievement marks it viewed but never awards points again',()=>{
 const visitor=freshVisitor();visitor.achievements.push('Primer reto');visitor.newAchievements.push('first_challenge');
 assert.equal(award(visitor,150,'','first-reward'),true);const score=visitor.score,rewards=[...visitor.rewards];
 markAchievementViewed(visitor,'first_challenge');markAchievementViewed(visitor,'first_challenge');
 assert.equal(visitor.score,score);assert.deepEqual(visitor.rewards,rewards);assert.deepEqual(visitor.newAchievements,[]);assert.deepEqual(visitor.viewedAchievements,['first_challenge']);
 const modal=AchievementModal({name:'Primer reto',description:'Completaste el primer reto.'},{score:150,ranks:[{name:'Explorador',min:0},{name:'Aprendiz Digital',min:500}]});assert.match(modal,/LOGRO DESBLOQUEADO/);assert.match(modal,/Primer reto/);
});
test('achievement card shows new and unlocked states with local Lucide icon',()=>{
 const card=AchievementCard({name:'Primera aventura',description:'Terminaste tu primera aventura.',icon:'gamepad-2',points:0},{state:'new'});
 assert.match(card,/achievement-new/);assert.match(card,/NUEVO/);assert.match(card,/achievement-icon/);
 assert.match(AchievementCard({name:'Logro futuro'},{state:'locked'}),/Por descubrir/);
 assert.match(AchievementCard({name:'Logro ganado'},{state:'unlocked'}),/Desbloqueado/);
});
test('missing Allen poses use the existing inline mascot without requesting absent images',()=>{
 assert.equal(getAllenPose('achievement'),null);const fallback=AllenPose('achievement','medium');assert.match(fallback,/<svg/);assert.doesNotMatch(fallback,/<img/);
 assert.equal(getAllenPose('achievement',{trophy:'/static/assets/allen/allen-trophy.png'}),'/static/assets/allen/allen-trophy.png');
});
test('session summary uses real visitor counters and stores idempotently without touching aggregate stats',()=>{
 const visitor=freshVisitor();visitor.visitorId='visitor-a';visitor.name='Ada';visitor.difficulty='Normal';visitor.sessionStartedAt=1000;visitor.score=350;visitor.rank='Explorador';visitor.activitiesCompleted=4;visitor.metrics.games=1;visitor.metrics.projects=1;visitor.achievements=['Primer reto'];visitor.routes.r1={modules:['m1'],challenge:true};visitor.projects.p1={status:'COMPLETED',evidence:{description:'local'}};
 const summary=buildSessionSummary(visitor,61000,[{id:'r1',name:'Python desde cero'}]);assert.equal(summary.pointsEarned,350);assert.equal(summary.gamesCompleted,1);assert.equal(summary.projectsCompleted,1);assert.equal(summary.durationSeconds,60);assert.deepEqual(summary.routeProgress,[{id:'r1',name:'Python desde cero',modulesCompleted:1,challengeCompleted:true,projectCompleted:false,completed:false}]);
 const values=new Map([['eventStats','{"games":9}']]);const storage={getItem:key=>values.get(key)||null,setItem:(key,value)=>values.set(key,value),removeItem:key=>values.delete(key)};
 assert.equal(saveSessionSummary(storage,summary),true);assert.equal(saveSessionSummary(storage,summary),true);const history=JSON.parse(values.get('allenSessionHistory'));assert.equal(history.length,1);assert.deepEqual(history[0].projectHistory.p1,visitor.projects.p1);assert.deepEqual(history[0].routeHistory.r1,visitor.routes.r1);assert.equal(values.get('eventStats'),' {"games":9}'.trim());
 saveVisitor(storage,visitor);assert.equal(readVisitor(storage).score,350);assert.equal(readVisitor(storage).achievements[0],'Primer reto');assert.ok(values.has('visitorSession'));
});
