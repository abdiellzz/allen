import {actions,actionBar,welcome,memoryForm,homeLearning,savedPage,studyControls,bindStudy,resetStudy} from './components/learning.js';
import {icon,AllenMascot,AllenLoader,FeatureCard,EmptyState} from './components/ui.js';
import {api,setToken,streamChat} from './services.js';
import {escapeHTML as esc,markdown} from './components/markdown.js';
import {adventurePage,bindAdventure,homeV2Extras,chatV2Bar,chatActionText,achievementPanel,libraryVisual,studyMethodPage} from './components/v2.js';
import {planAllenPage,bindPlanAllen} from './components/study-session.js';
import {adventureContinuityPage,bindAdventureContinuity} from './components/adventure-session.js';
import {continuityPanel,recommendationPanel,masteryPanel,reviewPanel,detectExamIntent} from './components/continuity.js';
import {teacherStudioPage,bindTeacherStudio,coursesPage,bindCourses} from './components/course-studio.js';
import {allenGuide} from './components/allen-guide.js';

if(localStorage.getItem('allen-fair-lock')==='true')location.replace('/fair');

const $=s=>document.querySelector(s), content=$('#content');
const levels=['Primaria','Premedia','Media','Universidad / Técnico'];
const modules=[
 ['Tutor','📖','Tutor con Allen','Entiende el porqué, paso a paso.'],
 ['Preguntar','💬','Pregúntale a Allen','Una pregunta, un nuevo descubrimiento.'],
 ['Quiz','🎯','Pon a prueba tu curiosidad','Pequeños retos. Grandes aprendizajes.'],
 ['Matemáticas','🔢','Matemáticas sin miedo','Practica, equivócate y vuelve a intentar.'],
 ['Idiomas','🌎','Un mundo de palabras','Practica inglés a tu ritmo.'],
 ['Biblioteca','📚','Tu biblioteca offline','Ideas que siempre van contigo.'],
 ['Resumir','📝','Organiza tus apuntes','Convierte un texto en una guía de estudio.'],
 ['Explicar','💡','Explícame esto','Otra forma de entenderlo.'],
 ['Tarjetas','🧠','Tarjetas de estudio','Un poquito hoy. Más claro mañana.'],
 ['Programación','💻','Aprende programación','De una idea a tu primera línea de código.'],
 ['Futuro','🚀','Mi futuro','Explora caminos y descubre posibilidades.'],
 ['Aprende IA','✦','Aprende sobre IA','Conoce la tecnología que te acompaña.']
];
let rememberedProfile=1;try{rememberedProfile=Number(localStorage.getItem('allen-active-profile'))||1;}catch{}
const storedTheme=localStorage.getItem('allen-theme')||'light';
document.documentElement.dataset.theme=storedTheme;
let state={profiles:[],settings:{},catalog:{},profile:rememberedProfile,page:'Inicio',model:null,license:null};
let chat={messages:[],id:null,controller:null},quiz=null,pageEpoch=0;
let lastActivity=Date.now();
document.addEventListener('pointerdown',()=>lastActivity=Date.now());
document.addEventListener('keydown',()=>lastActivity=Date.now());
function toast(text){$('#toast').textContent=text;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').textContent='',6000);}
function profile(){return state.profiles.find(p=>p.id===state.profile)||state.profiles[0];}
function licenseDate(value){
 if(!value)return '—';
 try{return new Intl.DateTimeFormat('es-PA',{day:'numeric',month:'short',year:'numeric'}).format(new Date(value+'T12:00:00'));}
 catch{return value;}
}
function licenseGate(status){
 const machine=esc(status?.machine_id||'—');
 document.body.classList.add('license-locked');
 $('#breadcrumb').textContent='Activación';
 $('#profile-select').closest('label')?.classList.add('hidden');
 content.innerHTML=`
 <section class="license-gate" aria-labelledby="license-title">
  <div class="license-card">
   <div class="license-mark">${icon('key-round',28)}</div>
   <span class="eyebrow">ACTIVACIÓN OFFLINE</span>
   <h1 id="license-title">Activa ALLEN</h1>
   <p>Esta instalación necesita un archivo de licencia válido. La verificación ocurre completamente en este equipo y no requiere Internet.</p>
   <div class="license-machine">
    <span>ID DE ESTE EQUIPO</span>
    <code id="machine-id">${machine}</code>
    <button id="copy-machine-id" type="button">Copiar ID</button>
   </div>
   <label class="license-file button-like">
    Seleccionar archivo .license
    <input id="license-file" type="file" accept=".license,application/json" hidden>
   </label>
   <div id="license-feedback" class="license-feedback ${status?.state==='expired'||status?.state==='invalid'?'error':''}" role="status">
    ${esc(status?.message||'Solicita una licencia para este Machine ID.')}
   </div>
   <p class="muted">La licencia no limita la cantidad de perfiles, estudiantes o profesores dentro de esta instalación.</p>
  </div>
 </section>`;
 $('#copy-machine-id').onclick=async()=>{try{await navigator.clipboard.writeText(status.machine_id);toast('Machine ID copiado.');}catch{toast('Copia el Machine ID manualmente.');}};
 $('#license-file').onchange=async e=>{
  const file=e.target.files?.[0];if(!file)return;
  const feedback=$('#license-feedback');feedback.classList.remove('error');feedback.textContent='Verificando licencia…';
  try{
   const raw=await file.text();
   const result=await api('/license/activate','POST',{content:raw});
   state.license=result;
   toast('Licencia activada.');
   const ready=await bootstrap();
   if(ready){state.page=decodeURIComponent(location.hash.slice(1))||'Inicio';await render();state.model=await api('/model/status').catch(()=>null);}
  }catch(error){feedback.classList.add('error');feedback.textContent=error.message||'No se pudo activar esta licencia.';}
 };
}

function options(values,selected){return values.map(v=>`<option value="${esc(v)}" ${v===selected?'selected':''}>${esc(v)}</option>`).join('');}
function field(label,id,values,selected){return `<label>${label}<select id="${id}">${options(values,selected)}</select></label>`;}
function heading(title,sub){return `<div class="page-heading"><div><div class="eyebrow">TU ESPACIO PARA CRECER</div><h1>${title}</h1><p class="muted">${sub}</p></div><span class="pill ai-state ${state.model?.connected?'green':''}">${esc(state.model?.connected?'IA LOCAL ACTIVA':state.model?'IA local sin conectar':'Comprobando IA…')}</span></div>`;}
const iconSVG=icon;
function stats(p){return `<div class="stats">${[['flame',p.streak,'días de racha'],['sparkles',p.xp,'XP de curiosidad'],['book-open',p.lessons,'ejercicios completados'],['target',p.quizzes,'quizzes completados']].map(([icon,v,label])=>`<div class="stat"><span class="stat-icon">${iconSVG(icon)}</span><div><b>${v}</b><small>${label}</small></div></div>`).join('')}</div>`;}
function applyAppearance(){document.documentElement.classList.toggle('large',state.settings.font_size==='grande');document.documentElement.classList.toggle('xlarge',state.settings.font_size==='muy grande');document.documentElement.classList.toggle('contrast',state.settings.high_contrast);}
function studentAvatar(){const palette=['🐵','🦊','🐼','🐸','🦉'].indexOf(profile()?.avatar);return `<span class="student-avatar palette-${Math.max(0,palette)}" aria-label="Avatar del estudiante">${icon('user-round',24)}</span>`;}
function updateProfiles(){try{localStorage.setItem('allen-active-profile',String(state.profile));}catch{}const select=$('#profile-select');select.innerHTML=state.profiles.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('');select.value=state.profile;const button=$('.sidebar-bottom [data-page="Perfil"]');if(button)button.innerHTML=studentAvatar()+`<span class="nav-text">${esc(profile().name)}</span>`;}
function network(){ $('#network').innerHTML=icon('shield-check',16)+' Privado y offline';$('#network').title='Allen procesa las conversaciones dentro de este dispositivo.'; }
addEventListener('online',network);addEventListener('offline',network);network();
window.addEventListener('allen-license-required',()=>guarded(async()=>{await bootstrap();}));
window.addEventListener('allen-teacher-auth-required',()=>{ensureTeacherAccess();});

async function ensureTeacherAccess(){
 try{
  const status=await api('/teacher/security/status');
  if(status.unlocked)return true;
  if(!status.configured){
   const pin=prompt('Crea un PIN de profesor de 6 a 12 dígitos. Se pedirá para Teacher Studio, respaldos y recuperación.');
   if(!pin)return false;
   const confirmPin=prompt('Confirma el PIN de profesor.');
   if(pin!==confirmPin){toast('Los PIN no coinciden.');return false;}
   await api('/teacher/security/setup','POST',{pin});
   toast('PIN de profesor configurado.');
   return true;
  }
  const pin=prompt('Introduce el PIN de profesor.');
  if(!pin)return false;
  await api('/teacher/security/unlock','POST',{pin});
  toast('Modo profesor desbloqueado.');
  return true;
 }catch(error){toast(error.message);return false;}
}
function applyDynamicStyles(root=document){
 root.querySelectorAll('[data-width-pct]').forEach(el=>el.style.width=Math.max(0,Math.min(100,Number(el.dataset.widthPct)||0))+'%');
 root.querySelectorAll('[data-height-pct]').forEach(el=>el.style.height=Math.max(0,Math.min(100,Number(el.dataset.heightPct)||0))+'%');
 root.querySelectorAll('[data-mastery-strong]').forEach(el=>{
  el.style.setProperty('--strong',Number(el.dataset.masteryStrong)||0);
  el.style.setProperty('--developing',Number(el.dataset.masteryDeveloping)||0);
  el.style.setProperty('--weak',Number(el.dataset.masteryWeak)||0);
  el.style.setProperty('--total',Math.max(1,Number(el.dataset.masteryTotal)||1));
 });
}

const navGroups=[
 ['INICIO','student',[['Inicio','house','Inicio']]],
 ['APRENDER','student',[['Aprender','book-open','Aprender'],['Cursos','library','Cursos'],['Método Allen','sparkles','Método Allen'],['Plan Allen','notebook-tabs','Plan Allen'],['Biblioteca','library','Biblioteca']]],
 ['PRACTICAR','student',[['Aventura','map','Aventura'],['Quiz','target','Quiz'],['Tarjetas','layers','Tarjetas']]],
 ['TU PROGRESO','student',[['Progreso','chart-no-axes-column','Progreso'],['Perfil','user-round','Perfil']]],
 ['PROFESOR','teacher',[['Teacher Studio','book-open','Teacher Studio']]],
 ['SISTEMA','both',[['Configuración','settings','Configuración']]]
];
const storedMode=localStorage.getItem('allen-workspace-mode')||'student';
document.body.dataset.workspaceMode=storedMode;
$('#nav').innerHTML=`<div class="workspace-mode" role="group" aria-label="Modo de trabajo"><button data-workspace-mode="student" class="${storedMode==='student'?'active':''}">Estudiante</button><button data-workspace-mode="teacher" class="${storedMode==='teacher'?'active':''}">Profesor</button></div>`+navGroups.map(([label,mode,items])=>`<div class="nav-group" data-nav-mode="${mode}"><span class="nav-group-label">${label}</span>${items.map(([page,name,title])=>`<button class="nav-btn" title="${title}" aria-label="${title}" data-page="${page}"><span class="nav-icon">${icon(name)}</span><span class="nav-text">${title}</span></button>`).join('')}</div>`).join('');
$('#nav').addEventListener('click',async e=>{const modeButton=e.target.closest('[data-workspace-mode]');if(!modeButton)return;const mode=modeButton.dataset.workspaceMode;if(mode==='teacher'&&!(await ensureTeacherAccess()))return;document.body.dataset.workspaceMode=mode;localStorage.setItem('allen-workspace-mode',mode);document.querySelectorAll('[data-workspace-mode]').forEach(b=>b.classList.toggle('active',b.dataset.workspaceMode===mode));if(mode==='teacher'&&state.page==='Inicio')go('Teacher Studio');if(mode==='student'&&state.page==='Teacher Studio')go('Inicio');});
$('.brand').innerHTML='<img class="brand-mascot" src="/static/assets/allen-brand.svg" alt="Allen"><span class="brand-text">ALLEN<small>Aprender es una aventura</small></span>';
$('.top-actions').insertAdjacentHTML('afterbegin',`<button id="global-search-open" class="icon-action" title="Buscar en Allen (Ctrl+K)" aria-label="Buscar en Allen">${icon('search',18)}<span>Buscar</span><kbd>Ctrl K</kbd></button><button id="theme-toggle" class="icon-action" title="Cambiar tema" aria-label="Cambiar tema">${icon(storedTheme==='dark'?'sun':'moon',18)}</button>`);
document.body.insertAdjacentHTML('beforeend',`<div id="command-palette" class="command-palette" hidden><div class="command-backdrop" data-command-close></div><section class="command-dialog" role="dialog" aria-modal="true" aria-labelledby="command-title"><h2 id="command-title" class="sr-only">Buscar y navegar en Allen</h2><div class="command-search-row">${icon('search',20)}<input id="command-input" autocomplete="off" placeholder="Buscar cursos, temas y acciones…" aria-label="Buscar en Allen" aria-controls="command-results"><kbd>Esc</kbd></div><div id="command-results" role="listbox" aria-label="Resultados de búsqueda"></div><p class="command-hint">Enter para abrir · Esc para cerrar · Ctrl+K desde cualquier página</p></section></div>`);
$('.sidebar-bottom').innerHTML=`<div class="sidebar-allen"><img src="/static/assets/allen-guide.svg" alt="Allen"><div><strong>¿Seguimos?</strong><small>Tu progreso se queda aquí.</small></div></div><button class="nav-btn" data-page="Perfil" title="Mi perfil">${icon('user-round')}<span class="nav-text">Mi perfil</span></button><button class="nav-btn" data-page="Privacidad" title="Privacidad">${icon('shield-check')}<span class="nav-text">Privado y offline</span></button>`;
const collapse=document.createElement('button');collapse.className='collapse-button';collapse.title='Contraer o expandir menú';collapse.setAttribute('aria-label',collapse.title);collapse.innerHTML=icon('panel-left-close');$('.sidebar').insertBefore(collapse,$('#nav'));collapse.onclick=()=>{const collapsed=document.body.classList.toggle('sidebar-collapsed');collapse.setAttribute('aria-expanded',String(!collapsed));};collapse.setAttribute('aria-expanded','true');
document.addEventListener('click',e=>{const button=e.target.closest('[data-page]');if(button)go(button.dataset.page);});
const commandItems=[
 ['Inicio','Inicio','Tu espacio de aprendizaje'],
 ['Aprender','Aprender','Explorar materias y explicaciones'],
 ['Cursos','Cursos','Rutas completas y diagnóstico'],
 ['Método Allen','Método Allen','Técnicas de estudio'],
 ['Plan Allen','Plan Allen','Planificar un examen o meta'],
 ['Biblioteca','Biblioteca','Apuntes y lecturas locales'],
 ['Aventura','Aventura','Misiones educativas'],
 ['Quiz','Quiz','Practicar con preguntas'],
 ['Tarjetas','Tarjetas','Repaso con flashcards'],
 ['Progreso','Progreso','Dashboard y mastery'],
 ['Teacher Studio','Teacher Studio','Crear y revisar cursos'],
 ['Configuración','Configuración','IA local, backups y preferencias']
];
let commandReturnFocus=null;
function commandOpen(){
 commandReturnFocus=document.activeElement;
 const modal=$('#command-palette');modal.hidden=false;document.body.classList.add('command-open');
 const input=$('#command-input');input.value='';renderCommandResults('');setTimeout(()=>input.focus(),0);
}
function commandClose(){const modal=$('#command-palette');modal.hidden=true;document.body.classList.remove('command-open');if(commandReturnFocus?.focus)commandReturnFocus.focus();}
function renderCommandResults(query=''){
 const q=query.trim().toLowerCase();
 const rows=commandItems.filter(x=>!q||x.join(' ').toLowerCase().includes(q)).slice(0,10);
 $('#command-results').innerHTML=rows.length?rows.map(([page,title,desc],i)=>`<button class="command-result ${i===0?'selected':''}" role="option" data-command-page="${esc(page)}"><span>${icon(page==='Teacher Studio'?'book-open':'arrow-right',18)}<b>${esc(title)}</b></span><small>${esc(desc)}</small></button>`).join(''):`<div class="command-empty"><b>Sin resultados</b><span>Prueba con “curso”, “quiz”, “progreso” o “configuración”.</span></div>`;
}
$('#global-search-open').onclick=commandOpen;
$('#command-input').addEventListener('input',e=>renderCommandResults(e.target.value));
$('#command-palette').addEventListener('click',e=>{if(e.target.closest('[data-command-close]'))commandClose();const item=e.target.closest('[data-command-page]');if(item){commandClose();go(item.dataset.commandPage);}});
$('#theme-toggle').onclick=()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;localStorage.setItem('allen-theme',next);const b=$('#theme-toggle');b.innerHTML=icon(next==='dark'?'sun':'moon',18);b.setAttribute('aria-label',next==='dark'?'Usar tema claro':'Usar tema oscuro');b.title=b.getAttribute('aria-label');};
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();commandOpen();}else if(e.key==='Escape'&&!$('#command-palette').hidden){commandClose();}else if(e.key==='Enter'&&!$('#command-palette').hidden&&document.activeElement===$('#command-input')){$('#command-results .command-result')?.click();}});
$('.skip').onclick=e=>{e.preventDefault();content.focus();content.scrollIntoView();};
$('#profile-select').addEventListener('change',async e=>{chat.controller?.abort();state.profile=Number(e.target.value);resetStudy();updateProfiles();chat={messages:[],id:null,controller:null};quiz=null;await render();});
function go(page){location.hash=encodeURIComponent(page);if(state.page===page)render();}
addEventListener('hashchange',()=>{chat.controller?.abort();state.page=decodeURIComponent(location.hash.slice(1))||'Inicio';render();});

async function render(){
 if(profile()&&!profile().memory?.onboarded){showWelcome();return;}
 const epoch=++pageEpoch;$('#breadcrumb').textContent=state.page==='Inicio'?'Tu espacio de aprendizaje':state.page;
 document.querySelectorAll('[data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===state.page));
 content.setAttribute('aria-busy','true');content.innerHTML=AllenLoader('Preparando tu espacio…');
 try{
  const pages={Guardado:()=>api('/saved?profile_id='+state.profile).then(savedPage),Inicio:home,Aprender:learnPage,Cursos:coursesPage,'Teacher Studio':teacherStudioPage,'Método Allen':studyMethodPage,'Plan Allen':()=>planAllenPage(profile().level),Practicar:practicePage,Aventura:()=>adventureContinuityPage(api,state.profile),Perfil:profilePage,Quiz:quizPage,Matemáticas:quizPage,Biblioteca:libraryPage,Tarjetas:cardsPage,Progreso:progressPage,Docente:progressPage,Configuración:settingsPage,Privacidad:privacyPage};
  const html=await (pages[state.page]||chatPage)();if(epoch!==pageEpoch)return;
  content.innerHTML=html;content.setAttribute('aria-busy','false');applyDynamicStyles(content);
  if(state.page==='Configuración')$('#profile-form')?.parentElement.remove();
  if(state.page==='Perfil'){const avatars=$('#profile-avatar');[...avatars.options].forEach((o,i)=>o.textContent=['Allen naranja','Allen ámbar','Allen crema','Allen verde','Allen violeta'][i]);}
  const group=['Quiz','Matemáticas','Tarjetas'].includes(state.page)?'Practicar':['Tutor','Explicar','Resumir','Aprende IA','Futuro','Idiomas','Programación'].includes(state.page)?'Aprender':state.page;
  document.querySelectorAll('#nav [data-page]').forEach(b=>{b.classList.toggle('active',b.dataset.page===group);if(b.dataset.page===group)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  window.scrollTo({top:0,behavior:'instant'});
  const binds={Guardado:bindSaved,Inicio:bindHome,Aprender:bindLearn,Cursos:()=>bindCourses(content,{api,profileId:state.profile,toast,go}),'Teacher Studio':()=>bindTeacherStudio(content,{api,profileId:state.profile,toast}),'Plan Allen':()=>bindPlanAllen(content,{api,profileId:state.profile,profile:profile(),go,toast}),Practicar:bindHome,Aventura:()=>bindAdventureContinuity(content,state.profile,{api,toast,refresh:()=>render()}),Perfil:bindProfile,Quiz:bindQuiz,Matemáticas:bindQuiz,Biblioteca:bindLibrary,Tarjetas:bindCards,Progreso:bindProgress,Docente:bindProgress,Configuración:bindSettings,Privacidad:bindPrivacy};
  await (binds[state.page]||bindChat)();
 }catch(error){if(epoch===pageEpoch){content.setAttribute('aria-busy','false');content.innerHTML=`<section class="panel global-error" role="alert">${AllenMascot('error')}<div><span class="eyebrow">ALGO NO CARGÓ BIEN</span><h1>Volvamos a intentarlo</h1><p>No pudimos preparar esta página. Tus datos locales no se borraron.</p><div class="row"><button class="primary" id="retry-page">Reintentar</button><button data-page="Inicio">Volver al inicio</button></div><details><summary>Ver detalles técnicos</summary><p>${esc(error.message)}</p></details></div></section>`;$('#retry-page')?.addEventListener('click',()=>render());}}
}
async function home(){const [rows,memory,progress,continuityData]=await Promise.all([api('/conversations?profile_id='+state.profile),api('/memory?profile_id='+state.profile),api('/progress?profile_id='+state.profile),api('/continuity?profile_id='+state.profile)]);const continuity=continuityPanel(continuityData),recommendation=recommendationPanel(continuityData),reviews=reviewPanel(continuityData),mastery=masteryPanel(continuityData);return `<section class="welcome continuity-welcome v3-home-hero"><div class="welcome-copy"><span class="eyebrow">TU ESPACIO DE APRENDIZAJE</span><h1>Hola, ${esc(profile().name)}.</h1><h2 class="sr-only">¿Qué quieres descubrir hoy?</h2><p>Continúa lo importante, repasa lo pendiente o pregúntale algo a Allen.</p><form id="home-question" class="home-question"><label class="sr-only" for="home-input">Pregunta para Allen</label><input id="home-input" required maxlength="12000" placeholder="Pregúntale algo a Allen…"><button class="primary" aria-label="Enviar pregunta">${icon('arrow-right')}</button></form><span class="privacy-caption">${icon('shield-check',16)} Tu progreso se guarda en este dispositivo.</span></div><div class="welcome-art"><img src="/static/assets/allen-brand.svg" alt="Allen te da la bienvenida"></div></section>${continuity}${recommendation}${reviews}${mastery}${homeV2Extras({progress,memory,recent:rows})}<div class="section-head"><h2>Explora</h2></div><div class="cards-grid four">${FeatureCard('Cursos','library','Mis cursos','Sigue una ruta completa creada desde material docente.')}${FeatureCard('Aprender','book-open','Aprender','Descubre un tema con ejemplos sencillos.')}${FeatureCard('Practicar','target','Practicar','Prueba lo que sabes. Cada intento cuenta.')}${FeatureCard('Preguntar','message-circle','Preguntar','No hay preguntas demasiado pequeñas.')}${FeatureCard('Tarjetas','layers','Estudiar','Recuerda más, un poquito cada día.')}</div>${homeLearning(rows,memory)}<details class="explore"><summary>Explora más</summary><div class="cards-grid">${FeatureCard('Método Allen','sparkles','Método Allen','Aprende a estudiar con técnicas que Allen aplica contigo.')}${FeatureCard('Plan Allen','calendar','Plan Allen','Organiza un examen o meta en sesiones cortas y activas.')}${FeatureCard('Biblioteca','library','Tu biblioteca','Lecturas y apuntes siempre contigo.')}${FeatureCard('Futuro','compass','Mi futuro','Explora tus intereses y posibilidades.')}${FeatureCard('Aprende IA','sparkles','Aprende IA','Entiende la tecnología que te acompaña.')}</div></details>`;}
let pendingPrompt='';
function bindHome(){bindHomeLearning();const form=$('#home-question');if(form)form.onsubmit=e=>{e.preventDefault();const value=$('#home-input').value.trim();const exam=detectExamIntent(value);if(exam){try{sessionStorage.setItem('allen-plan-prefill',JSON.stringify(exam));}catch{}go('Plan Allen');toast('Vamos a organizar ese examen. Solo te preguntaré lo necesario.');return;}pendingPrompt=value;go('Preguntar');};}
function moduleCard([page,name,title,sub]){return FeatureCard(page,'book-open',title,sub);}
function learnPage(){return heading('Sigue tu curiosidad','Elige una materia. Allen te ayuda a entenderla paso a paso.')+allenGuide('teaching','Primero entendemos la idea. Luego la usamos, la recordamos sin mirar y comprobamos qué quedó claro.')+`<div class="learning-banner"><img src="/static/assets/allen-teaching-official.svg" alt="Allen enseñando"><p>Una explicación, un ejemplo y una pregunta.<br><b>Aprendemos a tu ritmo.</b></p></div><div class="cards-grid">${FeatureCard('Método Allen','sparkles','Cómo estudiar con Allen','Recupera, explica, mezcla y revisa de forma espaciada.')}${FeatureCard('Explicar','lightbulb','Explicaciones sencillas','Mira una idea desde otra perspectiva.')}${FeatureCard('Resumir','layers','Organiza tus apuntes','Convierte tus textos en una guía de estudio.')}${Object.keys(state.catalog).map((subject,i)=>`<button class="module-card" data-subject="${esc(subject)}"><span class="module-icon">${icon(['calculator','flask-conical','languages','code','book-open','lightbulb','compass','compass'][i]||'book-open',44)}</span><b>${esc(subject)}</b><p>Explora, pregunta y entiende con ejemplos.</p><span class="card-action">Descubrir ${icon('arrow-right',18)}</span></button>`).join('')}</div>`;}
let selectedSubject='Matemáticas';
function bindLearn(){content.querySelectorAll('[data-subject]').forEach(b=>b.onclick=()=>{selectedSubject=b.dataset.subject;go('Tutor');});}
function practicePage(){return heading('Cada intento te hace crecer','Elige cómo quieres practicar hoy.')+`<div class="cards-grid four">${FeatureCard('Aventura','map','Aventura','Resuelve una misión educativa paso a paso.')}${FeatureCard('Quiz','target','Quiz','De 1 a 10 preguntas con explicación.')}${FeatureCard('Tarjetas','layers','Flashcards','Crea tarjetas con tus propios apuntes.')}${FeatureCard('Matemáticas','calculator','Ejercicios','Un problema a la vez, sin prisas.')}${FeatureCard('Tutor','book-open','Tutor','Pide una pista y descubre el siguiente paso.')}</div>`;}

const chatOptions={
 Tutor:['Explicación → ejemplo → práctica','Dame una pista','Revisa mi respuesta','Siguiente ejercicio'],
 Explicar:['Como si tuviera 10 años','Fácil','Normal','Avanzado','Dame un ejemplo','Usa una analogía','Hazme un resumen','Hazme preguntas'],
 Resumir:['Resumen corto','Puntos importantes','Guía de estudio','Preguntas para examen','Tarjetas de estudio'],
 Idiomas:['Traducción español → inglés','Traducción inglés → español','Significado y ejemplos','Vocabulario y pronunciación aproximada','Ejercicios','Conversación: en un restaurante'],
 Programación:['Lógica','Python','HTML','CSS','JavaScript','Explicar código','Encontrar errores','Desafío de programación','Revisar mi respuesta'],
 Futuro:['Descubrir áreas profesionales','Explorar una carrera','Ruta de aprendizaje','Preparar una entrevista','CV básico ficticio','Orientación tecnológica'],
 'Aprende IA':['Qué es IA','Machine Learning','Qué es un modelo','Qué es un LLM','Cómo aprende una IA','IA local y privacidad','Errores y alucinaciones','Uso responsable']
};
function chatPage(){const page=state.page,entry=modules.find(m=>m[0]===page),mode=page==='Preguntar'?'Aprender':page;
 return (page==='Preguntar'?`<div class="free-chat-heading">${AllenMascot('hello')}<div><h1>Pregúntame lo que quieras.</h1><p>Si algo no entiendes, podemos verlo de otra manera.</p></div></div>`:heading(entry?.[2]||'Pregúntale a Allen',entry?.[3]||'¿Qué quieres aprender hoy?'))+`
 ${page!=='Preguntar'?`<div class="panel"><div class="row toolbar">${field('Materia','chat-subject',Object.keys(state.catalog),selectedSubject)}${field('Nivel de tu perfil','chat-level',levels,profile().level)}${field('Cómo vamos a aprender','chat-option',chatOptions[page]||['Aprender paso a paso'])}</div><label class="check"><input type="checkbox" id="use-library">Consultar también mi biblioteca local</label><small class="muted">${mode==='Programación'?'El código se analiza como texto. No se ejecuta en este dispositivo.':'Allen puede equivocarse. Comparte tus dudas con tu docente.'}</small></div>`:'<label class="check"><input type="checkbox" id="use-library">Consultar mi biblioteca local</label>'}${studyControls()}
 ${state.model&&!state.model.connected?`<div class="model-notice">${AllenMascot("sleeping","small")}<div><b>Allen todavía está despertando.</b><p>La IA local está apagada, pero Plan Allen, aventuras, quizzes, tarjetas, biblioteca, Cornell, progreso y simulacros siguen disponibles.</p></div><button data-page="Quiz">Practicar ahora</button><button data-page="Aventura">Aventura</button><button data-page="Plan Allen">Planificar</button><button id="retry-model">Comprobar IA</button><button data-page="Configuración">Configuración</button></div>`:""}${chatV2Bar({subject:selectedSubject,level:profile().level,mode})}<div class="chat-layout"><section class="panel chat-panel"><div class="chat-header row spaced"><b class="chat-brand">${AllenMascot("happy","small")} Allen</b><div class="row"><button id="new-chat">＋ Nueva</button><button id="clear-chat" class="quiet">Limpiar</button></div></div><div class="messages" id="messages" aria-live="polite" aria-label="Conversación"></div><form class="composer" id="chat-form"><label for="chat-input" class="sr-only">Mensaje para Allen</label><textarea id="chat-input" maxlength="12000" required placeholder="${['Explicar','Resumir'].includes(page)?'Pega aquí el texto que quieres estudiar…':'Pregúntale algo a Allen…'}"></textarea><div class="row spaced"><small>Tu conversación se procesa localmente.</small><div class="row"><button type="button" id="stop" class="hidden">Detener</button><button class="primary" id="send">Enviar &nbsp; ↑</button></div></div></form></section><aside class="panel"><h2>Tus conversaciones</h2><p class="muted">${state.settings.save_history?'Guardadas hasta '+state.settings.retention_days+' días.':'Historial desactivado. Solo durante esta sesión.'}</p><div class="history" id="history"></div></aside></div>`;
}
function drawMessages(){const box=$('#messages');if(!box)return;box.innerHTML=chat.messages.length?chat.messages.map((m,i)=>`<article class="message ${m.role}">${m.role==='assistant'?AllenMascot('happy','small')+'<div class="answer-content">'+(m.content==='Allen está pensando…'?AllenLoader():markdown(m.content))+'</div>':studentAvatar()+esc(m.content)}${m.role==='assistant'?`<div class="message-tools">${!chat.controller?actionBar(i,m.content,chat.state||{},i===chat.messages.length-1):''}</div>`:''}</article>`).join(''):EmptyState('¿Qué te gustaría aprender?','Trae tus preguntas. Lo descubrimos juntos.','hello')+`<div class="suggestions">${['Explícame algo','Ayúdame a estudiar','Dame un ejemplo','Hazme preguntas','Ayúdame con una idea'].map(t=>`<button data-suggestion="${t}">${icon('lightbulb',16)} ${t}</button>`).join('')}</div>`;box.scrollTop=box.scrollHeight;}
async function loadHistory(){const rows=await api('/conversations?profile_id='+state.profile);if($('#history'))$('#history').innerHTML=rows.length?rows.map(r=>`<button data-conversation="${r.id}">${esc(r.title)}</button>`).join(''):'<p class="muted">Tu próxima pregunta puede ser el comienzo.</p>';}
async function bindChat(){bindStudy(toast);const sendPending=Boolean(pendingPrompt);try{const help=JSON.parse(sessionStorage.getItem('allen-course-help')||'null');if(help){pendingPrompt='Estoy estudiando «'+help.course+'», tema «'+help.topic+'». No lo entendí. Explícamelo más fácil, con un ejemplo concreto, usando este fragmento de mi curso como contexto: '+help.excerpt;selectedSubject=help.topic;sessionStorage.removeItem('allen-course-help');}}catch{}drawMessages();await loadHistory();if($('#retry-model'))$('#retry-model').onclick=()=>guarded(async()=>{state.model=await api('/model/status');toast(state.model.connected?'Allen está listo para ayudarte.':'Todavía no encontramos el modelo local.');render();}); if(pendingPrompt){$('#chat-input').value=pendingPrompt;pendingPrompt='';} $('#messages').addEventListener('click',e=>{const b=e.target.closest('[data-suggestion]');if(b){$('#chat-input').value=b.dataset.suggestion;$('#chat-input').focus();}});
 content.querySelectorAll('[data-v2-chat]').forEach(b=>b.onclick=()=>{const input=$('#chat-input');if(!input)return;input.value=chatActionText[b.dataset.v2Chat]||'';input.focus();});
 $('#chat-form').onsubmit=e=>{e.preventDefault();sendMessage();};
 $('#chat-input').onkeydown=e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();sendMessage();}};
 $('#new-chat').onclick=()=>{chat.controller?.abort();chat={messages:[],id:null,controller:null};$('#send').disabled=false;$('#stop').classList.add('hidden');drawMessages();$('#chat-input').focus();};
 $('#clear-chat').onclick=async()=>{if(!confirm('¿Limpiar esta conversación y eliminar su copia guardada?'))return;chat.controller?.abort();if(chat.id)await guarded(()=>api('/conversations/'+chat.id+'?profile_id='+state.profile,'DELETE'));chat={messages:[],id:null,controller:null};$('#send').disabled=false;$('#stop').classList.add('hidden');drawMessages();loadHistory();};
 $('#stop').onclick=()=>chat.controller?.abort();
 $('#messages').onclick=async e=>{const educational=e.target.closest('[data-learning-action]');if(educational&&!chat.controller){$('#chat-input').value=actions[educational.dataset.learningAction];sendMessage(false,educational.dataset.learningAction);return;}const save=e.target.closest('[data-save-answer]');if(save){await guarded(async()=>{const i=Number(save.dataset.saveAnswer);await api('/saved','POST',{profile_id:state.profile,title:(chat.messages.slice(0,i).reverse().find(m=>m.role==='user'&&!Object.values(actions).includes(m.content))?.content||'Idea para estudiar').slice(0,120),content:chat.messages[i].content.slice(0,20000)});toast('Guardado para estudiar.');});return;}const copy=e.target.closest('[data-copy]');if(copy){try{await navigator.clipboard.writeText(chat.messages[Number(copy.dataset.copy)].content);toast('Respuesta copiada.');}catch{toast('No se pudo copiar. Selecciona el texto y usa Ctrl+C.');}}if(e.target.closest('[data-regenerate]')&&!chat.controller)sendMessage(true);};
 if(sendPending)queueMicrotask(()=>sendMessage());
 $('#history').onclick=async e=>{const b=e.target.closest('[data-conversation]');if(!b)return;await guarded(async()=>{chat.controller?.abort();const row=await api('/conversations/'+b.dataset.conversation+'?profile_id='+state.profile);chat={messages:row.messages,id:row.id,controller:null,state:row.conversation_state||null};$('#send').disabled=false;$('#stop').classList.add('hidden');drawMessages();});};
}
async function sendMessage(regenerate=false,action=''){
 if(chat.controller)return;const input=$('#chat-input');let message=input.value.trim();
 if(regenerate){const previous=chat.messages.at(-2);if(previous?.role!=='user')return;message=previous.content;chat.messages.splice(-2);}
 if(!message)return;const previous=chat.messages.slice(-20).map(m=>({role:m.role,content:m.content.slice(0,12000)}));
 const currentChat=chat,epoch=pageEpoch;currentChat.controller=new AbortController();const controller=currentChat.controller;
 currentChat.messages.push({role:'user',content:message});input.value='';currentChat.messages.push({role:'assistant',content:'Allen está pensando…'});drawMessages();
 $('#send').disabled=true;$('#stop').classList.remove('hidden');let answer='',failed=false,done=false;
 try{
  const selectedLevel=$('#chat-level')?.value||profile().level;if(selectedLevel!==profile().level){const p=profile();await api('/profiles/'+p.id,'PUT',{name:p.name,age:p.age,avatar:p.avatar,level:selectedLevel});p.level=selectedLevel;}
  await streamChat({profile_id:state.profile,message,mode:state.page==='Preguntar'?'Aprender':(chatOptions[state.page]?state.page:'Aprender'),subject:$('#chat-subject')?.value||'General',option:$('#chat-option')?.value||'',action,conversation_state:currentChat.state||null,history:previous,conversation_id:currentChat.id,regenerate,use_library:$('#use-library').checked},controller.signal,event=>{
   if(event.type==='meta'&&event.queue_state==='queued'&&!answer){currentChat.messages.at(-1).content='Allen está terminando otra tarea…';if(epoch===pageEpoch&&chat===currentChat)drawMessages();}
   if(event.type==='meta'&&event.queue_state==='running'&&!answer){currentChat.messages.at(-1).content='Allen está pensando…';if(epoch===pageEpoch&&chat===currentChat)drawMessages();}
   if(event.type==='delta'){answer+=event.text;currentChat.messages.at(-1).content=answer;if(epoch===pageEpoch&&chat===currentChat)drawMessages();}
   if(event.type==='error'){failed=true;throw new Error(event.message);}
   if(event.type==='done'){done=true;currentChat.id=event.conversation_id;currentChat.state=event.conversation_state;if(event.demo)toast('Modo demo: esta respuesta no proviene de un modelo de IA.');}
  });
  if(!done)throw new Error('La respuesta se interrumpió. Puedes intentarlo de nuevo.');
 }catch(error){failed=true;currentChat.messages.at(-1).content=answer+(answer?'\n\n':'')+(error.name==='AbortError'?'Generación detenida. La respuesta parcial no se guardó.':error.message);}
 finally{if(done){const data=await api('/bootstrap').catch(()=>null);if(data){state.profiles=data.profiles;updateProfiles();}}currentChat.controller=null;if(epoch===pageEpoch&&chat===currentChat){$('#send').disabled=false;$('#stop').classList.add('hidden');drawMessages();loadHistory();}}
}

function quizPage(){const math=state.page==='Matemáticas';return heading(math?'Matemáticas sin miedo':'Quiz con Allen',math?'Un ejercicio, una explicación y otra oportunidad.':'Practica sin Internet. Conoce lo que dominas y lo que puedes repasar.')+`<section class="panel"><form id="quiz-config" class="stack"><div class="field-grid">${field('Materia','quiz-subject',math?['Matemáticas']:Object.keys(state.catalog),'Matemáticas')}${field('Tema','quiz-topic',state.catalog['Matemáticas'])}${field('Dificultad de matemáticas','quiz-difficulty',['Fácil','Normal','Difícil'])}${field('Tipo de respuesta','quiz-kind',['Selección múltiple','Verdadero / falso','Respuesta corta'])}<label>Número de preguntas<input type="number" id="quiz-count" min="1" max="10" value="${math?1:5}" required></label></div><p class="muted">Todos los temas incluyen hasta 10 preguntas distintas. La dificultad cambia los números en matemáticas.</p><div><button class="primary">${math?'Crear ejercicio':'Empezar mi quiz'} &nbsp; →</button></div></form></section><div id="quiz-body"></div>`;}
function bindQuiz(){
 $('#quiz-subject').onchange=()=>$('#quiz-topic').innerHTML=options(state.catalog[$('#quiz-subject').value]);
 $('#quiz-config').onsubmit=async e=>{e.preventDefault();await guarded(async()=>{quiz=await api('/quiz','POST',{profile_id:state.profile,subject:$('#quiz-subject').value,topic:$('#quiz-topic').value,difficulty:$('#quiz-difficulty').value,count:Number($('#quiz-count').value),kind:['multiple','boolean','short'][$('#quiz-kind').selectedIndex]});showQuiz();});};
 if(quiz)showQuiz();
}
function showQuiz(){
 const box=$('#quiz-body');if(!box)return;if(quiz.result){showResult(quiz.result);return;}
 quiz.answers??=[];if(quiz.answers.length===quiz.actual_count){box.innerHTML=EmptyState('Ya respondiste tu reto','Guarda el resultado para ver tu progreso.','celebrating')+'<button class="primary" id="finish-quiz">Guardar resultado</button>';$('#finish-quiz').onclick=()=>guarded(async()=>{quiz.result=await api('/quiz/'+quiz.id+'/submit','POST',{profile_id:state.profile,answers:quiz.answers});showResult(quiz.result);});return;}const i=quiz.answers.length,q=quiz.questions[i];
 box.innerHTML=`<section class="panel quiz-step"><div class="row spaced"><span class="eyebrow">A TU RITMO</span><b>Pregunta ${i+1} de ${quiz.actual_count}</b></div><progress value="${i}" max="${quiz.actual_count}" aria-label="Preguntas completadas"></progress><form id="answers"><fieldset><legend>${esc(q.prompt)}</legend>${q.options.length?q.options.map(o=>`<label class="answer-option"><input type="radio" name="answer" value="${esc(o)}" required>${esc(o)}</label>`).join(''):'<label>Tu respuesta<input name="answer" maxlength="500" required></label>'}</fieldset><button class="primary">Comprobar respuesta</button></form><div id="answer-feedback" aria-live="polite"></div></section>`;
 $('#answers').onsubmit=async e=>{e.preventDefault();const answer=new FormData(e.target).get('answer'),button=e.target.querySelector('button');button.disabled=true;try{const f=await api('/quiz/'+quiz.id+'/answer','POST',{profile_id:state.profile,index:i,answer});quiz.answers.push(answer);e.target.querySelectorAll('input').forEach(el=>el.disabled=true);$('#answer-feedback').innerHTML=`<div class="quiz-feedback ${f.correct?'correct':''}">${AllenMascot(f.correct?'celebrating':'thinking')}<div><h2>${icon(f.correct?'circle-check':'lightbulb')} ${f.correct?'¡Muy bien!':'Casi. Mira por qué…'}</h2><p>${esc(f.explanation)}</p><p>Respuesta: <b>${esc(f.answer)}</b></p><button class="primary" id="next-question">${i+1===quiz.actual_count?'Ver mi resultado':'Siguiente pregunta'}</button></div></div>`;$('#next-question').onclick=()=>guarded(async()=>{if(quiz.answers.length===quiz.actual_count){quiz.result=await api('/quiz/'+quiz.id+'/submit','POST',{profile_id:state.profile,answers:quiz.answers});showResult(quiz.result);}else showQuiz();});}catch(error){button.disabled=false;toast(error.message);}};
}
function showResult(r){if(!$('#quiz-body'))return;$('#quiz-body').innerHTML=`<section class="panel"><div class="eyebrow">OTRO PASO EN TU CAMINO</div><div class="score">${r.score}<span class="muted"> / ${r.total}</span></div>${AllenMascot("celebrating")}<h2>¡Otro paso en tu aprendizaje!</h2><p>Temas que dominas: ${esc(r.mastered.join(', ')||'Seguimos descubriendo.')}</p><p>Para repasar: ${esc(r.review.join(', ')||'¡Buen trabajo con estos ejercicios!')}</p>${r.feedback.map(f=>`<div class="feedback ${f.correct?'correct':''}"><b>${f.correct?'✓':'↻'} ${esc(f.prompt)}</b><p>Tu respuesta: ${esc(f.given)} · Respuesta: ${esc(f.answer)}</p><p>${esc(f.explanation)}</p></div>`).join('')}<div class="row"><button class="primary" id="practice-errors">Practicar errores</button><button id="another-quiz">Intentar otro quiz</button><button id="talk-quiz">Hablar con Allen sobre esto</button></div></section>`;$('#another-quiz').onclick=()=>{quiz=null;$('#quiz-body').innerHTML='';$('#quiz-config').requestSubmit();};$('#practice-errors').onclick=()=>{const topics=r.review.join(', ');pendingPrompt=topics?'Quiero practicar estos temas que fallé en mi último quiz: '+topics+'. Hazme una pregunta a la vez y dame pistas antes de mostrar la respuesta.':'Ponme un nuevo reto relacionado con este quiz.';go('Tutor');};$('#talk-quiz').onclick=()=>{pendingPrompt='Ayúdame a entender mi último quiz. Temas para repasar: '+(r.review.join(', ')||'ninguno')+'. Explícame qué debería reforzar y luego hazme una pregunta.';go('Preguntar');};}

async function libraryPage(){return heading('Tu biblioteca offline','Explora lecturas locales, filtra por materia y convierte contenido en práctica.')+`
 <section class="v2-adventure-hero v2-library-hero">
  <div><span class="eyebrow">BIBLIOTECA LOCAL</span><h2>Ideas que viajan contigo.</h2><p>Busca en tus lecturas incluidas o importa tus propios apuntes. Nada necesita una nube para abrirse.</p></div>
  <img src="/static/assets/allen-library.svg" alt="Allen junto a su biblioteca offline">
 </section>
 <section class="panel">
  <form id="library-search" class="v2-library-toolbar">
   <label>Buscar<input id="library-query" maxlength="200" placeholder="Fracciones, Python, privacidad…"></label>
   <label>Materia<select id="library-subject"><option value="">Todas</option></select></label>
   <button class="primary">Buscar</button>
  </form>
  <p class="muted">Contenido guardado en este dispositivo. Puedes añadir paquetes JSON, Markdown y TXT.</p>
  <details class="import-panel"><summary>Añadir mi biblioteca</summary><p>Importa apuntes en TXT o Markdown, o un JSON con title, subject y content. Hasta 90 KB por archivo; 20.000 caracteres por lectura.</p><form id="library-import" class="stack"><label>Archivo de lecturas<input id="library-file" type="file" accept=".json,.md,.txt" required></label><button class="primary">Importar a mi perfil</button></form><div id="library-packs"></div></details>
  <div id="library-results" class="v2-library-grid"></div>
  <div id="library-reader"></div>
 </section>`;}
async function bindLibrary(){
 let docsCache=[];
 function subjectOptions(docs){
  const select=$('#library-subject');if(!select)return;
  const current=select.value;
  const subjects=[...new Set(docs.map(d=>d.subject).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es'));
  select.innerHTML='<option value="">Todas</option>'+subjects.map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('');
  if(subjects.includes(current))select.value=current;
 }
 function indexFor(content){
  const headings=String(content||'').split('\n').filter(line=>/^#{1,3}\s+/.test(line)).map(line=>line.replace(/^#{1,3}\s+/,'').trim()).slice(0,8);
  return headings.length?headings:['Lectura completa'];
 }
 function openReader(doc){
  const reader=$('#library-reader');if(!reader)return;
  const headings=indexFor(doc.content);
  const minutes=Math.max(1,Math.ceil(String(doc.content||'').split(/\s+/).length/180));
  reader.innerHTML=`<section class="v2-reading-shell">
   <aside class="v2-reading-index"><span class="eyebrow">ÍNDICE</span>${headings.map((h,i)=>`<button type="button" data-reader-anchor="${i}">${esc(h)}</button>`).join('')}<hr><button type="button" id="reader-focus">Modo concentración</button><div class="row"><button type="button" data-reader-size="-1">A−</button><button type="button" data-reader-size="1">A+</button></div></aside>
   <article class="v2-reading-main" id="reader-main"><div class="row spaced"><div><span class="eyebrow">${esc(doc.subject||'Lectura')}</span><h1>${esc(doc.title)}</h1></div><span class="pill">≈ ${minutes} min</span></div><progress value="1" max="1" aria-label="Lectura abierta"></progress><div class="reading">${markdown(doc.content)}</div></article>
   <aside class="v2-reading-aside"><img src="${libraryVisual(doc.subject)}" alt="" class="reader-side-image"><h3>Aprende haciendo</h3><button type="button" id="reader-ask">Preguntar a Allen</button><button type="button" id="reader-quiz">Hazme preguntas</button><button type="button" data-page="Tarjetas">Crear tarjeta</button></aside>
  </section>`;
  let size=1;
  $('#reader-focus').onclick=()=>{$('.v2-reading-main').classList.toggle('focus');document.querySelector('.v2-reading-index').classList.toggle('hidden');document.querySelector('.v2-reading-aside').classList.toggle('hidden');};
  reader.querySelectorAll('[data-reader-size]').forEach(b=>b.onclick=()=>{size=Math.max(.85,Math.min(1.35,size+Number(b.dataset.readerSize)*.1));$('#reader-main').style.fontSize=size+'em';});
  $('#reader-ask').onclick=()=>{pendingPrompt='Estoy leyendo «'+doc.title+'». Ayúdame a entender esta idea de la lectura: '+String(doc.content).replace(/[#*\`]/g,'').slice(0,1200);go('Preguntar');};
  $('#reader-quiz').onclick=()=>{pendingPrompt='Estoy estudiando «'+doc.title+'». Hazme 3 preguntas para comprobar que entendí esta lectura. No me des las respuestas hasta que conteste. Contexto: '+String(doc.content).replace(/[#*\`]/g,'').slice(0,1800);go('Preguntar');};
  reader.scrollIntoView({behavior:'smooth',block:'start'});
 }
 async function search(){
  docsCache=await api('/library?profile_id='+state.profile+'&q='+encodeURIComponent($('#library-query').value));
  subjectOptions(docsCache);
  const subject=$('#library-subject')?.value||'';
  const docs=subject?docsCache.filter(d=>d.subject===subject):docsCache;
  if(!$('#library-results'))return;
  $('#library-results').innerHTML=docs.length?docs.map((d,i)=>{
   const clean=d.content.replace(/[#*\`]/g,'').replace(/\s+/g,' ').trim();
   const minutes=Math.max(1,Math.ceil(clean.split(/\s+/).length/180));
   return `<article class="v2-library-card"><img src="${libraryVisual(d.subject)}" alt=""><div class="v2-library-copy"><span class="eyebrow">${esc(d.subject||'LECTURA')}</span><h2>${esc(d.title)}</h2><p>${esc(clean.slice(0,150))}${clean.length>150?'…':''}</p><div class="row spaced"><small>≈ ${minutes} min</small><button data-read="${i}">Leer</button></div></div></article>`;
  }).join(''):'<p class="empty">No encontramos ese tema. Prueba otra palabra o cambia el filtro.</p>';
  $('#library-results').onclick=e=>{const b=e.target.closest('[data-read]');if(b){const visible=subject?docsCache.filter(d=>d.subject===subject):docsCache;openReader(visible[Number(b.dataset.read)]);}};
 }
 $('#library-search').onsubmit=e=>{e.preventDefault();guarded(search);};
 $('#library-subject').onchange=()=>guarded(search);
 async function packs(){const rows=await api('/library/packs?profile_id='+state.profile);$('#library-packs').innerHTML=rows.map(r=>`<div class="row spaced library-card"><span>${esc(r.title)}</span><button data-delete-pack="${r.id}">Eliminar biblioteca</button></div>`).join('');}
 $('#library-import').onsubmit=e=>{e.preventDefault();guarded(async()=>{const file=$('#library-file').files[0];if(!file||file.size>90000)throw new Error('Elige un archivo de hasta 90 KB.');const result=await api('/library/import','POST',{profile_id:state.profile,filename:file.name,content:await file.text()});toast(result.count+' lecturas importadas.');$('#library-import').reset();await packs();await search();});};
 $('#library-packs').onclick=e=>{const b=e.target.closest('[data-delete-pack]');if(b&&confirm('¿Eliminar esta biblioteca importada?'))guarded(async()=>{await api('/library/packs/'+b.dataset.deletePack+'?profile_id='+state.profile,'DELETE');await packs();await search();});};
 await packs();await search();
}

async function cardsPage(){return heading('Un poquito cada día','Tus tarjetas vuelven cuando es momento de repasarlas.')+`<div class="field-grid"><section class="panel"><h2>Crear una tarjeta</h2><p class="muted">Convierte tus apuntes en una pregunta y su respuesta. También puedes generar propuestas desde un tema, texto o apuntes con tu modelo local.</p><form id="card-form" class="stack"><label>Pregunta<input id="card-question" maxlength="500" required></label><label>Respuesta<textarea id="card-answer" maxlength="2000" required></textarea></label><button class="primary">Guardar tarjeta</button></form></section><section class="panel"><h2>Tu repaso de hoy</h2><div id="card-study"></div></section></div><section class="panel"><h2>Mis tarjetas</h2><div id="card-list"></div></section><section class="panel"><h2>Generar con mi IA local</h2><p class="muted">Revisa las tarjetas propuestas antes de guardarlas. Esta herramienta necesita el modelo local.</p><form id="card-generate" class="stack"><div class="field-grid">${field("Origen","card-source-kind",["Tema","Texto","Apuntes"])}<label>Cantidad<input id="card-count" type="number" min="1" max="10" value="5" required></label></div><label>Tema o contenido<textarea id="card-source" maxlength="8000" required></textarea></label><div><button class="primary" id="generate-cards-button">Generar propuestas</button></div></form><div id="card-proposals"></div></section>`;}
async function bindCards(){const cards=await api('/flashcards?profile_id='+state.profile);const d=new Date(),today=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;const due=cards.filter(c=>c.due<=today);let index=0;
 function show(){if(!$('#card-study'))return;const card=due[index];$('#card-study').innerHTML=card?`<div class="flashcard"><p class="muted">${index+1} / ${due.length} pendientes</p><h2>${esc(card.question)}</h2><button id="reveal">Mostrar respuesta</button><div id="card-back" class="hidden"><p>${esc(card.answer)}</p><div class="row">${[['No la sé','Otra vez'],['Difícil','Difícil'],['Bien','Bien'],['Fácil','Fácil']].map(([value,label])=>`<button data-rating="${value}">${label}</button>`).join('')}</div></div></div>`:`<div class="empty">${AllenMascot("studying")}<h2>¡Todo al día!</h2><p>Crea una tarjeta o vuelve en tu próxima fecha de repaso.</p></div>`;if(card){$('#reveal').onclick=()=>{$('#card-back').classList.remove('hidden');$('#reveal').classList.add('hidden');};$('#card-back').onclick=e=>{const b=e.target.closest('[data-rating]');if(b)guarded(async()=>{const review=await api('/flashcards/'+card.id+'/review','POST',{profile_id:state.profile,rating:b.dataset.rating});card.reviews++;if($('#card-meta-'+card.id))$('#card-meta-'+card.id).textContent='Próximo repaso: '+review.due+' · '+card.reviews+' repasos';index++;show();});};}}
 $('#card-generate').onsubmit=e=>{e.preventDefault();guarded(async()=>{const button=$('#generate-cards-button');button.disabled=true;button.textContent='Allen está pensando…';try{const generated=await api('/flashcards/generate','POST',{profile_id:state.profile,source:$('#card-source').value,kind:$('#card-source-kind').value,count:Number($('#card-count').value)});$('#card-proposals').innerHTML=generated.cards.map((c,i)=>`<div class="library-card"><h3>${esc(c.question)}</h3><p>${esc(c.answer)}</p><button data-save-proposal="${i}">Guardar esta tarjeta</button></div>`).join('');$('#card-proposals').onclick=event=>{const b=event.target.closest('[data-save-proposal]');if(b)guarded(async()=>{b.disabled=true;try{await api('/flashcards','POST',{profile_id:state.profile,...generated.cards[Number(b.dataset.saveProposal)]});b.textContent='Guardada ✓';toast('Tarjeta guardada. Vuelve a Estudiar para repasarla.');}catch(error){b.disabled=false;throw error;}});};}finally{button.disabled=false;button.textContent='Generar propuestas';}});};
 show();$('#card-list').innerHTML=cards.length?cards.map(c=>`<div class="library-card row spaced"><div><b>${esc(c.question)}</b><p id="card-meta-${c.id}">Próximo repaso: ${esc(c.due)} · ${c.reviews} repasos</p></div><button data-delete-card="${c.id}">Eliminar</button></div>`).join(''):'<p class="muted">Tu primera tarjeta empieza con una buena pregunta.</p>';
 $('#card-form').onsubmit=e=>{e.preventDefault();guarded(async()=>{await api('/flashcards','POST',{profile_id:state.profile,question:$('#card-question').value,answer:$('#card-answer').value});toast('Tarjeta guardada.');render();});};
 $('#card-list').onclick=e=>{const b=e.target.closest('[data-delete-card]');if(b&&confirm('¿Eliminar esta tarjeta?'))guarded(async()=>{await api('/flashcards/'+b.dataset.deleteCard+'?profile_id='+state.profile,'DELETE');render();});};
}

async function progressPage(){
 const [p,results,continuityData]=await Promise.all([api('/progress?profile_id='+state.profile),api('/quiz/results?profile_id='+state.profile),api('/continuity?profile_id='+state.profile)]);
 const mastery=continuityData?.mastery||[],strong=mastery.filter(x=>Number(x.mastery_score)>=80).length,developing=mastery.filter(x=>Number(x.mastery_score)>=55&&Number(x.mastery_score)<80).length,weak=mastery.filter(x=>Number(x.mastery_score)<55).length;
 const totalSeconds=(p.subjects||[]).reduce((a,x)=>a+(x.seconds||0),0)||1;
 const subjectBars=(p.subjects||[]).map(s=>`<article class="v4-subject-row"><div class="row spaced"><b>${esc(s.subject)}</b><span>${Math.floor((s.seconds||0)/60)} min</span></div><div><i data-width-pct="${Math.max(5,Math.round((s.seconds||0)/totalSeconds*100))}"></i></div></article>`).join('');
 const recent=results.slice(0,5).map(r=>`<article class="v4-recent-result"><span>${esc(r.config.subject+' · '+r.config.topic)}</span><b>${r.result.score}/${r.result.total}</b></article>`).join('');
 return heading(state.page==='Docente'?'Acompañar su aprendizaje':'Tu progreso','Entiende qué avanzó, qué necesita práctica y cuál es el siguiente paso.')+`
 <section class="v4-progress-hero"><div><span class="eyebrow">PANORAMA DE APRENDIZAJE</span><h2>${p.xp?'Estás construyendo constancia.':'Tu progreso empieza con la primera práctica.'}</h2><p>Sin rankings. Solo evidencia de tu propio aprendizaje.</p></div>${AllenMascot(p.xp?'celebrating':'studying')}</section>
 <section class="v4-kpi-grid"><article><span>Tiempo activo</span><b>${p.minutes} min</b><small>registrados localmente</small></article><article><span>Temas dominados</span><b>${strong}</b><small>${developing} en desarrollo</small></article><article><span>Por reforzar</span><b>${weak}</b><small>${continuityData?.due_topic_reviews?.length||0} repasos pendientes</small></article><article><span>Constancia</span><b>${p.streak} días</b><small>${p.xp} XP acumulados</small></article></section>
 <div class="v4-progress-grid"><section class="panel"><div class="row spaced"><div><span class="eyebrow">MATERIAS</span><h2>Dónde estás invirtiendo tiempo</h2></div></div><div class="v4-subject-list">${subjectBars||'<p class="muted">Tus materias aparecerán aquí cuando estudies.</p>'}</div></section>
 <section class="panel"><span class="eyebrow">MASTERY</span><h2>Estado de tus temas</h2><div class="v4-mastery-donut" data-mastery-strong="${strong}" data-mastery-developing="${developing}" data-mastery-weak="${weak}" data-mastery-total="${Math.max(1,strong+developing+weak)}"><div><b>${strong+developing+weak}</b><span>temas</span></div></div><div class="v4-legend"><span><i class="strong"></i>Dominados ${strong}</span><span><i class="developing"></i>En desarrollo ${developing}</span><span><i class="weak"></i>Reforzar ${weak}</span></div></section></div>
 <section class="panel v4-recent"><div class="row spaced"><div><span class="eyebrow">ACTIVIDAD RECIENTE</span><h2>Últimos quizzes</h2></div><button data-page="Quiz">Practicar</button></div><div>${recent||'<p class="muted">Aún no has terminado un quiz.</p>'}</div></section>
 ${achievementPanel(p,results)}`;
}
function bindProgress(){}

async function settingsPage(){const health=await api('/health'),license=await api('/license/status'),s=state.settings,p=profile();return heading('A tu manera','Tu perfil, tu espacio y el cerebro local de Allen.')+`
 <section class="panel license-settings"><div class="row spaced"><div><span class="eyebrow">LICENCIA OFFLINE</span><h2>Licencia y suscripción</h2></div><span class="pill ${license.active?'green':''}">${license.active?'ACTIVA':'REQUIERE RENOVACIÓN'}</span></div>
 <div class="license-summary"><div><span>Cliente</span><b>${esc(license.customer||'—')}</b></div><div><span>Plan</span><b>${esc(license.plan||'—')}</b></div><div><span>Licencia</span><b>${esc(license.license_id||'—')}</b></div><div><span>Válida hasta</span><b>${esc(licenseDate(license.valid_until))}</b></div><div><span>Días restantes</span><b>${license.days_remaining??'—'}</b></div><div><span>Perfiles</span><b>Sin límite</b></div></div>
 <div class="license-machine compact"><span>MACHINE ID</span><code>${esc(license.machine_id||'—')}</code></div>
 <div class="row"><label class="button-like">Importar renovación<input id="license-renew-file" type="file" accept=".license,application/json" hidden></label></div>
 <p id="license-renew-feedback" class="muted">Renovar no requiere reinstalar ALLEN y no elimina ningún dato.</p></section>
 <section class="panel"><h2>Modo Feria</h2><p>Retos, microlecciones y conversaciones temporales para visitantes.</p><a class="primary" href="/fair">Abrir Modo Feria</a></section>
 <div class="panel"><h2>Tu perfil local</h2><form id="profile-form" class="stack"><div class="field-grid"><label>Nombre o apodo<input id="profile-name" maxlength="40" value="${esc(p.name)}" required></label>${field('Nivel educativo','profile-level',levels,p.level)}<label>Edad (opcional)<input type="number" id="profile-age" min="5" max="120" value="${p.age??''}"></label>${field('Avatar','profile-avatar',['🐵','🦊','🐼','🐸','🦉'],p.avatar)}</div><div class="row"><button class="primary">Guardar perfil</button><button type="button" id="add-profile">Crear otro perfil con estos datos</button></div></form></div>
 <div class="panel"><h2>Preferencias del dispositivo</h2><p class="muted">Conecta el cerebro de Allen en este dispositivo. No hace falta una cuenta ni una API de pago.</p><form id="settings-form" class="stack"><details class="advanced"><summary>Avanzado · modelo local</summary><div class="field-grid"><label>Dirección local<input id="ai-server" value="${esc(s.ai_server)}" required></label><label>Modelo (vacío = detectar automáticamente)<input id="model" value="${esc(s.model)}" maxlength="200" list="models"><datalist id="models">${options(state.model?.models||[])}</datalist></label><label>Creatividad · 0 a 1.5<input id="temperature" type="number" min="0" max="1.5" step="0.1" value="${s.temperature}" required></label><label>Contexto · 2048 a 32768<input id="context" type="number" min="2048" max="32768" value="${s.context_size}" required></label><label>Respuesta máxima · 64 a 4096 tokens<input id="max-tokens" type="number" min="64" max="4096" value="${s.max_tokens}" required></label></div><p class="muted">El contexto también debe configurarse al iniciar llama.cpp con -c. Elegir un nombre aquí no descarga ni carga otro modelo.</p><label class="check"><input id="demo" type="checkbox" ${s.demo?'checked':''}>Usar siempre modo demo</label></details><div class="field-grid">${field('Rendimiento de la IA','performance',['Rápido','Equilibrado','Detallado'],s.performance||'Equilibrado')}<label>Conservar conversaciones (días)<input id="retention" type="number" min="1" max="90" value="${s.retention_days}" required></label></div><div class="row"><label class="check"><input id="save-history" type="checkbox" ${s.save_history?'checked':''}>Guardar historial</label></div><h2>Accesibilidad</h2><div class="field-grid">${field('Tamaño del texto','font-size',['normal','grande','muy grande'],s.font_size)}<label class="check"><input id="contrast" type="checkbox" ${s.high_contrast?'checked':''}>Alto contraste</label></div><div><button class="primary">Guardar configuración</button></div></form></div>
 <section class="panel"><div class="row spaced"><h2>Todo en su lugar</h2><button id="refresh-status">Comprobar conexión</button></div><p>✓ Aplicación funcionando &nbsp; ✓ Base de datos disponible</p><p>✓ Biblioteca: ${health.library} lecturas locales</p><p id="model-health">${esc(state.model?.state||'Comprobando…')}</p>${state.model?.metrics?.time_to_first_token!=null?`<p class="muted">Rendimiento local · primera respuesta: ${state.model.metrics.time_to_first_token}s · generación: ~${state.model.metrics.estimated_tokens_per_second??'—'} tok/s estimados · modo ${esc(state.model.metrics.mode||'Equilibrado')}</p>`:''}<p class="muted">${navigator.onLine?'Red disponible según el navegador; acceso a Internet no comprobado.':'Sin conexión de red según el navegador.'} No hacemos peticiones externas para comprobarlo.</p><p class="muted">Estas preferencias se comparten en este dispositivo.</p></section>
 <section class="panel"><div class="row spaced"><div><span class="eyebrow">RESPALDO LOCAL</span><h2>Tu progreso también puede viajar contigo.</h2></div><img src="/static/assets/allen-progress.svg" alt="" class="settings-visual progress-visual"></div><p>Exporta perfiles, progreso, conversaciones, cursos y demás datos a un respaldo cifrado con contraseña (AES-256-GCM). No incluye secretos de licencia.</p><div class="row"><button id="backup-export">Exportar mis datos</button><label class="button-like">Importar respaldo<input id="backup-import" type="file" accept=".allenbackup,.json,application/json" hidden></label></div><div id="backup-summary" class="muted"></div></section>
 <section class="panel reliability-panel v3-recovery"><div class="row spaced"><div><span class="eyebrow">PROTECCIÓN DE DATOS</span><h2>Estado de tus datos locales</h2><p>ALLEN crea copias seguras antes de cambios importantes para que puedas volver atrás si algo sale mal.</p></div><img src="/static/assets/allen-checklist-official.svg" alt="" class="settings-visual recovery-visual"></div><div class="recovery-primary-actions"><button id="db-diagnose" class="primary">Comprobar estado</button><button id="db-snapshot">Crear copia segura ahora</button></div><div id="db-health" class="recovery-status muted">Todavía no se ha comprobado el estado de la base.</div><details class="advanced recovery-advanced"><summary>Copias anteriores y detalles técnicos</summary><p class="muted">Aquí puedes restaurar snapshots locales y consultar la información técnica de SQLite.</p><div class="row"><select id="recovery-snapshot" aria-label="Snapshot de recuperación"><option value="">Selecciona una copia</option></select><button id="db-restore" class="danger">Restaurar copia</button></div></details></section>`;}
async function profilePage(){
 const progress=await api('/progress?profile_id='+state.profile);
 const html=await settingsPage();const doc=document.createElement('div');doc.innerHTML=html;
 const interests=profile().memory?.interests||[];
 return heading('Tu espacio, a tu manera','Un perfil local para adaptar nivel, intereses y ritmo de aprendizaje.')+`
 <section class="v2-profile-hero">
  <div class="v2-profile-identity">${studentAvatar()}<div><span class="eyebrow">PERFIL LOCAL</span><h2>${esc(profile().name)}</h2><p>${esc(profile().level)}</p></div></div>
  <img src="/static/assets/allen-study.svg" alt="Allen estudiando">
  <div><span class="eyebrow">INTERESES</span><div class="v2-interest-tags">${interests.length?interests.map(x=>`<span>${esc(x)}</span>`).join(''):'<span>Añade intereses para personalizar tus sugerencias</span>'}</div></div>
 </section>`+doc.querySelector('#profile-form').parentElement.outerHTML+memoryForm(profile().memory)+`
 <section class="panel"><div class="row spaced"><div><span class="eyebrow">TU CAMINO</span><h2>Aprendizaje personal, sin rankings.</h2></div><button data-page="Progreso">Ver progreso completo</button></div><p>Nivel actual: <b>${esc(progress.level)}</b></p>${stats(progress)}<p class="muted">Tus perfiles viven en este dispositivo y no requieren correo, teléfono ni cuenta en la nube.</p></section>`;
}
function bindProfile(){bindSettings();bindMemory();}
function bindSettings(){
 if($('#license-renew-file'))$('#license-renew-file').onchange=e=>guarded(async()=>{
  const file=e.target.files?.[0];if(!file)return;
  const box=$('#license-renew-feedback');box.textContent='Verificando renovación…';
  const result=await api('/license/activate','POST',{content:await file.text()});
  state.license=result;box.textContent='Licencia renovada hasta '+licenseDate(result.valid_until)+'.';toast('Licencia renovada.');
  setTimeout(()=>render(),700);
 });
 function profileData(){return {name:$('#profile-name').value,age:$('#profile-age').value?Number($('#profile-age').value):null,level:$('#profile-level').value,avatar:$('#profile-avatar').value};}
 async function saveProfile(create){const p=await api('/profiles'+(create?'':'/'+state.profile),create?'POST':'PUT',profileData());if(create){state.profiles.push(p);chat={messages:[],id:null,controller:null};quiz=null;}else state.profiles=state.profiles.map(old=>old.id===p.id?p:old);state.profile=p.id;updateProfiles();toast('Perfil guardado.');render();}
 if($('#profile-form'))$('#profile-form').onsubmit=e=>{e.preventDefault();guarded(()=>saveProfile(false));};if($('#add-profile'))$('#add-profile').onclick=()=>{if($('#profile-form').reportValidity())guarded(()=>saveProfile(true));};
 if($('#settings-form'))$('#settings-form').onsubmit=e=>{e.preventDefault();guarded(async()=>{state.settings=await api('/settings','PUT',{...state.settings,ai_server:$('#ai-server').value,model:$('#model').value,temperature:Number($('#temperature').value),context_size:Number($('#context').value),max_tokens:Number($('#max-tokens').value),retention_days:Number($('#retention').value),demo:$('#demo').checked,save_history:$('#save-history').checked,font_size:$('#font-size').value,high_contrast:$('#contrast').checked,performance:$('#performance').value});if(!state.settings.save_history)chat.id=null;applyAppearance();state.model=await api('/model/status');toast('Configuración guardada.');render();});};
 if($('#refresh-status'))$('#refresh-status').onclick=()=>guarded(async()=>{state.model=await api('/model/status');$('#model-health').textContent=state.model.state;toast(state.model.state);});
 if($('#backup-export'))$('#backup-export').onclick=()=>guarded(async()=>{if(!(await ensureTeacherAccess()))return;const password=prompt('Crea una contraseña para cifrar este respaldo (mínimo 8 caracteres).');if(!password)return;if(password.length<8)throw new Error('La contraseña debe tener al menos 8 caracteres.');const confirmPassword=prompt('Confirma la contraseña del respaldo.');if(password!==confirmPassword)throw new Error('Las contraseñas no coinciden.');const data=await api('/backup/export-encrypted','POST',{profile_id:state.profile,password});const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='allen-backup-'+new Date().toISOString().slice(0,10)+'.allenbackup';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);toast('Respaldo cifrado creado. Guarda también su contraseña.');});
 if($('#backup-import'))$('#backup-import').onchange=e=>guarded(async()=>{if(!(await ensureTeacherAccess()))return;const file=e.target.files[0];if(!file)return;if(file.size>8000000)throw new Error('El respaldo es demasiado grande.');let data=JSON.parse(await file.text());if(data?.format==='allen-backup-encrypted'){const password=prompt('Contraseña del respaldo cifrado.');if(!password)return;data=await api('/backup/decrypt','POST',{password,envelope:data});}const summary=await api('/backup/validate','POST',data);$('#backup-summary').textContent=summary.profiles+' perfiles · '+summary.flashcards+' tarjetas · '+summary.plans+' planes · '+summary.adventures+' aventuras · '+(summary.courses||0)+' cursos';if(confirm('¿Restaurar este respaldo? Reemplazará los datos locales actuales.')){const restored=await api('/backup/restore','POST',data);toast('Respaldo restaurado. Snapshot de seguridad: '+(restored.safety_snapshot||'creado'));location.reload();}});
 async function refreshRecovery(){const report=await api('/system/integrity');const box=$('#db-health'),select=$('#recovery-snapshot');if(box)box.innerHTML='<b>'+(report.ok?'Base íntegra':'Requiere atención')+'</b> · schema v'+report.schema_version+' · '+Math.round((report.bytes||0)/1024)+' KB'+(report.foreign_key_issues?.length?' · '+report.foreign_key_issues.length+' problemas FK':'');if(select){select.innerHTML='<option value="">Selecciona un snapshot</option>'+(report.snapshots||[]).map(x=>'<option value="'+esc(x.name)+'">'+esc(x.name)+' · '+Math.round(x.bytes/1024)+' KB</option>').join('');}}
 if($('#db-diagnose'))$('#db-diagnose').onclick=()=>guarded(async()=>{await refreshRecovery();toast('Diagnóstico local completado.');});
 if($('#db-snapshot'))$('#db-snapshot').onclick=()=>guarded(async()=>{const r=await api('/system/recovery/snapshot','POST',{});await refreshRecovery();toast(r.snapshot?'Snapshot creado.':'No había datos que respaldar.');});
 if($('#db-restore'))$('#db-restore').onclick=()=>guarded(async()=>{const name=$('#recovery-snapshot').value;if(!name)throw new Error('Selecciona un snapshot.');if(confirm('¿Restaurar '+name+'? Allen creará primero una copia de seguridad del estado actual.')){await api('/system/recovery/restore','POST',{snapshot:name});toast('Snapshot restaurado. Recargando ALLEN…');location.reload();}});
 if($('#db-health'))refreshRecovery().catch(()=>{});
}
function privacyPage(){return heading('Tu aprendizaje te pertenece','Sin cuentas en la nube. Sin anuncios. Sin seguimiento.')+`<section class="panel reading"><h2>Allen funciona dentro de este dispositivo.</h2><p>No necesitamos enviar tus conversaciones a Internet. El modelo se consulta exclusivamente por una dirección local; no usamos fuentes, imágenes ni scripts de una CDN.</p><h2>Tú eliges qué guardar</h2><p>Tu información educativa permanece local. El historial se conserva ${state.settings.retention_days} días como máximo, con limpieza al iniciar o consultar conversaciones. Si desactivas «Guardar historial», se borran las conversaciones guardadas de todos los perfiles. La conversación en pantalla dura hasta recargar o limpiarla.</p><p>Los perfiles, resultados, tarjetas y progreso permanecen hasta que los elimines. En Windows se guardan en %LOCALAPPDATA%\\ALLEN, fuera de la carpeta del proyecto y de OneDrive. Quien tenga acceso a tu cuenta de Windows puede acceder a estos datos; los perfiles no son cuentas protegidas por contraseña.</p><h2>Aprender con cuidado</h2><p>Allen usa reglas educativas y filtros básicos. Pueden cometer errores o no detectar una pregunta peligrosa. No sustituyen la supervisión de una persona adulta ni un servicio de ayuda profesional. Para temas importantes, consulta a tu docente o una fuente de confianza.</p><h2>Sobre la conexión</h2><p>El navegador informa si hay red; no comprobamos Internet mediante servicios externos. La instalación inicial y la descarga del modelo sí requieren conexión. Después, los módulos locales funcionan sin ella.</p><button data-page="Configuración">Cambiar mis preferencias</button></section><section class="panel"><h2>Eliminar todos mis datos</h2><p class="muted">Elimina el perfil activo «${esc(profile().name)}», sus conversaciones, memoria educativa, respuestas guardadas, tarjetas, quizzes, sesiones y progreso. También se eliminan tus bibliotecas importadas. Los otros perfiles y las lecturas incluidas con ALLEN se conservan.</p><button class="danger" id="erase-profile">Eliminar todos mis datos de este perfil</button><p class="muted">No se pueden retirar copias de seguridad que hayas hecho por separado.</p></section>`;}
function bindPrivacy(){$('#erase-profile').onclick=()=>{if(confirm('¿Eliminar definitivamente el perfil '+profile().name+' y todos sus datos?'))guarded(async()=>{await api('/profiles/'+state.profile,'DELETE');chat={messages:[],id:null,controller:null};quiz=null;await bootstrap();go('Inicio');toast('Los datos del perfil se eliminaron.');});};}

function showWelcome(){content.innerHTML=welcome();$('#welcome-form').onsubmit=e=>{e.preventDefault();guarded(async()=>{const p=profile();const updated=await api('/profiles/'+p.id,'PUT',{name:$('#welcome-name').value,age:p.age,level:p.level,avatar:p.avatar});state.profiles=state.profiles.map(old=>old.id===p.id?updated:old);updateProfiles();toast('¡Mucho gusto, '+updated.name+'!');go('Inicio');if(state.page==='Inicio')render();});};}
async function saveMemory(values){const memory=await api('/memory?profile_id='+state.profile);const saved=await api('/memory?profile_id='+state.profile,'PUT',{preferences:memory.preferences,interests:memory.interests,daily_goal:memory.daily_goal,...values});profile().memory=saved;return saved;}
function bindMemory(){const form=$('#learning-preferences');if(!form)return;form.onsubmit=e=>{e.preventDefault();guarded(async()=>{await saveMemory({preferences:[...form.querySelectorAll('[name=preference]:checked')].map(el=>el.value),interests:$('#learning-interests').value.split(',').map(s=>s.trim()).filter(Boolean)});toast('Tus preferencias quedaron guardadas en este dispositivo.');});};$('#forget-learning').onclick=()=>{if(confirm('¿Borrar intereses, preferencias, temas y objetivo? Tu nombre y conversaciones se conservan.'))guarded(async()=>{profile().memory=await api('/memory?profile_id='+state.profile,'DELETE');render();});};}
function bindHomeLearning(){const form=$('#daily-goal');if(form)form.onsubmit=e=>{e.preventDefault();guarded(async()=>{await saveMemory({daily_goal:$('#goal-input').value,set_goal:true});toast('Objetivo guardado. Vamos juntos.');});};content.querySelectorAll('[data-resume]').forEach(b=>b.onclick=()=>guarded(async()=>{const row=await api('/conversations/'+b.dataset.resume+'?profile_id='+state.profile);chat={messages:row.messages,id:row.id,controller:null,state:row.conversation_state||null};go('Preguntar');}));}
function bindSaved(){content.querySelectorAll('[data-delete-saved]').forEach(b=>b.onclick=()=>{if(confirm('¿Quitar esta respuesta de tus guardados?'))guarded(async()=>{await api('/saved/'+b.dataset.deleteSaved+'?profile_id='+state.profile,'DELETE');render();});});}
async function guarded(fn){try{return await fn();}catch(error){toast(error.message||'Algo no salió bien. Inténtalo de nuevo.');}}
async function bootstrap(){
 const data=await api('/bootstrap');
 setToken(data.token);
 state.license=data.license||null;
 state.profiles=data.profiles||[];
 state.settings=data.settings||{};
 state.catalog=data.catalog||{};
 if(state.license?.required&&!state.license?.active){licenseGate(state.license);return false;}
 document.body.classList.remove('license-locked');
 $('#profile-select').closest('label')?.classList.remove('hidden');
 if(!state.profiles.length)throw new Error('ALLEN no encontró perfiles locales.');
 if(!state.profiles.some(p=>p.id===state.profile))state.profile=state.profiles[0].id;
 updateProfiles();applyAppearance();return true;
}
setInterval(()=>{if(!document.hidden&&Date.now()-lastActivity<60000&&!['Inicio','Configuración','Privacidad','Progreso','Docente'].includes(state.page)){api('/study','POST',{profile_id:state.profile,subject:state.page==='Tutor'?($('#chat-subject')?.value||'Tutor'):state.page,seconds:30}).catch(()=>{});}},30000);
await guarded(async()=>{const ready=await bootstrap();if(!ready)return;state.page=decodeURIComponent(location.hash.slice(1))||'Inicio';await render();state.model=await api('/model/status');document.querySelectorAll('.ai-state').forEach(el=>{el.textContent=state.model.connected?'IA LOCAL ACTIVA':'IA local sin conectar';el.classList.toggle('green',state.model.connected);});if(state.model.connected)document.querySelector('.model-notice')?.remove();if($('#model-health'))$('#model-health').textContent=state.model.state;document.querySelectorAll('.model-description').forEach(el=>el.textContent=state.model.connected?'Tu modelo local está listo.':'Las respuestas libres necesitan conectar un modelo local.');});
