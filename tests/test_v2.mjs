import test from 'node:test';
import assert from 'node:assert/strict';
import {missions,achievements,chatActionText} from '../frontend/components/v2.js';

test('Allen v2 includes several educational missions',()=>{
  assert.ok(missions.length >= 5);
  const subjects=new Set(missions.map(m=>m.subject));
  for(const subject of ['Redes','Ciberseguridad','Programación','IA','Ciencias'])assert.ok(subjects.has(subject));
});

test('every mission has guided steps and explanations',()=>{
  for(const mission of missions){
    assert.ok(mission.steps.length >= 4);
    for(const step of mission.steps){
      assert.ok(step.options.length >= 3);
      assert.ok(Number.isInteger(step.correct));
      assert.ok(step.hint.length > 8);
      assert.ok(step.explanation.length > 12);
    }
  }
});

test('chat v2 exposes learning actions instead of generic gimmicks',()=>{
  for(const key of ['easy','example','question','challenge','summary']){
    assert.equal(typeof chatActionText[key],'string');
    assert.ok(chatActionText[key].length > 20);
  }
  assert.ok(achievements.length >= 8);
});
