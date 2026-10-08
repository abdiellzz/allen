import {missions} from './v2.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function card(m,active){
 const isActive=active?.adventure_id===m.id;
 return `<button class="v2-mission-card ${isActive?'current':''}" data-adventure-start="${esc(m.id)}">
  <img src="${m.image}" alt="">
  <span class="v2-mission-status">${isActive?'En curso':'Empezar'}</span>
  <span class="eyebrow">${esc(m.subject)} · ${esc(m.difficulty)}</span>
  <strong>${esc(m.title)}</strong><span>${esc(m.description)}</span><small>+${m.xp} puntos de misión</small>
 </button>`;
}
function stage(m,session){
 const i=Math.min(session.current_step||0,m.steps.length-1),step=m.steps[i],pct=Math.round((i/m.steps.length)*100);
 return `<section class="persistent-adventure" data-session-id="${session.id}" data-adventure-id="${esc(m.id)}" data-step="${i}">
  <div class="row spaced"><div><span class="eyebrow">AVENTURA EN CURSO</span><h2>${esc(m.title)}</h2><p>${esc(m.subject)} · Paso ${i+1}/${m.steps.length}</p></div><button class="quiet danger-soft" data-finish-adventure>Finalizar aventura</button></div>
  <div class="continuity-progress"><i data-width-pct="${pct}"></i></div>
  <article class="v2-stage-card">
   <span class="eyebrow">PASO ${i+1}</span><h2>${esc(step.title)}</h2><p class="v2-stage-question">${esc(step.text)}</p>
   <div class="v2-stage-options">${step.options.map((o,n)=>`<button data-adventure-answer="${n}">${esc(o)}</button>`).join('')}</div>
   <button class="hint-link" data-adventure-hint>Necesito una pista</button>
   <div class="v2-stage-feedback" aria-live="polite"></div>
  </article>
 </section>`;
}

export async function adventureContinuityPage(api,profileId){
 const active=await api('/adventures/active?profile_id='+profileId);
 const activeMission=active&&missions.find(m=>m.id===active.adventure_id);
 return `<div class="v2-page-heading"><div><span class="eyebrow">APRENDE HACIENDO</span><h1>Aventura con Allen</h1><p>Tu progreso se guarda en este dispositivo. Puedes cerrar ALLEN y continuar después.</p></div></div>
 ${activeMission?`<section class="continuity-hero"><img src="/static/assets/allen-guide.svg" alt="Allen listo para continuar"><div><span class="eyebrow">CONTINÚA TU AVENTURA</span><h2>${esc(activeMission.title)}</h2><p>Paso ${(active.current_step||0)+1} de ${activeMission.steps.length}. No se termina hasta que tú lo decidas.</p><button class="primary" data-resume-active>Continuar aventura</button></div></section>`:''}
 <section class="v2-mission-grid">${missions.map(m=>card(m,active)).join('')}</section>
 <div id="persistent-adventure-stage">${activeMission?stage(activeMission,active):''}</div>`;
}

export function bindAdventureContinuity(root,profileId,{api,toast,refresh=()=>{}}){
 const stageRoot=root.querySelector('#persistent-adventure-stage');
 async function start(id){
  const session=await api('/adventures/start','POST',{profile_id:profileId,adventure_id:id});
  const mission=missions.find(m=>m.id===id);stageRoot.innerHTML=stage(mission,session);
  stageRoot.scrollIntoView({behavior:'smooth',block:'start'});
 }
 root.querySelectorAll('[data-adventure-start]').forEach(b=>b.onclick=()=>start(b.dataset.adventureStart).catch(e=>toast(e.message)));
 root.querySelector('[data-resume-active]')?.addEventListener('click',()=>stageRoot.scrollIntoView({behavior:'smooth',block:'start'}));
 stageRoot?.addEventListener('click',async e=>{
  const shell=e.target.closest('[data-session-id]');if(!shell)return;
  const sid=Number(shell.dataset.sessionId),mission=missions.find(m=>m.id===shell.dataset.adventureId),index=Number(shell.dataset.step),step=mission.steps[index];
  if(e.target.closest('[data-adventure-hint]')){
   await api('/adventures/'+sid+'/event','POST',{profile_id:profileId,step:index,event:'hint',answer:''});
   shell.querySelector('.v2-stage-feedback').innerHTML=`<div class="v2-feedback"><strong>Pista</strong><p>${esc(step.hint)}</p></div>`;return;
  }
  const answer=e.target.closest('[data-adventure-answer]');
  if(answer){
   const choice=Number(answer.dataset.adventureAnswer);
   const answered=await api('/adventures/'+sid+'/event','POST',{profile_id:profileId,step:index,event:'answer',answer:step.options[choice]});
   if(!answered.correct){shell.querySelector('.v2-stage-feedback').innerHTML=`<div class="v2-feedback retry"><strong>Vamos a reforzarlo.</strong><p>${esc(step.explanation)}</p></div>`;return;}
   if(index<mission.steps.length-1){
    const updated=await api('/adventures/'+sid+'/event','POST',{profile_id:profileId,step:index+1,event:'advance',answer:''});
    stageRoot.innerHTML=stage(mission,updated);
   }else{
    const updated=await api('/adventures/'+sid+'/event','POST',{profile_id:profileId,step:mission.steps.length,event:'complete',answer:''});
    stageRoot.innerHTML=`<section class="adventure-complete"><img src="/static/assets/allen-celebrate-official.svg" alt="Allen celebrando"><div><span class="eyebrow">AVENTURA COMPLETADA</span><h2>${esc(mission.title)}</h2><p>Completaste ${mission.steps.length} pasos. Errores registrados: ${updated.mistakes}. Pistas usadas: ${updated.hints_used}.</p><button data-page="Progreso">Ver mi progreso</button></div></section>`;toast('Aventura completada y guardada.');
   }
   return;
  }
  if(e.target.closest('[data-finish-adventure]')){
   if(!confirm('¿Quieres terminar esta aventura? Tu progreso se guardará como finalizado.'))return;
   const updated=await api('/adventures/'+sid+'/event','POST',{profile_id:profileId,step:index,event:'abandon',answer:''});
   stageRoot.innerHTML=`<section class="adventure-complete"><img src="/static/assets/allen-celebrate-official.svg" alt="Allen celebrando"><div><h2>Aventura finalizada</h2><p>Tu progreso quedó guardado. Completaste ${updated.completed_steps} pasos y puedes volver cuando quieras.</p><button data-page="Inicio">Volver al inicio</button></div></section>`;toast('Aventura finalizada.');
  }
 });
}
