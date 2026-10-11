import {activeCourse,recommendation,localDay,diagnosed} from './engine.mjs';
import {topicById,questionById} from './course.mjs';
export function recap(state,now=new Date()){
 const day=localDay(now),events=state.events.filter(e=>localDay(new Date(e.at))===day),answers=events.filter(e=>e.type==='answer'),correct=answers.filter(e=>e.correct).length;
 const checked=[...new Set(events.filter(e=>{if(e.type!=='check_complete')return false;const last=state.events.findLast(a=>a.type==='answer'&&a.topicId===e.topicId&&a.at<=e.at&&(!e.sessionId||a.sessionId===e.sessionId));if(!last||!last.correct||questionById(last.questionId)?.kind!=='check')return false;return state.events.filter(a=>a.type==='answer'&&a.sessionId===last.sessionId&&a.correct).length>=2;}).map(e=>e.topicId))];
 const recentErrors=answers.filter(e=>!e.correct).slice(-2),reinforce=[...new Set(recentErrors.map(e=>topicById(e.topicId).title))];
 const next=recommendation(state,now);
 return {day,attempts:answers.length,correct,checked,reinforce,next,text:answers.length?`Hoy respondiste ${answers.length} actividades, con ${correct} aciertos. ${checked.length?`Comprobaste ${checked.map(id=>topicById(id).title).join(', ')}.`:'Cada intento aporta evidencia; seguimos construyendo las bases.'}`:'Hoy puedes dar tu primer paso: una explicación y un intento.',encouragement:reinforce.length?'Un error nos ayuda a elegir dónde practicar. Puedes volver con calma.':'Tu aprendizaje sigue guardado. Avanza a tu ritmo, sin prisa.'};
}
export function companionTip(state,view){
 const s=state.session,q=questionById(s?.questionIds[s?.index]),answer=s?.answers.find(a=>a.questionId===q?.id);
 if(view==='session'&&s?.phase==='complete')return {title:'Tu esfuerzo quedó guardado',text:recap(state).text,asset:'allen-celebrate.png'};
 if(view==='session'&&answer&&!answer.correct)return {title:'Vamos a revisar la idea',text:'Equivocarte nos da una pista. Lee el procedimiento, busca qué cambió y pide un ejemplo más sencillo.',asset:'allen-explaining-v1.png'};
 if(view==='session'&&answer?.correct)return {title:'Bien razonado',text:'Antes de seguir, explica con tus palabras por qué esa respuesta funciona.',asset:'allen-celebrate.png'};
 if(view==='session'&&s?.hints.filter(id=>id===q?.id).length)return {title:'Estoy contigo',text:'Usa una pista cada vez. Identifica los datos y prueba tu idea antes de mirar otra ayuda.',asset:'allen-reading.png'};
 if(view==='session')return {title:'Un paso cada vez',text:s?.phase==='lesson'?'Lee el ejemplo y pregúntate qué regla se aplicó. Después lo intentamos juntos.':'No necesitas responder rápido. Piensa qué te preguntan; si te atascas, puedes pedir una pista.',asset:s?.phase==='lesson'?'allen-explaining-v1.png':'allen-thinking-v1.png'};
 if(view==='allen')return {title:'Sigamos conversando',text:'Puedes decirme “No entendí”, ver otro ejemplo o preguntarme qué hacer después. Mis respuestas están preparadas para estas rutas.',asset:'allen-reading.png'};
 return {title:'Tu siguiente paso',text:recommendation(state).reason,asset:'allen-reading.png'};
}
export function followUpQuestions(id,topicId){
 if(id==='context:status'||id==='context:recommend')return [{id:`topic:${topicId}:simple`,label:'No entendí'},{id:'context:recommend',label:'¿Qué hago después?'}];
 if(id?.endsWith(':simple')||id?.endsWith(':explain'))return [{id:`topic:${topicId}:example`,label:'Dame un ejemplo'},{id:`topic:${topicId}:card`,label:'¿Qué debo recordar?'}];
 if(id?.endsWith(':example')||id?.endsWith(':alternative'))return [{id:`topic:${topicId}:simple`,label:'No entendí'},{id:'context:recommend',label:'¿Qué hago después?'}];
 if(id==='context:hint'||id==='context:feedback')return [{id:'context:status',label:'¿Cómo voy?'},{id:`topic:${topicId}:alternative`,label:'Dame otro ejemplo'}];
 return [{id:'context:recommend',label:'¿Qué hago después?'},{id:`topic:${topicId}:example`,label:'Dame un ejemplo'}];
}
export const shortMissions=[
 {id:'recipe',topicId:'fraction-unlike',title:'Une medidas de una receta',description:'Combina porciones y cantidades de una receta. Primero convierte las fracciones a partes del mismo tamaño.',intro:'Imagina que preparas una receta: una mezcla lleva 1/2 de taza y otra 1/4. Juntas necesitan 3/4 de taza. Ahora practica la misma estrategia en tres situaciones.',asset:'allen-reading.png'},
 {id:'message',topicId:'spot-phishing',title:'Detecta un mensaje sospechoso',description:'Observa señales de urgencia, enlaces y solicitudes de códigos. Decide cómo verificar sin compartir secretos.',intro:'Eres la persona que recibe un mensaje de supuesto soporte. Tu misión: detenerte, revisar señales y elegir un canal conocido para verificar.',asset:'allen-reading.png'},
 {id:'program',topicId:'python-condition',title:'Piensa como un pequeño programa',description:'Sigue una condición y predice qué mensaje mostrará un programa. No se ejecuta código de tus archivos.',intro:'Un programa muestra “Meta lograda” cuando los puntos son diez o más. Lee las condiciones, sigue cada caso y comprueba cuál bloque se ejecuta.',asset:'allen-reading.png'}
];
export function missionReadiness(state,mission){const t=topicById(mission.topicId);return diagnosed(state,t.courseId)&&(!t.prerequisite||state.completed.includes(t.prerequisite));}
// Supplemental UI preferences contain no educational evidence and never alter mastery.
export function readUiPreference(key,fallback){try{const value=localStorage.getItem(key);return value===null?fallback:JSON.parse(value);}catch{return fallback;}}
export function writeUiPreference(key,value){try{localStorage.setItem(key,JSON.stringify(value));return true;}catch{return false;}}
