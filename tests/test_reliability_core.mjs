import test from 'node:test';
import assert from 'node:assert/strict';
import {teacherStudioPage} from '../frontend/components/course-studio.js';

test('Teacher Studio remains the entry point for versioned course workflows',()=>{
 const html=teacherStudioPage();
 assert.ok(html.includes('ALLEN TEACHER STUDIO'));
 assert.ok(html.includes('teacher-course-list'));
});
