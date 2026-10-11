import {allTopics,courses,topicById,questionById} from './course.mjs';
import {recommendation,activeCourse,evidence} from './engine.mjs';
const FAQ=[
 ['start','¿Por dónde empiezo?','Elige un curso en Aprender. El diagnóstico breve orienta el apoyo; después verás una explicación, un ejemplo, dos prácticas y una comprobación.'],
 ['diagnostic','¿Para qué sirve el diagnóstico?','Es un punto de partida, no una nota. Tus respuestas ayudan a detectar qué bases conviene practicar. El dominio se comprueba después con las actividades.'],
 ['offline','¿Puedo aprender sin Internet?','Sí. En Android el contenido viene incluido. En la web espera a que indique que el curso está guardado antes de desconectarte. Las respuestas de este tutor también están preparadas en el dispositivo.'],
 ['progress','¿Cómo se guarda mi progreso?','Se guarda en este dispositivo y por perfil. Mi progreso muestra intentos, aciertos, errores, ayudas y comprobaciones. Haz una copia privada antes de borrar datos o cambiar de dispositivo.'],
 ['backup','¿Cómo recupero mi progreso?','En Mi progreso puedes exportar una copia y recuperar una existente. Recuperar crea otro perfil y conserva los anteriores. La copia no está cifrada: guárdala en un lugar privado.'],
 ['profiles','¿Puedo compartir el dispositivo?','Sí: crea un perfil para cada estudiante en Perfiles. Cada uno conserva su progreso. Los perfiles locales no tienen contraseña: quien use el dispositivo puede seleccionarlos.'],
 ['hints','¿Cuándo debo pedir una pista?','Intenta identificar primero los datos y qué te preguntan. Si te atascas, pide una pista: se muestran por pasos. Usar ayuda es parte del aprendizaje y queda registrado.'],
 ['errors','¿Qué hago si me equivoco?','Lee la retroalimentación, identifica qué idea confundiste y prueba otro ejemplo. En Practicar encontrarás tus dificultades recientes. Una respuesta incorrecta no borra tus logros.'],
 ['unlock','¿Por qué hay lecciones pendientes?','Las lecciones siguen una secuencia de bases. Completa el diagnóstico y comprueba el prerrequisito para abrir la siguiente. Pedir ayuda o conversar no desbloquea temas.'],
 ['review','¿Para qué sirven las tarjetas?','Ayudan a recuperar una idea de memoria. Piensa tu respuesta antes de abrir la tarjeta. Indica si la recordaste para programar el siguiente repaso.'],
 ['time','¿Cómo cambio mi tiempo de estudio?','En Mi progreso puedes elegir sesiones de 5, 10 o 15 minutos y ajustar el texto. La actividad queda guardada para continuar después.'],
 ['mastery','¿Mi porcentaje es una nota escolar?','No. Es una estimación a partir de evidencia, dificultad, recencia y ayudas. Repetir preguntas conocidas no garantiza aplicar lo aprendido en situaciones nuevas.'],
 ['chat','¿Cómo responde Allen?','Uso explicaciones, ejemplos y respuestas preparadas de los cursos. Puedes elegir preguntas o escribir una duda breve. Si no encuentro una respuesta cubierta, te lo digo y propongo opciones. No necesito un modelo externo.'],
 ['privacy','¿Dónde quedan mis datos?','El progreso permanece en el almacenamiento local de este dispositivo. Este tutor no envía preguntas ni materiales a un servidor y no guarda conversaciones. Evita escribir datos personales.'],
 ['switch','¿Cómo cambio de curso?','En Aprender elige una ruta. Si tienes una actividad sin terminar, continúa y termínala antes de cambiar. Elegir tu ruta actual te muestra sus lecciones.'],
 ['practice','¿Cómo compruebo que entendí?','Explica la idea con tus palabras y aplícala a un caso distinto. Las comprobaciones cierran la lección: necesitas acertar la comprobación y al menos dos de las tres actividades.'],
 ['motivation','¿Y si hoy me cuesta aprender?','Puedes dividir la tarea: una explicación, un ejemplo y un intento. Pide apoyo y vuelve a probar. Tu progreso cuenta por lo que comprendes, sin castigos por perder una racha.'],
 ['courses','¿Qué puedo aprender aquí?','Hay rutas de fracciones, comprensión lectora, inglés, Python, seguridad digital y ciencias. Cada ruta combina bases con aplicaciones y repasos; explora Aprender para ver sus lecciones.']
];
export const normalize = text => String(text??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
export const faq = FAQ.map(([id,label,text])=>({id:`faq:${id}`,label,text,source:'Guía de ALLEN'}));
const kinds=[['explain','¿Cómo funciona'],['simple','¿Me lo explicas más sencillo?'],['example','¿Puedes mostrar un ejemplo resuelto?'],['alternative','¿Me das otro ejemplo?'],['card','¿Qué idea debo recordar?'],['purpose','¿Qué aprenderé en este tema?'],['next','¿Qué debo aprender después?']];
export function topicQuestions(topic){return kinds.map(([kind,label])=>({id:`topic:${topic.id}:${kind}`,label:kind==='explain'?`${label} ${topic.title.toLowerCase()}?`:label,topicId:topic.id}));}
export const knowledgeQuestions = [...faq,...allTopics.flatMap(topicQuestions)];
export function contextualQuestions(state,topicId){const t=topicById(topicId)??topicById(state.session?.topicId??questionById(state.session?.questionIds[state.session?.index])?.topicId)??activeCourse(state).topics.find(t=>!state.completed.includes(t.id))??activeCourse(state).topics[0];return [...topicQuestions(t),{id:'context:hint',label:'¿Puedes darme una pista de mi ejercicio?'},{id:'context:feedback',label:'¿Por qué mi respuesta estuvo mal?'},{id:'context:recommend',label:'¿Qué me recomiendas ahora?'},{id:'context:status',label:'¿Cómo voy en este tema?'}];}
export function answerPrepared(state,id){
 const item=faq.find(q=>q.id===id);if(item)return {...item};
 const s=state.session,q=questionById(s?.questionIds[s?.index]),t=topicById(s?.topicId??q?.topicId)??activeCourse(state).topics[0];
 if(id==='context:recommend'){const r=recommendation(state);return {text:`${r.title}. ${r.reason}`,source:'Motor educativo ALLEN'};}
 if(id==='context:status'){const e=evidence(state,t.id);return {text:`En ${t.title} tienes ${e.correct} aciertos en ${e.attempts} intentos y ${e.hints} pistas utilizadas. ${state.completed.includes(t.id)?'La comprobación está superada.':'El objetivo todavía necesita comprobación.'}`,source:'Evidencia de este perfil'};}
 if(id==='context:hint')return {action:'hint',text:'Abre una práctica y pide una pista antes de responder.',source:'Ayuda guiada'};
 if(id==='context:feedback'){const a=s?.answers.find(a=>a.questionId===q?.id);return {text:a?`Tu respuesta fue ${a.answer}. ${q.feedback}`:'Primero intenta responder en tu actividad. Después revisamos el procedimiento y la retroalimentación, sin adelantar la solución.',source:t.source??activeCourse(state).source};}
 if(id.startsWith('topic:')){const [,topicId,kind]=id.split(':');const topic=topicById(topicId);if(topic){const next=courses.find(c=>c.id===topic.courseId).topics.find(x=>x.prerequisite===topicId);const text={explain:topic.explanation,simple:topic.simple,example:topic.example,alternative:topic.alternative,card:topic.card.back,purpose:topic.objective,next:next?`Después sigue ${next.title}. Primero comprueba ${topic.title}; puedes revisar el mapa en Mi progreso.`:'Has llegado al cierre de esta ruta. Repasa y aplica sus ideas en situaciones nuevas.'}[kind];if(text)return {text,source:topic.source,topicId,action:['explain','simple','alternative'].includes(kind)&&t.id===topicId&&s?.phase!=='complete'?kind:undefined};}}
 return {text:'No tengo una respuesta preparada para esa duda. Elige un tema del curso o una pregunta de la guía y lo revisamos juntos.',source:'Tutor guiado'};
}
export function findQuestion(message,state,topicId){
 const n=normalize(message);if(!n)return null;
 if(/(respuesta correcta|solucion|respuesta del ejercicio|resolver ejercicio|pista)/.test(n))return 'context:hint';
 if(/(por que.*(mal|incorrect)|me equivoque)/.test(n))return 'context:feedback';
 const contextual=contextualQuestions(state,topicId);if(/(mas sencillo|no entendi|no entiendo)/.test(n))return contextual.find(q=>q.id.endsWith(':simple'))?.id;
 if(/otro ejemplo/.test(n))return contextual.find(q=>q.id.endsWith(':alternative'))?.id;
 if(/ejemplo/.test(n))return contextual.find(q=>q.id.endsWith(':example'))?.id;
 if(/(recomienda|siguiente actividad|que hago ahora)/.test(n))return 'context:recommend';
 const words=n.split(' ').filter(w=>w.length>3&&!['como','puedo','para','quiero','allen','sobre','explica','tengo'].includes(w));
 const pool=[...contextual,...knowledgeQuestions];let best=null,score=0;
 for(const candidate of pool){const label=normalize(candidate.label);if(label===n)return candidate.id;const hits=words.filter(w=>label.split(' ').includes(w)).length;const value=hits/Math.max(1,words.length);if(hits&&value>score){score=value;best=candidate.id;}}
 return score>=.6?best:null;
}
