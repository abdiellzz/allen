import {allenGuide,learningStepRail} from './allen-guide.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function teacherStudioPage(){
 return `<div class="v2-page-heading"><div><span class="eyebrow">ALLEN TEACHER STUDIO</span><h1>Convierte material docente en una ruta de aprendizaje.</h1><p>Importa PDF, TXT o Markdown. Allen estructura el contenido localmente y el profesor decide qué se publica.</p></div></div>
 ${allenGuide('teaching','Primero organizo el material. Después tú revisas objetivos, temas, preguntas y fuentes antes de publicarlo.')}
 <section class="teacher-import panel">
  <form id="teacher-import-form" class="stack">
   <div class="field-grid">
    <label>Título del curso<input id="course-title" maxlength="140" required placeholder="Fundamentos de Redes"></label>
    <label>Materia<input id="course-subject" maxlength="80" required placeholder="Redes"></label>
    <label>Nivel<select id="course-level"><option>Primaria</option><option>Premedia</option><option>Media</option><option>Universidad / Técnico</option></select></label>
   </div>
   <label>Material docente<input id="course-file" type="file" accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown" required></label>
   <p class="muted">Todo se procesa en este equipo. Máximo 8 MB y 250 páginas en esta versión.</p>
   <button class="primary">Analizar y crear borrador</button>
  </form>
  <details class="import-panel"><summary>Importar un Course Pack de Allen</summary><p>Los .allenpack se importan como borrador y deben revisarse antes de publicarse en este dispositivo.</p><input id="course-pack-file" type="file" accept=".allenpack,application/json"><button id="course-pack-import" type="button">Importar Course Pack</button></details>
 </section>
 <section id="teacher-course-list"></section>
 <section id="teacher-course-review"></section>`;
}

function coverage(c={}){
 return `<div class="course-coverage"><span><b>${c.units||0}</b> unidades</span><span><b>${c.topics||0}</b> temas</span><span><b>${c.questions||0}</b> preguntas</span><span><b>${c.flashcards||0}</b> tarjetas</span><span class="${c.topics_without_questions?'warn':''}"><b>${c.topics_without_questions||0}</b> sin preguntas</span></div>`;
}
function courseList(rows){
 if(!rows.length)return '<section class="panel empty"><h2>Aún no hay cursos</h2><p>Importa un documento para crear el primer borrador.</p></section>';
 return `<section class="teacher-course-grid">${rows.map(r=>`<article class="teacher-course-card"><div class="row spaced"><span class="eyebrow">${esc(r.subject)} · ${esc(r.level)}</span><span class="pill">${esc(r.status)}</span></div><h2>${esc(r.title)}</h2>${coverage(r.coverage)}<div class="row"><button data-review-course="${r.id}">Revisar</button>${r.status==='reviewed'?`<button class="primary" data-publish-course="${r.id}">Publicar</button>`:''}${r.status==='published'?`<span class="pill green">Publicado</span><button data-export-pack="${r.id}">Exportar .allenpack</button>`:''}</div></article>`).join('')}</section>`;
}
function reviewView(row){
 const s=row.structure;
 return `<section class="course-review-shell">
  ${allenGuide('teaching','Nada generado se publica automáticamente. Revisa la estructura y las fuentes antes de aprobarla.')}
  <div class="row spaced"><div><span class="eyebrow">BORRADOR DEL CURSO</span><h1>${esc(row.title)}</h1><p>${esc(row.document?.filename||'Fuente local')} · ${row.document?.page_count||0} páginas</p></div><span class="pill">${esc(row.status)}</span></div>
  ${coverage(s.coverage)}
  <div class="course-unit-list">${s.units.map((u,ui)=>`<article class="course-unit"><div class="row spaced"><h2>${ui+1}. ${esc(u.title)}</h2><span>${u.topics.length} temas</span></div>${u.topics.map((t,ti)=>`<details ${ui===0&&ti===0?'open':''}><summary>${esc(t.title)} <small>· pág. ${t.source?.page||'—'}</small></summary><label>Objetivo<input data-objective="${ui}:${ti}" value="${esc(t.objective)}" maxlength="220"></label><blockquote>${esc(t.source_excerpt||'')}</blockquote><div class="course-route-mini">${(t.route||[]).map(x=>`<span>${esc(x.label)}</span>`).join('<i>→</i>')}</div><h3>Preguntas propuestas</h3>${(t.questions||[]).map((q,qi)=>`<label>Pregunta ${qi+1}<input data-question="${ui}:${ti}:${qi}" value="${esc(q.prompt)}" maxlength="320"></label>`).join('')}</details>`).join('')}</article>`).join('')}</div>
  <section class="teacher-exam-review"><div class="row spaced"><div><span class="eyebrow">EXAMEN FINAL PROPUESTO</span><h2>Comprueba la evaluación antes de publicar.</h2></div><span class="pill">${(s.final_exam||[]).length} preguntas</span></div>
   ${(s.final_exam||[]).length?(s.final_exam||[]).map((q,i)=>`<details><summary>${i+1}. ${esc(q.topic)}</summary><p><b>${esc(q.prompt)}</b></p><ul>${(q.options||[]).map(o=>`<li class="${o===q.correct?'correct-option':''}">${esc(o)}${o===q.correct?' · respuesta':''}</li>`).join('')}</ul><small>Fuente: página ${q.source?.page||'—'}</small></details>`).join(''):'<p class="muted">Todavía no hay preguntas para el examen final.</p>'}
  </section>
  <div class="row"><button class="primary" id="approve-course">Guardar revisión y aprobar</button><button id="close-course-review">Volver</button></div>
 </section>`;
}

export function bindTeacherStudio(root,{api,profileId,toast}){
 const form=root.querySelector('#teacher-import-form'),list=root.querySelector('#teacher-course-list'),review=root.querySelector('#teacher-course-review');
 let current=null;
 async function refresh(){const rows=await api('/teacher/courses?profile_id='+profileId);list.innerHTML=courseList(rows);}
 form.onsubmit=async e=>{e.preventDefault();try{
   const file=root.querySelector('#course-file').files[0];if(!file)throw new Error('Selecciona un archivo.');
   if(file.size>8_000_000)throw new Error('El archivo supera 8 MB.');
   const base64=await fileToBase64(file);
   const data=await api('/teacher/import','POST',{profile_id:profileId,title:root.querySelector('#course-title').value.trim(),subject:root.querySelector('#course-subject').value.trim(),level:root.querySelector('#course-level').value,filename:file.name,mime:file.type||mimeFor(file.name),content_base64:base64});
   toast('Borrador creado. Ahora revísalo antes de publicar.');form.reset();await refresh();await openReview(data.course_id);
  }catch(err){toast(err.message);}};
 async function openReview(id){current=await api('/teacher/courses/'+id+'?profile_id='+profileId);review.innerHTML=reviewView(current);review.scrollIntoView({behavior:'smooth',block:'start'});}
 list.onclick=e=>{const r=e.target.closest('[data-review-course]'),p=e.target.closest('[data-publish-course]'),x=e.target.closest('[data-export-pack]');if(r)openReview(r.dataset.reviewCourse).catch(err=>toast(err.message));if(p)publish(Number(p.dataset.publishCourse));if(x)exportPack(Number(x.dataset.exportPack));};
 async function publish(id){try{await api('/teacher/courses/'+id+'/publish','POST',{profile_id:profileId});toast('Curso publicado para este dispositivo.');await refresh();}catch(err){toast(err.message);}}
 async function exportPack(id){try{const pack=await api('/teacher/courses/'+id+'/pack?profile_id='+profileId);const blob=new Blob([JSON.stringify(pack,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(pack.course?.title||'curso-allen').replace(/[^a-z0-9áéíóúñ_-]+/gi,'-')+'.allenpack';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);toast('Course Pack exportado.');}catch(err){toast(err.message);}}
 review.onclick=async e=>{
  if(e.target.id==='close-course-review'){review.innerHTML='';return;}
  if(e.target.id!=='approve-course'||!current)return;
  review.querySelectorAll('[data-objective]').forEach(input=>{const [u,t]=input.dataset.objective.split(':').map(Number);current.structure.units[u].topics[t].objective=input.value.trim();});
  review.querySelectorAll('[data-question]').forEach(input=>{const [u,t,q]=input.dataset.question.split(':').map(Number);current.structure.units[u].topics[t].questions[q].prompt=input.value.trim();});
  try{await api('/teacher/courses/'+current.id+'/review','PUT',{profile_id:profileId,structure:current.structure});toast('Revisión guardada. Ya puedes publicar el curso.');review.innerHTML='';await refresh();}catch(err){toast(err.message);}
 };
 const packInput=root.querySelector('#course-pack-file'),packButton=root.querySelector('#course-pack-import');
 if(packButton)packButton.onclick=async()=>{try{const file=packInput.files[0];if(!file)throw new Error('Selecciona un archivo .allenpack.');if(file.size>3_000_000)throw new Error('El Course Pack es demasiado grande.');const pack=JSON.parse(await file.text());const result=await api('/teacher/packs/import','POST',{profile_id:profileId,pack});toast('Course Pack importado como borrador. Revísalo antes de publicar.');await refresh();await openReview(result.course_id);}catch(err){toast(err.message);}};
 refresh().catch(e=>toast(e.message));
}
function fileToBase64(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onerror=()=>reject(new Error('No pudimos leer el archivo.'));r.onload=()=>resolve(String(r.result).split(',')[1]||'');r.readAsDataURL(file);});}
function mimeFor(name){const ext=name.toLowerCase().split('.').pop();return ext==='pdf'?'application/pdf':ext==='md'?'text/markdown':'text/plain';}

export function coursesPage(){
 return `<div class="v2-page-heading"><div><span class="eyebrow">CURSOS EN ALLEN</span><h1>Aprende con una ruta, no con páginas sueltas.</h1><p>Cada curso publicado tiene unidades, temas, práctica y progreso local.</p></div></div>
 ${allenGuide('course','Yo te presento cada paso, te digo qué estamos aprendiendo y guardo dónde te quedaste.')}
 <section id="student-course-list"></section><section id="student-course-route"></section>`;
}
function studentCards(rows){
 if(!rows.length)return '<section class="panel empty"><h2>No hay cursos publicados todavía</h2><p>Un profesor puede crear uno desde Teacher Studio.</p></section>';
 return `<div class="student-course-grid">${rows.map(r=>`<article class="student-course-card"><img src="/static/assets/allen-course-official.svg" alt=""><span class="eyebrow">${esc(r.subject)} · ${esc(r.level)}</span><h2>${esc(r.title)}</h2>${coverage(r.coverage)}<button class="primary" data-course-action="${r.enrollment?'continue':'enroll'}" data-course-id="${r.id}">${r.enrollment?'Continuar ruta':'Empezar curso'}</button></article>`).join('')}</div>`;
}
function stepBody(topic,step){
 const type=step.type;
 if(type==='discover')return `<h2>${esc(topic.title)}</h2><p class="guided-objective">${esc(topic.objective)}</p><blockquote>${esc(topic.source_excerpt||'')}</blockquote><small>Fuente: página ${topic.source?.page||'—'}</small>`;
 if(type==='example')return `<h2>Miremos un ejemplo del material</h2><blockquote>${esc(topic.source_excerpt||'')}</blockquote><p>¿Qué parte de este ejemplo te ayuda a entender la idea?</p>`;
 if(type==='retrieval')return `<h2>Ahora sin mirar</h2><p>${esc(topic.questions?.[0]?.prompt||('Explica '+topic.title+' con tus palabras.'))}</p><textarea id="course-student-answer" rows="4" placeholder="Escribe lo que recuerdas…"></textarea>`;
 if(type==='practice')return `<h2>Practica</h2><p>${esc(topic.questions?.[1]?.prompt||('Aplica '+topic.title+' en un ejemplo propio.'))}</p><textarea id="course-student-answer" rows="4" placeholder="Inténtalo aquí…"></textarea>`;
 if(type==='quiz')return `<h2>Comprueba lo aprendido</h2><p>${esc(topic.questions?.[0]?.prompt||('¿Qué entendiste de '+topic.title+'?'))}</p><p class="muted">Allen registrará este paso como práctica; la corrección formal puede hacerse con el banco aprobado del docente.</p>`;
 return `<h2>Revisa después</h2><div class="course-flashcard"><strong>${esc(topic.flashcards?.[0]?.question||topic.title)}</strong><p>${esc(topic.flashcards?.[0]?.answer||topic.source_excerpt||'')}</p></div>`;
}
function routeView(data){
 const c=data.course,e=data.enrollment,unit=c.structure.units[e.unit_index],topic=unit.topics[e.topic_index],steps=topic.route||[],step=steps[Math.min(e.step_index,steps.length-1)]||{type:'discover',label:'Descubre'};
 return `<section class="guided-course-shell" data-course-id="${c.id}" data-unit="${e.unit_index}" data-topic="${e.topic_index}" data-step="${e.step_index}">
  ${allenGuide(step.type==='review'?'progress':'guide',`Estamos en ${topic.title}. ${step.label}: concéntrate solo en este paso.`)}
  <div class="row spaced"><div><span class="eyebrow">${esc(c.title)} · ${esc(unit.title)}</span><h1>${esc(topic.title)}</h1></div><span class="pill">Tema ${e.topic_index+1}/${unit.topics.length}</span></div>
  ${learningStepRail(e.step_index,steps.map(x=>x.label))}
  <article class="guided-learning-card">${stepBody(topic,step)}<div id="course-help-panel"></div><div class="row guided-actions"><button id="course-help">No entendí</button><button id="course-next" class="primary">${e.step_index>=steps.length-1?'Terminar tema':'Continuar'}</button></div></article>
 </section>`;
}
export function bindCourses(root,{api,profileId,toast,go}){
 const list=root.querySelector('#student-course-list'),route=root.querySelector('#student-course-route');
 async function refresh(){const rows=await api('/courses?profile_id='+profileId);list.innerHTML=studentCards(rows);}
 async function open(id){const data=await api('/courses/'+id+'/route?profile_id='+profileId);route.innerHTML=routeView(data);route.scrollIntoView({behavior:'smooth',block:'start'});}
 async function openExam(id){
  const data=await api('/courses/'+id+'/exam?profile_id='+profileId);
  route.innerHTML=`<section class="course-exam-shell" data-course-exam="${id}">
   ${allenGuide('teaching','Llegaste al examen final. Aquí ya no te doy pistas: primero demuestra lo que recuerdas y después revisamos juntos.')}
   <div class="row spaced"><div><span class="eyebrow">EXAMEN FINAL</span><h1>${esc(data.course.title)}</h1></div><span class="pill">${data.questions.length} preguntas</span></div>
   <form id="course-exam-form">${data.questions.map((q,i)=>`<fieldset><legend>${i+1}. ${esc(q.prompt)}</legend>${q.options.map(o=>`<label class="answer-option"><input type="radio" name="course-exam-${i}" value="${esc(o)}" required><span>${esc(o)}</span></label>`).join('')}</fieldset>`).join('')}<button class="primary">Entregar examen</button></form>
  </section>`;
  route.scrollIntoView({behavior:'smooth',block:'start'});
  route.querySelector('#course-exam-form').onsubmit=async e=>{e.preventDefault();try{
   const answers=data.questions.map((_,i)=>route.querySelector(`input[name="course-exam-${i}"]:checked`)?.value||'');
   const result=await api('/courses/'+id+'/exam/submit','POST',{profile_id:profileId,answers});
   route.innerHTML=`<section class="course-exam-result">${allenGuide(result.percentage>=70?'celebrate':'progress',result.percentage>=70?'Terminaste el curso. Ahora sabemos qué temas dominas y cuáles conviene revisar.':'Terminaste el examen. No hace falta empezar de cero: vamos a reforzar exactamente lo que costó.',[{label:'Ver progreso',page:'Progreso',primary:true}])}<div class="panel"><span class="eyebrow">RESULTADO DEL CURSO</span><h1>${result.score}/${result.total} · ${result.percentage}%</h1><p><b>Fuertes:</b> ${esc(result.strong_topics.join(', ')||'todavía construyéndose')}</p><p><b>Reforzar:</b> ${esc(result.weak_topics.join(', ')||'ninguno destacado')}</p><details><summary>Revisar respuestas y fuentes</summary>${result.feedback.map((x,i)=>`<article class="exam-review ${x.correct?'correct':'review'}"><strong>${i+1}. ${esc(x.topic)}</strong><p>${x.correct?'Correcto':'Respuesta esperada: '+esc(x.correct_answer)}</p><small>Fuente: página ${x.source?.page||'—'}</small></article>`).join('')}</details>${result.weak_topics.length?'<button class="primary" id="course-reinforce">Crear Plan Allen de refuerzo</button>':''}</div></section>`;
   const reinforce=route.querySelector('#course-reinforce');if(reinforce)reinforce.onclick=()=>{try{sessionStorage.setItem('allen-plan-prefill',JSON.stringify({subject:data.course.subject,topics:result.weak_topics,goal:'Reforzar examen del curso'}));}catch{}go('Plan Allen');};
   await refresh();
  }catch(err){toast(err.message);}};
 }
 list.onclick=async e=>{const b=e.target.closest('[data-course-id]');if(!b)return;const id=Number(b.dataset.courseId);try{if(b.dataset.courseAction==='enroll')await api('/courses/'+id+'/enroll','POST',{profile_id:profileId});await open(id);await refresh();}catch(err){toast(err.message);}};
 route.onclick=async e=>{
  const shell=e.target.closest('[data-course-id]');if(!shell)return;const cid=Number(shell.dataset.courseId),u=Number(shell.dataset.unit),t=Number(shell.dataset.topic),st=Number(shell.dataset.step);
  const data=await api('/courses/'+cid+'/route?profile_id='+profileId),unit=data.course.structure.units[u],topic=unit.topics[t],steps=topic.route||[];
  if(e.target.id==='course-help'){try{
   const help=await api('/courses/'+cid+'/help','POST',{profile_id:profileId,unit_index:u,topic_index:t});
   const panel=route.querySelector('#course-help-panel');
   panel.innerHTML=`${allenGuide(help.level>=4?'teaching':'guide',help.title+': '+help.text)}<div class="course-help-source"><small>Fuente: página ${help.source?.page||'—'}</small>${help.level>=3?'<button id="course-help-tutor">Hablar con Allen sobre esto</button>':''}</div>`;
   const tutor=panel.querySelector('#course-help-tutor');if(tutor)tutor.onclick=()=>{try{sessionStorage.setItem('allen-course-help',JSON.stringify({course:data.course.title,topic:topic.title,excerpt:topic.source_excerpt}));}catch{}go('Tutor');};
   toast(help.level<4?'Allen cambió la forma de explicarlo.':'Probemos una mini práctica.');
  }catch(err){toast(err.message);}return;}
  if(e.target.id!=='course-next')return;
  let nu=u,nt=t,ns=st+1,finishedRoute=false;
  if(ns>=steps.length){ns=0;nt++;if(nt>=unit.topics.length){nt=0;nu++;if(nu>=data.course.structure.units.length){finishedRoute=true;}}}
  try{if(finishedRoute){await openExam(cid);toast('Ruta completada. Ahora toca comprobar lo aprendido.');return;}await api('/courses/'+cid+'/progress','POST',{profile_id:profileId,unit_index:nu,topic_index:nt,step_index:ns,status:'active'});await open(cid);await refresh();}catch(err){toast(err.message);}
 };
 refresh().catch(e=>toast(e.message));
}
