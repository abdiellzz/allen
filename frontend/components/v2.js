const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export const missions=[
 {
  id:'recover-network',title:'Recupera la red',subject:'Redes',difficulty:'Intermedio',image:'/static/assets/allen-networking.svg',xp:80,achievement:'Maestro de redes',
  description:'El laboratorio perdió conectividad. Reconstruye la ruta de red junto a Allen.',
  steps:[
   {title:'Encuentra la dirección',text:'Un equipo tiene 192.168.10.34/24. ¿Qué parte identifica la red?',options:['192.168.10','34','/24 solamente'],correct:0,hint:'En una /24, los primeros 24 bits pertenecen a la red.',explanation:'En una /24, los tres primeros octetos forman la parte de red: 192.168.10.0/24.'},
   {title:'Lee la máscara',text:'¿Qué máscara decimal corresponde a /24?',options:['255.255.255.0','255.255.0.0','255.255.255.192'],correct:0,hint:'24 bits en 1 ocupan tres octetos completos.',explanation:'/24 equivale a 255.255.255.0.'},
   {title:'Divide la red',text:'Si divides una /24 en cuatro subredes iguales, ¿qué prefijo obtienes?',options:['/25','/26','/28'],correct:1,hint:'Cuatro subredes necesitan tomar 2 bits adicionales.',explanation:'Tomar 2 bits de host convierte /24 en /26 y produce cuatro subredes.'},
   {title:'Elige el gateway',text:'En 192.168.10.64/26, ¿cuál podría usarse como gateway si se elige la primera IP utilizable?',options:['192.168.10.64','192.168.10.65','192.168.10.127'],correct:1,hint:'La primera dirección es de red y la última es broadcast.',explanation:'El rango utilizable comienza en .65 y termina en .126.'}
  ]
 },
 {
  id:'digital-defender',title:'Defensor digital',subject:'Ciberseguridad',difficulty:'Inicial',image:'/static/assets/allen-cybersecurity.svg',xp:70,achievement:'Defensor digital',
  description:'Protege una cuenta y un equipo tomando decisiones seguras.',
  steps:[
   {title:'Contraseña fuerte',text:'¿Cuál práctica es mejor?',options:['Reutilizar una contraseña fácil','Usar una frase larga y única','Compartirla con un compañero'],correct:1,hint:'Piensa en longitud y reutilización.',explanation:'Una frase larga y única reduce el riesgo de reutilización y ataques por adivinación.'},
   {title:'Segundo factor',text:'¿Para qué sirve MFA?',options:['Acelerar Internet','Añadir otra comprobación de identidad','Crear copias de seguridad'],correct:1,hint:'No depende solo de saber la contraseña.',explanation:'MFA añade una barrera adicional si la contraseña se filtra.'},
   {title:'Mensaje sospechoso',text:'Un correo urgente pide iniciar sesión desde un enlace inesperado. ¿Qué haces?',options:['Abrirlo enseguida','Verificar por un canal conocido antes de actuar','Reenviarlo a todos'],correct:1,hint:'La urgencia puede usarse para presionarte.',explanation:'Verificar remitente, dominio y contexto por un canal conocido ayuda a detectar phishing.'},
   {title:'Recuperación',text:'¿Qué medida ayuda si un archivo importante se daña?',options:['Tener una copia de seguridad probada','Desactivar actualizaciones','Usar la misma contraseña'],correct:0,hint:'Piensa en recuperar el dato.',explanation:'Un backup útil debe existir, estar actualizado y poder restaurarse.'}
  ]
 },
 {
  id:'hidden-bug',title:'El bug escondido',subject:'Programación',difficulty:'Inicial',image:'/static/assets/allen-coding.svg',xp:70,achievement:'Aprendiz de Python',
  description:'Lee código corto, encuentra el problema y entiende por qué ocurre.',
  steps:[
   {title:'Variable',text:'Código: puntos = 10; puntos = puntos + 5. ¿Cuánto vale puntos?',options:['5','10','15'],correct:2,hint:'Usa primero el valor anterior.',explanation:'10 + 5 produce 15 y el resultado vuelve a guardarse en puntos.'},
   {title:'Condición',text:'Si edad = 18, ¿qué expresión comprueba que puede ser 18 o mayor?',options:['edad > 18','edad >= 18','edad =< 18'],correct:1,hint:'Necesitas incluir el valor 18.',explanation:'>= significa mayor o igual.'},
   {title:'Bucle',text:'¿Qué estructura repetiría una acción por cada elemento de una lista?',options:['for','if','return'],correct:0,hint:'Una de estas recorre elementos.',explanation:'for permite iterar sobre una colección.'},
   {title:'Función',text:'¿Para qué sirve una función?',options:['Agrupar lógica reutilizable','Cambiar el sistema operativo','Aumentar la RAM'],correct:0,hint:'Piensa en reutilizar pasos.',explanation:'Una función encapsula instrucciones para llamarlas cuando se necesiten.'}
  ]
 },
 {
  id:'ai-lab',title:'Laboratorio de IA',subject:'IA',difficulty:'Intermedio',image:'/static/assets/allen-thinking.svg',xp:80,achievement:'Explorador de IA',
  description:'Explora qué ocurre entre tu pregunta y la respuesta de un modelo local.',
  steps:[
   {title:'Tokens',text:'¿Qué es un token en un modelo de lenguaje?',options:['Una unidad de texto que procesa el modelo','Una contraseña obligatoria','Una imagen completa'],correct:0,hint:'El modelo no procesa siempre palabras completas.',explanation:'Los tokens son unidades de texto usadas para representar la entrada y la salida.'},
   {title:'Inferencia',text:'¿Qué describe mejor la inferencia?',options:['Usar un modelo ya entrenado para producir una salida','Comprar hardware','Crear una cuenta'],correct:0,hint:'Ocurre cuando haces una consulta.',explanation:'Inferencia es ejecutar el modelo con una entrada para obtener una respuesta.'},
   {title:'Alucinaciones',text:'Si una IA afirma un dato importante, ¿qué conviene hacer?',options:['Creerlo siempre','Verificarlo con una fuente confiable','Borrarlo sin leer'],correct:1,hint:'Los modelos pueden equivocarse.',explanation:'La verificación es esencial cuando la exactitud importa.'},
   {title:'Privacidad local',text:'¿Qué ventaja aporta ejecutar un modelo en tu equipo?',options:['Puede reducir el envío de contenido a servicios externos','Garantiza que nunca se equivoca','Elimina la necesidad de actualizaciones'],correct:0,hint:'Piensa en dónde viajan tus datos.',explanation:'Un modelo local puede procesar contenido sin mandarlo a una nube, según la configuración.'}
  ]
 },
 {
  id:'science-expedition',title:'Expedición científica',subject:'Ciencias',difficulty:'Inicial',image:'/static/assets/allen-science.svg',xp:70,achievement:'Pensador crítico',
  description:'Convierte una curiosidad en una pregunta que pueda ponerse a prueba.',
  steps:[
   {title:'Hipótesis',text:'¿Qué característica necesita una hipótesis científica?',options:['Poder ponerse a prueba','Ser siempre cierta','No depender de evidencia'],correct:0,hint:'Debe existir una forma de comprobarla.',explanation:'Una hipótesis útil permite recoger evidencia que la apoye o contradiga.'},
   {title:'Variable',text:'Si pruebas si la luz afecta el crecimiento, ¿qué cambias deliberadamente?',options:['La cantidad de luz','El nombre de la planta','La fecha escrita en la libreta'],correct:0,hint:'Es la variable independiente.',explanation:'La cantidad de luz es la variable que manipulas para observar su efecto.'},
   {title:'Evidencia',text:'¿Qué resultado es más útil?',options:['Una medición registrada de forma consistente','Una opinión sin datos','Un rumor'],correct:0,hint:'Busca algo observable y registrable.',explanation:'Las mediciones repetibles permiten comparar resultados.'},
   {title:'Conclusión',text:'Si los datos no apoyan la hipótesis, ¿qué corresponde?',options:['Cambiar o rechazar la hipótesis','Ocultar los datos','Inventar otro resultado'],correct:0,hint:'La evidencia guía la conclusión.',explanation:'Una hipótesis puede modificarse cuando la evidencia no la respalda.'}
  ]
 }
];

export const achievements=[
 {id:'first-step',name:'Primer paso',icon:'01',test:p=>(p.lessons||0)+(p.quizzes||0)>0},
 {id:'first-quiz',name:'Primer quiz',icon:'02',test:p=>(p.quizzes||0)>=1},
 {id:'curious',name:'Mente curiosa',icon:'03',test:p=>(p.xp||0)>=100},
 {id:'explorer',name:'Explorador digital',icon:'04',test:p=>(p.subjects||[]).length>=3},
 {id:'cards',name:'Memoria en marcha',icon:'05',test:p=>(p.cards||0)>=5},
 {id:'steady',name:'Constancia',icon:'06',test:p=>(p.streak||0)>=5},
 {id:'xp500',name:'500 XP',icon:'07',test:p=>(p.xp||0)>=500},
 {id:'quiz-perfect',name:'Quiz perfecto',icon:'08',test:(p,r)=>(r||[]).some(x=>x.result?.total>0&&x.result.score===x.result.total)}
];

function missionKey(profileId){return 'allen-v2-missions-'+profileId;}
export function missionState(profileId){
 try{return JSON.parse(localStorage.getItem(missionKey(profileId))||'{"completed":[],"points":0,"current":null}');}
 catch{return {completed:[],points:0,current:null};}
}
function saveMissionState(profileId,state){localStorage.setItem(missionKey(profileId),JSON.stringify(state));}

function missionCard(m,state,index){
 const done=state.completed.includes(m.id),current=state.current===m.id||(!state.current&&!done&&index===0);
 return `<button class="v2-mission-card ${done?'done':current?'current':''}" data-mission="${esc(m.id)}">
   <img src="${m.image}" alt="">
   <span class="v2-mission-status">${done?'Completada':current?'Disponible':'Explorar'}</span>
   <span class="eyebrow">${esc(m.subject)} · ${esc(m.difficulty)}</span>
   <strong>${esc(m.title)}</strong>
   <span>${esc(m.description)}</span>
   <small>+${m.xp} puntos de misión</small>
  </button>`;
}

export function adventurePage(profileId){
 const state=missionState(profileId);
 return `<div class="v2-page-heading">
   <div><span class="eyebrow">APRENDE HACIENDO</span><h1>Aventura con Allen</h1><p>Misiones cortas que convierten una idea en decisiones, práctica y feedback.</p></div>
   <div class="v2-score-card"><strong>${state.points}</strong><span>puntos de misión</span></div>
  </div>
  <section class="v2-adventure-hero">
   <div><span class="eyebrow">TU MAPA</span><h2>Elige una misión y avanza a tu ritmo.</h2><p>No hay vidas, rankings ni presión. Si fallas, Allen explica y puedes volver a intentarlo.</p></div>
   <img src="/static/assets/allen-adventure.svg" alt="Allen recorriendo un mapa de aprendizaje">
  </section>
  <div class="v2-mission-map" aria-label="Mapa de misiones">
   ${missions.map((m,i)=>`<span class="${state.completed.includes(m.id)?'done':state.current===m.id?'current':''}"><b>${i+1}</b>${esc(m.subject)}</span>`).join('<i aria-hidden="true">→</i>')}
  </div>
  <section class="v2-mission-grid">${missions.map((m,i)=>missionCard(m,state,i)).join('')}</section>
  <section id="adventure-stage" class="v2-adventure-stage" aria-live="polite"></section>`;
}

function renderMissionStage(mission,index=0,feedback=''){
 const step=mission.steps[index];
 if(!step)return '';
 return `<div class="v2-stage-card" data-mission-active="${esc(mission.id)}" data-step="${index}">
   <div class="v2-stage-top"><div><span class="eyebrow">${esc(mission.subject)} · PASO ${index+1}/${mission.steps.length}</span><h2>${esc(step.title)}</h2></div><button data-mission-close aria-label="Cerrar misión">Cerrar</button></div>
   <progress value="${index+1}" max="${mission.steps.length}" aria-label="Progreso de misión"></progress>
   <p class="v2-stage-question">${esc(step.text)}</p>
   <div class="v2-stage-options">${step.options.map((o,i)=>`<button data-mission-answer="${i}">${esc(o)}</button>`).join('')}</div>
   <details><summary>Necesito una pista</summary><p>${esc(step.hint)}</p></details>
   <div class="v2-stage-feedback">${feedback}</div>
  </div>`;
}

export function bindAdventure(root,profileId,{onComplete=()=>{},announce=()=>{}}={}){
 const stage=root.querySelector('#adventure-stage');
 root.querySelectorAll('[data-mission]').forEach(button=>button.addEventListener('click',()=>{
  const mission=missions.find(m=>m.id===button.dataset.mission);if(!mission)return;
  const state=missionState(profileId);state.current=mission.id;saveMissionState(profileId,state);
  stage.innerHTML=renderMissionStage(mission,0);
  stage.scrollIntoView({behavior:'smooth',block:'start'});
 }));
 stage?.addEventListener('click',event=>{
  const close=event.target.closest('[data-mission-close]');
  if(close){stage.innerHTML='';return;}
  const answer=event.target.closest('[data-mission-answer]');
  if(!answer)return;
  const card=stage.querySelector('[data-mission-active]');
  const mission=missions.find(m=>m.id===card?.dataset.missionActive);if(!mission)return;
  const index=Number(card.dataset.step),step=mission.steps[index],choice=Number(answer.dataset.missionAnswer);
  if(choice!==step.correct){
   stage.querySelector('.v2-stage-feedback').innerHTML=`<div class="v2-feedback retry"><strong>Casi.</strong><p>${esc(step.explanation)}</p><p>Puedes intentarlo otra vez.</p></div>`;
   announce('Respuesta incorrecta. Revisa la explicación e inténtalo otra vez.');return;
  }
  if(index<mission.steps.length-1){
   stage.innerHTML=renderMissionStage(mission,index+1,`<div class="v2-feedback correct"><strong>Bien pensado.</strong><p>${esc(step.explanation)}</p></div>`);
   announce('Respuesta correcta. Siguiente paso.');return;
  }
  const state=missionState(profileId);
  if(!state.completed.includes(mission.id)){state.completed.push(mission.id);state.points+=mission.xp;}
  const next=missions.find(m=>!state.completed.includes(m.id));state.current=next?.id||null;saveMissionState(profileId,state);
  stage.innerHTML=`<div class="v2-mission-complete">
    <img src="/static/assets/allen-achievement.svg" alt="Allen celebrando el logro">
    <div><span class="eyebrow">MISIÓN COMPLETADA</span><h2>${esc(mission.title)}</h2><p>${esc(step.explanation)}</p><p><strong>+${mission.xp} puntos de misión</strong> · Logro: ${esc(mission.achievement)}</p><button data-mission-finish>Volver al mapa</button></div>
   </div>`;
  stage.querySelector('[data-mission-finish]').onclick=()=>onComplete();
  announce('Misión completada.');
 });
}

export function homeV2Extras({progress={},memory={},recent=[]}={}){
 const strongest=(progress.subjects||[]).slice().sort((a,b)=>(b.seconds||0)-(a.seconds||0))[0];
 const recentTitle=recent?.[0]?.title||memory?.last_topic||'Tu próxima curiosidad';
 const suggestion=strongest?.subject?recommendFor(strongest.subject):'Prueba una misión corta y convierte una idea en práctica.';
 return `<section class="v2-home-strip">
   <article><span>HOY</span><strong>${progress.minutes||0} min</strong><small>de estudio activo</small></article>
   <article><span>PROGRESO</span><strong>${progress.xp||0} XP</strong><small>sin rankings ni comparaciones</small></article>
   <article><span>CONTINÚA</span><strong>${esc(recentTitle)}</strong><small>retoma desde donde estabas</small></article>
  </section>
  <section class="v2-home-grid">
   <article class="v2-home-feature">
    <div><span class="eyebrow">PRUEBA ALGO HOY</span><h2>${esc(suggestion)}</h2><p>Allen adapta la práctica a lo que ya vienes explorando.</p><button data-page="Aventura">Empezar una misión</button></div>
    <img src="/static/assets/allen-study.svg" alt="Allen estudiando">
   </article>
   <article class="v2-home-local">
    <span class="eyebrow">LOCAL POR DISEÑO</span><h2>Tu aprendizaje puede quedarse en tu equipo.</h2><p>Perfiles, progreso, biblioteca y conversaciones se gestionan localmente según tus preferencias.</p><button data-page="Privacidad">Cómo cuidamos tus datos</button>
   </article>
  </section>
  <section class="v2-path-panel"><div><span class="eyebrow">MÉTODO ALLEN</span><h2>Descubre → practica → comprueba → domina.</h2><p>No se trata solo de leer una respuesta. Cada paso busca que hagas algo con la idea.</p></div><div class="v2-path-steps"><span><b>1</b>Descubre</span><span><b>2</b>Practica</span><span><b>3</b>Comprueba</span><span><b>4</b>Domina</span></div></section>`;
}

function recommendFor(subject){
 const key=String(subject||'').toLowerCase();
 if(key.includes('program'))return 'Convierte una explicación de Python en un reto corto.';
 if(key.includes('red'))return 'Repasa máscaras y prueba la misión “Recupera la red”.';
 if(key.includes('mat'))return 'Haz un ejercicio y explica por qué funciona el resultado.';
 if(key.includes('ingl'))return 'Practica cinco frases y crea una tarjeta con la más difícil.';
 if(key.includes('ia'))return 'Compara entrenamiento e inferencia con un ejemplo propio.';
 if(key.includes('ciber'))return 'Haz un repaso de MFA, phishing y copias de seguridad.';
 return 'Elige un tema reciente y conviértelo en una pregunta de práctica.';
}

export function chatV2Bar({subject='General',level='Tu nivel',mode='Tutor'}={}){
 return `<div class="v2-chat-context"><span><small>Tema</small><b>${esc(subject)}</b></span><span><small>Nivel</small><b>${esc(level)}</b></span><span><small>Modo</small><b>${esc(mode)}</b></span></div>
 <div class="v2-chat-actions" aria-label="Acciones de aprendizaje">
  ${[['easy','Explícamelo más fácil'],['example','Ponme un ejemplo'],['question','Hazme una pregunta'],['recall','Hazme recordar sin mirar'],['interleave','Mézclame ejercicios'],['elaborate','Pregúntame por qué'],['summary','Resume']].map(([k,l])=>`<button type="button" data-v2-chat="${k}">${l}</button>`).join('')}
 </div>`;
}
export const chatActionText={
 easy:'Explícame lo anterior de una forma más sencilla, sin perder la idea importante.',
 example:'Ponme un ejemplo concreto de lo anterior y explícame cada paso.',
 question:'Hazme una pregunta para comprobar si entendí. No me des la respuesta todavía.',
 challenge:'Ponme un reto corto relacionado con lo que estamos viendo. Dame una pista solo si la pido.',
 recall:'Comprueba mi memoria sobre lo anterior: hazme una sola pregunta sin pistas ni respuesta. Espera a que yo conteste antes de corregirme.',
 interleave:'Dame una práctica que mezcle lo que estamos viendo con otro tipo de problema relacionado, para que yo tenga que decidir qué estrategia usar.',
 elaborate:'Hazme una pregunta de “por qué” o “cómo lo sé” sobre lo anterior. Espera mi explicación y luego dame feedback.',
 summary:'Resume lo anterior en puntos clave y termina con una pregunta de repaso.'
};

export function achievementPanel(progress={},results=[]){
 const cards=achievements.map(a=>{const unlocked=a.test(progress,results);return `<article class="v2-achievement ${unlocked?'unlocked':'locked'}"><b>${a.icon}</b><span><strong>${esc(a.name)}</strong><small>${unlocked?'Desbloqueado':'Sigue aprendiendo para descubrirlo'}</small></span></article>`;}).join('');
 const subjects=(progress.subjects||[]).slice().sort((a,b)=>(b.seconds||0)-(a.seconds||0));
 const maxSubject=Math.max(1,...subjects.map(s=>s.seconds||0));
 const subjectBars=subjects.length?subjects.slice(0,6).map(s=>`<div class="v2-subject-bar"><div class="row spaced"><span>${esc(s.subject)}</span><small>${Math.max(1,Math.round((s.seconds||0)/60))} min</small></div><div><i style="width:${Math.max(6,Math.round((s.seconds||0)/maxSubject*100))}%"></i></div></div>`).join(''):'<p class="muted">Cuando estudies, aquí aparecerán tus temas más explorados.</p>';
 const week=progress.week||[];
 const maxDay=Math.max(1,...week.map(d=>d.seconds||0));
 const labels=['D','L','M','X','J','V','S'];
 const weekBars=week.length?week.map(d=>{const day=new Date(d.day+'T12:00:00');const height=Math.max(7,Math.round((d.seconds||0)/maxDay*100));return `<div class="v2-week-day" title="${Math.round((d.seconds||0)/60)} min"><div><i style="height:${height}%"></i></div><span>${labels[day.getDay()]}</span></div>`;}).join(''):'';
 const rec=subjects.length?recommendFor(subjects[0]?.subject):'Empieza con una pregunta y completa tu primer reto.';
 return `<section class="v2-progress-section"><div class="section-head"><h2>Tus logros</h2><p>Reconocen constancia y exploración, no competencia.</p></div><div class="v2-achievements">${cards}</div></section>
 <section class="v2-progress-insights">
  <article><span class="eyebrow">TEMAS EXPLORADOS</span><h2>En qué has invertido tu tiempo</h2>${subjectBars}</article>
  <article><span class="eyebrow">ÚLTIMOS 7 DÍAS</span><h2>Actividad local</h2><div class="v2-week-chart">${weekBars}</div><p class="muted">Solo muestra tiempo activo registrado en este dispositivo.</p></article>
 </section>
 <section class="v2-recommendation"><img src="/static/assets/allen-thinking.svg" alt=""><div><span class="eyebrow">SIGUIENTE PASO</span><h2>${esc(rec)}</h2><p>Es una sugerencia local basada en tu actividad agregada.</p></div></section>`;
}

export function studyMethodPage(){
 const methods=[
  ['Recuperación activa','Intenta recordar o aplicar antes de volver a mirar la respuesta.','Haz una pregunta sin mostrar la solución y responde con tus palabras.'],
  ['Práctica espaciada','Vuelve a un concepto en distintos momentos en lugar de concentrarlo todo en una sola sesión.','Usa las tarjetas de Allen y repasa cuando vuelvan a aparecer.'],
  ['Intercalado','Alterna tipos de problemas relacionados para elegir la estrategia correcta.','Mezcla fracciones, porcentajes y ecuaciones en una práctica posterior.'],
  ['Elaboración','Explica por qué funciona una idea y conéctala con algo que ya conoces.','Responde “¿por qué?” o “¿cómo lo sabes?” después de resolver.'],
  ['Ejemplos concretos','Empieza con un caso específico antes de ir a la regla general.','Allen muestra un ejemplo y luego cambia los números o el contexto.'],
  ['Doble representación','Combina palabras con una estructura visual útil.','Usa tabla, esquema, pasos o mapa simple cuando el tema lo permita.']
 ];
 return `<div class="v2-page-heading"><div><span class="eyebrow">MÉTODO ALLEN</span><h1>Aprender no es solo leer una respuesta.</h1><p>Allen combina técnicas de estudio con evidencia para ayudarte a recordar, entender y aplicar lo que aprendes.</p></div></div>
 <section class="v2-adventure-hero">
  <div><span class="eyebrow">FLUJO DE APRENDIZAJE</span><h2>Descubre → recupera → explica → mezcla → representa → revisa.</h2><p>No se usan todos los pasos en cada turno. Allen elige los que tengan sentido para tu nivel y la tarea.</p><button data-page="Tutor">Probar el método con Allen</button></div>
  <img src="/static/assets/allen-study.svg" alt="Allen estudiando con su método de aprendizaje">
 </section>
 <section class="v2-method-grid">${methods.map(([name,why,example],i)=>`<article><b>${i+1}</b><div><h2>${esc(name)}</h2><p>${esc(why)}</p><small>${esc(example)}</small></div></article>`).join('')}</section>
 <section class="v2-cornell">
  <div><span class="eyebrow">PARA APUNTES</span><h2>Allen también puede ayudarte a estudiar con notas tipo Cornell.</h2><p>Cuando pegues apuntes, puede separar ideas principales, crear preguntas de recuperación, resumir lo esencial y ayudarte a revisarlo después.</p></div>
  <div class="v2-cornell-sheet"><aside><strong>Preguntas / pistas</strong><span>¿Qué significa?</span><span>¿Por qué importa?</span><span>¿Cómo se aplica?</span></aside><main><strong>Notas principales</strong><p>Conceptos, ejemplos, relaciones y datos importantes.</p><footer><b>Resumen:</b> la idea central en pocas líneas.</footer></main></div>
 </section>
 <section class="panel"><span class="eyebrow">BASE DEL MÉTODO</span><h2>Qué prioriza Allen</h2><p>La prioridad está en práctica de recuperación y estudio espaciado. Intercalado, autoexplicación, ejemplos concretos y representaciones visuales se usan cuando aportan valor.</p><p class="muted">Referencias de diseño pedagógico: Cornell Learning Strategies Center; Dunlosky et al. (2013). Allen adapta estas ideas a una experiencia local y offline.</p></section>`;
}

export function libraryVisual(subject='General'){
 const s=String(subject||'').toLowerCase();
 let image='/static/assets/allen-library.svg';
 if(s.includes('program')||s.includes('python'))image='/static/assets/allen-coding.svg';
 else if(s.includes('red'))image='/static/assets/allen-networking.svg';
 else if(s.includes('ciber'))image='/static/assets/allen-cybersecurity.svg';
 else if(s.includes('mat'))image='/static/assets/allen-math.svg';
 else if(s.includes('cien'))image='/static/assets/allen-science.svg';
 return image;
}
