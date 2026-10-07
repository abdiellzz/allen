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
 <section id="study-session-stage"></section>
 <section class="panel simulation-maker">
  <div class="row spaced"><div><span class="eyebrow">SIMULACRO ALLEN</span><h2>Practica como si fuera el examen.</h2><p>Sin pistas ni explicaciones hasta terminar.</p></div><img src="/static/assets/allen-exam.svg" alt="Allen preparando un simulacro"></div>
  <form id="simulation-form" class="field-grid">
   <label>Materia<input id="sim-subject" maxlength="80" required placeholder="Redes"></label>
   <label>Temas<input id="sim-topics" maxlength="500" required placeholder="IPv4, subnetting"></label>
   <label>Preguntas<input id="sim-count" type="number" min="3" max="10" value="5"></label>
   <label>Minutos<input id="sim-minutes" type="number" min="5" max="120" value="20"></label>
   <label>Modo<select id="sim-timed"><option value="true">Con tiempo</option><option value="false">Sin tiempo</option></select></label>
   <button class="primary">Comenzar simulacro</button>
  </form>
  <div id="simulation-stage"></div>
 </section>
 <section class="panel study-guide-maker">
  <div class="row spaced"><div><span class="eyebrow">GUÍAS DE ESTUDIO</span><h2>Convierte tus apuntes en práctica.</h2><p>Pega un texto y Allen lo organiza localmente como guía Cornell o guía de estudio.</p></div></div>
  <form id="study-guide-form" class="stack">
   <label>Título<input id="guide-title" maxlength="120" value="Mi guía de estudio"></label>
   <label>Apuntes<textarea id="guide-text" minlength="20" maxlength="20000" rows="8" required placeholder="Pega aquí tus apuntes…"></textarea></label>
   <div class="row"><button class="primary" data-guide-kind="cornell" type="submit">Convertir a Cornell</button><button data-guide-kind="study" type="button">Crear guía completa</button></div>
  </form>
  <div id="study-guide-output"></div>
 </section>`;
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
 try{const prefill=JSON.parse(sessionStorage.getItem('allen-plan-prefill')||'null');if(prefill){if(prefill.subject)root.querySelector('#plan-subject').value=prefill.subject;root.querySelector('#plan-goal').value='Prepararme para examen';sessionStorage.removeItem('allen-plan-prefill');}}catch{}
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
 const simulationForm=root.querySelector('#simulation-form'),simulationStage=root.querySelector('#simulation-stage');
 let simulationTimer=null;
 function stopTimer(){if(simulationTimer){clearInterval(simulationTimer);simulationTimer=null;}}
 function renderSimulation(sim){
  stopTimer();
  const saved=Array.isArray(sim.answers)?sim.answers:[];
  let seconds=sim.minutes>0?(Number.isFinite(Number(sim.remaining_seconds))&&Number(sim.remaining_seconds)>0?Number(sim.remaining_seconds):sim.minutes*60):0;
  const formatTime=value=>{const m=Math.max(0,Math.floor(value/60)),sec=Math.max(0,value%60);return m+':'+String(sec).padStart(2,'0');};
  simulationStage.innerHTML=`<section class="simulation-shell" data-sim-id="${sim.id}"><div class="row spaced"><div><span class="eyebrow">SIMULACRO EN CURSO</span><h2>${esc(sim.subject)}</h2></div><div class="simulation-meta"><strong>${sim.questions.length} preguntas</strong><span id="sim-timer">${sim.minutes>0?formatTime(seconds):'Sin límite de tiempo'}</span></div></div><progress value="${saved.filter(Boolean).length}" max="${sim.questions.length}" aria-label="Progreso del simulacro"></progress><form id="simulation-answers">${sim.questions.map((q,i)=>`<fieldset><legend>${i+1}. ${esc(q.prompt)}</legend>${(q.options||[]).map(o=>`<label class="answer-option"><input type="radio" name="sim-${i}" value="${esc(o)}" ${saved[i]===o?'checked':''} required><span>${esc(o)}</span></label>`).join('')}</fieldset>`).join('')}<button class="primary">Entregar simulacro</button></form></section>`;
  const formEl=simulationStage.querySelector('#simulation-answers');
  const collectAnswers=()=>sim.questions.map((_,i)=>simulationStage.querySelector(`input[name="sim-${i}"]:checked`)?.value||'');
  const persist=async(status='active')=>api('/simulations/'+sim.id+'/progress','POST',{profile_id:profileId,answers:collectAnswers(),status,remaining_seconds:sim.minutes>0?seconds:null}).catch(()=>{});
  formEl.addEventListener('change',async()=>{const answers=collectAnswers();simulationStage.querySelector('progress').value=answers.filter(Boolean).length;await persist('active');});
  if(sim.minutes>0){
   const timer=simulationStage.querySelector('#sim-timer');
   let ticks=0;
   simulationTimer=setInterval(async()=>{
    seconds=Math.max(0,seconds-1);ticks++;
    if(timer)timer.textContent=formatTime(seconds);
    if(seconds===0){
      stopTimer();
      await persist('interrupted');
      toast('Terminó el tiempo. Tus respuestas y el tiempo quedaron guardados.');
      return;
    }
    if(ticks%10===0)await persist('active');
   },1000);
  }
  formEl.onsubmit=async ev=>{ev.preventDefault();stopTimer();const answers=collectAnswers();const result=await api('/simulations/'+sim.id+'/submit','POST',{profile_id:profileId,answers});const total=result.total||sim.questions.length,score=result.score||0,pct=Math.round(score/Math.max(1,total)*100);simulationStage.innerHTML=`<section class="simulation-result" data-result-sim="${sim.id}"><img src="/static/assets/allen-celebrate-official.svg" alt="Allen celebrando"><div><span class="eyebrow">RESULTADO</span><h2>${score}/${total} · ${pct}%</h2><p><b>Fuerte:</b> ${esc((result.mastered||[]).join(', ')||'en construcción')}</p><p><b>Reforzar:</b> ${esc((result.review||[]).join(', ')||'ninguno destacado')}</p><div class="row"><button class="primary" id="create-reinforcement">Crear Plan de Refuerzo</button><button data-page="Progreso">Ver progreso</button></div></div></section>`;const reinforce=simulationStage.querySelector('#create-reinforcement');reinforce.onclick=async()=>{const created=await api('/simulations/'+sim.id+'/reinforcement?profile_id='+profileId,'POST',{});if(created.plan_id){toast('Plan de refuerzo creado.');await refresh();current.scrollIntoView({behavior:'smooth',block:'start'});}else toast(created.message||'No necesitas un refuerzo adicional ahora.');};};
 }
 simulationForm.onsubmit=async e=>{e.preventDefault();try{
  const timed=root.querySelector('#sim-timed').value==='true';
  const payload={profile_id:profileId,subject:root.querySelector('#sim-subject').value.trim(),topics:root.querySelector('#sim-topics').value.split(',').map(x=>x.trim()).filter(Boolean),question_count:Number(root.querySelector('#sim-count').value),minutes:Number(root.querySelector('#sim-minutes').value),timed,level:profile.level};
  const sim=await api('/simulations','POST',payload);renderSimulation({...sim,answers:[]});
 }catch(error){toast(error.message);}};
 try{const activeSim=await api('/simulations/active?profile_id='+profileId);if(activeSim)renderSimulation(activeSim);}catch{}
 const guideForm=root.querySelector('#study-guide-form'),guideOut=root.querySelector('#study-guide-output');
 async function makeGuide(kind){
  const text=root.querySelector('#guide-text').value.trim();if(text.length<20){toast('Añade un poco más de contenido.');return;}
  const payload={profile_id:profileId,title:root.querySelector('#guide-title').value.trim()||'Guía de estudio',text};
  const data=await api('/guides/'+kind,'POST',payload);
  if(kind==='cornell'){
   guideOut.innerHTML=`<section class="v2-cornell-sheet study-guide-result"><aside><strong>Preguntas / pistas</strong>${data.cues.map(x=>`<span>${esc(x)}</span>`).join('')}</aside><main><strong>Notas principales</strong>${data.notes.map(x=>`<p>${esc(x)}</p>`).join('')}<footer><b>Resumen:</b> ${esc(data.summary)}</footer></main></section>`;
  }else{
   guideOut.innerHTML=`<section class="study-guide-result panel"><span class="eyebrow">GUÍA ALLEN</span><h2>${esc(data.title)}</h2><h3>Conceptos importantes</h3><ul>${data.concepts.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><h3>Preguntas de recuperación</h3><ol>${data.questions.map(x=>`<li>${esc(x)}</li>`).join('')}</ol><h3>Mini quiz</h3><ol>${data.mini_quiz.map(x=>`<li>${esc(x)}</li>`).join('')}</ol><h3>Resumen</h3><p>${esc(data.summary)}</p></section>`;
  }
  guideOut.scrollIntoView({behavior:'smooth',block:'start'});
 }
 guideForm.onsubmit=e=>{e.preventDefault();makeGuide('cornell').catch(err=>toast(err.message));};
 root.querySelector('[data-guide-kind="study"]').onclick=()=>makeGuide('study').catch(err=>toast(err.message));
 await refresh();
}

function bindSession(stage,plan,session,{api,profileId,go,toast}){
 const day=(plan.plan?.days||[]).find(d=>d.date===session.day)||(plan.plan?.days||[])[0];let index=Math.min(session.current_activity_index||0,Math.max(0,(day?.activities?.length||1)-1));
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
   await api('/study-sessions/'+session.id+'/event','POST',{profile_id:profileId,kind:'paused',activity_index:index,note:'Sesión pausada por el estudiante.'}).catch(()=>{});
   stage.innerHTML='<section class="panel"><h2>Sesión en pausa</h2><p>Tu progreso quedó guardado. Puedes continuar desde este mismo paso cuando vuelvas.</p></section>';
  }
 };
}
