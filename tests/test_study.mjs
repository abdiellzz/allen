import test from 'node:test';
import assert from 'node:assert/strict';
import {bindStudy,resetStudy} from '../frontend/components/learning.js';

test('study timer reaches its goal without blocking, and can restart after exit',()=>{
 const original={document:globalThis.document,setInterval:globalThis.setInterval,clearInterval:globalThis.clearInterval,now:Date.now};
 let current=1000, tick, notices=[];
 const elements=Object.fromEntries(['#study-form','#study-progress','#session-progress','#study-duration','#exit-study'].map(id=>[id,{hidden:true,value:'5'}]));
 const classes=new Set();
 globalThis.document={querySelector:s=>elements[s],body:{classList:{add:c=>classes.add(c),remove:c=>classes.delete(c),toggle:(c,v)=>v?classes.add(c):classes.delete(c)}}};
 globalThis.setInterval=fn=>(tick=fn,1);globalThis.clearInterval=()=>{tick=null;};Date.now=()=>current;
 try{
  resetStudy();bindStudy(message=>notices.push(message));
  elements['#study-form'].onsubmit({preventDefault(){}});
  assert(classes.has('study-mode'));
  current+=300000;tick();assert.equal(notices.length,1);assert.match(notices[0],/Completaste/);
  assert.equal(elements['#session-progress'].value,300);
  current+=10000;tick();assert.equal(notices.length,1);assert.match(elements['#study-progress'].textContent,/5:10/);
  elements['#exit-study'].onclick();assert(!classes.has('study-mode'));assert(elements['#session-progress'].hidden);
  elements['#study-form'].onsubmit({preventDefault(){}});assert.equal(typeof tick,'function');
  current+=1000;tick();assert.match(elements['#study-progress'].textContent,/0:01/);
  elements['#study-duration'].value='0';elements['#study-form'].onsubmit({preventDefault(){}});
  current+=3600000;tick();assert.equal(notices.length,1);assert.match(elements['#study-progress'].textContent,/sin límite/);
 }finally{resetStudy();globalThis.document=original.document;globalThis.setInterval=original.setInterval;globalThis.clearInterval=original.clearInterval;Date.now=original.now;}
});
