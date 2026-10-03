// No cloud voice service is enabled implicitly. Browser recognition is opt-in.
export class SpeechRecognitionService {
 constructor(){this.mode='disabled';this.recognition=null;}
 get supported(){return !!(window.SpeechRecognition||window.webkitSpeechRecognition);}
 async listen(onText,onState){
  if(this.mode==='disabled'||!this.supported)throw new Error('No pude escucharte. Puedes escribirme aquí.');
  const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
  const recognition=new Recognition();this.recognition=recognition;
  recognition.lang='es-ES';recognition.continuous=false;recognition.interimResults=false;
  if(this.mode==='local'){
   if(!('processLocally' in recognition))throw new Error('Este navegador no ofrece reconocimiento local. Puedes escribir tu pregunta.');
   recognition.processLocally=true;
  }
  recognition.onresult=e=>{if(this.recognition===recognition)onText(e.results[0][0].transcript);};
  recognition.onerror=()=>{if(this.recognition===recognition)onState('error');};recognition.onend=()=>{if(this.recognition===recognition)onState('idle');};
  recognition.start();onState('listening');
 }
 cancel(){this.recognition?.abort();this.recognition=null;}
}
export class TextToSpeechService {
 constructor(){this.enabled=false;this.rate=1;}
 get voices(){return window.speechSynthesis?.getVoices().filter(v=>v.localService&&v.lang.startsWith('es'))||[];}
 play(text,onState=()=>{}){
  this.stop();
  if(!this.enabled)throw new Error('La voz está desactivada. Puedes seguir leyendo y escribir tu pregunta.');
  if(!this.voices.length)throw new Error('No hay una voz española local disponible. La respuesta sigue disponible para leer.');
  const utterance=new SpeechSynthesisUtterance(text.replace(/[*#`]/g,''));utterance.voice=this.voices[0];utterance.rate=this.rate;
  utterance.onend=()=>onState('idle');utterance.onerror=()=>onState('error');
  window.speechSynthesis.speak(utterance);onState('speaking');
 }
 pause(){window.speechSynthesis?.pause();}
 resume(){window.speechSynthesis?.resume();}
 stop(){window.speechSynthesis?.cancel();}
}
export function sound(enabled,celebrate=false,tone='normal'){
 if(!enabled)return;
 try{const Audio=window.AudioContext||window.webkitAudioContext;const ctx=new Audio();const gain=ctx.createGain();gain.gain.value=tone==='soft'?.012:.025;gain.connect(ctx.destination);const notes=tone==='soft'?[392]:tone==='unlock'?[392,523,659]:celebrate?[523,659,784]:[523];notes.forEach((frequency,i)=>{const osc=ctx.createOscillator();osc.frequency.value=frequency;osc.connect(gain);osc.start(ctx.currentTime+i*.15);osc.stop(ctx.currentTime+i*.15+.12);});setTimeout(()=>ctx.close(),800);}catch{/* Sound is optional. */}
}
