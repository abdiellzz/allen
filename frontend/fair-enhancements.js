const main=document.querySelector('#fair-main');
document.body.classList.add('allen-refresh');

function addHeaderPill(){
  const nav=document.querySelector('header nav');
  if(!nav||nav.querySelector('.allen-local-pill'))return;
  const pill=document.createElement('span');
  pill.className='allen-local-pill';
  pill.textContent='Local · privado';
  pill.title='ALLEN funciona en este equipo y no necesita una cuenta para esta experiencia.';
  nav.prepend(pill);
}

function isHome(){
  const h1=main?.querySelector('h1');
  return Boolean(h1&&/Aprende con inteligencia artificial/i.test(h1.textContent));
}

function isOffline(){
  const h1=main?.querySelector('h1');
  return Boolean(h1&&/Desafío sin Internet/i.test(h1.textContent));
}

function enhanceHome(){
  if(!isHome()||main.querySelector('[data-allen-refresh-home]'))return;
  const hero=main.querySelector('.hero');
  const firstHeading=[...main.querySelectorAll(':scope > h2')].find(el=>/qué quieres probar/i.test(el.textContent));
  if(!hero||!firstHeading)return;

  const launcher=document.createElement('section');
  launcher.className='allen-refresh-launcher';
  launcher.dataset.allenRefreshHome='true';
  launcher.innerHTML=`
    <div class="allen-refresh-launcher-head">
      <strong>Empieza en segundos</strong>
      <span>Sin cuenta · tu progreso queda en este dispositivo</span>
    </div>
    <div class="allen-quick-actions" aria-label="Accesos rápidos">
      <button data-go="chat">Pregúntale a Allen</button>
      <button data-go="learn">Aprende en 1 minuto</button>
      <button data-go="challenge">Haz un reto</button>
      <button data-go="game">Juega y practica</button>
    </div>`;
  firstHeading.before(launcher);

  const deck=document.createElement('section');
  deck.className='allen-explore-deck';
  deck.innerHTML=`
    <div class="allen-explore-art">
      <img src="/static/assets/allen-study-space.svg" alt="Allen explorando matemáticas, programación y una ruta de aprendizaje">
    </div>
    <div class="allen-explore-copy">
      <span class="eyebrow">Tu compañero de estudio</span>
      <h2>No solo respondas: prueba, falla y vuelve a intentar.</h2>
      <p>ALLEN combina actividades cortas, conversación local y práctica para que cada sesión termine con algo que realmente entendiste.</p>
      <div class="allen-feature-list">
        <div class="allen-feature-item"><b>01</b><span><strong>Pregunta.</strong> Explica con palabras simples o sube el nivel cuando quieras.</span></div>
        <div class="allen-feature-item"><b>02</b><span><strong>Practica.</strong> Convierte la explicación en un reto, quiz o ejercicio.</span></div>
        <div class="allen-feature-item"><b>03</b><span><strong>Recuerda.</strong> Usa tarjetas y progreso local para reforzar lo importante.</span></div>
      </div>
    </div>`;
  const grid=main.querySelector('.grid');
  if(grid)grid.after(deck);

  const path=document.createElement('section');
  path.className='allen-learning-path';
  path.innerHTML=`
    <div>
      <span class="eyebrow">Método ALLEN</span>
      <h2>Aprender también puede sentirse como avanzar.</h2>
      <p>Empieza con una idea, conviértela en práctica, comprueba lo que sabes y vuelve cuando quieras. Todo sin depender de una nube.</p>
      <div class="allen-path-tags"><span>Descubre</span><span>Practica</span><span>Comprueba</span><span>Domina</span></div>
    </div>
    <img src="/static/assets/learning-path.svg" alt="Ruta visual de cuatro pasos: descubre, practica, comprueba y domina">`;
  deck.after(path);
}

function enhanceOffline(){
  if(!isOffline()||main.querySelector('.offline-visual'))return;
  const hero=main.querySelector('.hero');
  if(!hero)return;
  const section=document.createElement('section');
  section.className='offline-visual';
  section.innerHTML=`
    <div>
      <span class="eyebrow">Privacidad por diseño</span>
      <h2>Tu sesión puede quedarse aquí.</h2>
      <p>Las actividades deterministas, el progreso y el modelo local funcionan en tu equipo. ALLEN está diseñado para poder enseñar incluso cuando la conexión no está disponible.</p>
    </div>
    <img src="/static/assets/privacy-local.svg" alt="Computadora con recursos educativos y un candado que representa privacidad local">`;
  hero.after(section);
}

function enhanceChat(){
  const form=main?.querySelector('.chat-form');
  if(!form||main.querySelector('.allen-chat-starters'))return;
  const helper=document.createElement('section');
  helper.className='allen-chat-starters';
  helper.innerHTML=`
    <p>¿No sabes cómo empezar? Prueba una de estas ideas:</p>
    <div class="chips">
      <button type="button" data-allen-prompt="Explícame un tema con un ejemplo sencillo">Explícame algo</button>
      <button type="button" data-allen-prompt="Ponme un reto corto y no me des la respuesta todavía">Ponme un reto</button>
      <button type="button" data-allen-prompt="Ayúdame a estudiar paso a paso">Estudiemos</button>
      <button type="button" data-allen-prompt="Explícame algo de programación desde cero">Programación</button>
    </div>`;
  form.before(helper);
}

function bindPromptButtons(){
  main?.querySelectorAll('[data-allen-prompt]:not([data-bound])').forEach(btn=>{
    btn.dataset.bound='1';
    btn.addEventListener('click',()=>{
      const input=main.querySelector('.chat-form input,.chat-form textarea');
      if(!input)return;
      input.value=btn.dataset.allenPrompt||'';
      input.dispatchEvent(new Event('input',{bubbles:true}));
      input.focus();
    });
  });
}

function bindTileMotion(){
  if(matchMedia('(prefers-reduced-motion: reduce)').matches||!matchMedia('(pointer:fine)').matches)return;
  main?.querySelectorAll('.tile:not([data-tilt-ready])').forEach(tile=>{
    tile.dataset.tiltReady='1';
    tile.addEventListener('pointermove',event=>{
      const rect=tile.getBoundingClientRect();
      const x=(event.clientX-rect.left)/rect.width;
      const y=(event.clientY-rect.top)/rect.height;
      tile.style.setProperty('--tilt-y',`${((x-.5)*5).toFixed(2)}deg`);
      tile.style.setProperty('--tilt-x',`${((.5-y)*5).toFixed(2)}deg`);
      tile.style.setProperty('--glow-x',`${(x*100).toFixed(1)}%`);
      tile.style.setProperty('--glow-y',`${(y*100).toFixed(1)}%`);
    });
    tile.addEventListener('pointerleave',()=>{
      tile.style.setProperty('--tilt-x','0deg');
      tile.style.setProperty('--tilt-y','0deg');
    });
  });
}

function enhance(){
  addHeaderPill();
  enhanceHome();
  enhanceOffline();
  enhanceChat();
  bindPromptButtons();
  bindTileMotion();
}

const observer=new MutationObserver(()=>requestAnimationFrame(enhance));
if(main)observer.observe(main,{childList:true,subtree:true});
window.addEventListener('DOMContentLoaded',enhance);
enhance();
