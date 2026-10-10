// Informational plans; no checkout, no paid claims, no client-provided entitlements.
export const plans = [
  {id:'free',name:'Gratis',description:'Curso inicial, prácticas, tarjetas y progreso local disponibles.'},
  {id:'premium',name:'Premium',description:'Propuesta futura: más cursos y rutas. Compras todavía no disponibles.'},
  {id:'institution',name:'Instituciones',description:'Propuesta futura: implementación y contenidos propios. Teacher Studio sigue en escritorio.'}
];
export const aiStatus = Object.freeze({available:false,mode:'structured',label:'Tutor guiado sin conexión',detail:'Explicaciones preparadas del curso. La IA generativa está desconectada por defecto. Puedes conectar el modelo local desde ALLEN de escritorio.'});
export function hasAccess(feature){return ['fractions-v1','reading-v1','english-v1','python-v1','digital-safety-v1','science-v1','local-progress','structured-tutor','flashcards'].includes(feature);}
export function paidEntitlement(){return {active:false,reason:'Proveedor de compras y verificador de derechos no configurados.'};}
export async function requestGenerativeTutor(){throw Error('La IA generativa móvil todavía no está configurada.');}
