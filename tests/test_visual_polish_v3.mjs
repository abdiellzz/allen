import test from 'node:test';
import assert from 'node:assert/strict';
import {continuityPanel,masteryPanel,recommendationPanel} from '../frontend/components/continuity.js';
import {teacherStudioPage} from '../frontend/components/course-studio.js';

test('Visual Polish v3 keeps Home focused on the next action',()=>{
 const html=continuityPanel({current_activity:{activity_type:'course',status:'active',subject:'Redes',topic:'CIDR'}});
 assert.ok(html.includes('CONTINÚA DONDE LO DEJASTE'));
 assert.ok(html.includes('v3-focus-card'));
 assert.ok(html.includes('CIDR'));
});

test('mastery explains evidence instead of showing an opaque score',()=>{
 const html=masteryPanel({mastery:[{topic:'CIDR',subject:'Redes',mastery_score:64,correct_answers:4,attempts:5,practice_count:2,hints_used:1,next_review:'hoy'}]});
 assert.ok(html.includes('En desarrollo'));
 assert.ok(html.includes('4/5'));
 assert.ok(html.includes('2'));
 assert.ok(html.includes('1'));
 assert.ok(html.includes('Qué sabes y por qué Allen lo cree'));
});

test('recommendation is a clear actionable card',()=>{
 const html=recommendationPanel({recommendation:{reason:'Repasa CIDR antes de Subnetting'}});
 assert.ok(html.includes('ALLEN RECOMIENDA'));
 assert.ok(html.includes('Empezar una práctica'));
});

test('Teacher Studio exposes professional internal navigation',()=>{
 const html=teacherStudioPage();
 for(const label of ['Crear curso','Analytics','Cursos','Revisión']) assert.ok(html.includes(label));
 assert.ok(html.includes('MODO PROFESOR'));
});
