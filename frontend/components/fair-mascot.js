import {AllenMascot as BaseMascot} from './ui.js';
const descriptions={hello:'te saluda',thinking:'está pensando',listening:'te escucha',speaking:'está hablando',happy:'está feliz',celebrating:'celebra tu esfuerzo',reading:'está leyendo',teaching:'te enseña',confused:'piensa contigo',sleeping:'está despertando',offline:'descansa sin conexión',challenge:'te propone un reto',success:'celebra tu respuesta',error:'necesita intentarlo de nuevo'};
export function AllenMascot(state='happy',size='medium'){
 if(!Object.hasOwn(descriptions,state))state='happy';
 const pose=({teaching:'reading',offline:'sleeping',confused:'thinking',error:'thinking'})[state]||state;
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
  error:'<path d="M169 22v14m0 6v1" stroke="#a55d32" stroke-width="5" stroke-linecap="round"/>'
 };
 return svg.replace('</svg>',(accents[state]||'')+'</svg>');
}
