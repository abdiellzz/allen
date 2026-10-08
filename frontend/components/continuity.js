const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const masteryLabel=score=>score>=80?'Dominado':score>=55?'En desarrollo':'Necesita refuerzo';
const masteryClass=score=>score>=80?'strong':score>=55?'developing':'weak';

export function continuityPanel(c){
 if(c?.current_activity?.activity_type==='course'&&['active','paused'].includes(c.current_activity.status)){
  const topicText=c.current_activity.topic?esc(c.current_activity.topic):'Tu siguiente tema';
  return `<section class="continuity-card primary-continuity v3-focus-card"><img src="/static/assets/allen-course-official.svg" alt=""><div><span class="eyebrow">CONTINÚA DONDE LO DEJASTE</span><h2>${esc(c.current_activity.subject||'Tu curso')}</h2><p><b>${topicText}</b> · Allen guardó exactamente dónde te quedaste.</p><div class="v3-focus-actions"><button class="primary" data-page="Cursos">Continuar curso</button><span>Tu progreso está guardado localmente</span></div></div></section>`;
 }
 if(c.adventure){
  return `<section class="continuity-card primary-continuity v3-focus-card"><img src="/static/assets/allen-resume.svg" alt=""><div><span class="eyebrow">CONTINÚA DONDE LO DEJASTE</span><h2>Aventura en curso</h2><p><b>Paso ${(c.adventure.current_step||0)+1}</b> · Puedes retomarla sin perder tu avance.</p><div class="v3-focus-actions"><button class="primary" data-page="Aventura">Continuar aventura</button><span>Guardado en este dispositivo</span></div></div></section>`;
 }
 if(c.study_session){
  const day=(c.study_session.plan?.days||[]).find(d=>d.date===c.study_session.day);
  const total=day?.activities?.length||1,idx=c.study_session.current_activity_index||0;
  return `<section class="continuity-card primary-continuity v3-focus-card"><img src="/static/assets/allen-paused.svg" alt=""><div><span class="eyebrow">SESIÓN EN PAUSA</span><h2>${esc(c.study_session.subject)}</h2><p><b>Paso ${Math.min(idx+1,total)} de ${total}</b> · Continúa sin repetir lo que ya hiciste.</p><div class="v3-focus-actions"><button class="primary" data-page="Plan Allen">Continuar sesión</button><span>Sesión recuperable</span></div></div></section>`;
 }
 if(c.study_plan){
  return `<section class="continuity-card v3-focus-card"><img src="/static/assets/allen-plan.svg" alt=""><div><span class="eyebrow">TU PLAN ACTIVO</span><h2>${esc(c.study_plan.subject)}</h2><p>Meta: <b>${esc(c.study_plan.goal)}</b> · ${esc(c.study_plan.deadline)}</p><button data-page="Plan Allen">Ver Plan Allen</button></div></section>`;
 }
 return `<section class="continuity-card v3-focus-card"><img src="/static/assets/allen-welcome.svg" alt=""><div><span class="eyebrow">EMPIEZA ALGO NUEVO</span><h2>Tu próxima curiosidad te espera.</h2><p>No tienes nada pendiente. Explora un tema o crea una meta concreta.</p><button data-page="Aprender">Explorar</button></div></section>`;
}

export function recommendationPanel(c){
 const r=c?.recommendation||{};
 const text=r.reason||'Elige un tema y conviértelo en una pequeña práctica.';
 return `<section class="recommendation-card v3-recommendation"><img src="/static/assets/allen-thinking-hard.svg" alt=""><div><span class="eyebrow">ALLEN RECOMIENDA</span><h2>${esc(text)}</h2><p>Esta recomendación usa tu progreso y actividad local. No depende de rankings ni telemetría.</p><button data-page="Practicar">Empezar una práctica</button></div></section>`;
}

export function masteryPanel(c){
 const rows=c?.mastery||[];
 if(!rows.length)return '';
 return '<section class="mastery-panel v3-mastery"><div class="section-head"><div><span class="eyebrow">EVIDENCIA DE DOMINIO</span><h2>Qué sabes y por qué Allen lo cree.</h2><p class="muted">El porcentaje siempre aparece junto a la evidencia que lo sostiene.</p></div><button data-page="Progreso">Ver progreso completo</button></div><div class="mastery-grid">'+rows.slice(0,6).map(row=>{
  const score=Math.max(0,Math.min(100,Number(row.mastery_score)||0));
  return '<article class="mastery-card '+masteryClass(score)+'"><div class="row spaced"><div><strong>'+esc(row.topic)+'</strong><small>'+esc(row.subject)+'</small></div><b class="mastery-score">'+score+'%</b></div><div class="row spaced mastery-state"><span>'+masteryLabel(score)+'</span><small>'+(row.next_review?'Revisión: '+esc(row.next_review):'Sin revisión pendiente')+'</small></div><div class="mastery-track" aria-label="Dominio '+score+'%"><i data-progress-width="'+Math.max(3,score)+'"></i></div><div class="mastery-evidence-grid"><span><b>'+esc(row.correct_answers||0)+'/'+esc(row.attempts||0)+'</b> respuestas</span><span aria-label="'+esc(row.practice_count||0)+' prácticas"><b>'+esc(row.practice_count||0)+'</b> prácticas</span><span aria-label="'+esc(row.hints_used||0)+' pistas"><b>'+esc(row.hints_used||0)+'</b> pistas</span></div></article>';
 }).join('')+'</div></section>';
}

export function reviewPanel(c){
 const rows=c?.due_topic_reviews||[];
 if(!rows.length)return '';
 return '<section class="review-due-panel v3-review"><div class="row spaced"><div><span class="eyebrow">REPASO ESPACIADO</span><h2>Hoy conviene recordar '+rows.length+' '+(rows.length===1?'tema':'temas')+'.</h2><p>Refuerza lo aprendido antes de que se vuelva más difícil recuperarlo.</p></div><img src="/static/assets/allen-checklist-official.svg" alt="Allen preparando tu repaso"></div><div class="review-due-list">'+rows.map(r=>'<article><div><strong>'+esc(r.topic)+'</strong><small>'+esc(r.subject)+' · dominio '+r.mastery_score+'%</small></div><span>'+esc(r.next_review||'hoy')+'</span></article>').join('')+'</div><button data-page="Practicar" class="primary">Repasar ahora</button></section>';
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
