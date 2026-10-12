import {evidence} from './engine.mjs';
export function lessonStage(topic){return topic.title.startsWith('Proyecto:')?'project':topic.id.includes('-workshop-')||topic.title.startsWith('Misión:')?'apply':topic.prerequisite?'practice':'bases';}
export const stageLabels={bases:'Bases',practice:'Desarrollo',apply:'Aplicación',project:'Proyecto'};
export function routeMatches(course,state,focus='all',stage='all'){
 const used=course.topics.some(t=>state.completed.includes(t.id)),pending=state.session?.courseId===course.id&&state.session.phase!=='complete'||Boolean(state.savedSessions?.[course.id]);
 if(focus==='continue'&&!used&&!pending)return false;
 if(focus==='reinforce'&&!course.topics.some(t=>evidence(state,t.id).incorrect>0))return false;
 if(focus==='explore'&&(used||pending))return false;
 return stage==='all'||course.topics.some(t=>lessonStage(t)===stage);
}
export const crossProjects=[
 {id:'school-library',title:'Una biblioteca que cuida a todos',courses:['reading-v1','citizenship-school-v1','money-school-v1'],intro:'Tu grupo quiere mejorar una biblioteca con un presupuesto ficticio de 20 unidades.',steps:['Escribe una idea principal y dos razones para la mejora.','Escucha una necesidad de acceso: letra legible, espacio o formato alternativo.','Divide las 20 unidades entre dos gastos y explica qué debes priorizar.'],finish:'Revisa si tu texto, el acceso y el presupuesto responden al mismo objetivo.'},
 {id:'garden-record',title:'Un huerto con evidencia',courses:['science-v1','fractions-v1','biology-school-v1'],intro:'En un registro ficticio, tres plantas miden 4, 6 y 8 cm. Una de tres recibe menos luz.',steps:['Representa una de tres plantas con una fracción.','Dibuja los tres valores y calcula su promedio.','Explica qué otros factores debes controlar antes de atribuir la diferencia a la luz.'],finish:'Promedio: 6 cm. Una comparación aislada no demuestra una causa; revisa agua, tipo de planta y otras condiciones.'},
 {id:'safe-invitation',title:'Una invitación clara y segura',courses:['english-v1','digital-safety-v1','reading-v1'],intro:'Tu grupo prepara una invitación para estudiar en la biblioteca.',steps:['Escribe una frase con el lugar: Meet me at the library.','Distingue qué información necesita la invitación y qué datos personales sobran.','Comprueba que la instrucción sea clara y que la fuente del mensaje sea conocida.'],finish:'No incluyas contraseñas, dirección de casa ni datos de otras personas. Una invitación no necesita esos secretos.'},
 {id:'route-and-units',title:'Un recorrido bien explicado',courses:['geography-school-v1','physics-school-v1','study-school-v1'],intro:'En un plano ficticio, 1 cm representa 2 km. La ruta mide 3 cm.',steps:['Describe una dirección con norte arriba y convierte la distancia del plano.','Distingue distancia de rapidez: falta conocer el tiempo para calcular rapidez.','Prepara una explicación breve con datos, regla y una conclusión.'],finish:'La ruta representa 6 km. Esa distancia no permite saber por sí sola cuánto se tarda.'}
];
