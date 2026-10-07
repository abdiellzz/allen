import test from 'node:test';
import assert from 'node:assert/strict';
import {allenGuide,learningStepRail} from '../frontend/components/allen-guide.js';
import {teacherStudioPage,coursesPage} from '../frontend/components/course-studio.js';

test('Allen guide uses canonical brand variants and guided copy',()=>{
  const html=allenGuide('teaching','Primero entendamos esto juntos.');
  assert.ok(html.includes('allen-teaching-official.svg'));
  assert.ok(html.includes('Primero entendamos'));
  assert.ok(learningStepRail(2).includes('current'));
});

test('Teacher Studio exposes local import and review workflow',()=>{
  const html=teacherStudioPage();
  assert.ok(html.includes('ALLEN TEACHER STUDIO'));
  assert.ok(html.includes('course-file'));
  assert.ok(html.includes('PDF'));
  assert.ok(coursesPage().includes('CURSOS EN ALLEN'));
});
