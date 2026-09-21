import {test} from 'node:test';
import assert from 'node:assert/strict';
import {api,setToken,streamChat} from '../frontend/services.js';

test('local writes include the instance token',async()=>{
 setToken('test-token');let captured;
 globalThis.fetch=async(url,options)=>{captured={url,...options};return new Response('{"ok":true}');};
 assert.equal((await api('/chat','POST',{message:'hola'})).ok,true);
 assert.equal(captured.url,'/api/chat');assert.equal(captured.headers['X-Allen-Token'],'test-token');
});
test('connection and malformed responses become friendly Spanish messages',async()=>{
 globalThis.fetch=async()=>{throw new TypeError('Failed to fetch');};
 await assert.rejects(api('/health'),/No pudimos conectar con Allen/);
 globalThis.fetch=async()=>new Response('not JSON');
 await assert.rejects(api('/health'),/Allen no pudo leer/);
});
test('streaming reconstructs fragmented UTF-8 and NDJSON',async()=>{
 const bytes=new TextEncoder().encode('{"type":"delta","text":"🐵 Fracción"}\n{"type":"done"}\n');
 globalThis.fetch=async()=>new Response(new ReadableStream({start(controller){for(const byte of bytes)controller.enqueue(new Uint8Array([byte]));controller.close();}}));
 const events=[];await streamChat({},new AbortController().signal,e=>events.push(e));
 assert.equal(events[0].text,'🐵 Fracción');assert.equal(events.at(-1).type,'done');
});
test('abort preserves cancellation semantics',async()=>{
 globalThis.fetch=async()=>{throw new DOMException('Aborted','AbortError');};
 await assert.rejects(streamChat({},new AbortController().signal,()=>{}),{name:'AbortError'});
});
