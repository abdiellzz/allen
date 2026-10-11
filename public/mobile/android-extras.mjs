// Extras for the Android APK only (app.mjs imports this file when bundled in the APK):
// a guided tour adapted to the goal chosen in the profile, and an "Actualizar ALLEN" panel.
// It moves around by clicking the app's own section buttons; it never changes learning data.
const TOUR_KEY = 'allen-mobile-tour';
const APK_URL = 'https://github.com/abdiellzz/allen/raw/main/android/release/ALLEN-demo-android.apk';
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const stylesheet = document.createElement('link');
stylesheet.rel = 'stylesheet';
stylesheet.href = new URL('./android-extras.css', import.meta.url).href;
document.head.append(stylesheet);

const installedVersion = fetch('/allen-manifest.json', {cache: 'no-store'})
  .then(response => response.json()).then(manifest => manifest.allen || '', () => '');

const GOALS = {
  school: {
    label: 'Reforzar la escuela',
    intro: 'Elegiste reforzar lo que aprendes en la escuela. Te muestro en un minuto dónde está cada cosa y qué puedes hacer.',
    today: 'Empieza por el diagnóstico: unas preguntas breves para saber dónde necesitas apoyo. No es una calificación. Después te propongo una lección o un repaso.',
    learn: 'Elige el curso que estás viendo en clase y sigue su ruta. Cada lección se abre al comprobar la anterior.',
    can: ['Hacer el diagnóstico y reforzar los temas de clase', 'Estudiar lecciones con pistas, misiones y tarjetas de repaso',
      'Ver tu progreso por tema y guardar una copia'],
  },
  explore: {
    label: 'Aprender algo nuevo',
    intro: 'Elegiste aprender algo nuevo por tu cuenta. Te muestro en un minuto dónde está cada cosa y qué puedes hacer.',
    today: 'Aquí te propongo qué hacer ahora: el diagnóstico del curso elegido, una lección nueva o un repaso pendiente.',
    learn: 'Busca un tema que te interese, elige una ruta de cualquier área y avanza a tu ritmo.',
    can: ['Explorar las rutas de todas las áreas y cambiar de curso cuando quieras', 'Estudiar lecciones con pistas, misiones y tarjetas de repaso',
      'Ver tu progreso por tema y guardar una copia'],
  },
};
const CANNOT = ['Crear o editar cursos: vienen incluidos en la app',
  'Sincronizar con otros dispositivos: tu progreso se queda en este teléfono', 'Guardar la copia como archivo: por ahora se copia como texto'];

function stepsFor(goal, name) {
  const g = GOALS[goal] ?? GOALS.school;
  return [
    {image: 'allen-reading.png', title: `Hola, ${name}`, text: g.intro},
    {view: 'today', target: '.recommended', image: 'allen-reading.png', title: 'Hoy', text: g.today},
    {target: '#section-menu > summary', image: 'allen-reading.png', title: 'Secciones',
      text: 'Desde este menú pasas a Hoy, Aprender, Practicar, Allen y Mi progreso.'},
    {view: 'learn', target: '.catalogue', image: 'allen-reading.png', title: 'Aprender', text: g.learn},
    {view: 'practice', image: 'allen-reading.png', title: 'Practicar',
      text: 'Misiones para aplicar lo aprendido y tarjetas de repaso, que se habilitan al superar la comprobación de cada lección.'},
    {view: 'allen', image: 'allen-reading.png', title: 'Allen',
      text: 'Elige preguntas sobre cualquier curso o la app. Te explico con ejemplos preparados y te doy pistas por pasos. Las ayudas de una actividad quedan registradas en tu progreso.'},
    {view: 'progress', image: 'allen-reading.png', title: 'Mi progreso',
      text: 'Tu dominio estimado por tema, con aciertos, pistas y próximos repasos. Aquí también puedes hacer una copia de tu progreso.'},
    {target: '#profiles-button', image: 'allen-reading.png', title: 'Perfiles',
      text: 'Cambia de perfil o crea otro (cada uno guarda su propio progreso), recupera una copia, actualiza ALLEN y repite este recorrido.'},
    {image: 'allen-reading.png', title: `Qué puedes hacer · ${g.label}`, can: g.can, cannot: CANNOT},
    {image: 'allen-celebrate.png', title: '¡A aprender!', text: 'Puedes repetir el recorrido cuando quieras desde Perfiles.'},
  ];
}

let seen = {};
try { seen = JSON.parse(localStorage.getItem(TOUR_KEY) || '{}') || {}; } catch { seen = {}; }
const remember = (key, value) => {
  seen[key] = value;
  try { localStorage.setItem(TOUR_KEY, JSON.stringify(seen)); } catch { /* storage blocked */ }
};

let layer = null, ring = null, sheet = null, steps = [], index = 0, goal = null, returnFocus = null;
const isOpen = () => Boolean(layer?.isConnected);

function build() {
  if (layer) return;
  layer = document.createElement('div');
  layer.className = 'allen-tour';
  layer.innerHTML = '<div class="allen-tour-ring" hidden></div><section class="allen-tour-sheet" role="dialog" aria-modal="true" aria-labelledby="allen-tour-title"></section>';
  ring = layer.querySelector('.allen-tour-ring');
  sheet = layer.querySelector('.allen-tour-sheet');
  layer.addEventListener('click', onClick);
  document.addEventListener('keydown', event => { if (isOpen() && event.key === 'Escape') close(true); });
  addEventListener('resize', place);
  addEventListener('scroll', place, {passive: true});
}

async function openView(view) {
  const button = document.querySelector(`#navigation button[data-view="${view}"]`);
  if (!button || button.getAttribute('aria-current') === 'page') return;
  button.click();
  await sleep(150);
  scrollTo(0, 0);
}

async function start(profile) {
  build();
  goal = GOALS[profile.goal] ? profile.goal : 'school';
  steps = stepsFor(goal, profile.name);
  index = 0;
  returnFocus = document.activeElement;
  document.body.append(layer);
  document.documentElement.classList.add('allen-tour-open');
  await show();
}

function close(skipped) {
  if (goal) remember(goal, skipped ? 'skipped' : 'done');
  goal = null;
  layer?.remove();
  document.documentElement.classList.remove('allen-tour-open');
  openView('today');
  if (returnFocus?.isConnected) returnFocus.focus();
}

async function show() {
  const step = steps[index], last = index === steps.length - 1;
  if (step.view) await openView(step.view);
  const lists = step.can
    ? `<div class="allen-tour-lists"><div class="allen-tour-can"><h3>Puedes</h3><ul>${step.can.map(i => `<li>${escape(i)}</li>`).join('')}</ul></div>` +
      `<div class="allen-tour-cannot"><h3>No puedes</h3><ul>${step.cannot.map(i => `<li>${escape(i)}</li>`).join('')}</ul></div></div>`
    : '';
  sheet.innerHTML =
    `<div class="allen-tour-head"><span class="eyebrow">Recorrido · ${index + 1} de ${steps.length}</span>` +
    (last ? '' : '<button type="button" class="allen-tour-skip" data-tour="skip">Saltar recorrido</button>') + '</div>' +
    `<div class="allen-tour-body"><img src="./assets/${step.image}" alt="" width="80" height="80"><div>` +
    `<h2 id="allen-tour-title">${escape(step.title)}</h2>${step.text ? `<p>${escape(step.text)}</p>` : ''}</div></div>${lists}` +
    '<div class="allen-tour-actions">' + (index ? '<button type="button" data-tour="back">Atrás</button>' : '<span></span>') +
    `<button type="button" class="primary" data-tour="next">${last ? 'Empezar' : 'Siguiente'}</button></div>`;
  place();
  sheet.querySelector('[data-tour="next"]').focus();
}

function place() {
  if (!isOpen()) return;
  const step = steps[index];
  const target = step.target && document.querySelector(step.target);
  const box = target?.getBoundingClientRect();
  const visible = Boolean(box && box.width && box.height);
  ring.hidden = !visible;
  layer.classList.toggle('allen-tour-dim', !visible);
  if (visible) {
    const pad = 6;
    ring.style.setProperty('--x', `${Math.max(4, box.left - pad)}px`);
    ring.style.setProperty('--y', `${Math.max(4, box.top - pad)}px`);
    ring.style.setProperty('--w', `${Math.min(innerWidth - 8, box.width + pad * 2)}px`);
    ring.style.setProperty('--h', `${Math.min(innerHeight - 8, box.height + pad * 2)}px`);
  }
  // Keep the sheet away from what it points at.
  const low = visible && box.top + Math.min(box.height, innerHeight) / 2 > innerHeight / 2;
  sheet.className = `allen-tour-sheet ${low ? 'allen-tour-top' : 'allen-tour-bottom'}`;
}

async function onClick(event) {
  const action = event.target.closest('[data-tour]')?.dataset.tour;
  if (action === 'skip') close(true);
  else if (action === 'back' && index > 0) { index--; await show(); }
  else if (action === 'next') {
    if (index === steps.length - 1) close(false);
    else { index++; await show(); }
  }
}

function addProfilePanels(main, profile) {
  if (main.querySelector('#allen-apk-update')) return;
  const update = document.createElement('section');
  update.id = 'allen-apk-update';
  update.className = 'panel allen-extra-panel';
  update.innerHTML = '<span class="eyebrow">App de Android</span><h2>Actualizar ALLEN</h2>' +
    '<p>Versión instalada: <strong class="allen-apk-version">demo</strong>. Guarda una copia privada de tu progreso antes de instalar. La actualización conserva datos cuando coincide la firma de la APK. Si Android rechaza la actualización, conserva la app anterior hasta tener tu copia.</p>' +
    `<a class="allen-extra-button" href="${APK_URL}">Descargar actualización</a>` +
    '<p class="small muted">Se abre en el navegador del teléfono y necesita una cuenta de GitHub con acceso a ALLEN. La app no se conecta a Internet, así que no puede comprobar sola si hay una versión nueva.</p>';
  installedVersion.then(version => { if (version) update.querySelector('.allen-apk-version').textContent = version; });
  main.append(update);
  if (!profile) return;
  const tour = document.createElement('section');
  tour.className = 'panel allen-extra-panel';
  tour.innerHTML = '<span class="eyebrow">Primeros pasos</span><h2>Recorrido por ALLEN</h2>' +
    `<p>Vuelve a ver qué hay en cada sección y qué puedes hacer, según lo que elegiste para ${escape(profile.name)}.</p>` +
    '<button type="button" class="secondary" data-allen-tour-replay>Ver el recorrido</button>';
  tour.querySelector('[data-allen-tour-replay]').addEventListener('click', () => start(profile));
  update.before(tour);
}

// Called by app.mjs after every screen it draws.
export function rendered({view, profile, main}) {
  if (view === 'profiles') { addProfilePanels(main, profile); return; }
  if (profile && !isOpen() && !seen[profile.goal]) start(profile);
}

