import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const app=fs.readFileSync(new URL('../frontend/app.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../frontend/styles/v2.css',import.meta.url),'utf8');
const studio=fs.readFileSync(new URL('../frontend/components/course-studio.js',import.meta.url),'utf8');

test('Visual Polish v4 exposes Ctrl+K command palette and local search',()=>{
 assert.ok(app.includes('command-palette'));
 assert.ok(app.includes("e.key.toLowerCase()==='k'"));
 assert.ok(app.includes('Buscar cursos, temas y acciones'));
 assert.ok(app.includes('commandItems'));
});

test('Visual Polish v4 supports persistent light and dark themes',()=>{
 assert.ok(app.includes("allen-theme"));
 assert.ok(app.includes("document.documentElement.dataset.theme"));
 assert.ok(css.includes('html[data-theme="dark"]'));
});

test('Progress Dashboard v4 exposes actionable learning KPIs',()=>{
 for(const term of ['PANORAMA DE APRENDIZAJE','Temas dominados','Por reforzar','ACTIVIDAD RECIENTE']) assert.ok(app.includes(term));
 assert.ok(css.includes('.v4-mastery-donut'));
});

test('Course route exposes graphical Learning Journey',()=>{
 assert.ok(studio.includes('LEARNING JOURNEY'));
 assert.ok(studio.includes('learning-journey-track'));
 assert.ok(studio.includes('Recorrido del curso'));
});
