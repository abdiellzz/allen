import {newState, RULES_VERSION, SUMMARY_FIELDS} from './engine.mjs';
import {course, courses, allTopics, getCourse, topicById, questionById} from './course.mjs';
const NAME='allen-mobile-v1';
const requestResult = request => new Promise((resolve,reject)=>{request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);});
const done = tx => new Promise((resolve,reject)=>{tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error??Error('No se pudo guardar.'));});
export async function openStorage(){
  const request=indexedDB.open(NAME,1);
  request.onupgradeneeded=()=>{request.result.createObjectStore('profiles',{keyPath:'profile.id'});request.result.createObjectStore('meta');};
  const db=await requestResult(request);
  db.onversionchange=()=>db.close();
  return db;
}
export async function listProfiles(db){const tx=db.transaction('profiles','readonly');return requestResult(tx.objectStore('profiles').getAll());}
export async function activeProfile(db){const tx=db.transaction('meta','readonly');return requestResult(tx.objectStore('meta').get('active'));}
export async function loadProfile(db,id){const tx=db.transaction('profiles','readonly');return requestResult(tx.objectStore('profiles').get(id));}
export async function selectProfile(db,id){if(!await loadProfile(db,id))throw Error('No existe ese perfil.');const tx=db.transaction('meta','readwrite');const complete=done(tx);tx.objectStore('meta').put(id,'active');await complete;}
export async function saveProfile(db,state,{creating=false}={}){
  validateState(state);
  const tx=db.transaction(['profiles','meta'],'readwrite'),complete=done(tx);
  try {
    const store=tx.objectStore('profiles'); const current=await requestResult(store.get(state.profile.id));
    if((creating&&current)||(!creating&&(!current||current.revision!==state.revision)))throw Error('El perfil cambió en otra pestaña. Recarga para continuar.');
    const next={...state,revision:(current?.revision??0)+1};store.put(next);tx.objectStore('meta').put(state.profile.id,'active');await complete;
    return next;
  } catch(error) {
    try{tx.abort();}catch{/* The transaction may already be aborted. */}
    await complete.catch(()=>{});throw error;
  }
}
export async function createProfile(db,{name,goal,level,minutes}) {
  const profile={id:crypto.randomUUID(),name:String(name).trim(),goal,level,minutes:Number(minutes)};
  return saveProfile(db,{...newState(profile),revision:0},{creating:true});
}
export async function deleteProfile(db,id){
  const tx=db.transaction(['profiles','meta'],'readwrite'),complete=done(tx);tx.objectStore('profiles').delete(id);
  const meta=tx.objectStore('meta');const current=await requestResult(meta.get('active'));if(current===id)meta.delete('active');await complete;
}
function fail(){throw Error('La copia no es compatible o contiene datos no válidos.');}
const day=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&!Number.isNaN(Date.parse(value));
const timestamp=value=>typeof value==='string'&&value.length<=30&&!Number.isNaN(Date.parse(value));
const uuid=value=>typeof value==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
export function validateState(s){
  if(!s||s.version!==1||s.rulesVersion!==RULES_VERSION||s.courseId!==course.id||!Number.isSafeInteger(s.revision)||s.revision<0)fail();
  if(s.activeCourse!==undefined&&!getCourse(s.activeCourse))fail();
  if(s.diagnosticCourses!==undefined&&(!Array.isArray(s.diagnosticCourses)||s.diagnosticCourses.length>courses.length||s.diagnosticCourses.some(id=>!getCourse(id))||new Set(s.diagnosticCourses).size!==s.diagnosticCourses.length))fail();
  if(s.preferences!==undefined&&(!s.preferences||!['normal','large'].includes(s.preferences.textSize)))fail();
  const p=s.profile;if(!p||!uuid(p.id)||typeof p.name!=='string'||p.name.trim().length<1||p.name.length>40||!['school','explore'].includes(p.goal)||!['bases','practice','challenge'].includes(p.level)||![5,10,15].includes(p.minutes))fail();
  if(typeof s.diagnosticComplete!=='boolean'||!Array.isArray(s.completed)||s.completed.length>allTopics.length||new Set(s.completed).size!==s.completed.length||s.completed.some(id=>!topicById(id)))fail();
  for(const id of s.completed){const pre=topicById(id).prerequisite;if(pre&&!s.completed.includes(pre))fail();}
  if(!Array.isArray(s.events)||s.events.length>5000)fail();
  const eventIds=new Set();
  for(const e of s.events){
    if(!e||!uuid(e.id)||eventIds.has(e.id)||!topicById(e.topicId)||!timestamp(e.at)||!['answer','hint','help','practice_complete','check_complete','review_scheduled','card_review','summary'].includes(e.type))fail();eventIds.add(e.id);
    if(e.type==='summary'&&(SUMMARY_FIELDS.some(k=>!Number.isSafeInteger(e[k])||e[k]<0)||e.correct+e.incorrect!==e.attempts))fail();
    if(['answer','hint'].includes(e.type)){const q=questionById(e.questionId);if(!q||q.topicId!==e.topicId||!uuid(e.sessionId))fail();if(e.type==='answer'&&(!q.options.includes(e.answer)||typeof e.correct!=='boolean'||e.correct!==(e.answer===q.answer)))fail();}
    if(e.type==='review_scheduled'&&!day(e.due))fail();
    if(e.type==='card_review'&&typeof e.remembered!=='boolean')fail();
    if(e.type==='help'&&!['explain','simple','alternative'].includes(e.action))fail();
  }
  if(!s.cards||typeof s.cards!=='object'||Array.isArray(s.cards))fail();
  for(const [id,c] of Object.entries(s.cards)){if(!topicById(id)||!c||typeof c.remembered!=='boolean'||!day(c.due)||!timestamp(c.at))fail();}
  if(s.session!==null){
    const a=s.session;if(!a||!uuid(a.id)||!['diagnostic','learn','review'].includes(a.kind)||!['lesson','practice','complete'].includes(a.phase))fail();
    if(a.kind!=='diagnostic'&&!topicById(a.topicId))fail();
    if(a.kind==='diagnostic'&&(a.topicId!==null||a.phase==='lesson'))fail();
    const selected=getCourse(a.courseId??course.id);if(!selected)fail();
    if(a.kind!=='diagnostic'&&topicById(a.topicId).courseId!==selected.id)fail();
    const expected=a.kind==='diagnostic'?selected.topics.flatMap(t=>t.questions.filter(q=>q.kind==='diagnostic').map(q=>q.id)):topicById(a.topicId).questions.filter(q=>q.kind!=='diagnostic').map(q=>q.id);
    if(JSON.stringify(a.questionIds)!==JSON.stringify(expected)||!Number.isInteger(a.index)||a.index<0||a.index>=expected.length||!Array.isArray(a.answers)||a.answers.length>expected.length||!Array.isArray(a.hints)||a.hints.length>expected.length*2)fail();
    const seen=new Set();for(const [index,r] of a.answers.entries()){const q=questionById(r.questionId);if(!q||r.questionId!==expected[index]||index>a.index||seen.has(r.questionId)||!q.options.includes(r.answer)||r.correct!==(r.answer===q.answer))fail();seen.add(r.questionId);}
    for(const id of a.hints){if(!expected.includes(id)||a.hints.filter(x=>x===id).length>questionById(id).hints.length)fail();}
    if(a.phase==='practice'&&![a.index,a.index+1].includes(a.answers.length))fail();
    if(a.phase==='complete'&&a.answers.length!==expected.length)fail();
    if(a.phase==='lesson'&&a.answers.length)fail();
  }
  return s;
}
export function exportBackup(state){validateState(state);return JSON.stringify({format:'allen-mobile-backup',version:1,state},null,2);}
export function parseBackup(text){
  if(typeof text!=='string'||text.length>2_000_000)fail();
  let value;try{value=JSON.parse(text);}catch{fail();}
  if(value?.format!=='allen-mobile-backup'||value.version!==1)fail();
  validateState(value.state);
  // Only copy known properties. Never accept executable courses, privileges or AI settings.
  const s=value.state;
  return structuredClone({version:s.version,rulesVersion:s.rulesVersion,courseId:s.courseId,...(s.preferences?{preferences:{textSize:s.preferences.textSize}}:{}),...(s.activeCourse?{activeCourse:s.activeCourse}:{}),...(s.diagnosticCourses?{diagnosticCourses:s.diagnosticCourses}:{}),profile:{id:s.profile.id,name:s.profile.name,goal:s.profile.goal,level:s.profile.level,minutes:s.profile.minutes},diagnosticComplete:s.diagnosticComplete,events:s.events.map(e=>Object.fromEntries(Object.entries(e).filter(([k])=>['id','type','topicId','at','questionId','answer','correct','sessionId','action','due','remembered',...SUMMARY_FIELDS].includes(k)))),completed:s.completed,session:s.session?{id:s.session.id,...(s.session.courseId?{courseId:s.session.courseId}:{}),kind:s.session.kind,topicId:s.session.topicId,index:s.session.index,phase:s.session.phase,questionIds:s.session.questionIds,answers:s.session.answers.map(a=>({questionId:a.questionId,answer:a.answer,correct:a.correct})),hints:s.session.hints}:null,cards:Object.fromEntries(Object.entries(s.cards).map(([k,c])=>[k,{due:c.due,remembered:c.remembered,at:c.at}])),revision:s.revision});
}
export function prepareRecovery(text){const s=parseBackup(text);const suffix=' · recuperado';s.profile.id=crypto.randomUUID();s.profile.name=s.profile.name.slice(0,40-suffix.length)+suffix;s.revision=0;validateState(s);return s;}
export async function restoreBackup(db,text){return saveProfile(db,prepareRecovery(text),{creating:true});}
