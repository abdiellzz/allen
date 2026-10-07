const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export async function continuityPanel(api,profileId){
 const c=await api('/continuity?profile_id='+profileId);
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

export async function recommendationPanel(api,profileId){
 const c=await api('/continuity?profile_id='+profileId);
 const text=c.recommendation||'Elige un tema y conviértelo en una pequeña práctica.';
 return `<section class="recommendation-card"><img src="/static/assets/allen-thinking-hard.svg" alt=""><div><span class="eyebrow">RECOMENDADO PARA TI</span><h2>${esc(text)}</h2><p>Esta sugerencia usa únicamente tu actividad local.</p></div></section>`;
}

export function detectExamIntent(text){
 const q=String(text||'').toLowerCase();
 const hit=/(examen|parcial|prueba|evaluaci[oó]n|estudiar para)/.test(q);
 if(!hit)return null;
 const subject=(q.match(/(?:de|para)s+(matem[aá]ticas|redes|ciberseguridad|programaci[oó]n|python|ingl[eé]s|ciencias|ia)/)||[])[1]||'';
 return {subject,raw:text};
}
