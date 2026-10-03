import {icon} from './components/ui.js';
import {AllenMascot} from './components/fair-mascot.js';
import {escapeHTML as esc} from './components/markdown.js';
import {ZONES} from './game-adventure.js';

const WORLD_ZONES=[
 {name:'Laboratorio de Allen',detail:'Descubre cómo funciona una IA local.',icon:'flask-conical',destination:'how'},
 {name:'Biblioteca',detail:'Una idea nueva en pocos pasos.',icon:'book-open',destination:'learn'},
 {name:'Zona Matemática',detail:'Fracciones, números y ejemplos.',icon:'calculator',lesson:'Matemáticas'},
 {name:'Sala de Idiomas',detail:'Aprende una palabra en inglés.',icon:'languages',lesson:'Inglés'},
 {name:'Zona de Código',detail:'Dale instrucciones a una computadora.',icon:'code',lesson:'Programación'},
 {name:'Isla de Lógica',detail:'Encuentra patrones y resuelve retos.',icon:'compass',destination:'game'},
 {name:'Centro de IA',detail:'Explora la tecnología detrás de Allen.',icon:'sparkles',lesson:'IA'}
];
export const WHEEL_CATEGORIES=['Matemáticas','Inglés','Programación','Lógica','IA','Tecnología'];
export const WHEEL_QUESTIONS={...Object.fromEntries(ZONES.slice(0,5).map(z=>[z.name,z])),Tecnología:{name:'Tecnología',place:'Zona tecnológica',item:'Sello tecnológico',icon:'lightbulb',pose:'ai',question:'¿Para qué sirve una dirección IP?',options:['Dirigir datos a un dispositivo','Cargar la batería','Dibujar imágenes'],correct:0,explanation:'Una dirección IP ayuda a dirigir datos hacia un dispositivo en una red.'}};
const MISSIONS=[
 {id:'question',title:'Haz una pregunta a Allen',detail:'Explora algo que te dé curiosidad.',target:1,metric:p=>p.questions,icon:'message-circle'},
 {id:'lesson',title:'Aprende algo nuevo',detail:'Completa una microlección.',target:1,metric:p=>p.lessons,icon:'book-open'},
 {id:'challenge',title:'Completa un reto',detail:'Prueba cualquier desafío.',target:1,metric:p=>p.challenges,icon:'target'},
 {id:'correct',title:'Tres descubrimientos',detail:'Responde tres preguntas correctamente.',target:3,metric:p=>p.correct,icon:'circle-check'},
 {id:'nohint',title:'Sin pistas',detail:'Resuelve una zona sin usar pistas.',target:1,metric:p=>p.noHint,icon:'lightbulb'},
 {id:'offline',title:'Comprueba la IA local',detail:'Haz una pregunta en el desafío sin Internet.',target:1,metric:p=>p.offline,icon:'shield-check'}
];
const ACHIEVEMENTS={first:'Primera pregunta',curious:'Curioso',explorer:'Explorador',quick:'Pensador veloz',offline:'OFFLINE EXPLORER',nohint:'Sin pistas',streak:'Cinco seguidas'};
const BOX_ITEMS=['Gorra exploradora','Lentes de laboratorio','Mochila de ideas','Audífonos de idiomas'];
export const createFairProgress=()=>({activities:0,questions:0,lessons:0,challenges:0,correct:0,streak:0,bestStreak:0,noHint:0,offline:0,categories:[],items:[],achievements:[],boxReady:false,boxOpened:false,surprise:false,areas:[],lastReward:''});
export function recordFairActivity(progress,event,random=Math.random){
 progress.activities++;
 if(event.type==='question')progress.questions++;
 if(event.type==='lesson')progress.lessons++;
 if(event.type==='challenge')progress.challenges++;
 if(event.type==='offline')progress.offline++;
 if(event.type==='correct'){progress.correct++;progress.streak++;progress.bestStreak=Math.max(progress.bestStreak,progress.streak);if(event.noHint)progress.noHint++;}
 if(event.type==='wrong')progress.streak=0;
 if(event.category&&!progress.categories.includes(event.category))progress.categories.push(event.category);
 if(event.area&&!progress.areas.includes(event.area))progress.areas.push(event.area);
 if(event.item&&!progress.items.includes(event.item)){progress.items.push(event.item);progress.lastReward=event.item;}
 const newly=[];
 const award=(id,yes)=>{if(yes&&!progress.achievements.includes(id)){progress.achievements.push(id);newly.push(ACHIEVEMENTS[id]);}};
 award('first',progress.questions>=1);award('curious',progress.questions>=5);award('explorer',progress.categories.length>=3);award('quick',event.quick===true);award('offline',progress.offline>=1);award('nohint',progress.noHint>=1);award('streak',progress.bestStreak>=5);
 if(progress.activities>=3&&!progress.boxOpened)progress.boxReady=true;
 if(progress.activities>=4&&!progress.surprise&&random()<.08)progress.surprise=true;
 return newly;
}
export function openMysteryBox(progress){if(!progress.boxReady||progress.boxOpened)return '';const item=BOX_ITEMS[(progress.activities+progress.correct)%BOX_ITEMS.length];progress.boxOpened=true;progress.boxReady=false;progress.lastReward=item;progress.items.push(item);return item;}
export function progressLevel(progress){const n=progress.activities;return n>=15?'Inventor':n>=10?'Investigador':n>=6?'Aprendiz':n>=3?'Curioso':'Explorador';}
const action=(label,attr,ico,primary=false)=>`<button class="${primary?'primary':''}" ${attr}>${icon(ico,20)}<span>${label}</span></button>`;
export function renderMissionBoard(p){const complete=MISSIONS.filter(m=>m.metric(p)>=m.target).length;return `<section class="world-header">${AllenMascot('challenge','medium')}<div><span class="eyebrow">Misiones opcionales</span><h1>Tu aventura con Allen</h1><p>Elige lo que te dé curiosidad. Puedes aprender a tu ritmo.</p></div></section><div class="world-progress"><div><strong>${progressLevel(p)}</strong><span>Progreso con Allen · ${p.activities} actividades</span></div><div><strong>${complete} / ${MISSIONS.length}</strong><span>misiones completadas</span></div></div><div class="mission-grid">${MISSIONS.map(m=>`<article class="mission-card ${m.metric(p)>=m.target?'done':''}">${icon(m.icon,30)}<div><h2>${m.title}</h2><p>${m.detail}</p><span>${Math.min(m.metric(p),m.target)} / ${m.target} ${m.metric(p)>=m.target?'· completada':''}</span></div></article>`).join('')}</div><div class="world-actions">${action('Explorar el mundo','data-go="world"','map',true)}${action('Mi colección','data-go="collection"','star')}${action('Volver','data-go="home"','arrow-right')}</div>`;}
export function renderWorld(p){return `<section class="world-header">${AllenMascot('explorer','medium')}<div><span class="eyebrow">ALLEN WORLD</span><h1>Explora con Allen</h1><p>Elige una zona. Todas están abiertas para descubrirlas a tu ritmo.</p></div></section><div class="world-map">${WORLD_ZONES.map((z,i)=>`<button class="world-zone ${p.areas.includes(z.name)?'visited':''}" ${z.lesson?`data-world-lesson="${esc(z.lesson)}"`:`data-go="${z.destination}"`}>${icon(z.icon,40)}<span class="world-zone-number">${String(i+1).padStart(2,'0')}</span><strong>${esc(z.name)}</strong><span>${esc(z.detail)}</span><small>${p.areas.includes(z.name)?'Explorada':'Disponible'}</small></button>`).join('')}</div><div class="world-actions">${action('Ver misiones','data-go="missions"','target')}${action('Mi colección','data-go="collection"','star')}${action('Volver','data-go="home"','arrow-right')}</div>`;}
export function renderCollection(p){return `<section class="world-header">${AllenMascot('reading','medium')}<div><span class="eyebrow">Un recuerdo de lo aprendido</span><h1>Mi colección</h1><p>Los objetos y logros de esta visita se limpian al pulsar Nueva persona.</p></div></section><div class="collection-layout"><section class="panel"><h2>Objetos encontrados</h2>${p.items.length?`<div class="collection-items">${p.items.map(item=>`<div>${icon('star',24)}<strong>${esc(item)}</strong></div>`).join('')}</div>`:'<p>Tu colección empieza con una actividad. Allen te acompañará.</p>'}${p.boxReady&&!p.boxOpened?`<div class="mystery-box">${icon('sparkles',35)}<div><strong>Caja misteriosa desbloqueada</strong><span>Una sorpresa virtual por seguir aprendiendo.</span></div>${action('Abrir caja','data-open-box','eye',true)}</div>`:''}</section><section class="panel"><h2>Logros</h2>${p.achievements.length?`<div class="achievement-list">${p.achievements.map(id=>`<span>${icon('circle-check',20)}${esc(ACHIEVEMENTS[id])}</span>`).join('')}</div>`:'<p>Tu primer logro aparecerá aquí cuando participes.</p>'}<p class="muted">Algunos logros son sorpresa.</p></section></div><div class="world-actions">${action('Seguir explorando','data-go="world"','map',true)}${action('Ver misiones','data-go="missions"','target')}${action('Volver','data-go="home"','arrow-right')}</div>`;}
export function renderWheel(category='',spinning=false){return `<section class="wheel-screen"><span class="eyebrow">Un descubrimiento rápido</span><h1>La ruleta de Allen</h1><p>Gira y descubre qué tema te toca. Una pregunta, una explicación y listo.</p><div class="wheel-layout"><div class="allen-wheel ${spinning?'spinning':''}" role="img" aria-label="Ruleta con seis áreas: matemáticas, inglés, programación, lógica, IA y tecnología">${WHEEL_CATEGORIES.map((c,i)=>`<span style="--n:${i}">${esc(c)}</span>`).join('')}</div>${AllenMascot(category?'celebrating':'thinking','large')}</div>${category?`<div class="wheel-picked"><h2>Te tocó ${esc(category)}</h2>${action('Comenzar reto','data-wheel-start','arrow-right',true)}${action('Girar otra vez','data-wheel-spin','rotate-ccw')}</div>`:action(spinning?'Girando…':'Girar','data-wheel-spin '+(spinning?'disabled':''),'rotate-ccw',true)}<div class="world-actions">${action('Volver','data-go="home"','arrow-right')}</div></section>`;}
export function renderWheelQuestion(category,answer=null){const q=WHEEL_QUESTIONS[category];return `<section class="wheel-question"><span class="eyebrow">Reto relámpago · ${esc(category)}</span>${AllenMascot(answer===null?'thinking':answer===q.correct?'celebrating':'teaching','medium')}<h1>${esc(q.question)}</h1><div class="options">${q.options.map((o,i)=>`<button class="${answer!==null&&i===q.correct?'answer-correct':''}" data-wheel-answer="${i}" ${answer!==null?'disabled':''}><span>${'ABC'[i]}</span>${esc(o)}</button>`).join('')}</div>${answer!==null?`<div class="panel wheel-feedback"><h2>${answer===q.correct?'¡Lo tienes!':'Casi. Mira esta idea.'}</h2><p>${esc(q.explanation)}</p>${action('Ver mi resultado','data-wheel-result','arrow-right',true)}</div>`:''}${action('Salir','data-go="wheel"','arrow-right')}</section>`;}
export function renderWheelResult(category,correct){return `<section class="wheel-result">${AllenMascot(correct?'celebrating':'thinking','large')}<span class="eyebrow">Reto completado</span><h1>${correct?'¡Descubrimiento logrado!':'Aprendiste algo nuevo'}</h1><p>Hoy exploraste ${esc(category)} con Allen.</p><div class="world-actions">${action('Otra vuelta','data-go="wheel"','rotate-ccw',true)}${action('Ver misiones','data-go="missions"','target')}${action('Hablar con Allen','data-go="chat"','message-circle')}${action('Volver','data-go="home"','arrow-right')}</div></section>`;}
export function renderNextSteps(){return `<section class="next-steps"><h2>¿Qué quieres hacer ahora?</h2><div>${action('Algo diferente','data-go="wheel"','rotate-ccw')}${action('Seguir aprendiendo','data-go="learn"','book-open')}${action('Explorar con Allen','data-go="world"','map')}</div></section>`;}
