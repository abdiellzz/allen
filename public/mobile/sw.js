// Scope and cache are limited to the public mobile sample. Never cache desktop API/data.
const VERSION='allen-mobile-shell-v12';
const ROOT=new URL('./',self.location).pathname;
const FILES=['./','./index.html','./mobile.css','./glass-and-trail.css','./app.mjs','./engine.mjs','./storage.mjs','./course.mjs','./course-extensions.mjs','./guided-tutor.mjs','./companion.mjs','./variants.mjs','./activities.mjs','./activity-ui.mjs','./reinforcement.mjs','./reinforcement-content.mjs','./school-courses.mjs','./school-content.mjs','./workshops.mjs','./workshop-content.mjs','./learning-labs.mjs','./lab-ui.mjs','./topic-models.mjs','./learning-coach.mjs','./route-discovery.mjs','./allen-trail.mjs','./learning-tools.mjs','./extra-courses.mjs','./scenario-courses.mjs','./capabilities.mjs','./manifest.webmanifest','./assets/allen-user-logo.png','./assets/rank-explorer.webp','./assets/allen-explorer-game-v1.webp','./assets/allen-forest-game-v1.webp','./assets/rank-apprentice.webp','./assets/rank-builder.webp','./assets/rank-analyst.webp','./assets/rank-mentor.webp','./assets/allen-reading.png','./assets/allen-celebrate.png','./assets/allen-thinking-v1.png','./assets/allen-explaining-v1.png'];
FILES.push('./bootstrap.mjs','./page-metadata.mjs','./error-ui.mjs','./legal-errors.css','./legal.css','./privacidad.html','./terminos.html','./contacto.html','./404.html','./error.html');
const URLS=FILES.map(f=>new URL(f,self.location).href);
const navigationHtml=html=>html.replace('<head>',`<head><base href="${ROOT}">`);
async function navigationResponse(page,status){
 const headers=new Headers(page.headers);
 for(const name of ['content-length','content-encoding','etag'])headers.delete(name);
 headers.set('Content-Type','text/html; charset=utf-8');
 return new Response(navigationHtml(await page.text()),{status,headers});
}
self.addEventListener('install',event=>{event.waitUntil((async()=>{const cache=await caches.open(VERSION);try{await cache.addAll(URLS);}catch(error){await caches.delete(VERSION);throw error;}})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith('allen-mobile-shell-')&&key!==VERSION)await caches.delete(key);await self.clients.claim();})());});
self.addEventListener('fetch',event=>{
 const u=new URL(event.request.url);if(event.request.method!=='GET'||u.origin!==self.location.origin||!u.pathname.startsWith(ROOT))return;
 // Cache only explicit bundled resources. No backups, imports, APIs, auth or dynamic data.
 const canonical=new URL(u.pathname,self.location.origin).href;
 if(!URLS.includes(canonical)){
  // Navigation only: never turn API requests or imported data into HTML.
  if(event.request.mode!=='navigate')return;
  event.respondWith((async()=>{
   const cache=await caches.open(VERSION);
   try{const response=await fetch(event.request);if(response.status!==404)return response;const page=await cache.match(new URL('./404.html',self.location).href);return page?await navigationResponse(page,404):response;}
   catch{const page=await cache.match(new URL('./error.html',self.location).href);return page?await navigationResponse(page,503):new Response('No se pudo abrir esta página. Vuelve a ALLEN.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});}
  })());return;
 }
 event.respondWith((async()=>{const cache=await caches.open(VERSION);return await cache.match(canonical)||fetch(event.request);})());
});
self.addEventListener('message',event=>{if(event.data?.type!=='CACHE_STATUS'||!event.ports[0])return;event.waitUntil((async()=>{const cache=await caches.open(VERSION);const present=await Promise.all(URLS.map(u=>cache.match(u)));event.ports[0].postMessage({type:'CACHE_STATUS',ready:present.every(Boolean),version:VERSION});})());});
