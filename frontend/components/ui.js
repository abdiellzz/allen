import {escapeHTML as esc} from './markdown.js';
export function icon(name,size=24){return `<svg class="icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" role="presentation"><use href="/static/assets/icons.svg#${name}"></use></svg>`;}

const mascotLabels={
 happy:'te acompaña',hello:'te saluda',idle:'te acompaña',thinking:'está pensando',curious:'explora contigo',focused:'está concentrado',
 listening:'te escucha',speaking:'está hablando',teaching:'te enseña',reading:'está leyendo',studying:'está estudiando',
 coding:'programa contigo',cybersecurity:'practica seguridad digital contigo',networking:'explora redes contigo',science:'investiga contigo',
 math:'resuelve matemáticas contigo',english:'practica inglés contigo',hint:'te da una pista',challenge:'te propone un reto',
 success:'celebra una respuesta',error:'necesita intentarlo de nuevo',confused:'piensa contigo',celebrating:'celebra tu esfuerzo',
 victory:'celebra la misión',proud:'está orgulloso de tu avance',sleeping:'está descansando',explorer:'explora contigo'
};
const mascotAssets={
 teaching:'/static/assets/allen-teaching-official.svg',
 reading:'/static/assets/allen-reading-official.svg',
 studying:'/static/assets/allen-reading-official.svg',
 thinking:'/static/assets/allen-thinking-official.svg',
 confused:'/static/assets/allen-thinking-official.svg',
 hint:'/static/assets/allen-checklist-official.svg',
 success:'/static/assets/allen-celebrate-official.svg',
 celebrating:'/static/assets/allen-celebrate-official.svg',
 victory:'/static/assets/allen-celebrate-official.svg',
 proud:'/static/assets/allen-trophy-official.svg',
 explorer:'/static/assets/allen-path-official.svg',
 networking:'/static/assets/allen-course-official.svg',
 cybersecurity:'/static/assets/allen-course-official.svg',
 science:'/static/assets/allen-course-official.svg',
 math:'/static/assets/allen-course-official.svg',
 english:'/static/assets/allen-reading-official.svg',
 coding:'/static/assets/allen-laptop-official.svg',
 error:'/static/assets/allen-guide.svg',
 sleeping:'/static/assets/allen-brand.svg'
};
export function AllenMascot(state='happy',size='medium'){
 if(!mascotLabels[state])state='happy';
 const src=mascotAssets[state]||'/static/assets/allen-brand.svg';
 return `<img class="allen-mascot allen-official ${esc(state)} ${esc(size)}" src="${src}" role="img" alt="Allen ${esc(mascotLabels[state])}">`;
}
export function AllenLoader(text='Allen está pensando…'){return `<div class="allen-loader" role="status">${AllenMascot('thinking','small')}<span>${esc(text)}<span class="loading-dots"> · · ·</span></span></div>`;}
export function FeatureCard(page,name,title,description){return `<button class="module-card" data-page="${esc(page)}"><span class="module-icon">${icon(name,44)}</span><b>${esc(title)}</b><p>${esc(description)}</p><span class="card-action">Empezar ${icon('arrow-right',18)}</span></button>`;}
export function EmptyState(title,text,state='reading'){return `<div class="empty">${AllenMascot(state)}<h2>${esc(title)}</h2><p>${esc(text)}</p></div>`;}
