import {escapeHTML as esc} from './markdown.js';
import {icon} from './ui.js';
export const actions={simplify:'Más fácil',another_example:'Otro ejemplo',step_by_step:'Paso a paso',quiz_me:'Ponme a prueba',different:'Explícalo diferente',dont_understand:'No entiendo',lost:'Estoy perdido',reveal_answer:'Dame la respuesta',summary_learning:'¿Qué aprendí?',hint:'Pista',explain:'Explicar',next:'Siguiente',save_response:'Guardar',copy_response:'Copiar',regenerate:'Regenerar'};
const icons={simplify:'sparkles',another_example:'refresh-cw',step_by_step:'list-ordered',quiz_me:'circle-help',different:'lightbulb',dont_understand:'circle-help',lost:'life-buoy',reveal_answer:'eye',summary_learning:'notebook-tabs',hint:'lightbulb',explain:'book-open',next:'arrow-right',save_response:'bookmark',copy_response:'copy',regenerate:'rotate-ccw'};
export function getAvailableActions(message,state={},latest=true){
 const text=typeof message==='string'?message:message.content;
 const utility=['save_response','copy_response'];
 if(!latest)return {primary:[],more:utility};
 if(state.mode==='identity'||/^(¡?Sí|Soy Allen|Mucho gusto|Estoy configurado|No soy un animal|El mono soy yo|No tengo un ejercicio|\*\*MODO DEMO)/i.test(text))return {primary:[],more:[...utility,'regenerate']};
 let primary,more=['step_by_step','dont_understand','lost','different',...utility,'summary_learning','regenerate'];
 if(state.mode==='quiz') {primary=['hint','explain'];more=['dont_understand','lost',...utility,'regenerate'];}
 else if(state.mode==='quiz_feedback'){primary=['another_example','next','summary_learning'];}
 else if(state.answer_revealed){primary=['another_example','quiz_me','summary_learning'];}
 else if(state.active_exercise){primary=['hint','step_by_step','reveal_answer'];}
 else if(text.length>65){primary=['simplify','another_example','quiz_me'];}
 else {primary=[];more=[...utility,'regenerate'];}
 more=more.filter(a=>!primary.includes(a));
 return {primary,more};
}
function actionButton(action,index){const attr=action==='save_response'?`data-save-answer="${index}"`:action==='copy_response'?`data-copy="${index}"`:action==='regenerate'?'data-regenerate':`data-learning-action="${action}" data-answer-index="${index}"`;return `<button type="button" class="action-chip" ${attr} aria-label="${esc(actions[action])}" title="${esc(actions[action])}">${icon(icons[action],16)}<span class="action-label">${esc(actions[action])}</span></button>`;}
export function actionBar(index,text,state={},latest=true){const available=getAvailableActions(text,state,latest);return `<div class="learning-actions">${available.primary.map(action=>actionButton(action,index)).join('')}${available.more.length?`<details class="action-menu"><summary aria-label="Más opciones">${icon('settings',16)}<span>Más opciones</span></summary><div class="action-menu-items">${available.more.map(action=>actionButton(action,index)).join('')}</div></details>`:''}</div>`;}
