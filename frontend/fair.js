import {api,setToken} from './services.js';
import {icon} from './components/ui.js';
import {AllenMascot,AllenPose} from './components/fair-mascot.js';
import {escapeHTML as esc,markdown} from './components/markdown.js';
import {getAvailableActions,actions} from './components/actions.js';
import {inactivityDecision,ATTRACT_MESSAGES,AFK_MESSAGE_INTERVAL_MS} from './fair-content.js';
import {SpeechRecognitionService,TextToSpeechService,sound} from './fair-voice.js';
import {ZONES,gameZone,createGame,gameLimit,GameCover,GameHeader,QuestionCard,Inventory,LevelUnlocked,GameResult} from './game-adventure.js';
import {LearningExperiences,TITLES} from './fair-learning.js';
import {freshVisitor,readVisitor,saveVisitor,effectiveDifficulty,award,rankFor,rankProgress,buildSessionSummary,saveSessionSummary,markAchievementViewed} from './fair-session.js';
import {AchievementCard,AchievementModal} from './components/achievements.js';

const main=document.querySelector('main'),notice=document.querySelector('#notice');
const speech=new SpeechRecognitionService(),tts=new TextToSpeechService();
let visitorSession=readVisitor(localStorage);
try{if(!localStorage.getItem('visitorSession')&&localStorage.getItem('allen-new-visitor')!=='true'){const previousTabSession=readVisitor(sessionStorage);if(previousTabSession.ready){visitorSession=previousTabSession;saveVisitor(localStorage,visitorSession);}}}catch{}
let participant=visitorSession.name,level='Premedia',page=visitorSession.ready?(visitorSession.currentExperience==='attract'?'welcome':visitorSession.currentExperience):(localStorage.getItem('allen-new-visitor')==='true'?'welcome':'attract'),welcomeStep=visitorSession.ready?3:1;
let session=visitorSession.backendSession||null,startingSession=null,revision=0,busy=false,messages=[],conversationState=null;
let model=null,systemHealth=null,stats=null,health=null,projectLinks={};
let sounds=false,autoSpeak=false,audioState='',photo=false,pendingRank='',motivation='',messageIndex=0;
try{localStorage.removeItem('allen-fair-lock');}catch{}
let howStep=0,game=createGame(),lastActivity=Date.now(),attractIdx=0,afkReturnPage='welcome';
if(page==='game-result'&&visitorSession.lastGameResult){game={...game,...visitorSession.lastGameResult};}
const learning=new LearningExperiences({api,get visitor(){return visitorSession;},page:()=>page,go,render,persist,send,toast,event:recordEvent,reward,complete,motivate,evaluateLocal,logEvaluation:entry=>api('/fair/evaluation-log','POST',entry).catch(()=>{}),chooseDifficulty:()=>{welcomeStep=2;page='welcome';render();}});
const button=(label,attr='',primary=false)=>`<button ${attr} class="${primary?'primary':''}">${label}</button>`;
const tile=(label,description,ico,attr)=>`<button class="tile" ${attr}>${icon(ico,32)}<strong>${label}</strong><span>${description}</span></button>`;
function toast(text){notice.textContent=text;setTimeout(()=>{if(notice.textContent===text)notice.textContent='';},6500);}
function persist(){visitorSession.name=participant;if(page!=='attract')visitorSession.currentExperience=page;visitorSession.backendSession=session;if(visitorSession.ready&&!visitorSession.sessionStartedAt)visitorSession.sessionStartedAt=Date.now();saveVisitor(localStorage,visitorSession);}
function checkAchievements(){
 const newly=[];
 for(const a of learning.data.achievements?.achievements||[]){const value=visitorSession[a.metric]??visitorSession.metrics[a.metric]??0;if(value>=a.target&&!visitorSession.achievements.includes(a.name)){visitorSession.achievements.push(a.name);visitorSession.achievementIds.push(a.id);visitorSession.newAchievements.push(a.id);visitorSession.achievementDates[a.id]=Date.now();newly.push(a);}}
 return newly;
}
function reward(points,achievement='',key=''){
 const previous=visitorSession.rank;
 if(!award(visitorSession,points,achievement,key))return false;
 const ranks=learning.data.ranks?.ranks;
 if(ranks){const rank=rankFor(visitorSession.score,ranks);visitorSession.rank=rank.name;visitorSession.level=rank.level;if(previous!==rank.name)pendingRank=rank.name;}
 checkAchievements();persist();return true;
}
function complete(metric,key,points){
 if(!reward(points,'','complete:'+key))return false;
 visitorSession.activitiesCompleted++;visitorSession.streak++;
 visitorSession.metrics[metric]=(visitorSession.metrics[metric]||0)+1;
 checkAchievements();motivate('complete');persist();recordEvent('activity');return true;
}
function motivate(kind){
 const bank=learning.data.motivational_messages?.messages[kind]||[];
 if(bank.length){motivation=bank[messageIndex++%bank.length].replace('{name}',participant||'visitante');toast(motivation);}
}
function syncLevel(){level={'Fácil':'Primaria','Normal':'Premedia','Difícil':'Universidad / Técnico'}[effectiveDifficulty(visitorSession)];}
async function ensureSession(){
 if(session)return session;if(startingSession)return startingSession;
 const current=revision;syncLevel();
 const pending=api('/fair/sessions','POST',{level}).then(data=>{
  if(current!==revision){api('/fair/end','POST',{session:data.session}).catch(()=>{});throw new Error('La visita anterior terminó.');}
  session=data.session;persist();return session;
 });
 startingSession=pending;try{return await pending;}finally{if(startingSession===pending)startingSession=null;}
}
async function recordEvent(kind,lesson=''){
 const current=revision;try{await ensureSession();if(current!==revision)return;await api('/fair/event','POST',{session,kind,lesson});}catch{toast('La actividad sigue disponible. No se pudo actualizar el contador.');}
}
async function heartbeatSession(){if(!session)return;try{await api('/fair/event','POST',{session,kind:'heartbeat',lesson:''});}catch{session=null;visitorSession.backendSession=null;persist();try{await ensureSession();}catch{}}persist();}
async function evaluateLocal(prompt){await ensureSession();syncLevel();const body={session,name:participant,level,chat:{message:prompt,history:[],action:'',conversation_state:null}};try{return await api('/fair/chat','POST',body);}catch(error){if(error.status!==410)throw error;session=null;visitorSession.backendSession=null;persist();await ensureSession();body.session=session;return api('/fair/chat','POST',body);}}
async function reset(attract=true){
 const previous=session;revision++;session=null;startingSession=null;visitorSession=freshVisitor();participant='';messages=[];conversationState=null;busy=false;
 speech.cancel();tts.stop();game=createGame();learning.reset();welcomeStep=1;page=attract?'attract':'welcome';lastActivity=Date.now();
 document.body.classList.remove('photo','game-photo');notice.textContent='';pendingRank='';motivation='';document.querySelector('#rank-dialog')?.close();persist();render();
 try{localStorage.removeItem('visitorSession');localStorage.setItem('allen-new-visitor','true');}catch{}if(previous)api('/fair/end','POST',{session:previous}).catch(()=>{});
}
function showSessionSummary(){page='session-summary';game.photo=false;document.body.classList.remove('photo','game-photo');render();window.scrollTo({top:0,behavior:'instant'});main.focus({preventScroll:true});}
function sessionSummaryView(){const summary=buildSessionSummary(visitorSession,Date.now(),learning.paths.routes||[]),ranks=learning.data.ranks?.ranks||[],progress=ranks.length?rankProgress(visitorSession.score,ranks):null,achievements=(learning.data.achievements?.achievements||[]).filter(a=>visitorSession.achievements.includes(a.name)),activityLabels=[];if(summary.gamesCompleted)activityLabels.push(`${summary.gamesCompleted} ${summary.gamesCompleted===1?'juego completado':'juegos completados'}`);if(summary.challengesCompleted)activityLabels.push(`${summary.challengesCompleted} ${summary.challengesCompleted===1?'reto completado':'retos completados'}`);if(summary.simulationsCompleted)activityLabels.push(`${summary.simulationsCompleted} ${summary.simulationsCompleted===1?'simulación completada':'simulaciones completadas'}`);if(summary.projectsCompleted)activityLabels.push(`${summary.projectsCompleted} ${summary.projectsCompleted===1?'proyecto terminado':'proyectos terminados'}`);if(summary.lessonsCompleted)activityLabels.push(`${summary.lessonsCompleted} ${summary.lessonsCompleted===1?'tema practicado':'temas practicados'}`);return `<section class="session-summary-screen"><header class="session-summary-hero">${AllenPose('sessionEnd','large')}<div><span class="eyebrow">Resumen de tu sesión</span><h1>¡Buen trabajo${visitorSession.name?`, ${esc(visitorSession.name)}`:''}!</h1><p>Esto es lo que lograste con Allen</p></div></header><section class="session-summary-stats"><article><strong>+${summary.pointsEarned.toLocaleString('es')}</strong><span>Puntos</span></article><article><strong>${summary.activitiesCompleted}</strong><span>Actividades</span></article>${summary.achievementsUnlocked.length?`<article><strong>${summary.achievementsUnlocked.length}</strong><span>Logros</span></article>`:''}${summary.projectsCompleted?`<article><strong>${summary.projectsCompleted}</strong><span>Proyectos</span></article>`:''}${summary.durationSeconds!=null?`<article><strong>${Math.floor(summary.durationSeconds/60)} min</strong><span>Tiempo de sesión</span></article>`:''}</section>${achievements.length?`<section class="session-summary-section"><h2>Logros obtenidos</h2><div class="achievement-list">${achievements.map(a=>AchievementCard(a,{state:visitorSession.newAchievements.includes(a.id)?'new':'unlocked',date:visitorSession.achievementDates[a.id]?new Date(visitorSession.achievementDates[a.id]).toLocaleDateString('es'):''})).join('')}</div></section>`:''}${progress?`<section class="session-summary-section summary-rank"><h2>Tu progreso</h2><strong>${esc(progress.rank.name)}</strong><progress value="${progress.value}" max="${progress.max}" aria-label="Progreso del rango"></progress><p>${visitorSession.score.toLocaleString('es')} puntos${progress.next?` · ${progress.remaining.toLocaleString('es')} para el siguiente rango`: ' · rango máximo'}</p></section>`:''}${activityLabels.length?`<section class="session-summary-section"><h2>Hoy avanzaste en</h2><ul class="session-activity-list">${activityLabels.map(label=>`<li>${icon('circle-check',18)} ${esc(label)}</li>`).join('')}</ul></section>`:''}${summary.routeProgress.length?`<section class="session-summary-section"><h2>Rutas de aprendizaje</h2><ul class="session-activity-list">${summary.routeProgress.map(route=>`<li>${icon(route.completed?'circle-check':'map',18)} ${esc(route.name)} · ${route.modulesCompleted} módulos${route.completed?' · completada':''}</li>`).join('')}</ul></section>`:''}<footer class="session-summary-actions"><button class="primary" data-session-continue>Seguir aprendiendo</button><button class="session-finish-button" data-session-ask-finish>Terminar sesión</button></footer></section>`;}
function enterAfk(){if(page==='attract')return;afkReturnPage=page==='welcome'?'welcome':page;page='attract';lastActivity=Date.now();render();}
function leaveAfk(){const target=visitorSession.ready?(afkReturnPage==='attract'||afkReturnPage==='welcome'?'welcome':afkReturnPage):'welcome';page=target;welcomeStep=visitorSession.ready?3:1;lastActivity=Date.now();render();}
function go(next){
 if(next==='home'||next==='experiences')next='welcome';
 if(!visitorSession.ready&&!['welcome','attract'].includes(next)){next='welcome';welcomeStep=1;}
 else if(next==='welcome'&&visitorSession.ready)welcomeStep=3;
 page=next;tts.stop();speech.cancel();audioState='';photo=false;game.photo=false;document.body.classList.remove('photo','game-photo');
 syncLevel();learning.enter(page);
 if(page==='game'){game=createGame();game.name=participant;game.level=level;}
 render();window.scrollTo({top:0,behavior:'instant'});main.focus({preventScroll:true});if(page==='stats')loadStats();if(page==='offline')refreshModel();
}
function updateTopBar(){
 const onboarding=page==='welcome'&&welcomeStep<3;
 document.querySelector('header').hidden=page==='attract';
 const back=document.querySelector('#top-back');back.hidden=page==='attract'||(page==='welcome'&&welcomeStep!==2);
 back.querySelector('span').textContent=onboarding?'Volver':'Volver a experiencias';
 document.querySelector('#top-title').textContent=TITLES[page]||(page.startsWith('game-')?'Escapa con Allen':page==='compare'?'¿Por qué Allen enseña?':'');
 const chip=document.querySelector('#visitor-chip');chip.hidden=!visitorSession.ready;
 document.querySelector('#visitor-name').innerHTML=esc(participant||'Visitante')+'<small>'+esc(visitorSession.rank)+' · '+visitorSession.score.toLocaleString('es')+' pts</small>';
 const sessionExit=document.querySelector('[data-reset]');sessionExit.hidden=onboarding||!visitorSession.ready||page==='session-summary';sessionExit.querySelector('span').textContent=visitorSession.ready?'Finalizar sesión':'Nueva persona';
 document.body.dataset.page=page;
}
function FairQRCode(){
 const url=projectLinks.PROJECT_URL||projectLinks.GITHUB_URL||projectLinks.SOCIAL_URL;if(!url)return '';
 try{const u=new URL(url);if(!['http:','https:'].includes(u.protocol)||u.username||u.password)return '';}catch{return '';}
 return `<section class="panel center"><h2>Conoce más sobre Allen</h2><img width="208" height="208" src="/api/fair/qr?url=${encodeURIComponent(url)}" alt="QR del proyecto"><p>${esc(url)}</p><p class="muted">Abrir este enlace puede requerir Internet.</p></section>`;
}
async function refreshModel(){
 const results=await Promise.allSettled([api('/model/status'),api('/health')]);
 model=results[0].status==='fulfilled'?results[0].value:null;systemHealth=results[1].status==='fulfilled'?results[1].value:null;
 if(page==='offline')render();
}
async function loadStats(){try{stats=await api('/fair/stats');try{localStorage.setItem('eventStats',JSON.stringify(stats.eventStats));}catch{}if(page==='stats')render();}catch{toast('No se pudieron actualizar las estadísticas.');}}
function saveGameResult(){
 const key=`game:${game.startedAt}`;if(visitorSession.lastGameResult?.key===key)return;
 complete('games',key,0);recordEvent('game');
 const gameAchievementIds=new Set(game.unlockedAchievementIds||[]),newGameAchievement=(learning.data.achievements?.achievements||[]).find(a=>gameAchievementIds.has(a.id)&&visitorSession.achievements.includes(a.name));
 const now=Date.now();game.pointsEarned=Math.max(0,visitorSession.score-(game.sessionScoreAtStart||0));game.elapsedSeconds=game.startedAt?Math.max(0,Math.floor((now-game.startedAt)/1000)):null;game.completedAt=now;game.resultKey=key;game.newAchievement=newGameAchievement||null;
 visitorSession.lastGameResult=JSON.parse(JSON.stringify(game));persist();
}
function openAchievement(id){const config=(learning.data.achievements?.achievements||[]).find(a=>a.id===id);if(!config||!visitorSession.achievements.includes(config.name))return;const dialog=document.querySelector('#achievement-dialog');dialog.innerHTML=AchievementModal(config,{score:visitorSession.score,ranks:learning.data.ranks?.ranks||[],date:visitorSession.achievementDates?.[id]?new Date(visitorSession.achievementDates[id]).toLocaleDateString('es'):''});markAchievementViewed(visitorSession,id);persist();dialog.querySelector('[data-achievement-close]')?.addEventListener('click',()=>dialog.close(),{once:true});if(!dialog.open)dialog.showModal();dialog.querySelector('[data-achievement-close]')?.focus();}
function render(){
 syncLevel();persist();updateTopBar();
 let html='';
 if(page==='attract'){
  const m=ATTRACT_MESSAGES[attractIdx%ATTRACT_MESSAGES.length];
  html=`<section class="attract"><div id="attract-mascot">${AllenMascot(m.pose,'large')}</div><span class="eyebrow">ALLEN · Aprende a tu ritmo</span><h1 id="attract-text">${esc(m.text)}</h1><button class="primary attract-cta" data-begin>Empezar</button></section>`;
 }
 if(page==='session-summary')html=sessionSummaryView();
 if(page==='welcome'){
  if(welcomeStep===1)html=`<section class="onboard-container"><div class="onboard-hero">${AllenMascot('hello','large')}<h1>¡Hola! Soy Allen.</h1><p>¿Cómo quieres que te llame?</p></div><form id="welcome-form"><label for="welcome-name" class="sr-only">Tu nombre o apodo</label><input id="welcome-name" class="onboard-input" maxlength="30" value="${esc(participant)}" placeholder="Tu nombre o apodo" autocomplete="off"><div class="onboard-actions"><button class="primary">Continuar</button>${button('Seguir sin nombre','type="button" data-skip-name')}</div></form><p class="muted">Solo lo usaré durante tu visita.</p></section>`;
  if(welcomeStep===2)html=`<section class="onboard-container"><div class="onboard-hero">${AllenMascot('thinking','medium')}<h1>Elige tu dificultad</h1><p>Allen adaptará las explicaciones y actividades.</p></div><div class="experience-grid difficulty-grid">${[['Fácil','Vocabulario sencillo, más pistas y ejemplos guiados.'],['Normal','Un equilibrio entre explicación y práctica.'],['Difícil','Más profundidad, menos ayuda inicial.'],['Sorpréndeme','Allen ajusta el nivel según tus logros.']].map(([d,description])=>`<button class="experience-card" data-difficulty="${d}">${icon('target',28)}<strong>${d}</strong><span>${description}</span></button>`).join('')}</div></section>`;
  if(welcomeStep===3)html=learning.home();
 }
 const educational=learning.render(page);if(educational!==null)html=educational;
 if(page==='game')html=GameCover();
 if(page==='game-unlocked')html=LevelUnlocked(game);
 if(page==='chat')html=`<div class="row">${AllenMascot(busy?'thinking':'hello','small')}<div><h1>Habla con Allen</h1><p class="muted">Pregunta, aprende, explora o pide ayuda.</p></div></div><div class="chat-log" aria-live="polite">${messages.map(m=>`<article class="bubble ${m.role}"><b>${m.role==='assistant'?'Allen':'Tú'}</b>${markdown(m.content)}</article>`).join('')}${busy?'<p role="status">Allen está pensando…</p>':''}</div>${chatActions()}<form id="chat-form" class="chat-form"><input id="question" aria-label="Pregúntale algo a Allen" maxlength="4000" placeholder="Pregúntale algo a Allen…" required ${busy?'disabled':''}><button class="primary" ${busy?'disabled':''}>Enviar</button></form><p class="muted">La conversación se borra al cambiar de persona.</p>`;
 if(page==='how'){const how=[['Tu pregunta','Escribes una pregunta como “¿Qué es una fracción?”', 'hello'],['Allen recibe','Allen prepara el contexto y piensa en una explicación útil.', 'thinking'],['IA local','El modelo funciona dentro de este dispositivo, sin nube.', 'teaching'],['Respuesta','Allen convierte el resultado en una explicación educativa.', 'celebrating']];const current=how[howStep];html=`<span class="eyebrow">Descubre cada parte</span><h1>¿Cómo funciona Allen?</h1><p>Descubre qué pasa desde que haces una pregunta hasta que recibes una respuesta.</p><div class="how-map">${how.map((s,i)=>`<button class="how-node ${i===howStep?'active':''} ${i<howStep?'done':''}" data-how-step="${i}"><b>${i+1}</b><span>${s[0]}</span></button>`).join('')}</div><section class="panel how-card">${AllenMascot(current[2],'medium')}<span class="eyebrow">Paso ${howStep+1} de 4</span><h2>${current[0]}</h2><p>${current[1]}</p>${howStep===0?'<div class="demo-question">¿Qué es una fracción?</div>':''}${howStep===2?'<div class="badges"><span class="badge">Sin nube</span><span class="badge">Procesamiento local</span></div>':''}${howStep===3?'<div class="demo-answer">Una fracción representa partes iguales de un todo.</div>':''}<div class="row">${howStep>0?button('Anterior','data-how-prev'):''}${howStep<3?button('Siguiente','data-how-next',true):button('Probar en vivo','data-go="chat"',true)}</div></section><h2>¿Qué quieres descubrir ahora?</h2><div class="grid related-grid">${tile('IA local','Qué significa procesar aquí.','sparkles','data-go="offline"')}${tile('Privacidad','Dónde quedan tus datos.','shield-check','data-go="privacy"')}${tile('Aprendizaje','Por qué Allen enseña.','book-open','data-go="compare"')}</div><div class="row">${button('Ver otra explicación','data-how-reset')}</div>`;}
 if(page==='privacy')html=`${AllenMascot('reading')}<h1>Tus preguntas se quedan en este dispositivo.</h1><p>En la feria, tu nombre temporal, progreso y proyectos se guardan localmente en este navegador para que sobrevivan al cierre de ALLEN. Al pulsar Nueva persona se limpian. Los contadores generales son anónimos y no se borran al cambiar de persona.</p><p>No grabamos audio. El reconocimiento del navegador puede enviar audio a su proveedor: por eso está desactivado por defecto.</p>`;
 if(page==='game-play')html=`${GameHeader(game)}${QuestionCard(game)}${Inventory(game)}`;
 if(page==='game-result')html=GameResult(game);
 if(page==='compare'){const _ds=window._compareDemoState||'none';const _feats=[['💬','Explica, no solo responde','Allen intenta ayudarte a entender cómo se llega a una respuesta.'],['🔄','Se adapta a ti','Puede explicar un mismo concepto de forma más fácil, paso a paso o utilizando otro ejemplo.'],['✏️','Te permite practicar','Después de aprender algo, Allen puede hacerte preguntas y ejercicios para comprobar que realmente lo entendiste.'],['📈','Aprende contigo','Allen puede recordar tu nivel, tus preferencias de aprendizaje y los temas que estás estudiando.'],['📡','Funciona localmente','Allen está pensado para que estudiantes con conectividad limitada también puedan acceder a herramientas educativas basadas en inteligencia artificial.'],['🔍','Promueve la curiosidad','El objetivo no es que memorices una respuesta, sino que quieras seguir preguntando y descubriendo.']];const _impacts=[['🧠','Comprensión','Entender conceptos difíciles de diferentes maneras.'],['🎯','Autonomía','Aprender y practicar incluso cuando no hay un profesor disponible.'],['🌐','Acceso','Acercar herramientas modernas de IA a estudiantes con conectividad limitada.'],['💡','Curiosidad','Motivar a los jóvenes a explorar tecnología, ciencia, programación y otras áreas.'],['🤔','Pensamiento','Ayudar a razonar antes de entregar una solución.'],['🚀','Preparación digital','Familiarizar a los jóvenes con una tecnología que formará parte de su futuro académico y profesional.']];let _demoHtml='';if(_ds==='simple')_demoHtml=`<div class="compare-demo-result compare-demo-simple-result"><span class="eyebrow">Respuesta directa</span><p>Una variable es un espacio en la memoria del computador que almacena un valor que puede cambiar durante la ejecución del programa.</p></div>`;else if(_ds==='allen')_demoHtml=`<div class="compare-demo-result compare-demo-allen-result"><span class="eyebrow">Allen te enseña</span><p><strong>Explicación sencilla:</strong> Una variable es como una caja con una etiqueta. Adentro guardas algo, por ejemplo un número o un nombre.</p><p><strong>Analogía:</strong> Imagina que tienes una caja que dice <em>"edad"</em> y dentro pones el número 14. Mañana puedes cambiar el 14 por 15 y la caja sigue llamándose igual.</p><p><strong>Ejemplo:</strong><br><code>edad = 14</code><br><code>nombre = "Sofía"</code></p><p class="compare-demo-check"><strong>Pregunta de comprobación:</strong> Si escribo <code>puntos = 0</code> y luego gano 3 puntos, ¿cómo quedaría la variable?</p><div class="compare-demo-more">${button('¿No entendiste? Explícalo diferente','data-demo-alt')} ${button('Ponme a prueba','data-demo-quiz',true)}</div></div>`;else if(_ds==='alt')_demoHtml=`<div class="compare-demo-result compare-demo-allen-result"><span class="eyebrow">Otra explicación</span><p><strong>Piénsalo así:</strong> Cuando juegas un videojuego, el juego recuerda cuántas vidas tienes, cuántos puntos llevas y cuál es tu personaje. Cada uno de esos datos es una variable.</p><p>La pantalla muestra <em>vidas = 3</em>. Cuando pierdes una vida, se convierte en <em>vidas = 2</em>. El nombre no cambia, pero el valor adentro sí.</p><p><strong>Ejemplo:</strong><br><code>vidas = 3</code><br><code>vidas = vidas - 1</code> <span class="muted">→ ahora vidas = 2</span></p><div class="compare-demo-more">${button('Ponme a prueba','data-demo-quiz',true)}</div></div>`;else if(_ds==='quiz')_demoHtml=`<div class="compare-demo-result compare-demo-quiz-result"><span class="eyebrow">Comprobación</span><p><strong>¿Cuál de estas describe mejor una variable?</strong></p><div class="compare-quiz-options"><button class="compare-quiz-opt" data-quiz-ans="a">Un número fijo que nunca cambia</button><button class="compare-quiz-opt" data-quiz-ans="b">Un espacio que guarda un valor y puede actualizarse</button><button class="compare-quiz-opt" data-quiz-ans="c">Un tipo de pantalla del computador</button></div></div>`;html=`<span class="eyebrow">Propósito educativo</span><h1>¿Por qué Allen enseña?</h1><p class="compare-subtitle">Porque aprender vale más que simplemente recibir una respuesta.</p><section class="compare-block panel compare-problem"><h2>El problema</h2><p>Muchas herramientas de inteligencia artificial pueden entregar una respuesta en segundos, pero obtener una respuesta no significa necesariamente haber aprendido.</p><p>Además, no todos los estudiantes tienen acceso constante a Internet, profesores particulares o herramientas digitales avanzadas.</p></section><section class="compare-block"><h2>Lo que hace Allen diferente</h2><div class="compare-features-grid">${_feats.map(([emoji,title,desc])=>`<article class="compare-feature-card"><span class="compare-feature-icon">${icon('lightbulb',24)}</span><strong>${title}</strong><p>${desc}</p></article>`).join('')}</div></section><section class="compare-block"><h2>La diferencia en acción</h2><div class="compare-vs"><article class="compare-vs-card compare-vs-answer"><span class="eyebrow">Solo responder</span><p class="compare-math-q">18 × 7 = ?</p><p class="compare-math-result">= <strong>126</strong></p></article><div class="compare-vs-divider"><span>vs</span></div><article class="compare-vs-card compare-vs-teach"><span class="eyebrow">Enseñar con Allen</span><p class="compare-math-q">18 × 7 = ?</p><div class="compare-steps"><p>Dividimos 18 en partes: <strong>10 + 8</strong></p><p>10 × 7 = <strong>70</strong></p><p>8 × 7 = <strong>56</strong></p><p>Sumamos: 70 + 56 = <strong>126</strong> ✓</p></div></article></div><p class="compare-caption muted">Allen busca que entiendas el camino, no solo el resultado.</p></section><section class="compare-block panel compare-goal"><h2>Nuestro objetivo</h2><p>El objetivo de ALLEN es democratizar el acceso al aprendizaje asistido por inteligencia artificial, especialmente para jóvenes que no siempre cuentan con conectividad constante o acceso a herramientas educativas modernas.</p><p>Queremos que la inteligencia artificial sea una herramienta para aprender, explorar y desarrollar habilidades, no simplemente una máquina de respuestas.</p></section><section class="compare-block"><h2>Impacto que busca generar</h2><div class="compare-impact-grid">${_impacts.map(([emoji,title,desc])=>`<article class="compare-impact-card"><span class="compare-impact-icon">${icon('lightbulb',24)}</span><strong>${title}</strong><p>${desc}</p></article>`).join('')}</div></section><section class="compare-block panel compare-demo-section"><h2>Comprueba la diferencia</h2><p>¿Qué es una variable en programación?</p><div class="compare-demo-btns">${button('Solo respuesta','data-demo-simple')} ${button('Enséñame con Allen','data-demo-allen',true)}</div>${_demoHtml}</section><section class="compare-block compare-final"><div class="compare-final-inner">${AllenMascot('teaching','medium')}<div class="compare-final-text"><p class="compare-quote">"No quiero hacer todo por ti.<br>Quiero ayudarte a entenderlo."</p><p class="compare-tagline">Aprende. Practica. Pregunta. Descubre.</p></div></div></section><h2>¿Qué quieres descubrir ahora?</h2><div class="grid related-grid">${tile('Cómo funciona Allen','Qué pasa dentro de cada respuesta.','lightbulb','data-go="how"')}${tile('Estado de Allen','Comprueba si Allen está listo.','shield-check','data-go="offline"')}${tile('Privacidad','Dónde quedan tus datos.','shield-check','data-go="privacy"')}${tile('Probar Allen','Hazle una pregunta ahora.','message-circle','data-go="chat"')}</div>`;}
 if(page==='how')html+=`<section class="panel"><h2>¿Por qué Allen enseña?</h2><p>Allen no busca hacer todo por ti. Busca ayudarte a entenderlo.</p><p>Te acompaña para explicar, practicar y explorar tecnología, también en lugares con conectividad limitada. El modelo y las actividades están instalados en este dispositivo.</p><p>Tu nombre y conversación pertenecen a esta visita. Los contadores generales no guardan datos personales.</p></section>`;
 if(page==='offline'){
  const connected=!!model?.connected,prepared=!!(systemHealth?.application&&systemHealth?.database);
  const actualModel=String(model?.effective_model||model?.models?.[0]||'').split(/[\\/]/).pop().replace(/\.gguf$/i,'');
  const entries=[['Internet',navigator.onLine?'Conectado':'Desconectado'],['IA local',connected?'Activa':'No disponible'],['Modelo',connected?actualModel:'No cargado'],['Sistema',prepared?'Preparado':'Problema'],['Allen',connected?'Listo para ayudarte':'Actividades locales disponibles']];
  html=`<section class="experience-intro"><div><h1>Estado de Allen</h1><p>Comprueba si Allen está listo.</p></div>${AllenMascot('hello','medium')}</section><div class="status-grid">${entries.map(([title,value])=>`<section class="panel"><h2>${title}</h2><p>${value}</p></section>`).join('')}</div><p class="muted">El indicador de Internet refleja la red del navegador; no comprueba acceso externo.</p>${button('Comprobar de nuevo','data-reconnect')}<section class="panel"><h2>Prueba la respuesta de Allen</h2><form id="status-form" class="chat-form"><input name="question" aria-label="Pregúntame algo" placeholder="Pregúntame algo..." required maxlength="4000"><button class="primary">Preguntar</button></form></section>`;
 }
 if(page==='stats'){
  const s=stats?.eventStats;
  html=`<h1>ALLEN hoy</h1><h2>Durante tu visita</h2>${learning.rankPanel()}<div class="chips"><span>${visitorSession.activitiesCompleted} actividades</span><span>${visitorSession.completedLessons.length} temas practicados</span><span>${visitorSession.metrics.routes||0} rutas</span><span>${visitorSession.metrics.challenges||0} retos</span><span>${visitorSession.metrics.simulations||0} simulaciones</span><span>${visitorSession.metrics.projects||0} proyectos</span></div><details><summary>Mis logros (${visitorSession.achievements.length})</summary><ul>${visitorSession.achievements.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details><h2>Estadísticas del evento</h2><p>Actividad anónima de este dispositivo. Las visitas cuentan sesiones, no personas únicas.</p>${s?`<div class="experience-grid">${[['Visitantes',s.visitors],['Preguntas',s.questions],['Retos',s.challenges],['Simulaciones',s.simulations],['Juegos',s.games],['Actividades completadas',s.activitiesCompleted],['Proyectos explorados',s.projects],['Minutos de aprendizaje',s.learningMinutes]].map(([label,value])=>`<section class="panel stat"><strong>${value}</strong>${label}</section>`).join('')}</div>`:'<p>Cargando estadísticas…</p>'}<p class="muted">El tiempo es una estimación de actividad, no una medición del aprendizaje.</p>${button('Actualizar','data-stats')}`;
 }
 if(visitorSession.ready&&!['attract','welcome'].includes(page))html='<div class="activity-hud"><span>'+icon('star',16)+' '+visitorSession.score+' puntos</span><span>'+esc(visitorSession.rank)+'</span><span>Racha: '+visitorSession.streak+' actividades</span><span>'+visitorSession.activitiesCompleted+' completadas</span></div>'+html;
 main.innerHTML=html;bind();learning.bind(main);
 const achievementDialog=document.querySelector('#achievement-dialog');achievementDialog.querySelector('[data-achievement-close]')?.addEventListener('click',()=>achievementDialog.close());achievementDialog.onclick=e=>{if(e.target===achievementDialog)achievementDialog.close();};
 if(pendingRank){const dialog=document.querySelector('#rank-dialog');dialog.querySelector('h2').textContent=pendingRank;if(!dialog.open)dialog.showModal();}

}
function chatActions(){
 const last=messages.at(-1);if(busy||last?.role!=='assistant')return '';
 return `<div class="chips">${[['simplify','Más fácil'],['another_example','Otro ejemplo'],['quiz_me','Ponme a prueba']].map(([key,title])=>button(title,`data-action="${key}"`)).join('')}<details><summary>Más opciones</summary><div class="chips">${button('Paso a paso','data-action="step_by_step"')}${button('Resumir lo aprendido','data-action="summary_learning"')}${button('Escuchar respuesta','data-listen')}${button('Detener audio','data-stop')}${button('Dictar pregunta (voz local)','data-mic')}${button('Comprobar conexión','data-reconnect')}</div></details></div>`;
}
async function send(text,action=''){
 if(busy||!text.trim())return;
 if(text==='Ponme un reto'&&!action){go('challenge');return;}
 const current=revision;busy=true;const history=messages.slice(-12);messages.push({role:'user',content:text});render();
 try{
  await ensureSession();syncLevel();
  const result=await api('/fair/chat','POST',{session,name:participant,level,chat:{message:text,history,action,conversation_state:conversationState}});
  if(current!==revision)return;
  messages.push({role:'assistant',content:result.text});conversationState=result.conversation_state;
  if(autoSpeak&&tts.enabled)try{tts.play(result.text,speechState);}catch(e){toast(e.message);}
 }catch{
  if(current===revision)messages.push({role:'assistant',content:localReply(text)});
 }finally{if(current===revision){busy=false;render();document.querySelector('.chat-log')?.scrollTo(0,999999);}}
}
function localReply(text){
 const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const q=clean(text),lesson=learning.data.lessons?.lessons.find(l=>q.includes(clean(l.topic)));
 return 'Allen está usando contenido disponible en el dispositivo.\n\n'+(lesson?lesson.concept+'\n\nEjemplo: '+lesson.example+'\n\n'+lesson.question:'No tengo una respuesta local preparada para esa pregunta. Puedes explorar una lección, practicar un reto o probar una simulación.');
}
function speechState(state){audioState=['listening','speaking'].includes(state)?state:'';if(state==='error')toast('La voz no está disponible. Puedes seguir leyendo y escribiendo.');if(page==='chat')render();}
async function mic(){if(audioState==='listening'){speech.cancel();audioState='';render();return;}try{speech.mode='local';await speech.listen(text=>{if(page==='chat')send(text);else toast('Micrófono comprobado. No se guardó el audio ni la transcripción.');},speechState);}catch(e){toast(e.message);}}
function bind(){

 main.querySelectorAll('[data-game-mode]').forEach(b=>b.onclick=()=>{game=createGame();game.mode=b.dataset.gameMode;game.name=participant;game.level=level;game.startedAt=Date.now();game.sessionScoreAtStart=visitorSession.score;page='game-unlocked';render();});
 main.querySelector('[data-game-continue]')?.addEventListener('click',()=>{if(game.index>0)sound(sounds,false,'unlock');game.justEarned='';page='game-play';render();});
 main.querySelectorAll('[data-game-answer]').forEach(b=>b.onclick=()=>{if(game.feedback)return;const zone=gameZone(game),selected=Number(b.dataset.gameAnswer),correct=selected===zone.correct;if(correct){game.combo++;game.correct++;const bonus=(game.hints===0&&!game.wrong?25:0)+(game.combo>0&&game.combo%3===0?50:0);const points=Math.max(25,100-game.hints*15)+bonus;game.score+=points;reward(points,'',`game-answer:${game.startedAt}:${game.index}`);game.justEarned=zone.item;game.collected.push(zone.item);game.feedback={correct:true,selected,points,bonus};}else{game.combo=0;game.wrong=true;game.feedback={correct:false,selected};}sound(sounds,false,correct?'normal':'soft');render();});
 main.querySelector('[data-game-retry]')?.addEventListener('click',()=>{game.feedback=null;render();});
 main.querySelector('[data-game-hint]')?.addEventListener('click',()=>{game.hints=Math.min(3,game.hints+1);game.totalHints++;game.feedback=null;render();});
 main.querySelector('[data-game-skip]')?.addEventListener('click',()=>{game.combo=0;game.feedback={skipped:true};render();});
 main.querySelector('[data-game-explain]')?.addEventListener('click',()=>{game.combo=0;game.feedback={explained:true};render();});
 main.querySelector('[data-game-next]')?.addEventListener('click',()=>{const achievementsBefore=new Set(visitorSession.achievements);complete('zones',`game-zone:${game.startedAt}:${game.index}`,150);const unlockedNow=(learning.data.achievements?.achievements||[]).filter(a=>!achievementsBefore.has(a.name)&&visitorSession.achievements.includes(a.name)).map(a=>a.id);game.unlockedAchievementIds=[...new Set([...(game.unlockedAchievementIds||[]),...unlockedNow])];motivate('zone');if(game.index+1>=gameLimit(game)){saveGameResult();sound(sounds,true);page='game-result';}else{game.index++;game.hints=0;game.wrong=false;game.feedback=null;page='game-unlocked';}render();});
 main.querySelector('[data-game-restart]')?.addEventListener('click',()=>{document.body.classList.remove('game-photo');const mode=game.mode;game=createGame();game.mode=mode;game.level=level;game.name=participant;game.startedAt=Date.now();game.sessionScoreAtStart=visitorSession.score;page='game-unlocked';render();});
 main.querySelector('[data-game-quick]')?.addEventListener('click',()=>{document.body.classList.remove('game-photo');game=createGame();game.mode='quick';game.level=level;game.name=participant;game.startedAt=Date.now();game.sessionScoreAtStart=visitorSession.score;page='game-unlocked';render();});
 main.querySelectorAll('[data-game-photo]').forEach(b=>b.addEventListener('click',()=>{game.photo=!game.photo;document.body.classList.toggle('game-photo',game.photo);render();}));
 main.querySelectorAll('[data-achievement-open]').forEach(b=>b.addEventListener('click',()=>openAchievement(b.dataset.achievementOpen)));
 main.querySelector('#game-participant')?.addEventListener('input',e=>{game.name=e.target.value;const title=main.querySelector('.photo-achievement h1');if(title)title.textContent=game.name||'Explorador de Allen';});

 main.querySelector('#chat-form')?.addEventListener('submit',e=>{e.preventDefault();send(document.querySelector('#question').value);});
 main.querySelector('#welcome-form')?.addEventListener('submit',e=>{e.preventDefault();participant=document.querySelector('#welcome-name').value.trim();welcomeStep=2;render();});
 main.querySelector('#status-form')?.addEventListener('submit',e=>{e.preventDefault();const text=new FormData(e.target).get('question');go('chat');send(text);});
 main.querySelectorAll('[data-how-step]').forEach(b=>b.onclick=()=>{howStep=Number(b.dataset.howStep);render();});
 main.querySelector('[data-how-next]')?.addEventListener('click',()=>{howStep=Math.min(3,howStep+1);render();});
 main.querySelector('[data-how-prev]')?.addEventListener('click',()=>{howStep=Math.max(0,howStep-1);render();});
 main.querySelector('[data-how-reset]')?.addEventListener('click',()=>{howStep=0;render();});
 main.querySelector('[data-demo-simple]')?.addEventListener('click',()=>{window._compareDemoState='simple';page='compare';render();});
 main.querySelector('[data-demo-allen]')?.addEventListener('click',()=>{window._compareDemoState='allen';page='compare';render();});
 main.querySelector('[data-demo-alt]')?.addEventListener('click',()=>{window._compareDemoState='alt';page='compare';render();});
 main.querySelector('[data-demo-quiz]')?.addEventListener('click',()=>{window._compareDemoState='quiz';page='compare';render();});
 main.querySelectorAll('[data-quiz-ans]').forEach(b=>b.addEventListener('click',()=>{const correct=b.dataset.quizAns==='b';b.classList.add(correct?'quiz-correct':'quiz-wrong');main.querySelectorAll('[data-quiz-ans]').forEach(q=>{if(q.dataset.quizAns==='b')q.classList.add('quiz-correct');q.disabled=true;});const fb=document.createElement('p');fb.className='compare-quiz-feedback';fb.textContent=correct?'¡Exacto! Una variable guarda un valor que puede cambiar. ¡Lo entendiste muy bien!':'No del todo. La respuesta correcta es la B: una variable guarda un valor que puede actualizarse.';b.closest('.compare-demo-result').appendChild(fb);}));
 main.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>send(actions[b.dataset.action],b.dataset.action));
 main.querySelector('[data-mic]')?.addEventListener('click',mic);
 main.querySelector('[data-listen]')?.addEventListener('click',()=>{try{tts.enabled=true;tts.play(messages.at(-1).content,speechState);}catch(e){toast(e.message);}});
 main.querySelector('[data-pause]')?.addEventListener('click',()=>{tts.pause();audioState='';});
 main.querySelector('[data-resume]')?.addEventListener('click',()=>tts.resume());
 main.querySelector('[data-stop]')?.addEventListener('click',()=>{tts.stop();audioState='';render();});
 main.querySelector('[data-reconnect]')?.addEventListener('click',async()=>{await refreshModel();toast(model?.connected?'IA local activa. Puedes repetir tu pregunta.':'Allen sigue despertando. Los retos y las microlecciones están disponibles.');});
 main.querySelectorAll('[data-photo]').forEach(button=>button.addEventListener('click',()=>{photo=!photo;document.body.classList.toggle('photo',photo);render();}));
 main.querySelector('[data-stats]')?.addEventListener('click',loadStats);
 main.querySelector('[data-session-continue]')?.addEventListener('click',()=>{welcomeStep=3;page='welcome';render();window.scrollTo({top:0,behavior:'instant'});});
 main.querySelector('[data-session-ask-finish]')?.addEventListener('click',()=>document.querySelector('#session-confirm-dialog').showModal());


}
document.addEventListener('click',async e=>{
 const b=e.target.closest('button');if(!b||b.disabled)return;
 if(b.hasAttribute('data-begin')){if(page==='attract'){leaveAfk();return;}welcomeStep=visitorSession.ready?3:1;page='welcome';render();return;}
 if(b.hasAttribute('data-skip-name')){participant='';welcomeStep=2;render();return;}
 if(b.dataset.difficulty){
  visitorSession.difficulty=b.dataset.difficulty;visitorSession.ready=true;try{localStorage.removeItem('allen-new-visitor');}catch{}syncLevel();welcomeStep=3;page='welcome';render();
  try{await ensureSession();}catch{toast('Las actividades preparadas siguen disponibles en el dispositivo.');}return;
 }
 if(b.hasAttribute('data-global-back')){if(page==='welcome'&&welcomeStep===2){welcomeStep=visitorSession.ready?3:1;render();}else go('experiences');return;}
 if(b.hasAttribute('data-attract')){enterAfk();return;}
 if(b.hasAttribute('data-reset')){if(visitorSession.ready)showSessionSummary();else{welcomeStep=1;page='welcome';render();}return;}
 if(b.hasAttribute('data-session-cancel')){document.querySelector('#session-confirm-dialog').close();return;}
 if(b.hasAttribute('data-session-confirm')){const dialog=document.querySelector('#session-confirm-dialog');const summary=buildSessionSummary(visitorSession,Date.now(),learning.paths.routes||[]);if(!saveSessionSummary(localStorage,summary)){toast('No se pudo guardar el resumen. Tu sesión sigue abierta.');return;}dialog.close();reset(true);return;}
 if(b.hasAttribute('data-rank-continue')){pendingRank='';document.querySelector('#rank-dialog').close();return;}
 if(b.dataset.edu){await learning.handle(b.dataset.edu,b.dataset.value);return;}
 if(b.hasAttribute('data-resume-route')){learning.paths.selected=b.dataset.resumeRoute;learning.paths.view='map';learning.routesView=true;learning.lesson=null;page='learn';render();return;}
 if(b.dataset.go){go(b.dataset.go);return;}
});
function activity(){lastActivity=Date.now();}
['pointerdown','keydown'].forEach(type=>document.addEventListener(type,activity,{passive:true}));
document.querySelector('#rank-dialog').addEventListener('cancel',()=>{pendingRank='';});
document.querySelector('#achievement-dialog').addEventListener('cancel',()=>{});
document.querySelector('#session-confirm-dialog').addEventListener('cancel',()=>{});
setInterval(()=>{
 if(page==='attract')return;
 const decision=inactivityDecision(Date.now()-lastActivity,-1,visitorSession.ready||!!participant,page==='welcome');
 if(decision==='afk')enterAfk();
 if(decision==='attract')go('attract');
},1000);
setInterval(()=>{if(page==='attract'){attractIdx=(attractIdx+1)%ATTRACT_MESSAGES.length;const m=ATTRACT_MESSAGES[attractIdx];document.querySelector('#attract-text').textContent=m.text;document.querySelector('#attract-mascot').innerHTML=AllenMascot(m.pose,'large');}},AFK_MESSAGE_INTERVAL_MS);
setInterval(heartbeatSession,60000);
window.addEventListener('online',()=>{if(page==='offline')render();});window.addEventListener('offline',()=>{if(page==='offline')render();});
async function boot(){
 render();
 try{const data=await api('/fair/token');setToken(data.token);if(session)await heartbeatSession();try{projectLinks=JSON.parse(localStorage.getItem('allen-fair-links')||'null')||await api('/fair/links');}catch{projectLinks={};}await learning.load();render();refreshModel();}
 catch{toast('No se pudo conectar con Allen. Vuelve a abrir la aplicación para cargar sus actividades.');}
}
boot();
