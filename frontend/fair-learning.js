import {icon} from './components/ui.js';
import {AllenMascot} from './components/fair-mascot.js';
import {escapeHTML as esc} from './components/markdown.js';
import {effectiveDifficulty,answerPoints,chooseQuestions,rankProgress} from './fair-session.js';
import {Roadmaps,projectEvidence,readEvidence} from './fair-paths.js';
import {evaluateSubmission,retryEvaluationFeedback} from './fair-evaluation.js';

const btn=(label,action,value='',primary=false,disabled=false)=>`<button data-edu="${action}" data-value="${esc(String(value))}" class="${primary?'primary':''}" ${disabled?'disabled':''}>${esc(label)}</button>`;
const card=(title,description,action,value,ico='book-open')=>`<button class="experience-card" data-edu="${action}" data-value="${esc(value)}">${icon(ico,24)}<strong>${esc(title)}</strong><span>${esc(description)}</span>${icon('arrow-right',16)}</button>`;
const list=items=>`<ul>${items.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>`;
const block=(title,text)=>`<section class="panel"><h2>${esc(title)}</h2><p>${esc(text)}</p></section>`;
const AREAS={Matemáticas:'calculator',Programación:'code',Ciberseguridad:'shield-check','Inteligencia Artificial':'sparkles',Inglés:'languages',Ciencia:'flask-conical',Tecnología:'cpu',Lógica:'compass',Robótica:'bot',Electrónica:'zap',Datos:'database',Redes:'network',STEAM:'flask-conical'};
export const EXPERIENCE_GROUPS=[
 ['Aprender',[
  ['learn','Enséñame algo','Elige un área y aprende paso a paso.','book-open'],
  ['explore','Explora Tecnología','Descubre áreas tecnológicas y para qué sirven.','compass'],
  ['steam','Proyectos STEAM','Convierte una idea en algo que puedas construir.','flask-conical']]],
 ['Practicar',[
  ['challenge','Rétame','Preguntas, pistas y nuevos descubrimientos.','target'],
  ['simulator','Simulador','¿Qué harías en esta situación?','shield-check'],
  ['game','Escapa con Allen','Supera estaciones, gana puntos y aprende jugando.','gamepad-2']]],
 ['Explorar',[
  ['chat','Habla con Allen','Pregunta, aprende, explora o pide ayuda.','message-circle'],
  ['surprise','Sorpréndeme','Allen elegirá algo diferente para ti.','sparkles'],
  ['how','¿Cómo funciona?','Descubre cómo Allen aprende contigo.','lightbulb']]],
 ['Sistema',[
  ['offline','Estado de Allen','Comprueba si Allen está listo.','activity'],
  ['stats','ALLEN hoy','Lo que hemos aprendido juntos.','chart-no-axes-column']]]
];
export const TITLES=Object.fromEntries(EXPERIENCE_GROUPS.flatMap(([,items])=>items.map(([id,title])=>[id,id==='game'?'Escapa con Allen':title])));

export class LearningExperiences{
 constructor(host){this.host=host;this.data={};this.errors=new Set();this.paths=new Roadmaps(host,this);this.reset();}
 reset(){this.routesView=false;this.assessment=null;this.paths.selected=null;this.paths.view='map';this.area='';this.lesson=null;this.step=0;this.quick=false;this.easy=false;this.alt=false;this.answer=null;this.completed=false;this.category='Tecnología';this.round=null;this.sim=null;this.simChoice=null;this.tech=null;this.project=null;this.interest='tecnología';this.projectCategory='Todas';this.surprise=null;this.lastSurprise='';this.surpriseMore=false;this.surpriseTest=false;this.surpriseChoice=null;this.surpriseRevision=(this.surpriseRevision||0)+1;}
 get difficulty(){return effectiveDifficulty(this.host.visitor);}
 get name(){return this.host.visitor.name?`, ${esc(this.host.visitor.name)}`:'';}
 async load(){await Promise.all(['lessons','challenges','simulations','steam_projects','tech_topics','curiosities','routes','ranks','achievements','motivational_messages','assessments'].map(async key=>{try{this.data[key]=await this.host.api('/fair/data/'+key);this.errors.delete(key);}catch{this.errors.add(key);}}));}
 enter(page){
  if(page==='learn'){this.area='';this.lesson=null;this.routesView=false;}
  if(page==='challenge')this.round=null;
  if(page==='simulator'){this.sim=null;this.simChoice=null;}
  if(page==='explore')this.tech=null;
  if(page==='steam'){const saved=this.host.visitor.currentProjectId;this.project=this.data.steam_projects?.projects.find(p=>p.id===saved)||null;}
  if(page==='surprise')this.prepareSurprise();
 }
 home(){const visitor=this.host.visitor,activeRoute=Object.entries(visitor.routes||{}).find(([,s])=>s&&!s.complete&&(s.modules?.length||s.challenge||s.project)),route=activeRoute&&this.paths.routes.find(r=>r.id===activeRoute[0]);const resume=route?`<section class="home-nudge"><div><span class="eyebrow">Continúa donde lo dejaste</span><h2>${esc(route.name)}</h2><p>${activeRoute[1].modules?.length||0} de ${route.modules.length} módulos completados</p><progress value="${activeRoute[1].modules?.length||0}" max="${route.modules.length}" aria-label="Progreso de ${esc(route.name)}"></progress></div><button class="primary" data-resume-route="${esc(route.id)}">Continuar</button></section>`:'';const recommendation=activeRoute?`<section class="home-recommendation">${AllenMascot('thinking','small')}<div><span class="eyebrow">Allen te recomienda</span><p>Sigue con <strong>${esc(route.name)}</strong>, que ya empezaste.</p></div><button data-resume-route="${esc(route.id)}">Continuar</button></section>`:`<section class="home-recommendation">${AllenMascot('teaching','small')}<div><span class="eyebrow">Allen te recomienda</span><p>${visitor.difficulty==='Fácil'?'Prueba una microlección para descubrir algo nuevo.':visitor.difficulty==='Difícil'?'Pon a prueba tus ideas con un reto corto.':'Practica lógica con un reto corto.'}</p></div><button data-edu="navigate" data-value="challenge">Comenzar reto</button></section>`;return `<section class="experience-intro"><div><span class="eyebrow">Tu próxima idea empieza aquí</span><h1>Hola${visitor.name?`, ${esc(visitor.name)}`:''}</h1><p>¿Qué quieres aprender hoy?</p><span class="session-caption">${esc(visitor.difficulty)} · ${visitor.score.toLocaleString('es')} puntos</span></div>${AllenMascot('hello','medium')}</section>${this.rankPanel()}${resume}${recommendation}${EXPERIENCE_GROUPS.map(([group,items])=>`<section class="experience-group"><h2>${group}</h2><div class="experience-grid">${items.map(([id,title,desc,ico])=>card(title,desc,'navigate',id,ico)).join('')}</div></section>`).join('')}<div class="row">${btn('Cambiar dificultad','difficulty')}<span class="muted">${visitor.achievements.length} logros · ${visitor.activitiesCompleted} actividades completadas</span></div>`;}
 header(title,sub,pose='teaching'){return `<section class="experience-intro"><div><h1>${esc(title)}</h1><p>${esc(sub)}</p><span class="session-caption">${esc(this.host.visitor.difficulty==='Sorpréndeme'?'Allen adapta el nivel · '+this.difficulty:this.difficulty)}</span></div>${AllenMascot(pose,'medium')}</section>`;}
 render(page){
  const dataset={learn:'lessons',challenge:'challenges',simulator:'simulations',explore:'tech_topics',steam:'steam_projects',surprise:'curiosities'}[page];
  if(!dataset)return null;
  if(!this.data[dataset])return this.header(TITLES[page],'El contenido de esta actividad no pudo abrirse.')+btn('Reintentar contenido local','reload');
  return page==='surprise'?this.surpriseView():this[page]();
 }

 rankPanel(){
  const ranks=this.data.ranks?.ranks;if(!ranks)return '';
  const p=rankProgress(this.host.visitor.score,ranks);
  return `<section class="rank-panel"><div>${icon('star',20)}<strong>${esc(p.rank.name)}</strong><span>${this.host.visitor.score.toLocaleString('es')} puntos</span></div><progress value="${p.value}" max="${p.max}" aria-label="Progreso de rango"></progress><small>${p.next?`${this.host.visitor.score.toLocaleString('es')} / ${p.next.min.toLocaleString('es')} · ${p.remaining.toLocaleString('es')} puntos para el siguiente rango.`:'Has alcanzado el rango máximo. Sigue explorando a tu ritmo.'}</small></section>`;
 }
 openLesson(id){
  this.lesson=this.data.lessons.lessons.find(l=>l.id===id);this.step=0;this.answer=null;this.completed=false;this.easy=false;this.alt=false;
  this.assessment={phase:'pre',index:0,preAnswers:[],postAnswers:[],preScore:0,postScore:0};
 }
 assessmentView(){
  const a=this.assessment,l=this.lesson,set=this.data.assessments?.topics[l.id];
  if(!set)return '<p>La comprobación local no está disponible.</p>'+btn('Reintentar contenido local','reload');
  if(a.phase==='result'){
   const delta=a.postScore-a.preScore;
   return `<section class="panel assessment-result"><h1>Tu progreso</h1><h2>${esc(l.topic)}</h2><div class="assessment-comparison"><div>Antes<strong>${a.preScore}/3</strong></div><div>Después<strong>${a.postScore}/3</strong></div></div><p>${delta>0?`Mejoraste ${delta} ${delta===1?'respuesta':'respuestas'}.`:a.preScore===3&&a.postScore===3?'Ya resolvías las tres preguntas. Buen trabajo.':'Vamos a reforzarlo con otro ejemplo.'}</p><p>+50 por completar la lección${delta>0?' · +50 por mejora':''}${a.postScore===3?' · +100 por 3/3':''}. Las recompensas se entregan una vez por tema en esta visita.</p><p class="muted">Son tres preguntas breves y similares, una señal de práctica; no certifican dominio del tema.</p><details><summary>Revisar la comprobación</summary>${set.post.map((q,i)=>`<div><h3>${esc(q.question)}</h3><p>Tu respuesta: ${esc(q.options[a.postAnswers[i]])}</p><p>${esc(q.explanation)}</p></div>`).join('')}</details><div class="row">${this.paths.selected?btn('Seguir ruta','path-map','',true):btn('Elegir otro tema','topic-list','',true)}${btn('Repasar lección','review')}</div></section>`;
  }
  const questions=set[a.phase],q=questions[a.index];
  return `<section class="panel assessment"><span class="eyebrow">${a.phase==='pre'?'Antes de aprender':'Comprobación final'} · ${a.index+1}/3</span><h1>${a.phase==='pre'?'Antes de empezar, vamos a ver qué sabes.':'Vamos a comprobar lo aprendido.'}</h1><p>${esc(l.topic)} · Sin presión de tiempo.</p><h2>${esc(q.question)}</h2><div class="options">${q.options.map((o,i)=>btn(o,'assessment-answer',i)).join('')}</div><p class="muted">Responde con lo que sabes. Revisaremos las explicaciones al terminar.</p></section>`;
 }
 finishLesson(){
  const a=this.assessment,l=this.lesson,v=this.host.visitor,delta=a.postScore-a.preScore;
  v.preAssessmentScore=a.preScore;v.postAssessmentScore=a.postScore;
  v.assessments[l.id]={preAssessmentScore:a.preScore,postAssessmentScore:a.postScore};
  if(!v.completedLessons.includes(l.id))v.completedLessons.push(l.id);
  this.host.complete('lessons','lesson:'+l.id,50);
  if(delta>0){if(this.host.reward(50,'','improvement:'+l.id)){v.metrics.improvements=(v.metrics.improvements||0)+1;this.host.motivate('progress');}}
  if(a.postScore===3)this.host.reward(100,'','perfect:'+l.id);
  if(delta<=0&&a.postScore<3)this.host.motivate('mistake');
  this.paths.markLesson(l.id);this.host.event('lesson',l.id);
 }
 learn(){
  if(this.routesView)return this.paths.render();
  const all=this.data.lessons.lessons;
  if(!this.area)return this.header('Aprende algo con Allen','Elige un área y aprende paso a paso.')+`<div class="row">${btn(this.quick?'Ver lecciones de 6 pasos':'Aprende en 1 minuto','quick','',true)}${btn('Rutas de aprendizaje','paths')}<p>${this.quick?'Explicación · ejemplo · pregunta · resultado':'Diagnóstico · seis pasos · comprobación de progreso'}</p></div><div class="experience-grid">${this.data.lessons.areas.map(area=>card(area,`${all.filter(l=>l.area===area).length} temas disponibles`,'area',area,AREAS[area])).join('')}</div>`;
  if(!this.lesson)return this.header(this.area,'Elige el tema que quieres descubrir.')+`<div class="row">${btn('Cambiar área','area','')}${btn(this.quick?'Usar 6 pasos':'Aprende en 1 minuto','quick')}${btn('Rutas de aprendizaje','paths')}</div><div class="experience-grid">${all.filter(l=>l.area===this.area).map(l=>card(l.topic,l.title,'lesson',l.id,AREAS[this.area])).join('')}</div>`;
  if(this.assessment&&this.assessment.phase!=='lesson')return this.assessmentView();
  const l=this.lesson,labels=this.quick?['Explicación breve','Ejemplo','Práctica']:['Qué es','Ejemplo','Cómo funciona','Aplicación real','Práctica','Comprobación'];
  const content=this.quick?[l.quickSummary,l.example]:[(this.easy||this.difficulty==='Fácil')?l.conceptEasy:l.concept,l.example,l.howItWorks,l.realWorld];
  const practice=this.quick?this.step===2:this.step===4,final=!this.quick&&this.step===5;
  return `<div class="lesson-toolbar"><span class="eyebrow">${esc(this.area)} · ${this.quick?'Aprende en 1 minuto':`Paso ${this.step+1} de 6`}</span>${this.paths.selected?btn('Ver ruta','path-map'):btn('Cambiar tema','topic-list')}</div><progress value="${this.step+1}" max="${labels.length}" aria-label="Progreso de la lección"></progress><section class="panel lesson-card"><div class="row">${AllenMascot(this.answer!==null?'celebrating':'teaching','small')}<span>${esc(labels[this.step])}</span></div><h1>${esc(l.topic)}</h1>${this.step===0?`<p>Vamos paso a paso${this.name}.</p>`:''}${final?`<p>Ahora responderás tres preguntas para comparar con tu diagnóstico inicial.</p>${btn('Comenzar comprobación','post-start','',true)}`:practice?`<p>${esc(l.practice)}</p><h2>${esc(l.question)}</h2><div class="options">${l.options.map((o,i)=>btn(o,'lesson-answer',i,false,this.answer!==null)).join('')}</div>${this.answer!==null?`<div class="feedback"><h2>${this.answer===l.correct?`Buen trabajo${this.name}.`:'Veamos cómo reforzarlo.'}</h2><p>${esc(l.feedback)}</p>${btn('Continuar',this.quick?'post-start':'continue','',true)}</div>`:''}`:`<p class="lesson-copy">${esc(this.alt?l.altExample:this.easy?l.conceptEasy:content[this.step])}</p>${this.difficulty==='Difícil'&&!this.easy?`<aside class="depth-note"><strong>Para profundizar</strong><p>${esc(l.advanced||l.howItWorks)}</p></aside>`:''}<div class="row">${btn('Más fácil','easier')}${btn(this.alt?'Ver explicación':'Otro ejemplo','example')}${btn('Continuar','continue','',true)}${btn('Ponme a prueba','test')}</div>`}</section>`;
 }
 challenge(){
  if(!this.round)return this.header('Rétame','Elige una categoría y la duración de tu reto.','challenge')+`<label>Categoría<select id="challenge-category">${this.data.challenges.categories.map(c=>`<option ${c===this.category?'selected':''}>${esc(c)}</option>`).join('')}</select></label><div class="experience-grid">${[['quick','Reto rápido','3 preguntas'],['normal','Reto normal','5 preguntas'],['hard','Reto difícil','5 preguntas avanzadas'],['mixed','Reto mixto','5 preguntas de varias categorías'],['surprise','Reto sorpresa','Allen decide la combinación']].map(([v,t,d])=>card(t,d,'start-round',v,'target')).join('')}</div><p class="muted">Respuesta correcta: +100 · con pista: +75 · segundo intento: +50.</p>`;
  const r=this.round;
  if(r.done)return `<section class="achievement center">${AllenMascot('celebrating','large')}<h1>Buen trabajo${this.name}.</h1><p>Reto completado · ${r.questions.length} preguntas</p><div class="score">${r.score}</div><p>${r.correct} respuestas correctas · mejor racha: ${r.best}</p>${btn('Elegir otro reto','new-round','',true)}</section>`;
  const q=r.questions[r.index],f=r.feedback;
  return `<div class="round-summary"><span>${esc(q.category)} · ${esc(q.difficulty)}</span><strong>${r.score} puntos</strong><span>Racha: ${r.streak}</span><span>Pregunta ${r.index+1} de ${r.questions.length}</span></div><progress value="${r.index+1}" max="${r.questions.length}" aria-label="Progreso del reto"></progress><section class="panel"><h1>${esc(q.question)}</h1>${this.difficulty==='Fácil'?'<p>Lee cada opción con calma. Puedes pedir una pista antes de responder.</p>':''}<div class="options">${q.options.map((o,i)=>btn(o,'round-answer',i,false,!!f||r.tried.includes(i))).join('')}</div>${r.hinted?`<p class="hint-card">${icon('lightbulb',18)} ${esc(q.hint)}</p>`:!f?btn('Pedir pista','round-hint'):''}${f?`<div class="feedback" role="status"><h2>${f.correct?`¡Correcto! +${f.points}`:r.attempts<2?'Todavía puedes intentarlo.':'Veamos la explicación.'}</h2><p>${esc(f.correct||r.attempts>=2?q.explanation:q.hint)}</p>${!f.correct&&r.attempts<2?btn('Segundo intento','round-retry','',true):btn(r.index+1===r.questions.length?'Ver resultado':'Siguiente pregunta','round-next','',true)}</div>`:''}</section>`;
 }
 simulator(){
  if(!this.sim)return this.header('Simulador','¿Qué harías en esta situación?','thinking')+`<div class="experience-grid">${this.data.simulations.scenarios.map(s=>card(s.category,s.title,'scenario',s.id,'shield-check')).join('')}</div>`;
  const s=this.sim,chosen=this.simChoice!==null?s.options[this.simChoice]:null;
  return this.header(s.category,s.title,'thinking')+`<section class="panel"><p class="scenario-text">${esc(s.scenario)}</p>${this.difficulty==='Fácil'?`<p class="hint-card">Antes de actuar, piensa qué datos o permisos te están pidiendo y si puedes verificar el origen.</p>`:''}<div class="options">${s.options.map((o,i)=>btn(o.text,'sim-answer',i,false,!!chosen)).join('')}</div>${chosen?`<div class="feedback" role="status"><h2>${chosen.isCorrect?`Buena decisión${this.name}.`:'Esta decisión se puede mejorar.'}</h2><h3>Qué estuvo bien</h3><p>${chosen.isCorrect?'Elegiste una acción que ayuda a comprobar o proteger la información.':'Te detuviste a practicar antes de encontrarte con una situación real.'}</p><h3>Qué riesgo existía</h3><p>${esc(s.riskExplanation||s.allenExplanation)}</p><h3>Qué hacer realmente</h3><p>${esc(s.options.find(o=>o.isCorrect).text)}</p><h3>Qué aprendemos</h3><p>${esc(s.lesson)}</p>${this.difficulty==='Difícil'?'<p>Para profundizar: identifica qué información falta, cómo la verificarías y qué harías si ya hubieras actuado.</p>':''}${btn('Otra situación','sim-list','',true)}</div>`:''}</section>`;
 }
 explore(){
  if(!this.tech)return this.header('Explora Tecnología','Descubre áreas tecnológicas y aprende para qué sirven.')+`<div class="experience-grid">${this.data.tech_topics.areas.map(a=>card(a.name,a.desc,'tech',a.id,a.icon)).join('')}</div>`;
  const a=this.tech;
  return this.header(a.name,a.tagline)+block('Qué es',this.difficulty==='Fácil'?a.desc:a.whatIs)+block('Para qué sirve',a.usedFor)+`<div class="detail-grid"><section class="panel"><h2>Ejemplos reales</h2>${list(a.realExamples)}</section><section class="panel"><h2>Habilidades que necesitas</h2>${list(a.skills)}</section></div>`+block('Proyecto sencillo',a.simpleProject)+`<section class="panel"><h2>Ruta de aprendizaje</h2><ol>${a.learningPath.map(s=>`<li>${esc(s)}</li>`).join('')}</ol>${this.difficulty==='Difícil'?`<h3>Compara y diseña</h3><p>Elige dos ejemplos anteriores. Explica sus límites, los datos que necesitan y cómo comprobarías que funcionan.</p>`:'<p>Empieza por el primer paso y comprueba lo aprendido con un pequeño proyecto.</p>'}</section><div class="row">${btn('Ver otras áreas','tech-list')}${btn('Aprender un tema de esta área','tech-learn','',true)}</div>`;
 }
 projects(){const all=this.data.steam_projects.projects;return all.filter(p=>(this.projectCategory==='Todas'||p.category===this.projectCategory)&&(!this.interest||p.interest.includes(this.interest)));}
 steam(){
  const d=this.data.steam_projects;
  if(!this.project&&this.host.visitor.currentProjectId)this.project=d.projects.find(p=>p.id===this.host.visitor.currentProjectId)||null;
  if(!this.project)return this.header('Proyectos STEAM','Convierte una idea en algo que puedas construir.')+`<section class="panel"><h2>¿Qué te interesa?</h2><div class="chips">${d.interests.map(i=>`<button data-edu="interest" data-value="${esc(i)}" aria-pressed="${this.interest===i}">${esc(i.charAt(0).toUpperCase()+i.slice(1))}</button>`).join('')}</div><label>Categoría<select id="project-category">${['Todas','Ciencia','Tecnología','Ingeniería','Arte','Matemáticas','Robótica','Programación','Electrónica'].map(c=>`<option ${this.projectCategory===c?'selected':''}>${c}</option>`).join('')}</select></label>${btn('Generar idea','generate-project','',true)}</section><div class="experience-grid">${this.projects().map(p=>card(p.name,p.problem,'project',p.id,'flask-conical')).join('')||'<p>No hay coincidencias con ambos filtros. Cambia la categoría o el interés.</p>'}</div>`;
  const p=this.project,submission=this.host.visitor.projects?.[`steam:${p.id}`],done=['COMPLETED','EVALUATED'].includes(submission?.status);
  return this.header(p.name,`Proyecto local · ${p.category}`)+`<div class="round-summary"><span>Dificultad del proyecto: ${esc(p.difficulty)}</span><span>Tiempo aproximado: ${esc(p.estimatedTime)}</span></div>`+block('Problema',p.problem)+block('Solución',p.solution)+`<div class="detail-grid"><section class="panel"><h2>Materiales</h2>${list(p.materials)}</section><section class="panel"><h2>Qué aprenderás</h2>${list(p.learnings)}</section></div><section class="panel"><h2>Pasos</h2><ol>${p.steps.map(s=>`<li>${esc(s)}</li>`).join('')}</ol><h3>${this.difficulty==='Difícil'?'Tu ampliación':this.difficulty==='Fácil'?'Tu primer paso':'Comprueba tu proyecto'}</h3><p>${esc(this.difficulty==='Difícil'?'Define dos casos de fallo, añade pruebas y documenta una mejora medible.':this.difficulty==='Fácil'?p.steps[0]+' Haz una parte y comprueba el resultado antes de continuar.':'Prueba un caso habitual y uno inesperado. Anota qué funciona y qué cambiarías.')}</p><p class="muted">Prepara los materiales y programas antes de desconectarte. En circuitos usa baja tensión, una resistencia para cada LED y ayuda de una persona con experiencia.</p></section>${projectEvidence({...p,task:'Describe tu proyecto y lo que aprendiste.',checklist:['Seguí los pasos o documenté un prototipo en papel','Probé o expliqué un caso de uso','Identifiqué una mejora'],difficulty:this.difficulty},'project-finish',p.id,submission||null,{visitor:this.host.visitor,ranks:this.data.ranks?.ranks||[]})}${done?'':`<div class="row">${btn('Otra idea','generate-project','',true)}${btn('Explorar proyectos','project-list')}${btn('Pedir ayuda a Allen','project-help')}</div>`}`;
 }
 prepareSurprise(){
  const version=++this.surpriseRevision;this.surprise=null;this.surpriseMore=false;this.surpriseTest=false;this.surpriseChoice=null;
  setTimeout(()=>{if(version!==this.surpriseRevision)return;const pool=(this.data.curiosities?.activities||[]).filter(a=>a.id!==this.lastSurprise);this.surprise=pool[Math.floor(Math.random()*pool.length)]||null;this.lastSurprise=this.surprise?.id||'';if(this.host.page()==='surprise')this.host.render();},500);
 }
 surpriseView(){const s=this.surprise;if(!s)return this.header('Sorpréndeme','Allen elegirá algo diferente para ti.','thinking')+'<p role="status">Allen está preparando algo...</p>';
  return this.header('Sorpresa para ti',s.type,'celebrating')+`<section class="panel"><h2>${esc(s.title)}</h2><p>${esc(s.text)}</p>${this.difficulty==='Fácil'?`<p class="hint-card">${esc(s.hint)}</p>`:''}${this.surpriseMore||this.difficulty==='Difícil'?`<div class="depth-note"><h3>Explícame más</h3><p>${esc(s.explanation)}</p></div>`:''}${this.surpriseTest?`<h3>${esc(s.question)}</h3><div class="options">${s.options.map((o,i)=>btn(o,'surprise-answer',i,false,this.surpriseChoice!==null)).join('')}</div>${this.surpriseChoice!==null?`<div class="feedback"><strong>${this.surpriseChoice===s.correct?'¡Correcto!':'Ahora sabes algo nuevo.'}</strong><p>${esc(s.explanation)}</p></div>`:''}`:''}<div class="row">${btn('Otra sorpresa','surprise-next','',true)}${btn('Explícame más','surprise-more')}${btn('Ponme a prueba','surprise-test')}</div></section>`;
 }
 openProject(p){if(!p){this.host.toast('Prueba otra categoría o interés para encontrar una idea.');return;}this.project=p;this.host.visitor.currentProjectId=p.id;this.host.persist?.();this.host.event('project',p.id);}
 async handle(action,value){
  const h=this.host;
 if(action==='navigate'){h.go(value);return;}
  if(action==='game'){h.go('game');return;}
  if(action==='difficulty'){h.chooseDifficulty();return;}
  if(action==='reload'){await this.load();h.render();return;}
  if(action==='quick'){this.quick=!this.quick;this.lesson=null;}
  if(action==='area'){this.area=value;this.lesson=null;}
  if(action==='lesson')this.openLesson(value);
  if(action==='paths'){this.routesView=true;this.paths.selected=null;}
  if(action.startsWith('path-')){await this.paths.handle(action,value);return;}
  if(action==='assessment-answer'){
   const a=this.assessment;if(!a||!['pre','post'].includes(a.phase))return;
   const q=this.data.assessments.topics[this.lesson.id][a.phase][a.index],choice=Number(value);a[a.phase+'Answers'].push(choice);
   if(choice===q.correct){a[a.phase+'Score']++;h.reward(a.phase==='pre'?25:100,'',`${a.phase}:${this.lesson.id}:${a.index}`);}
   a.index++;
   if(a.index===3){if(a.phase==='pre'){h.visitor.preAssessmentScore=a.preScore;a.phase='lesson';a.index=0;}else{a.phase='result';this.finishLesson();}}
  }
  if(action==='post-start'){this.assessment.phase='post';this.assessment.index=0;}
  if(action==='topic-list')this.lesson=null;
  if(action==='review'){this.step=0;this.answer=null;this.alt=false;this.assessment.phase='lesson';this.assessment.postScore=0;this.assessment.postAnswers=[];}
  if(action==='easier'){this.easy=true;this.alt=false;h.toast(this.lesson.conceptEasy);}
  if(action==='example')this.alt=!this.alt;
  if(action==='continue'){this.step++;this.alt=false;}
  if(action==='test'){this.step=this.quick?2:4;this.alt=false;}
  if(action==='lesson-answer'&&this.answer===null){this.answer=Number(value);if(!this.completed){this.completed=true;h.reward(this.answer===this.lesson.correct?100:0,'','practice:'+this.lesson.id);if(this.answer!==this.lesson.correct)h.motivate('mistake');}}
  if(action==='start-round'){
   this.category=document.querySelector('#challenge-category').value;
   const mixed=value==='mixed'||(value==='surprise'&&Math.random()<.5),count=value==='quick'?3:value==='surprise'?(Math.random()<.5?3:5):5;
   const diff=value==='hard'?'Difícil':this.difficulty;
   const questions=chooseQuestions(this.data.challenges.questions,mixed?'Mixto':this.category,diff,count);
   this.round={questions,index:0,score:0,correct:0,streak:0,best:0,attempts:0,tried:[],hinted:false,feedback:null,done:false};
  }
  if(action==='round-hint'&&!this.round.feedback)this.round.hinted=true;
  if(action==='round-answer'&&!this.round.feedback){const r=this.round,q=r.questions[r.index],choice=Number(value);if(r.tried.includes(choice))return;r.attempts++;r.tried.push(choice);const correct=choice===q.correct,points=answerPoints(correct,r.attempts,r.hinted);r.feedback={correct,points};r.score+=points;if(correct){r.correct++;r.streak++;r.best=Math.max(r.best,r.streak);h.reward(points);}else r.streak=0;}
  if(action==='round-retry'&&this.round.attempts<2)this.round.feedback=null;
  if(action==='round-next'&&this.round.feedback){const r=this.round;if(r.index+1===r.questions.length){r.done=true;h.complete('challenges',`challenge:${Date.now()}`,0);h.event('challenge');}else{r.index++;r.feedback=null;r.hinted=false;r.attempts=0;r.tried=[];}}
  if(action==='new-round')this.round=null;
  if(action==='scenario'){this.sim=this.data.simulations.scenarios.find(s=>s.id===value);this.simChoice=null;}
  if(action==='sim-answer'&&this.simChoice===null){this.simChoice=Number(value);h.event('simulation');h.complete('simulations','simulation:'+this.sim.id,100);if(!this.sim.options[this.simChoice].isCorrect)h.motivate('mistake');}
  if(action==='sim-list'){this.sim=null;this.simChoice=null;}
  if(action==='tech')this.tech=this.data.tech_topics.areas.find(a=>a.id===value);
  if(action==='tech-list')this.tech=null;
  if(action==='tech-learn'){const name=this.tech.name;h.go('learn');this.area=this.data.lessons.areas.includes(name)?name:'Tecnología';}
  if(action==='interest'){this.interest=value;this.project=null;}
  if(action==='project')this.openProject(this.data.steam_projects.projects.find(p=>p.id===value));
  if(action==='generate-project'){const pool=this.projects().filter(p=>p.id!==this.project?.id);this.openProject(pool[Math.floor(Math.random()*pool.length)]||this.projects()[0]);}
  if(action==='project-list'){this.project=null;delete h.visitor.currentProjectId;h.persist?.();}
  if(action==='project-finish'){const key=`steam:${this.project.id}`,existing=h.visitor.projects?.[key];if(!existing){const evidence=readEvidence();if(!evidence)return;h.visitor.projects||={};h.visitor.projects[key]={projectId:this.project.id,status:'SUBMITTED',submittedAt:new Date().toISOString(),evidence,difficulty:h.visitor.difficulty,route:'STEAM y proyectos',evaluation:null,evaluatedAt:null,rewardsGranted:false};h.persist?.();}await evaluateSubmission(h,this.project,key,h.visitor.projects[key].evidence,{route:'STEAM y proyectos'});}
  if(action==='project-feedback-retry'){const key=`steam:${this.project.id}`;await retryEvaluationFeedback(h,this.project,key,h.visitor.projects?.[key]);}
  if(action==='project-help'){h.go('chat');h.send(`Ayúdame a empezar el proyecto ${this.project.name}: ${this.project.problem}`);return;}
  if(action==='surprise-next')this.prepareSurprise();
  if(action==='surprise-more')this.surpriseMore=true;
  if(action==='surprise-test')this.surpriseTest=true;
  if(action==='surprise-answer'&&this.surpriseChoice===null){this.surpriseChoice=Number(value);h.reward(this.surpriseChoice===this.surprise.correct?100:0,'Sorpresa: '+this.surprise.type);}
  h.render();
 }
 bind(main){main.querySelector('#project-category')?.addEventListener('change',e=>{this.projectCategory=e.target.value;this.host.render();});}
}
