import test from 'node:test';
import assert from 'node:assert/strict';
import {SpeechRecognitionService,TextToSpeechService} from '../frontend/fair-voice.js';
import {inactivityDecision,lessons} from '../frontend/fair-content.js';
test('visitor receives warning then reset; empty home attracts',()=>{
 assert.equal(inactivityDecision(119999,-1,true,false),'stay');
 assert.equal(inactivityDecision(120000,-1,true,false),'warn');
 assert.equal(inactivityDecision(140000,20000,true,false),'reset');
 assert.equal(inactivityDecision(45000,-1,false,true),'attract');
 assert.equal(inactivityDecision(45000,-1,true,true),'stay');
});
test('every offline micro lesson includes a valid answer and feedback',()=>{
 assert.equal(Object.keys(lessons).length,6);
 for(const lesson of Object.values(lessons)){assert.equal(lesson.options.length,3);assert.ok(lesson.options[lesson.correct]);assert.ok(lesson.feedback.length>20);}
});
test('speech defaults off and local mode never silently switches to cloud',async()=>{
 globalThis.window={SpeechRecognition:class{start(){throw new Error('must not start cloud recognition');}}};
 const speech=new SpeechRecognitionService();
 await assert.rejects(speech.listen(()=>{},()=>{}),/Puedes escribirme/);
 speech.mode='local';await assert.rejects(speech.listen(()=>{},()=>{}),/no ofrece reconocimiento local/);
});
test('cancelled recognition cannot deliver an old visitor transcript',async()=>{
 let instance,received=false;
 globalThis.window={SpeechRecognition:class{constructor(){instance=this;this.processLocally=false;}start(){}abort(){}}};
 const speech=new SpeechRecognitionService();speech.mode='local';
 await speech.listen(()=>received=true,()=>{});assert.equal(instance.processLocally,true);
 speech.cancel();instance.onresult({results:[[{transcript:'private'}]]});assert.equal(received,false);
});
test('TTS rejects remote voices and handles absent browser audio',()=>{
 globalThis.window={};const tts=new TextToSpeechService();tts.enabled=true;
 assert.throws(()=>tts.play('hello'),/No hay una voz/);tts.pause();tts.resume();tts.stop();
 globalThis.window={speechSynthesis:{getVoices:()=>[{lang:'es-ES',localService:false}],cancel(){}}};
 assert.throws(()=>tts.play('hello'),/No hay una voz/);
});
