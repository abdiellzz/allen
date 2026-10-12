// Browser projection of backend/learning_engine.py. Parity covered by Python tests.
// Keep changes synchronized with that implementation; see docs/MOBILE.md.
import {course, courses, getCourse, questions, questionById, topicById} from './course.mjs';
export const RULES_VERSION = 'learning-engine-1';
// Python round uses ties-to-even; preserve it in the browser projection.
const roundEven = v => {const n=Math.floor(v),f=v-n;return f===.5?(n%2===0?n:n+1):Math.round(v);};
export function localDay(now = new Date()) {
  return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
}
export function nextReviewDate(score, now = new Date()) {
  const d=new Date(now); d.setDate(d.getDate()+(score<40?1:score<60?2:score<80?4:7)); return localDay(d);
}
export function computeMastery({attempts=0,correct=0,incorrect=0,hints=0,practice_count=0,quiz_count=0,last_seen=null,next_review=null,difficulty='Normal'}={}, now=new Date()) {
  if(attempts<=0 && practice_count<=0 && quiz_count<=0) return {score:0,confidence:0,status:'new'};
  const accuracy=correct/Math.max(1,attempts), evidence=Math.min(1,(attempts+practice_count+quiz_count)/12);
  const bonus={'Fácil':0,'Normal':4,'Difícil':8}[difficulty]??2;
  let recent=0;
  if(last_seen){const seenDay=String(last_seen).includes('T')?localDay(new Date(last_seen)):String(last_seen).slice(0,10);const day=new Date(`${localDay(now)}T00:00:00Z`),seen=new Date(`${seenDay}T00:00:00Z`); const age=(day-seen)/86400000;recent=Number.isFinite(age)?age<=1?6:age<=7?3:0:0;}
  const score=roundEven(Math.max(0,Math.min(100,accuracy*72+evidence*16+bonus+recent-Math.min(18,hints*3))));
  const confidence=roundEven(evidence*100);
  const status=score>=85&&confidence>=55?'mastered':incorrect>=3&&score<45?'needs_reinforcement':next_review&&next_review<=localDay(now)?'reviewing':score>=55?'practicing':'learning';
  return {score,confidence,status};
}
export function recommendForState({mastery_score:score=0,topic='este tema',status}) {
  if(status==='needs_reinforcement'||score<30) return {action:'explain',reason:`Conviene reconstruir ${topic} con una explicación corta y un ejemplo concreto.`,priority:.95};
  if(score<60) return {action:'guided_practice',reason:`Tu dominio de ${topic} está creciendo; una práctica guiada es el siguiente paso.`,priority:.82};
  if(score<80) return {action:'interleave',reason:`Ya tienes base en ${topic}; mezclar ejercicios comprobará si eliges bien la estrategia.`,priority:.72};
  return {action:'challenge',reason:`Tu dominio de ${topic} es alto; conviene un reto y dejar una revisión futura.`,priority:.62};
}
// Old events are folded into one 'summary' per topic (see compactEvents); their counters still count as evidence.
export const SUMMARY_FIELDS=['attempts','correct','incorrect','hints','explanations','practice','checks'];
const EVENT_LIMIT=5000, KEEP_RECENT=2500;
export function evidence(state,topicId,now=new Date()) {
  const events=state.events.filter(e=>e.topicId===topicId), answers=events.filter(e=>e.type==='answer');
  const summaries=events.filter(e=>e.type==='summary'), sum=key=>summaries.reduce((n,e)=>n+e[key],0);
  const row={attempts:answers.length+sum('attempts'),correct:answers.filter(e=>e.correct).length+sum('correct'),incorrect:answers.filter(e=>!e.correct).length+sum('incorrect'),hints:events.filter(e=>e.type==='hint').length+sum('hints'),explanations:events.filter(e=>e.type==='help').length+sum('explanations'),practice_count:events.filter(e=>e.type==='practice_complete').length+sum('practice'),quiz_count:events.filter(e=>e.type==='check_complete').length+sum('checks'),last_seen:events.at(-1)?.at??null,difficulty:state.profile.level==='bases'?'Fácil':'Normal'};
  const last=events.findLast(e=>e.type==='review_scheduled');
  const result=computeMastery({...row,next_review:last?.due??null},now);
  return {...row,...result,next_review:last?.due??null};
}
export const activeCourse = state => getCourse(state.activeCourse??course.id)??course;
export const diagnosed = (state,id=activeCourse(state).id) => id===course.id?state.diagnosticComplete:(state.diagnosticCourses??[]).includes(id);
export function chooseCourse(state,id){
  if(!getCourse(id))throw Error('Curso no válido.');
  if(state.session&&state.session.phase!=='complete')throw Error('Termina la actividad actual antes de cambiar de curso.');
  state.activeCourse=id;
}
export function recommendation(state,now=new Date()) {
  const course=activeCourse(state);
  const minutes=state.profile.minutes;
  if(state.session && state.session.phase!=='complete') return {kind:'continue',topicId:state.session.topicId,title:'Continúa tu sesión',reason:`Tu actividad está guardada. Dispones de ${minutes} minutos.`};
  if(!diagnosed(state)) return {kind:'diagnostic',title:'Encuentra tu punto de partida',reason:`${course.topics.length*2} preguntas breves para elegir el apoyo que necesitas. No es una calificación.`};
  const due=course.topics.find(t=>{const e=evidence(state,t.id,now);return e.next_review&&e.next_review<=localDay(now);});
  if(due) return {kind:'review',topicId:due.id,title:`Repasa ${due.title.toLowerCase()}`,reason:`Tu repaso estaba previsto para ${evidence(state,due.id,now).next_review}. Vamos a comprobar qué recuerdas.`};
  const target=course.topics.find(t=>!state.completed.includes(t.id));
  if(target){const e=evidence(state,target.id,now);const rec=recommendForState({mastery_score:e.score,topic:target.title,status:e.status});
    return {kind:'learn',topicId:target.id,title:target.title,reason:`${rec.reason} ${minutes<=5?'Hoy puedes hacer una explicación y una práctica; el resto queda guardado.':'La sesión incluye un ejemplo, dos prácticas y una comprobación.'}`};}
  return {kind:'review',topicId:course.topics.reduce((a,b)=>evidence(state,a.id,now).score<=evidence(state,b.id,now).score?a:b).id,title:'Consolida lo que aprendiste',reason:`Completaste las ${course.topics.length} comprobaciones del curso. Puedes repasar sin esperar la fecha programada.`};
}
export function newState(profile) {return {version:1,rulesVersion:RULES_VERSION,courseId:course.id,profile,diagnosticComplete:false,events:[],completed:[],session:null,cards:{}};}
export function startSession(state,kind='learn',topicId=null) {
  if(state.session && state.session.phase!=='complete') throw Error('Continúa la sesión actual antes de iniciar otra.');
  if(kind!=='diagnostic'&&!diagnosed(state,topicById(topicId)?.courseId)) throw Error('Completa primero el diagnóstico.');
  if(!['diagnostic','learn','review'].includes(kind)) throw Error('Actividad no válida.');
  const topic=topicById(topicId);
  const selected=kind==='diagnostic'?activeCourse(state):getCourse(topic?.courseId);
  if(kind!=='diagnostic'&&!topic) throw Error('Tema no válido.');
  if(kind!=='diagnostic'&&topic.prerequisite&&!state.completed.includes(topic.prerequisite)) throw Error(`Primero completa ${topicById(topic.prerequisite).title}.`);
  const ids=kind==='diagnostic'?questions.filter(q=>q.kind==='diagnostic'&&q.courseId===selected.id).map(q=>q.id):topic.questions.filter(q=>q.kind!=='diagnostic').map(q=>q.id);
  state.activeCourse=selected.id;
  state.session={id:crypto.randomUUID(),courseId:selected.id,kind,topicId,index:0,phase:kind==='diagnostic'?'practice':'lesson',questionIds:ids,answers:[],hints:[]};
}
// Keeps long-term profiles usable: the oldest events become per-topic summaries with the same counters,
// so mastery is unchanged. The latest review_scheduled of each topic and the newest events stay as they are.
export function compactEvents(state) {
  const lastReview=new Map();state.events.forEach((e,i)=>{if(e.type==='review_scheduled')lastReview.set(e.topicId,i);});
  const keepFrom=state.events.length-KEEP_RECENT, totals=new Map(), kept=[];
  state.events.forEach((e,i)=>{
    if(e.type!=='summary'&&(i>=keepFrom||lastReview.get(e.topicId)===i)){kept.push(e);return;}
    const t=totals.get(e.topicId)??{id:crypto.randomUUID(),type:'summary',topicId:e.topicId,at:e.at,...Object.fromEntries(SUMMARY_FIELDS.map(k=>[k,0]))};
    if(e.type==='summary')SUMMARY_FIELDS.forEach(k=>{t[k]+=e[k];});
    else if(e.type==='answer'){t.attempts++;if(e.correct)t.correct++;else t.incorrect++;}
    else if(e.type==='hint')t.hints++;else if(e.type==='help')t.explanations++;
    else if(e.type==='practice_complete')t.practice++;else if(e.type==='check_complete')t.checks++;
    if(e.at>t.at)t.at=e.at;
    totals.set(e.topicId,t);
  });
  state.events=[...totals.values(),...kept];
}
function event(state,type,topicId,values={},now=new Date()) {if(state.events.length>=EVENT_LIMIT)compactEvents(state);state.events.push({id:crypto.randomUUID(),type,topicId,at:now.toISOString(),...values});}
export function requestHelp(state,action,now=new Date()) {
  const s=state.session;const q=s&&questionById(s.questionIds[s.index]); const topic=topicById(s?.topicId??q?.topicId);
  if(!topic) throw Error('Abre una lección para recibir ayuda contextual.');
  if(action==='hint'){
    if(s.phase!=='practice'||s.answers.some(a=>a.questionId===q.id))throw Error('Las pistas se usan antes de responder.');
    const count=s.hints.filter(id=>id===q.id).length;
    if(count>=q.hints.length)return {text:q.hints.at(-1),source:topic.source};
    s.hints.push(q.id);event(state,'hint',topic.id,{questionId:q.id,sessionId:s.id},now);return {text:q.hints[count],source:topic.source};
  }
  if(!['explain','alternative','simple'].includes(action))throw Error('Ayuda no válida.');
  const answered=q&&s.answers.find(a=>a.questionId===q.id);
  const text=action==='alternative'?topic.alternative:action==='simple'?topic.simple:answered&&!answered.correct?`Revisemos tu respuesta ${answered.answer}. ${q.feedback} ${topic.simple}`:topic.explanation;
  event(state,'help',topic.id,{action},now);return {text,source:topic.source};
}
export function submitAnswer(state,answer,now=new Date()) {
  const s=state.session;if(!s||s.phase!=='practice')throw Error('No hay una pregunta activa.');
  const q=questionById(s.questionIds[s.index]);if(!q||!q.options.includes(answer))throw Error('Elige una respuesta válida.');
  if(s.answers.some(a=>a.questionId===q.id))throw Error('Esta respuesta ya fue registrada.');
  const correct=answer===q.answer;const row={questionId:q.id,answer,correct};
  s.answers.push(row);event(state,'answer',q.topicId,{...row,sessionId:s.id},now);
  return {correct,text:q.feedback};
}
export function advance(state,now=new Date()) {
  const s=state.session;if(!s)throw Error('No hay una sesión activa.');
  if(s.phase==='lesson'){s.phase='practice';return;}
  if(s.phase!=='practice'||!s.answers.some(a=>a.questionId===s.questionIds[s.index]))throw Error('Responde antes de continuar.');
  if(s.index<s.questionIds.length-1){s.index++;return;}
  s.phase='complete';
  if(s.kind==='diagnostic'){if((s.courseId??course.id)===course.id)state.diagnosticComplete=true;else state.diagnosticCourses=[...new Set([...(state.diagnosticCourses??[]),s.courseId])];return;}
  const correct=s.answers.filter(a=>a.correct).length, check=s.answers.at(-1).correct;
  event(state,'practice_complete',s.topicId,{},now);event(state,'check_complete',s.topicId,{},now);
  if(correct>=2&&check&&!state.completed.includes(s.topicId))state.completed.push(s.topicId);
  const due=nextReviewDate(evidence(state,s.topicId,now).score,now);event(state,'review_scheduled',s.topicId,{due},now);
}
export function reviewCard(state,topicId,remembered,now=new Date()) {
  if(!topicById(topicId)||!state.completed.includes(topicId))throw Error('Completa primero la lección.');
  const due=nextReviewDate(remembered?80:20,now);state.cards[topicId]={due,remembered,at:now.toISOString()};
  event(state,'card_review',topicId,{remembered},now);
}
