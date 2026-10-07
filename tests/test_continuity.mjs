import test from 'node:test';
import assert from 'node:assert/strict';
import {detectExamIntent} from '../frontend/components/continuity.js';

test('exam intent detects common Spanish study phrases',()=>{
  assert.equal(detectExamIntent('Tengo examen de redes el viernes').subject,'redes');
  assert.ok(detectExamIntent('Mi parcial es el lunes'));
  assert.ok(detectExamIntent('Necesito estudiar para matemáticas'));
  assert.equal(detectExamIntent('Explícame DNS'),null);
});
