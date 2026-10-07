import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const app=fs.readFileSync(new URL('../frontend/app.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../frontend/styles/v2.css',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../frontend/components/ui.js',import.meta.url),'utf8');

test('product finish exposes accessible command dialog and focus return',()=>{
 assert.ok(app.includes('id="command-title"'));
 assert.ok(app.includes('aria-labelledby="command-title"'));
 assert.ok(app.includes('role="listbox"'));
 assert.ok(app.includes('role="option"'));
 assert.ok(app.includes('commandReturnFocus'));
});

test('global page rendering exposes busy and retry states',()=>{
 assert.ok(app.includes("content.setAttribute('aria-busy','true')"));
 assert.ok(app.includes("content.setAttribute('aria-busy','false')"));
 assert.ok(app.includes('id="retry-page"'));
 assert.ok(app.includes('Tus datos locales no se borraron'));
});

test('loading and empty states are structured and accessible',()=>{
 assert.ok(ui.includes('allen-loader-shell'));
 assert.ok(ui.includes('aria-busy="true"'));
 assert.ok(ui.includes('skeleton-grid'));
 assert.ok(ui.includes('polished-empty'));
});

test('responsive finish includes phone breakpoint and focus visibility',()=>{
 assert.ok(css.includes('@media(max-width:430px)'));
 assert.ok(css.includes(':focus-visible'));
 assert.ok(css.includes('.global-error'));
 assert.ok(css.includes('.skeleton-grid'));
});
