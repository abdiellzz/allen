const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function continuityPanel(c){
 if(c?.current_activity?.activity_type==='course'&&['active','paused'].includes(c.current_activity.status)){
  const topicText=c.current_activity.topic?('Tema: '+esc(c.current_activity.topic)+'. '):'';
  return `<section class="continuity-card primary-continuity"><img src="/static/assets/allen-course-official.svg" alt=""><div><span class="eyebrow">CONTINÚA DONDE LO DEJASTE</span><h2>${esc(c.current_activity.subject||'Tu curso')}</h2><p>${topicText}Allen guardó tu ruta en este dispositivo.</p><button class="primary" data-page="Cursos">Continuar curso</button></div></section>`;
 }
 if(c.adventure){
  return `<section class="continuity-card primary-continuity"><img src="/static/assets/allen-resume.svg" alt=""><div><span class="eyebrow">CONTINÚA DONDE LO DEJASTE</span><h2>Aventura en curso</h2><p>Paso ${(c.adventure.current_step||0)+1}. Tu progreso está guardado en este dispositivo.</p><button class="primary" data-page="Aventura">Continuar aventura</button></div></section>`;
 }
 if(c.study_session){
  const day=(c.study_session.plan?.days||[]).find(d=>d.date===c.study_session.day);
  const total=day?.activities?.length||1,idx=c.study_session.current_activity_index||0;
  return `<section class="continuity-card primary-continuity"><img src="/static/assets/allen-paused.svg" alt=""><div><span class="eyebrow">SESIÓN EN PAUSA</span><h2>${esc(c.study_session.subject)}</h2><p>Paso ${Math.min(idx+1,total)} de ${total}. Puedes continuar desde donde estabas.</p><button class="primary" data-page="Plan Allen">Continuar sesión</button></div></section>`;
 }
 if(c.study_plan){
  return `<section class="continuity-card"><img src="/static/assets/allen-plan.svg" alt=""><div><span class="eyebrow">TU PLAN ACTIVO</span><h2>${esc(c.study_plan.subject)}</h2><p>Meta: ${esc(c.study_plan.goal)} · Fecha: ${esc(c.study_plan.deadline)}</p><button data-page="Plan Allen">Ver Plan Allen</button></div></section>`;
 }
 return `<section class="continuity-card"><img src="/static/assets/allen-welcome.svg" alt=""><div><span class="eyebrow">EMPIEZA ALGO NUEVO</span><h2>Tu próxima curiosidad te espera.</h2><p>No tienes una sesión activa. Puedes explorar, practicar o crear un plan.</p><button data-page="Aprender">Explorar</button></div></section>`;
}

export function recommendationPanel(c){
 const r=c?.recommendation||{};
 const text=r.reason||'Elige un tema y conviértelo en una pequeña práctica.';
 return `<section class="recommendation-card"><img src="/static/assets/allen-thinking-hard.svg" alt=""><div><span class="eyebrow">PRÓXIMA MEJOR ACCIÓN</span><h2>${esc(text)}</h2><p>Allen usa tu progreso local, no un ranking.</p></div></section>`;
}

export function masteryPanel(c){
 const rows=c?.mastery||[];
 if(!rows.length)return '';
 return '<section class="mastery-panel"><div class="section-head"><div><span class="eyebrow">QUÉ ESTÁS DOMINANDO</span><h2>Tu progreso por tema</h2></div></div><div class="mastery-grid">'+rows.slice(0,6).map(row=>'<article><div class="row spaced"><strong>'+esc(row.topic)+'</strong><span>'+row.mastery_score+'%</span></div><small>'+esc(row.subject)+' · '+esc(String(row.status||'').replaceAll('_',' '))+'</small><div class="mastery-track"><i style="width:'+Math.max(3,row.mastery_score)+'%"></i></div></article>').join('')+'</div></section>';
}

export function detectExamIntent(text){
 const q=String(text||'').toLowerCase();
 const hit=['examen','parcial','prueba','evaluación','evaluacion','estudiar para'].some(term=>q.includes(term));
 if(!hit)return null;
 const subjects=['matemáticas','matematicas','redes','ciberseguridad','programación','programacion','python','inglés','ingles','ciencias','ia'];
 const subject=subjects.find(name=>q.includes('de '+name)||q.includes('para '+name)||q.includes(name))||'';
 const normalized={matematicas:'matemáticas',programacion:'programación',ingles:'inglés'};
 return {subject:normalized[subject]||subject,raw:text};
}
