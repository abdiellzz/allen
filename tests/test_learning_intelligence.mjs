import test from 'node:test';
import assert from 'node:assert/strict';
import {masteryPanel,reviewPanel} from '../frontend/components/continuity.js';
import {teacherStudioPage} from '../frontend/components/course-studio.js';

test('mastery UI explains evidence instead of showing a naked score',()=>{
 const html=masteryPanel({mastery:[{subject:'Redes',topic:'CIDR',mastery_score:64,status:'practicing',attempts:5,correct_answers:4,practice_count:2,hints_used:1}]});
 assert.ok(html.includes('EVIDENCIA DE DOMINIO'));
 assert.ok(html.includes('4/5'));
 assert.ok(html.includes('2 prácticas'));
});

test('Home can show centralized spaced topic reviews',()=>{
 const html=reviewPanel({due_topic_reviews:[{subject:'Redes',topic:'CIDR',mastery_score:64,next_review:'2026-10-07'}]});
 assert.ok(html.includes('REPASO ESPACIADO'));
 assert.ok(html.includes('CIDR'));
});

test('Teacher Studio includes local analytics surface',()=>{
 assert.ok(teacherStudioPage().includes('teacher-analytics'));
});
