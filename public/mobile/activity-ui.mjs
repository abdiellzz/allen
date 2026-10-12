export const safe=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function newDraft(q){
 return {questionId:q.id,input:'',order:q.steps?[...q.steps.slice(1),q.steps[0]]:[],matches:q.pairs?q.pairs.map(()=> ''):[]};
}
export function draftAnswer(q,draft){
 if(q.activity==='order')return draft.order.join(' → ');
 if(q.activity==='match')return q.pairs.map(([label],i)=>`${label} → ${draft.matches[i]}`).join(' | ');
 return draft.input;
}
export function questionForm(q,draft){
 let body;
 if(q.activity==='input')body=`<label class="field">Escribe tu respuesta<input name="answer" type="text" maxlength="240" autocomplete="off" ${q.numeric?'inputmode="decimal"':''} value="${safe(draft.input)}" required></label><p class="small muted">${q.numeric?'Puedes usar punto o coma decimal.':'Mayúsculas y acentos no cambian la evaluación.'}</p>`;
 else if(q.activity==='order')body=`<p class="small muted">Mueve los pasos con los botones. También funciona con teclado.</p><ol class="order-steps">${draft.order.map((step,i)=>`<li><span>${safe(step)}</span><div><button type="button" data-action="move-step" data-index="${i}" data-direction="-1" data-boundary="${i===0}" ${i===0?'disabled':''} aria-label="Subir paso ${i+1}">↑</button><button type="button" data-action="move-step" data-index="${i}" data-direction="1" data-boundary="${i===draft.order.length-1}" ${i===draft.order.length-1?'disabled':''} aria-label="Bajar paso ${i+1}">↓</button></div></li>`).join('')}</ol>`;
 else if(q.activity==='match'){
  // Reverse displayed descriptions so the initial layout does not give the solution.
  const targets=[...q.pairs.map(p=>p[1])].reverse();
  body=`<div class="match-pairs">${q.pairs.map(([label],i)=>`<label class="field">${safe(label)}<select name="match-${i}" data-match="${i}" required><option value="">Elige su relación</option>${targets.map(t=>`<option value="${safe(t)}" ${draft.matches[i]===t?'selected':''}>${safe(t)}</option>`).join('')}</select></label>`).join('')}</div><p class="small muted">Usa cada descripción una sola vez.</p>`;
 }else body=`<fieldset class="options"><legend>${q.activity==='error'?'Señala el error':'Elige una respuesta'}</legend>${q.options.map(o=>`<label><input type="radio" name="answer" value="${safe(o)}" required><span>${safe(o)}</span></label>`).join('')}</fieldset>`;
 return `<form id="answer-form" data-activity="${q.activity??'choice'}">${body}<button class="primary" type="submit">Comprobar respuesta</button></form>`;
}
export function visualExplanation(topic){
 if(topic.guide){return `<details class="visual-guide"><summary>${topic.guide.kind==='code'?'Sigue el programa paso a paso':'Descubre las pistas del texto'}</summary>${topic.guide.lines.map(([line,help],i)=>`<details class="visual-step"><summary>${topic.guide.kind==='code'?`<code>${safe(line)}</code>`:safe(line)}</summary><p>${safe(help)}</p></details>`).join('')}<p class="small muted">Toca cada línea para revelar su explicación.</p></details>`;}
 if(topic.courseId==='python-v1')return `<details class="visual-guide"><summary>Sigue el ejemplo paso a paso</summary>${topic.example.split('\n').map(line=>`<details class="visual-step"><summary><code>${safe(line)}</code></summary><p>${safe(topic.simple)}</p></details>`).join('')}<p class="small muted">Ejemplo preparado; no se ejecuta código.</p></details>`;
 if(['reading-v1','english-v1'].includes(topic.courseId))return `<details class="visual-guide"><summary>Encuentra una pista en el ejemplo</summary><p>${safe(topic.example)}</p><details><summary>¿En qué debo fijarme?</summary><p>${safe(topic.simple)}</p></details></details>`;
 if(topic.visual)return `<div class="fraction-picture" role="img" aria-label="${topic.visual.selected} de ${topic.visual.total} partes iguales seleccionadas">${Array.from({length:topic.visual.total},(_,i)=>`<span class="${i<topic.visual.selected?'filled':''}"></span>`).join('')}</div>`;
 return '';
}
