import {escapeHTML as esc} from './markdown.js';
export function icon(name,size=24){return `<svg class="icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" role="presentation"><use href="/static/assets/icons.svg#${name}"></use></svg>`;}

const mascotLabels={
 happy:'te acompaña',hello:'te saluda',idle:'te acompaña',thinking:'está pensando',curious:'explora contigo',focused:'está concentrado',
 listening:'te escucha',speaking:'está hablando',teaching:'te enseña',reading:'está leyendo',studying:'está estudiando',
 coding:'programa contigo',cybersecurity:'practica seguridad digital contigo',networking:'explora redes contigo',science:'investiga contigo',
 math:'resuelve matemáticas contigo',english:'practica inglés contigo',hint:'te da una pista',challenge:'te propone un reto',
 success:'celebra una respuesta',error:'necesita intentarlo de nuevo',confused:'piensa contigo',celebrating:'celebra tu esfuerzo',
 victory:'celebra la misión',proud:'está orgulloso de tu avance',sleeping:'está despertando',explorer:'explora contigo'
};
function mascotAccent(state){
 const accents={
  listening:'<g fill="none" stroke="#55796f" stroke-width="6"><path d="M43 77a58 58 0 0 1 116 0"/><path d="M43 75v23m116-23v23"/></g>',
  thinking:'<g fill="#e8b957"><circle cx="169" cy="38" r="14"/><circle cx="154" cy="55" r="6"/><circle cx="147" cy="66" r="3"/></g>',
  curious:'<g fill="#e8b957"><path d="m164 25 4 9 10 1-8 7 2 10-8-5-9 5 2-10-8-7 11-1z"/></g>',
  focused:'<path d="M68 69q12-8 24-1m16 0q12-7 24 1" fill="none" stroke="#533827" stroke-width="4" stroke-linecap="round"/>',
  teaching:'<path d="m157 33 5-12 5 12 12 5-12 5-5 12-5-12-12-5z" fill="#e8b957"/>',
  coding:'<rect x="128" y="136" width="66" height="40" rx="5" fill="#55796f" stroke="#3f5f56" stroke-width="3"/><path d="m147 148-8 7 8 7m16-14 8 7-8 7" fill="none" stroke="#fff8ed" stroke-width="3"/>',
  cybersecurity:'<path d="M166 129l24 9v19c0 17-12 28-24 34-12-6-24-17-24-34v-19z" fill="#55796f" stroke="#3f5f56" stroke-width="3"/><path d="m153 157 8 8 17-22" fill="none" stroke="#fff8ed" stroke-width="4"/>',
  networking:'<g fill="#fff8ed" stroke="#55796f" stroke-width="3"><rect x="135" y="136" width="26" height="20" rx="4"/><rect x="171" y="136" width="26" height="20" rx="4"/><rect x="153" y="169" width="26" height="20" rx="4"/></g><path d="M161 146h10m-23 10 17 13m19-13-18 13" stroke="#55796f" stroke-width="3"/>',
  science:'<path d="M152 130v20l-17 30c-5 9 2 19 12 19h42c10 0 17-10 12-19l-17-30v-20" fill="#fff8ed" stroke="#55796f" stroke-width="3"/><path d="M143 177h50" stroke="#e8b957" stroke-width="4"/>',
  math:'<rect x="139" y="132" width="48" height="56" rx="5" fill="#fff8ed" stroke="#735a40" stroke-width="3"/><text x="163" y="157" text-anchor="middle" font-size="15" font-family="Segoe UI,Arial" font-weight="800" fill="#c8662a">3/4</text><path d="M148 169h29" stroke="#c8662a" stroke-width="3"/>',
  english:'<path d="M138 140q15-7 29 0 13-7 25 0v34q-12-5-25 2-14-7-29-2z" fill="#55796f" stroke="#3f5f56" stroke-width="3"/><text x="165" y="160" text-anchor="middle" font-size="12" font-family="Segoe UI,Arial" fill="#fff">ABC</text>',
  hint:'<circle cx="169" cy="45" r="17" fill="#ffd978" stroke="#ad7627" stroke-width="3"/><path d="M163 63h12m-10 6h8" stroke="#ad7627" stroke-width="4"/>',
  challenge:'<path d="M163 119V55m1 1 27 8-27 12" fill="#e8b957" stroke="#94622e" stroke-width="4"/>',
  success:'<path d="m149 38 10 10 22-26" fill="none" stroke="#55796f" stroke-width="7"/>',
  celebrating:'<g fill="#e8b957"><path d="m20 28 3 8 9 1-7 6 2 9-7-5-8 5 2-9-7-6 10-1z"/><path d="m176 20 3 8 9 1-7 6 2 9-7-5-8 5 2-9-7-6 10-1z"/></g>',
  victory:'<path d="M151 35h34v25q-17 20-34 0z" fill="#ffd978" stroke="#a66c1e" stroke-width="3"/><path d="M151 40h-10q-2 19 13 20m31-20h10q2 19-13 20M168 78v16m-12 0h24" fill="none" stroke="#a66c1e" stroke-width="4"/>',
  proud:'<path d="m154 33 8 16 18 3-13 12 3 18-16-8-16 8 3-18-13-12 18-3z" fill="#e8b957" stroke="#a66c1e" stroke-width="2"/>',
  sleeping:'<path d="M164 28h18l-18 18h18" fill="none" stroke="#8b735c" stroke-width="3"/>',
  explorer:'<path d="M53 39q48-31 94 0l-10 11H63z" fill="#a65a24" stroke="#674024" stroke-width="3"/><path d="M71 27q30-15 58 0" fill="none" stroke="#e8b957" stroke-width="8"/>',
  error:'<path d="M169 22v14m0 6v1" stroke="#a55d32" stroke-width="5" stroke-linecap="round"/>'
 };
 return accents[state]||'';
}
export function AllenMascot(state='happy',size='medium'){
 if(!mascotLabels[state])state='happy';
 const sleeping=state==='sleeping',thinking=['thinking','error','confused'].includes(state);
 const reading=['reading','studying','teaching'].includes(state);
 const mouth=state==='speaking'?'M90 105q11 26 22 0z':thinking?'M91 110q10 -7 20 0':'M85 104q16 20 32 0';
 return `<svg class="allen-mascot ${state} ${size}" viewBox="0 0 200 200" role="img" aria-label="Allen ${esc(mascotLabels[state])}">
 <ellipse cx="100" cy="182" rx="58" ry="9" fill="#ead8bd"/>
 <path d="M55 166 Q27 150 35 130 Q41 116 50 130" fill="none" stroke="#d86e23" stroke-width="13" stroke-linecap="round"/>
 <ellipse cx="101" cy="146" rx="45" ry="36" fill="#ed852e"/><ellipse cx="101" cy="148" rx="28" ry="26" fill="#ffdc9c"/>
 <circle cx="40" cy="80" r="23" fill="#dd7226"/><circle cx="160" cy="80" r="23" fill="#dd7226"/><circle cx="40" cy="80" r="14" fill="#ffce92"/><circle cx="160" cy="80" r="14" fill="#ffce92"/>
 <path d="M46 81 Q42 30 93 26 Q93 14 113 17 L107 27 Q158 31 155 83 Q156 131 101 135 Q44 133 46 81" fill="#ef8b30"/>
 <path d="M57 83 Q55 47 78 47 Q94 46 101 59 Q110 46 125 48 Q147 52 143 83 Q153 113 122 122 Q102 131 78 122 Q48 115 57 83" fill="#ffe0a8"/>
 ${sleeping?'<path d="M72 80q9 8 18 0m23 0q9 8 18 0" fill="none" stroke="#533827" stroke-width="4" stroke-linecap="round"/>':'<ellipse cx="81" cy="80" rx="5" ry="7"/><ellipse cx="120" cy="80" rx="5" ry="7"/>'}
 <g fill="none" stroke="#533827" stroke-width="4" stroke-linecap="round"><path d="M96 94q5 5 10 0"/><path d="${mouth}"/></g>
 <ellipse cx="66" cy="98" rx="8" ry="4" fill="#f7b077"/><ellipse cx="135" cy="98" rx="8" ry="4" fill="#f7b077"/>
 ${reading?'<path d="M62 141q20 -8 39 2q19 -10 39 -2v32q-20 -5 -39 3q-19 -8 -39 -3z" fill="#719987" stroke="#476e5c" stroke-width="3"/><path d="M101 143v31" stroke="#fff8ed" stroke-width="3"/>':'<path class="mascot-hand" d="M139 138q33 -17 28 -47" fill="none" stroke="#ed852e" stroke-width="16" stroke-linecap="round"/>'}
 ${mascotAccent(state)}
 </svg>`;
}
export function AllenLoader(text='Allen está pensando…'){return `<div class="allen-loader" role="status">${AllenMascot('thinking','small')}<span>${esc(text)}<span class="loading-dots"> · · ·</span></span></div>`;}
export function FeatureCard(page,name,title,description){return `<button class="module-card" data-page="${esc(page)}"><span class="module-icon">${icon(name,44)}</span><b>${esc(title)}</b><p>${esc(description)}</p><span class="card-action">Empezar ${icon('arrow-right',18)}</span></button>`;}
export function EmptyState(title,text,state='reading'){return `<div class="empty">${AllenMascot(state)}<h2>${esc(title)}</h2><p>${esc(text)}</p></div>`;}
