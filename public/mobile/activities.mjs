// Deterministic grading shared by UI, learning engine and backup validation.
// Prepared answers remain data; student input is never evaluated as code.
export const normalizeInput=value=>String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toLowerCase().replace(/\s+/g,' ');
export function validAnswer(q,value){
 if(typeof value!=='string'||value.length>240||!value.trim())return false;
 return q.activity==='input'?true:q.options.includes(value);
}
export function correctAnswer(q,value){
 if(!validAnswer(q,value))return false;
 if(q.activity!=='input')return value===q.answer;
 if(q.numeric){const input=normalizeInput(value).replace(',','.');return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(input)&&Number.isFinite(Number(input))&&Number(input)===Number(q.answer);}
 return normalizeInput(value)===normalizeInput(q.answer);
}
export function feedbackFor(q,value){
 const correct=correctAnswer(q,value);
 const reason=!correct?q.feedbackByAnswer?.[value]:null;
 return {correct,text:reason?`${reason} ${q.feedback}`:q.feedback};
}
export function permutations(items){
 if(items.length===0)return [[]];
 return items.flatMap((item,i)=>permutations(items.filter((_,n)=>n!==i)).map(rest=>[item,...rest]));
}
export function interactiveQuestion(type,prompt,values,feedback,extra={}){
 const base={activity:type,prompt,feedback,...extra};
 if(type==='order'){const options=permutations(values).map(items=>items.join(' → '));return {...base,steps:values,options,answer:options[0]};}
 if(type==='match'){const options=permutations(values.map(p=>p[1])).map(targets=>values.map((p,i)=>`${p[0]} → ${targets[i]}`).join(' | '));return {...base,pairs:values,options,answer:options[0]};}
 return {...base,options:values,answer:values[0]};
}
