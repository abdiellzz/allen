import test from 'node:test';
import assert from 'node:assert/strict';
import {getAvailableActions,actionBar} from '../frontend/components/actions.js';
const explanation='Una dirección IP identifica una conexión de un dispositivo dentro de una red. Por ejemplo, 192.168.1.10 puede ser una dirección privada.';
test('contextual actions never exceed three primary chips plus More',()=>{
 for(const state of [{},{mode:'guided_learning',active_exercise:'18 × 7'},{mode:'quiz',pending_question:'8 × 7?'},{mode:'quiz_feedback',answer_revealed:true},{mode:'final_answer',answer_revealed:true},{mode:'identity'}]){
  const result=getAvailableActions(explanation,state);
  assert(result.primary.length+(result.more.length?1:0)<=4);
  assert.equal(new Set([...result.primary,...result.more]).size,result.primary.length+result.more.length);
 }
});
test('reveal is only available for an unresolved exercise',()=>{
 assert(!getAvailableActions(explanation,{}).primary.includes('reveal_answer'));
 assert(getAvailableActions(explanation,{active_exercise:'18 × 7'}).primary.includes('reveal_answer'));
 const final=getAvailableActions('El resultado es 126.',{active_exercise:'18 × 7',answer_revealed:true});
 assert(![...final.primary,...final.more].includes('reveal_answer'));
 assert.deepEqual(final.primary,['another_example','quiz_me','summary_learning']);
});
test('old messages offer only save and copy, not stale actions',()=>{
 assert.deepEqual(getAvailableActions(explanation,{},false),{primary:[],more:['save_response','copy_response']});
});
test('icons are SVG nodes, separated from labels, with no literal svg text',()=>{
 const html=actionBar(0,explanation,{active_exercise:'18 × 7'});
 assert(html.includes('<svg'));
 assert(html.includes('aria-hidden="true"'));
 assert(html.includes('<span class="action-label">Dame la respuesta</span>'));
 assert(!/svg/i.test(html.replace(/<[^>]*>/g,'')));
 assert(!html.includes('&lt;svg'));
});
