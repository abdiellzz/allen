import {test} from 'node:test';
import assert from 'node:assert/strict';
import {markdown} from '../frontend/components/markdown.js';

test('raw HTML and scripts are escaped',()=>{
 const output=markdown('<img src=x onerror=alert(1)>\n<script>alert(1)</script>');
 assert.ok(!output.includes('<img'));assert.ok(!output.includes('<script>'));assert.ok(output.includes('&lt;script&gt;'));
});
test('code, tables, lists and headings remain readable',()=>{
 const output=markdown('# Título\n- Uno\n- Dos\n\n```html\n<script>x</script>\n```\n\n| A | B |\n| --- | --- |\n| 1 | 2 |');
 for(const expected of ['<h2>Título</h2>','<li>Uno</li>','<pre><code>&lt;script&gt;x&lt;/script&gt;','<table>','<td>2</td>'])assert.ok(output.includes(expected));
});
test('links and images never fetch external content',()=>{
 const output=markdown('![x](https://remote.example/track) [click](javascript:alert(1))');
 assert.ok(!output.includes('<a'));assert.ok(!output.includes('<img'));
});
