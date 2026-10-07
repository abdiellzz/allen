import test from 'node:test';
import assert from 'node:assert/strict';
import {continuityPanel,recommendationPanel,masteryPanel} from '../frontend/components/continuity.js';

test('dashboard renders continuity and mastery from one model',()=>{
 const model={
   adventure:{current_step:2},
   recommendation:{reason:'Practica subnetting.',topic:'Subnetting',action:'guided_practice'},
   mastery:[{subject:'Redes',topic:'Subnetting',mastery_score:58,status:'practicing'}]
 };
 assert.ok(continuityPanel(model).includes('CONTINÚA'));
 assert.ok(recommendationPanel(model).includes('Practica subnetting'));
 assert.ok(masteryPanel(model).includes('58%'));
});
