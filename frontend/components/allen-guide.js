const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const STATES={
 welcome:{image:'/static/assets/allen-brand.svg',eyebrow:'HOLA, SOY ALLEN',title:'Yo te guío. Tú solo empieza.'},
 guide:{image:'/static/assets/allen-guide.svg',eyebrow:'SIGUIENTE PASO',title:'Vamos paso a paso.'},
 teaching:{image:'/static/assets/allen-teaching-official.svg',eyebrow:'APRENDEMOS JUNTOS',title:'Primero entendamos esta idea.'},
 reading:{image:'/static/assets/allen-reading-official.svg',eyebrow:'LECTURA GUIADA',title:'Busquemos la idea importante.'},
 progress:{image:'/static/assets/allen-progress-official.svg',eyebrow:'TU AVANCE',title:'Mira cuánto has construido.'},
 celebrate:{image:'/static/assets/allen-celebrate-official.svg',eyebrow:'BIEN HECHO',title:'Ya superaste esta parte.'},
 course:{image:'/static/assets/allen-course-official.svg',eyebrow:'RUTA DE APRENDIZAJE',title:'Yo te acompaño por este curso.'}
};

export function allenGuide(kind='guide',message='',actions=[]){
 const state=STATES[kind]||STATES.guide;
 return `<section class="allen-guide-card allen-guide-${kind}">
   <div class="allen-guide-visual"><img src="${state.image}" alt="Allen acompañando al estudiante"></div>
   <div class="allen-guide-copy"><span class="eyebrow">${state.eyebrow}</span><h2>${esc(state.title)}</h2><p>${esc(message||'Cuando estés listo, seguimos juntos.')}</p>
   ${actions.length?`<div class="row allen-guide-actions">${actions.map(a=>`<button ${a.primary?'class="primary"':''} data-page="${esc(a.page||'')}" ${a.action?`data-allen-action="${esc(a.action)}"`:''}>${esc(a.label)}</button>`).join('')}</div>`:''}
   </div>
  </section>`;
}

export function learningStepRail(current=0,labels=['Descubre','Ejemplo','Recupera','Practica','Comprueba','Revisa']){
 return `<div class="allen-step-rail" aria-label="Ruta de aprendizaje">${labels.map((label,i)=>`<div class="${i<current?'done':i===current?'current':''}"><b>${i+1}</b><span>${esc(label)}</span></div>`).join('')}</div>`;
}
