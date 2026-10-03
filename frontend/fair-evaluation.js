const criteria=['objetivo','comprension','pasos_completados','explicacion','aplicacion','reflexion'];
const normalized=value=>String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const words=value=>(normalized(value).match(/[a-z0-9]{3,}/g)||[]);
const countWords=value=>words(value).length;
const filled=value=>typeof value==='string'&&value.trim().length>0;

function scoreSteps(steps){
 if(!Array.isArray(steps)||steps.length===0)return 0;
 const ratio=steps.filter(Boolean).length/steps.length;
 return ratio===0?0:ratio<.34?1:ratio<.67?2:ratio===1?3:2;
}
function scoreObjective(project,description){
 if(!filled(description))return 0;
 if(description.trim().length<25)return 1;
 const goal=words(project?.objective||project?.problem||project?.task||'');
 const stop=new Set(['para','con','una','uno','que','como','los','las','del','por','the','and','use','from','will']);
 const unique=[...new Set(goal.filter(w=>!stop.has(w)))];
 const hits=unique.filter(w=>normalized(description).includes(w)).length;
 return hits>=2?3:hits===1?2:1;
}
function scoreExplanation(description){
 if(!filled(description))return 0;
 const n=countWords(description);return n<8?1:n<20?2:3;
}
function scoreApplication(evidence){
 const d=countWords(evidence.description),m=countWords(evidence.materials),steps=scoreSteps(evidence.steps);
 if(!d&&!m)return 0;if(!m||d<5)return 1;if(d>=15&&m>=2&&steps>=2)return 3;return 2;
}
function scoreReflection(reflection){
 if(!filled(reflection))return 0;
 const n=countWords(reflection),detail=/aprend|dific|cambiar|mejor|descubr|porque|por qué|funcion|proxim|próxim/i.test(reflection);
 return n<5?1:n>=12&&detail?3:n>=7?2:1;
}
function scoreComprehension(project,evidence){
 const reflection=scoreReflection(evidence.reflection),goal=scoreObjective(project,evidence.description);
 if(!filled(evidence.description)&&!filled(evidence.reflection))return 0;
 if(reflection>=3&&goal>=2)return 3;
 if(reflection>=2||goal>=2)return 2;
 return 1;
}
const highFeedback={
 objetivo:'Relacionaste tu explicación con el objetivo del proyecto.',
 comprension:'Mostraste comprensión al explicar tu proceso y aprendizaje.',
 pasos_completados:'Completaste los pasos que documentaste.',
 explicacion:'Explicaste con claridad cómo desarrollaste tu proyecto.',
 aplicacion:'Conectaste los materiales o ideas con una aplicación concreta.',
 reflexion:'Identificaste lo que aprendiste durante el proceso.'
};
const lowFeedback={
 objetivo:'Vuelve al objetivo y explica cómo se conecta con tu entrega.',
 comprension:'Describe qué idea entendiste y cómo la aplicaste.',
 pasos_completados:'Completa o documenta los pasos que todavía faltan.',
 explicacion:'Añade detalles sobre cómo desarrollaste el proyecto.',
 aplicacion:'Explica cómo usaste los materiales o las ideas elegidas.',
 reflexion:'Cuenta qué aprendiste, qué fue difícil y qué cambiarías.'
};
export const criterionLabels={objetivo:'Cumplimiento del objetivo',comprension:'Comprensión',pasos_completados:'Pasos completados',explicacion:'Explicación',aplicacion:'Aplicación',reflexion:'Reflexión'};
export const criterionText=n=>['No demostrado','Básico','Adecuado','Muy bien logrado'][n]||'No demostrado';

export function evaluateLocalRubric(project,evidence={}){
 const safe={steps:Array.isArray(evidence.steps)?evidence.steps:[],description:String(evidence.description||''),materials:String(evidence.materials||''),reflection:String(evidence.reflection||'')};
 const rubric_scores={objetivo:scoreObjective(project,safe.description),comprension:scoreComprehension(project,safe),pasos_completados:scoreSteps(safe.steps),explicacion:scoreExplanation(safe.description),aplicacion:scoreApplication(safe),reflexion:scoreReflection(safe.reflection)};
 const total_score=Object.values(rubric_scores).reduce((sum,n)=>sum+n,0),max_score=criteria.length*3,percentage=Math.round(total_score/max_score*100);
 const result_label=percentage>=85?'Muy bien logrado':percentage>=65?'Logrado':percentage>=40?'En desarrollo':'Necesita reforzarse';
 const ranked=[...criteria].sort((a,b)=>rubric_scores[b]-rubric_scores[a]);
 const strengths=ranked.filter(k=>rubric_scores[k]>=2).slice(0,2).map(k=>highFeedback[k]);
 const improvements=[...criteria].filter(k=>rubric_scores[k]<2).slice(0,2).map(k=>lowFeedback[k]);
 const lowest=[...criteria].sort((a,b)=>rubric_scores[a]-rubric_scores[b])[0];
 const feedback_local={strengths:strengths.join(' ')||'Gracias por compartir tu avance. La rúbrica señala qué información puedes añadir.',improvements:improvements.join(' ')||'Sigue probando otras ideas y documenta tus decisiones.',next_step:lowFeedback[lowest]};
 const objective_status=percentage>=65?'logrado':percentage>=40?'parcial':'no_demostrado';
 return {objective_status,criteria:{...rubric_scores},rubric_scores,total_score,max_score,percentage,result_label,...feedback_local,summary:`Evaluación local por rúbrica: ${total_score} de ${max_score} puntos (${percentage}%). ${result_label}.`,feedback_local,feedback_ai:'',points:200};
}

export function feedbackPrompt(project,evidence,evaluation){
 return `Da una recomendación educativa adicional y breve (máximo 3 oraciones) basada solo en esta entrega y rúbrica ya calculada. No cambies puntuaciones ni afirmes pruebas físicas. Proyecto: ${project?.name||project?.title||'Proyecto'}. Evidencia: ${JSON.stringify({description:evidence.description,materials:evidence.materials,reflection:evidence.reflection})}. Rúbrica: ${JSON.stringify(evaluation.rubric_scores)}. Resultado: ${evaluation.result_label}. Escribe únicamente el comentario complementario.`;
}

export async function retryEvaluationFeedback(host,project,key,submission=host.visitor.projects?.[key]){
 if(!submission||submission.status!=='COMPLETED'||submission.feedbackStatus==='GENERATING')return submission;
 submission.feedbackStatus='GENERATING';submission.feedbackError='';host.persist?.();host.render?.();
 const prompt=feedbackPrompt(project,submission.evidence,submission.evaluation);
 try{
  const response=await host.evaluateLocal(prompt);
  const feedback=String(response?.text||'').trim().replace(/^```(?:text|markdown)?\s*/i,'').replace(/\s*```$/,'');
  if(response?.demo||response?.unavailable||response?.error_code||feedback.length<20||/IA local no disponible|IA local no respondió|TIMEOUT|no pudo leer esta respuesta/i.test(feedback))throw new Error(response?.error||feedback||'Feedback opcional no disponible.');
  submission.feedback_ai=feedback.slice(0,1000);submission.feedbackStatus='ADDED';submission.evaluationStatus='AI_FEEDBACK_ADDED';if(!submission.stateHistory.includes('AI_FEEDBACK_ADDED'))submission.stateHistory.push('AI_FEEDBACK_ADDED');
 }catch(error){submission.feedbackStatus='UNAVAILABLE';submission.feedbackError=String(error?.message||error).slice(0,240);}
 host.persist?.();host.render?.();return submission;
}

export async function evaluateSubmission(host,project,key,evidence,context={}){
 const all=host.visitor.projects||(host.visitor.projects={});let submission=all[key];
 if(submission?.status==='COMPLETED'||submission?.status==='EVALUATED')return submission;
 if(!submission){submission=all[key]={projectId:key,visitorId:host.visitor.visitorId||'',sessionId:host.visitor.backendSession||'',status:'SUBMITTED',submittedAt:new Date().toISOString(),evidence,difficulty:host.visitor.difficulty,route:context.route||'',evaluation:null,evaluatedAt:null,rewardsGranted:false};}
 submission.project_id ||= key;submission.answers ||= submission.evidence;
 submission.status='SUBMITTED';submission.stateHistory||=['SUBMITTED'];submission.evaluationInProgress=true;host.persist?.();host.render?.();
 const evaluation=evaluateLocalRubric(project,submission.evidence||{}),evaluatedAt=new Date().toISOString();
 Object.assign(submission,{evaluation,rubric_scores:evaluation.rubric_scores,total_score:evaluation.total_score,result_label:evaluation.result_label,feedback_local:evaluation.feedback_local,feedback_ai:'',points:200,evaluatedAt,evaluated_at:evaluatedAt,status:'COMPLETED',state:'COMPLETED',evaluationStatus:'LOCAL_EVALUATED',feedbackStatus:'PENDING',evaluationInProgress:false,lastEvaluationError:'',stateHistory:[...submission.stateHistory,'LOCAL_EVALUATED','COMPLETED']});
 if(!submission.rewardsGranted){host.complete('projects',`project-evaluation:${key}`,200);submission.rewardsGranted=true;host.event?.('project_completed');}
 host.persist?.();host.render?.();
 void retryEvaluationFeedback(host,project,key,submission);
 return submission;
}
