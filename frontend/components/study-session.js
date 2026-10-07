const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function planAllenPage(level='Premedia'){
 return `<div class="v2-page-heading"><div><span class="eyebrow">PLAN ALLEN</span><h1>Planifica cómo vas a aprender.</h1><p>Allen organiza temas, práctica y repasos según tu tiempo, tu objetivo y tu progreso local.</p></div></div>
 <section class="v2-adventure-hero">
  <div><span class="eyebrow">ESTUDIO ACTIVO</span><h2>Menos “leer todo”. Más recuperar, practicar y revisar.</h2><p>El plan se construye offline con reglas pedagógicas y usa tu historial local para priorizar temas débiles y tarjetas pendientes.</p></div>
  <img src="/static/assets/allen-study.svg" alt="Allen organizando una sesión de estudio">
 </section>
 <section class="panel">
  <form id="study-plan-form" class="stack">
   <div class="field-grid">
    <label>Materia<input id="plan-subject" maxlength="80" required placeholder="Redes"></label>
    <label>Temas<input id="plan-topics" maxlength="500" required placeholder="IPv4, subnetting, DNS, DHCP"></label>
    <label>Fecha objetivo<input id="plan-deadline" type="date" required></label>
    <label>Minutos por día<input id="plan-minutes" type="number" min="10" max="240" value="40" required></label>
    <label>Nivel<select id="plan-level"><option>Primaria</option><option>Premedia</option><option>Media</option><option>Universidad / Técnico</option></select></label>
    <label>Objetivo<input id="plan-goal" maxlength="160" value="Prepararme para examen" required></label>
   </div>
   <button class="primary">Crear mi plan</button>
  </form>
 </section>
 <section id="study-plan-current"></section>
 <section id="study-session-stage"></section>`;
}

function activityIcon(type){
 return ({explanation:'01',retrieval:'02',practice:'03',spaced_review:'04',simulation:'EX',review:'R'})[type]||'•';
}

function renderPlan(plan){
 const days=plan.plan?.days||plan.days||[];
 return `<section class="plan-allen-shell">
  <div class="row spaced"><div><span class="eyebrow">PLAN ALLEN · ${esc(plan.subject)}</span><h2>${esc(plan.goal)}</h2><p>${esc((plan.topics||plan.plan?.topics||[]).join(' · '))}</p></div><button class="primary" data-start-plan="${plan.id}">Iniciar sesión de hoy</button></div>
  <div class="plan-allen-days">${days.map((d,i)=>`<article><div class="row spaced"><strong>Día ${i+1}</strong><span>${esc(d.date)}</span></div>${d.activities.map(a=>`<div class="plan-activity"><b>${activityIcon(a.type)}</b><span><strong>${esc(a.label)}</strong><small>${a.minutes} min · ${esc(a.topic)}</small></span></div>`).join('')}</article>`).join('')}</div>
 </section>`;
}

function renderSession(plan,session){
 const day=(plan.plan?.days||[]).find(d=>d.date===session.day)||(plan.plan?.days||[])[0];
 if(!day)return '<section class="panel"><p>No hay actividades para hoy. Puedes ajustar el plan.</p></section>';
 return `<section class="session-allen">
  <div class="row spaced"><div><span class="eyebrow">SESIÓN ALLEN</span><h2>${esc(plan.subject)} · ${day.activities.reduce((n,a)=>n+a.minutes,0)} min</h2></div><button data-end-session>Terminar sesión</button></div>
  <progress id="session-progress" value="0" max="${day.activities.length}" aria-label="Progreso de sesión"></progress>
  <div id="session-activity">${renderActivity(day.activities[0],0,day.activities.length)}</div>
 </section>`;
}

function renderActivity(a,index,total){
 return `<article class="session-activity-card" data-activity-index="${index}">
  <span class="eyebrow">PASO ${index+1}/${total}</span>
  <h2>${esc(a.label)}</h2><p>${esc(a.topic)} · ${a.minutes} minutos estimados</p>
  <div class="session-method-note">${methodText(a.type)}</div>
  <div class="v2-chat-actions"><button data-session-action="hint">Necesito una pista</button><button data-session-action="explain">Explícamelo mejor</button><button data-session-action="understood">Ya entendí</button><button data-session-action="not_understood">No entendí</button><button data-session-action="skip">Saltar</button><button class="primary" data-session-next>Continuar</button></div>
 </article>`;
}
function methodText(type){
 return ({explanation:'Primero comprende la idea con un ejemplo concreto.',retrieval:'Intenta recordar sin mirar. Allen no debe mostrarte la respuesta todavía.',practice:'Aplica la idea en un ejercicio nuevo o mezclado.',spaced_review:'Vuelve a una idea anterior o a tarjetas pendientes.',simulation:'Responde sin pistas, como preparación de examen.',review:'Revisa errores y explica por qué la respuesta correcta funciona.'})[type]||'Aprende a tu ritmo.';
}

export async function bindPlanAllen(root,{api,profileId,profile,go,toast}){
 const form=root.querySelector('#study-plan-form'),current=root.querySelector('#study-plan-current'),stage=root.querySelector('#study-session-stage');
 const level=root.querySelector('#plan-level'); if(level&&profile?.level)level.value=profile.level;
 const deadline=root.querySelector('#plan-deadline');if(deadline){const d=new Date();d.setDate(d.getDate()+7);deadline.value=d.toISOString().slice(0,10);deadline.min=new Date().toISOString().slice(0,10);}
 async function refresh(){
  const plans=await api('/study-plans?profile_id='+profileId);
  current.innerHTML=plans.length?renderPlan(plans[0]):'<section class="panel empty"><h2>Aún no tienes un plan</h2><p>Crea uno para organizar tus próximas sesiones.</p></section>';
 }
 form.onsubmit=async e=>{e.preventDefault();try{
  const payload={profile_id:profileId,subject:root.querySelector('#plan-subject').value.trim(),topics:root.querySelector('#plan-topics').value.split(',').map(x=>x.trim()).filter(Boolean),deadline:deadline.value,minutes_per_day:Number(root.querySelector('#plan-minutes').value),level:level.value,goal:root.querySelector('#plan-goal').value.trim()};
  await api('/study-plans','POST',payload);toast('Plan Allen creado.');await refresh();
 }catch(error){toast(error.message);}};
 current.addEventListener('click',async e=>{
  const b=e.target.closest('[data-start-plan]');if(!b)return;
  try{
   const plan=await api('/study-plans/'+b.dataset.startPlan+'?profile_id='+profileId);
   const session=await api('/study-plans/'+b.dataset.startPlan+'/start?profile_id='+profileId,'POST',{});
   stage.innerHTML=renderSession(plan,session);
   bindSession(stage,plan,session,{api,profileId,go,toast});
   stage.scrollIntoView({behavior:'smooth',block:'start'});
  }catch(error){toast(error.message);}
 });
 await refresh();
}

function bindSession(stage,plan,session,{api,profileId,go,toast}){
 const day=(plan.plan?.days||[]).find(d=>d.date===session.day)||(plan.plan?.days||[])[0];let index=0;
 const show=()=>{const activity=day.activities[index];stage.querySelector('#session-activity').innerHTML=renderActivity(activity,index,day.activities.length);stage.querySelector('#session-progress').value=index;};
 stage.onclick=async e=>{
  const action=e.target.closest('[data-session-action]')?.dataset.sessionAction;
  if(action){
   const kind=action==='skip'?'skipped':action==='hint'?'hint':action==='understood'?'understood':action==='not_understood'?'not_understood':'started';
   await api('/study-sessions/'+session.id+'/event','POST',{profile_id:profileId,kind,activity_index:index,note:''}).catch(()=>{});
   const activity=day.activities[index];
   if(action==='hint'||action==='explain'||action==='not_understood'){go('Tutor');setTimeout(()=>{const input=document.querySelector('#chat-input');if(input){input.value=(action==='hint'?'Dame una pista sin revelar la respuesta sobre ':'Explícame de otra forma, con un ejemplo concreto, ')+activity.topic;input.focus();}},50);}
   if(action==='skip'){if(index<day.activities.length-1){index++;show();}else toast('Sesión terminada.');}
   return;
  }
  if(e.target.closest('[data-session-next]')){
   await api('/study-sessions/'+session.id+'/event','POST',{profile_id:profileId,kind:index===day.activities.length-1?'completed':'understood',activity_index:index,note:''}).catch(()=>{});
   if(index<day.activities.length-1){index++;show();}else{stage.innerHTML='<section class="panel"><h2>Sesión completada</h2><p>Buen trabajo. Allen usará este avance para tu próxima recomendación.</p></section>';toast('Sesión Allen completada.');}
  }
  if(e.target.closest('[data-end-session]')){
   await api('/study-sessions/'+session.id+'/event','POST',{profile_id:profileId,kind:'skipped',activity_index:index,note:'Sesión terminada por el estudiante.'}).catch(()=>{});
   stage.innerHTML='<section class="panel"><h2>Sesión guardada</h2><p>Podemos ajustar el plan cuando quieras.</p></section>';
  }
 };
}
