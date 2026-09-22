import {AllenMascot as BaseMascot} from './ui.js';
const descriptions={hello:'te saluda',thinking:'está pensando',listening:'te escucha',speaking:'está hablando',happy:'está feliz',celebrating:'celebra tu esfuerzo',reading:'está leyendo',teaching:'te enseña',confused:'piensa contigo',sleeping:'está despertando',offline:'descansa sin conexión',challenge:'te propone un reto',success:'celebra tu respuesta',error:'necesita intentarlo de nuevo',explorer:'explora contigo',logic:'investiga con una lupa',math:'resuelve con una libreta',english:'lee una palabra',coding:'programa contigo',ai:'piensa en inteligencia artificial',hint:'te da una pista',victory:'celebra la misión con un trofeo'};
export function AllenMascot(state='happy',size='medium'){
 if(!Object.hasOwn(descriptions,state))state='happy';
 const pose=({teaching:'reading',offline:'sleeping',confused:'thinking',error:'thinking',explorer:'challenge',logic:'thinking',math:'reading',english:'reading',coding:'reading',ai:'thinking',hint:'thinking',victory:'celebrating'})[state]||state;
 let svg=BaseMascot(pose,size).replace(`allen-mascot ${pose}`,`allen-mascot ${state}`).replace(/aria-label="[^"]*"/,`aria-label="Allen ${descriptions[state]}"`);
 if(state==='speaking')svg=svg.replace('M85 104q16 20 32 0','M90 105q11 26 22 0z');
 const accents={
  listening:'<g fill="none" stroke="#547d75" stroke-width="7"><path d="M44 77a57 57 0 0 1 114 0"/><path d="M43 75v23m115-23v23"/></g>',
  thinking:'<g fill="#ffd978"><circle cx="168" cy="37" r="15"/><circle cx="154" cy="54" r="6"/><circle cx="147" cy="65" r="3"/></g>',
  teaching:'<path d="m153 35 5-12 5 12 12 5-12 5-5 12-5-12-12-5z" fill="#e7b84c"/>',
  challenge:'<path d="M162 119V55m1 1 27 8-27 12" fill="#e7b84c" stroke="#94622e" stroke-width="4"/>',
  success:'<path d="m149 38 10 10 22-26" fill="none" stroke="#547d75" stroke-width="7"/>',
  celebrating:'<g fill="#e7b84c"><path d="m20 28 3 8 9 1-7 6 2 9-7-5-8 5 2-9-7-6 10-1z"/><path d="m176 20 3 8 9 1-7 6 2 9-7-5-8 5 2-9-7-6 10-1z"/></g>',
  sleeping:'<path d="M164 28h18l-18 18h18" fill="none" stroke="#8b735c" stroke-width="3"/>',
  error:'<path d="M169 22v14m0 6v1" stroke="#a55d32" stroke-width="5" stroke-linecap="round"/>',
  explorer:'<path d="M53 39q48-31 94 0l-10 11H63z" fill="#a65a24" stroke="#674024" stroke-width="3"/><path d="M71 27q30-15 58 0" fill="none" stroke="#e7b84c" stroke-width="8"/>',
  logic:'<circle cx="165" cy="57" r="20" fill="none" stroke="#735a40" stroke-width="5"/><path d="m180 72 15 16" stroke="#735a40" stroke-width="6" stroke-linecap="round"/>',
  math:'<rect x="141" y="130" width="42" height="52" rx="5" fill="#fff8ed" stroke="#735a40" stroke-width="3"/><path d="M151 145h21m-21 12h16m-16 12h20" stroke="#d9864b" stroke-width="3"/>',
  english:'<path d="M139 139q15-7 28 0q12-7 24 0v34q-11-5-24 2q-13-7-28-2z" fill="#719987" stroke="#476e5c" stroke-width="3"/>',
  coding:'<rect x="130" y="136" width="64" height="39" rx="5" fill="#719987" stroke="#476e5c" stroke-width="3"/><path d="m149 148-8 7 8 7m15-14 8 7-8 7" fill="none" stroke="#fff8ed" stroke-width="3"/>',
  ai:'<circle cx="169" cy="45" r="17" fill="#ffd978" stroke="#ad7627" stroke-width="3"/><path d="M163 63h12m-10 6h8" stroke="#ad7627" stroke-width="4"/>',
  hint:'<circle cx="169" cy="45" r="17" fill="#ffd978" stroke="#ad7627" stroke-width="3"/><path d="M163 63h12m-10 6h8" stroke="#ad7627" stroke-width="4"/>',
  victory:'<path d="M151 35h34v25q-17 20-34 0z" fill="#ffd978" stroke="#a66c1e" stroke-width="3"/><path d="M151 40h-10q-2 19 13 20m31-20h10q2 19-13 20M168 78v16m-12 0h24" fill="none" stroke="#a66c1e" stroke-width="4"/>'
 };
 return svg.replace('</svg>',(accents[state]||'')+'</svg>');
}
