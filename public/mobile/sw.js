// Scope and cache are limited to the public mobile sample. Never cache desktop API/data.
const VERSION='allen-mobile-shell-v7';
const ROOT=new URL('./',self.location).pathname;
const FILES=['./','./index.html','./mobile.css','./app.mjs','./engine.mjs','./storage.mjs','./course.mjs','./course-extensions.mjs','./guided-tutor.mjs','./companion.mjs','./variants.mjs','./learning-tools.mjs','./extra-courses.mjs','./scenario-courses.mjs','./capabilities.mjs','./manifest.webmanifest','./assets/allen-user-logo.png','./assets/allen-reading.png','./assets/allen-celebrate.png','./assets/allen-thinking-v1.png','./assets/allen-explaining-v1.png'];
const URLS=FILES.map(f=>new URL(f,self.location).href);
self.addEventListener('install',event=>{event.waitUntil((async()=>{const cache=await caches.open(VERSION);try{await cache.addAll(URLS);}catch(error){await caches.delete(VERSION);throw error;}})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith('allen-mobile-shell-')&&key!==VERSION)await caches.delete(key);await self.clients.claim();})());});
self.addEventListener('fetch',event=>{
 const u=new URL(event.request.url);if(event.request.method!=='GET'||u.origin!==self.location.origin||!u.pathname.startsWith(ROOT))return;
 // Cache only explicit bundled resources. No backups, imports, APIs, auth or dynamic data.
 const canonical=new URL(u.pathname,self.location.origin).href;
 if(!URLS.includes(canonical))return;
 event.respondWith((async()=>{const cache=await caches.open(VERSION);return await cache.match(canonical)||fetch(event.request);})());
});
self.addEventListener('message',event=>{if(event.data?.type!=='CACHE_STATUS'||!event.ports[0])return;event.waitUntil((async()=>{const cache=await caches.open(VERSION);const present=await Promise.all(URLS.map(u=>cache.match(u)));event.ports[0].postMessage({type:'CACHE_STATUS',ready:present.every(Boolean),version:VERSION});})());});
