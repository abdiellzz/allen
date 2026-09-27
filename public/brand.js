const menuButton = document.querySelector('.menu-toggle');
const mobileNav = document.querySelector('.mobile-nav');

if (menuButton && mobileNav) {
  menuButton.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!expanded));
    menuButton.setAttribute('aria-label', expanded ? 'Abrir menú' : 'Cerrar menú');
    mobileNav.hidden = expanded;
  });
  mobileNav.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Abrir menú');
      mobileNav.hidden = true;
    }
  });
}

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.documentElement.classList.add('has-motion');
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

const demoBoard = document.querySelector('[data-demo-board]');
const demoNext = document.querySelector('[data-demo-next]');
if (demoBoard && demoNext) {
  const messages = [
    'El flujo comienza con una solicitud de ejemplo. Aún no se ha procesado información.',
    'En un proyecto real se definiría cómo organizar la información y qué datos se pueden usar.',
    'Una persona revisaría la propuesta y decidiría qué hacer. Esta demostración no envía respuestas.'
  ];
  let activeStep = 0;
  demoNext.addEventListener('click', () => {
    activeStep = (activeStep + 1) % messages.length;
    demoBoard.dataset.step = String(activeStep);
    demoBoard.querySelectorAll('[data-demo-step]').forEach((step) => {
      const active = Number(step.dataset.demoStep) === activeStep;
      step.classList.toggle('is-active', active);
      if (active) step.setAttribute('aria-current', 'step');
      else step.removeAttribute('aria-current');
    });
    const counter = demoBoard.querySelector('[data-demo-counter]');
    const message = demoBoard.querySelector('[data-demo-message]');
    counter.textContent = `PASO ${activeStep + 1} DE ${messages.length}`;
    message.textContent = messages[activeStep];
    demoNext.innerHTML = activeStep === messages.length - 1
      ? 'Volver al inicio <span aria-hidden="true">↺</span>'
      : 'Ver siguiente paso <span aria-hidden="true">→</span>';
  });
}

const cases = {
  service: {
    eyebrow: 'POSIBLE ÁREA DE EXPLORACIÓN',
    title: 'Atención y solicitudes',
    description: 'Explorar si un agente podría clasificar solicitudes frecuentes y preparar un borrador para que el equipo lo revise.',
    boundary: 'El equipo valida la categoría y aprueba cualquier respuesta antes de enviarla.'
  },
  documents: {
    eyebrow: 'POSIBLE ÁREA DE EXPLORACIÓN',
    title: 'Documentos y conocimiento',
    description: 'Estudiar una forma de encontrar información dentro de documentos autorizados y presentar referencias para revisión.',
    boundary: 'Una persona confirma que la fuente sea pertinente y que la respuesta represente el documento.'
  },
  operations: {
    eyebrow: 'POSIBLE ÁREA DE EXPLORACIÓN',
    title: 'Tareas operativas',
    description: 'Mapear pasos repetidos y evaluar si una herramienta podría preparar resúmenes, listas o avisos para el equipo.',
    boundary: 'El equipo define las reglas, revisa el resultado y conserva las decisiones importantes.'
  }
};

const caseTabs = [...document.querySelectorAll('[data-case]')];
const casePanel = document.querySelector('#case-panel');
if (caseTabs.length && casePanel) {
  const selectCase = (tab) => {
    const item = cases[tab.dataset.case];
    caseTabs.forEach((candidate) => {
      const selected = candidate === tab;
      candidate.setAttribute('aria-selected', String(selected));
      candidate.tabIndex = selected ? 0 : -1;
    });
    casePanel.setAttribute('aria-labelledby', tab.id);
    casePanel.querySelector('[data-case-eyebrow]').textContent = item.eyebrow;
    casePanel.querySelector('[data-case-title]').textContent = item.title;
    casePanel.querySelector('[data-case-description]').textContent = item.description;
    casePanel.querySelector('[data-case-boundary]').textContent = item.boundary;
  };
  caseTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectCase(tab));
    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const nextIndex = event.key === 'Home' ? 0
        : event.key === 'End' ? caseTabs.length - 1
          : (index + (event.key === 'ArrowRight' ? 1 : -1) + caseTabs.length) % caseTabs.length;
      caseTabs[nextIndex].focus();
      selectCase(caseTabs[nextIndex]);
    });
  });
}
