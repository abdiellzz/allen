import {setPageMetadata} from './page-metadata.mjs';

export function showActionError(message) {
  const panel = document.querySelector('#action-error');
  if (!panel) return;
  panel.querySelector('[data-error-message]').textContent = message;
  panel.hidden = false;
  panel.scrollIntoView({block: 'nearest', behavior: 'instant'});
  panel.focus({preventScroll: true});
}

export function showStartupError(kind = 'startup') {
  const main = document.querySelector('#content');
  if (!main) return;
  setPageMetadata('error');
  document.querySelector('#navigation')?.setAttribute('hidden', '');
  document.querySelector('#section-menu')?.setAttribute('hidden', '');
  const storage = kind === 'storage';
  main.innerHTML = `<section class="panel startup-error" role="alert"><img src="./assets/allen-thinking-v1.png" width="96" height="96" alt="Allen pensando cómo ayudarte"><h1>${storage ? 'No pudimos abrir el almacenamiento' : 'No pudimos abrir ALLEN'}</h1><p>${storage ? 'ALLEN necesita almacenamiento local para guardar tu progreso. Comprueba los permisos del navegador y recarga.' : 'Puede faltar un recurso o haber ocurrido un problema al cargar. Si es tu primera visita, comprueba la conexión e inténtalo de nuevo.'}</p><p>No hemos borrado tus datos. Evita borrar el almacenamiento o desinstalar la app sin una copia de progreso.</p><div class="actions"><button type="button" data-reload>Intentar de nuevo</button><a href="./error.html">Ver opciones de ayuda</a></div></section>`;
  main.querySelector('[data-reload]').addEventListener('click', () => location.reload());
  main.focus();
}

export function installErrorControls() {
  document.querySelector('#dismiss-error')?.addEventListener('click', () => {
    document.querySelector('#action-error').hidden = true;
    document.querySelector('#content').focus({preventScroll: true});
  });
}
