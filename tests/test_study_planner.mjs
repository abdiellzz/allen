import test from 'node:test';
import assert from 'node:assert/strict';
import {planAllenPage} from '../frontend/components/study-session.js';

test('Plan Allen page exposes the required planning fields',()=>{
  const html=planAllenPage('Universidad / Técnico');
  for(const id of ['plan-subject','plan-topics','plan-deadline','plan-minutes','plan-level','plan-goal']) assert.ok(html.includes(id));
  assert.ok(html.includes('PLAN ALLEN'));
  assert.ok(html.toLowerCase().includes('estudio activo'));
});
