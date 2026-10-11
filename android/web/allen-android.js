// ALLEN Android demo: routes fetch('/api/...') to the Python backend running in allen-worker.js.
// Loaded as a classic script before the app module so the very first API call already waits for Python.
(function () {
  // Scopes allen-android.css to the APK; set on <html> because <body> does not exist yet.
  const root = document.documentElement;
  root.classList.add("allen-android");
  // The phone's light/dark setting applies until the user picks a theme with ALLEN's toggle.
  let themeChosen = false;
  try { themeChosen = Boolean(localStorage.getItem("allen-theme")); } catch (error) { /* storage blocked */ }
  if (!themeChosen) root.classList.add("allen-theme-system");
  document.addEventListener("click", event => {
    if (!root.classList.contains("allen-theme-system") || !event.target.closest("#theme-toggle")) return;
    // Runs before app.js's handler, which flips data-theme: start from what is on screen.
    if (matchMedia("(prefers-color-scheme: dark)").matches) root.dataset.theme = "dark";
    root.classList.remove("allen-theme-system");
  }, true);
  const nativeFetch = window.fetch.bind(window);
  const worker = new Worker("/static/android/allen-worker.js");
  const pending = new Map();
  let nextId = 1;

  const overlay = document.createElement("div");
  overlay.id = "allen-android-boot";
  overlay.innerHTML = '<img src="/static/assets/allen-brand.svg" alt=""><b>Iniciando ALLEN…</b><span id="allen-android-step">Preparando Python en tu teléfono</span>';
  const showOverlay = () => document.body.appendChild(overlay);
  if (document.body) showOverlay(); else document.addEventListener("DOMContentLoaded", showOverlay);
  const step = text => { const el = document.getElementById("allen-android-step"); if (el) el.textContent = text; };

  let markReady, markFailed;
  const ready = new Promise((resolve, reject) => { markReady = resolve; markFailed = reject; });
  ready.then(() => overlay.remove(), error => step("No se pudo iniciar ALLEN: " + error.message));

  worker.onmessage = ({ data }) => {
    if (data.type === "step") step(data.text);
    else if (data.type === "ready") markReady();
    else if (data.type === "failed") markFailed(new Error(data.message));
    else if (data.type === "response") {
      const request = pending.get(data.id);
      pending.delete(data.id);
      if (!request) return;
      if (data.error) request.reject(new TypeError(data.error));
      else request.resolve(JSON.parse(data.raw));
    }
  };
  worker.onerror = event => markFailed(new Error(event.message || "Error en el motor de ALLEN"));

  window.fetch = async function (input, init) {
    init = init || {};
    const url = new URL(typeof input === "string" ? input : input.url, location.href);
    if (url.origin !== location.origin || !url.pathname.startsWith("/api/")) return nativeFetch(input, init);
    await ready;
    const headers = {};
    new Headers(init.headers || {}).forEach((value, key) => { headers[key] = value; });
    const id = nextId++;
    const result = await new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
      worker.postMessage({
        type: "request",
        id,
        method: (init.method || "GET").toUpperCase(),
        url: url.pathname + url.search,
        headers: JSON.stringify(headers),
        body: typeof init.body === "string" ? init.body : "",
      });
    });
    return new Response(result.body, { status: result.status, headers: result.headers });
  };

  // APK-only option in Configuración to get the newest demo APK. MainActivity opens links that
  // leave the app in the phone's browser, so ALLEN itself still needs no Internet permission.
  const APK_URL = "https://github.com/abdiellzz/allen/raw/main/android/release/ALLEN-demo-android.apk";
  const installedVersion = nativeFetch("/allen-manifest.json")
    .then(response => response.json())
    .then(manifest => manifest.allen || "", () => "");
  function addUpdateOption(content) {
    if (!content.querySelector(".license-settings") || content.querySelector("#allen-apk-update")) return;
    const panel = document.createElement("section");
    panel.id = "allen-apk-update";
    panel.className = "panel allen-apk-update";
    panel.innerHTML =
      '<span class="eyebrow">App de Android</span><h2>Actualizar ALLEN</h2>' +
      '<p>Versión instalada: <b class="allen-apk-version">demo</b>. Descarga el APK más reciente e ' +
      "instálalo encima de esta versión: tus datos se conservan.</p>" +
      '<a class="button-like primary" href="' + APK_URL + '">Descargar actualización</a>' +
      "<small>Se abre en el navegador del teléfono y necesita una cuenta de GitHub con acceso a ALLEN.</small>";
    installedVersion.then(version => { if (version) panel.querySelector(".allen-apk-version").textContent = version; });
    const heading = content.querySelector(".page-heading");
    if (heading) heading.after(panel); else content.prepend(panel);
  }
  function addTourOption(content) {
    if (!content.querySelector("#allen-apk-update") || content.querySelector("#allen-apk-tour")) return;
    const panel = document.createElement("section");
    panel.id = "allen-apk-tour";
    panel.className = "panel allen-apk-update";
    panel.innerHTML =
      '<span class="eyebrow">Primeros pasos</span><h2>Recorrido por ALLEN</h2>' +
      "<p>Vuelve a ver qué hay en cada zona y qué puedes hacer en cada modo.</p>" +
      '<button type="button" data-allen-tour-replay>Ver el recorrido</button>';
    panel.querySelector("[data-allen-tour-replay]").addEventListener("click", () => tour.openChooser(true));
    content.querySelector("#allen-apk-update").after(panel);
  }

  // ---------- First-run tour (APK only) ----------
  // A short guided tour per workspace mode. It only clicks ALLEN's own buttons ([data-page],
  // [data-workspace-mode]) to move around, and remembers on this device what was already seen.
  const TOUR_KEY = "allen-android-tour";
  const art = name => "/static/assets/" + name + ".svg";
  const MODES = {
    student: {
      label: "Estudiante",
      home: "Inicio",
      hint: "Aprender, practicar y ver tu progreso.",
      image: "allen-reading-official",
      steps: [
        { image: "allen-guide", title: "Hola, soy Allen",
          text: "Te muestro la app en un minuto: dónde está cada cosa y qué puedes hacer como estudiante. Puedes saltar el recorrido cuando quieras." },
        { page: "Inicio", target: '#nav [data-page="Inicio"]', image: "allen-guide", title: "Inicio",
          text: "Tu punto de partida: continúa donde lo dejaste, repasa lo pendiente y hazme una pregunta desde el cuadro de arriba." },
        { page: "Aprender", target: '#nav [data-page="Aprender"]', image: "allen-course-official", title: "Aprender",
          text: "Elige una materia y te explico paso a paso, con ejemplos. Desde Aprender también llegas a Cursos, Biblioteca, Método Allen y Plan Allen." },
        { page: "Quiz", target: '#nav [data-page="Quiz"]', image: "allen-teaching-official", title: "Practicar",
          text: "Pon a prueba lo que sabes con quizzes. También tienes Tarjetas de repaso y Aventuras con misiones cortas." },
        { page: "Progreso", target: '#nav [data-page="Progreso"]', image: "allen-progress-official", title: "Progreso",
          text: "Mira qué temas dominas, cuáles están en desarrollo y qué toca repasar. Sin rankings: solo tu propio avance." },
        { page: "Perfil", target: '#nav [data-page="Perfil"]', image: "allen-reading-official", title: "Perfil",
          text: "Tu nombre, nivel e intereses. Aquí también cambias entre los modos Estudiante y Profesor." },
        { target: "#global-search-open", image: "allen-guide", title: "Buscar",
          text: "La lupa te lleva a cualquier sección: escribe, por ejemplo, Biblioteca, Tarjetas o Configuración." },
        { image: "allen-brand", title: "Qué puedes hacer como estudiante",
          can: ["Aprender, practicar y repasar a tu ritmo", "Hacer quizzes, tarjetas, aventuras y planes de estudio",
            "Ver tu progreso y cambiar tu perfil o el tema"],
          cannot: ["Crear, editar o publicar cursos: eso es del modo Profesor", "Ver la analítica de los cursos",
            "Usar la IA generativa completa: en el teléfono responde en modo demo", "Exportar respaldos: aún no está disponible en la app"] },
        { image: "allen-celebrate-official", title: "¡Listo para empezar!",
          text: "Si quieres ver el recorrido otra vez, lo tienes en Configuración." },
      ],
    },
    teacher: {
      label: "Profesor",
      home: "Teacher Studio",
      hint: "Crear cursos con tu material y revisarlos.",
      image: "allen-teaching-official",
      steps: [
        { image: "allen-teaching-official", title: "Modo Profesor",
          text: "Aquí preparas cursos con tu propio material y revisas cómo funcionan. Te muestro las zonas en un minuto." },
        { page: "Teacher Studio", target: '#nav [data-page="Teacher Studio"]', image: "allen-course-official", title: "Teacher Studio",
          text: "Tu taller: importa un PDF, TXT o Markdown y Allen arma un borrador del curso con unidades, temas y preguntas." },
        { page: "Teacher Studio", target: ".teacher-studio-nav", image: "allen-progress-official", title: "Secciones del taller",
          text: "Crear curso, Analytics, Cursos y Revisión. Nada se publica sin que revises objetivos, temas, preguntas y fuentes." },
        { page: "Configuración", target: '#nav [data-page="Configuración"]', image: "allen-guide", title: "Configuración",
          text: "Preferencias del dispositivo, accesibilidad, respaldo local, licencia y la actualización de la app." },
        { page: "Configuración", target: "#nav .workspace-mode", image: "allen-reading-official", title: "Cambiar de modo",
          text: "Vuelve a Estudiante cuando quieras aprender o practicar como alumno." },
        { image: "allen-brand", title: "Qué puedes hacer como profesor",
          can: ["Crear cursos desde tu material", "Revisar la calidad, el banco de preguntas y las versiones antes de publicar",
            "Ver la analítica de tus cursos"],
          cannot: ["Usar Inicio, Quiz o Progreso: se ocultan en este modo, cambia a Estudiante",
            "Exportar Course Packs o respaldos: aún no está disponible en la app",
            "Usar la IA generativa completa: en el teléfono responde en modo demo"] },
        { image: "allen-celebrate-official", title: "¡A crear tu primer curso!",
          text: "Si quieres ver el recorrido otra vez, lo tienes en Configuración." },
      ],
    },
    fair: {
      label: "Modo Feria",
      steps: [
        { image: "allen-guide", title: "Modo Feria",
          text: "Pensado para visitantes de una feria o exposición: retos y microlecciones rápidas. El nombre de cada visitante no se guarda." },
        { target: "[data-reset]", image: "allen-celebrate-official", title: "Nueva persona",
          text: "Borra la sesión actual para que el siguiente visitante empiece desde cero." },
        { target: '[data-go="presenter"]', image: "allen-teaching-official", title: "Presentador",
          text: "Controles del stand: Modo Jurado, prueba del sistema, estadísticas y enlaces para el código QR." },
        { image: "allen-brand", title: "Qué se puede hacer aquí",
          can: ["Probar retos, microlecciones y conversaciones con Allen", "Reiniciar la experiencia para cada visitante"],
          cannot: ["Guardar progreso de los visitantes: la sesión se limpia sola tras un rato sin uso",
            "Entrar a cursos, perfiles o Teacher Studio: vuelve a la app para eso"] },
        { image: "allen-celebrate-official", title: "¡Que empiece la feria!", text: "Toca cualquier reto para comenzar." },
      ],
    },
  };

  const tour = (() => {
    let seen = {};
    try { seen = JSON.parse(localStorage.getItem(TOUR_KEY) || "{}") || {}; } catch (error) { seen = {}; }
    const remember = (key, value) => {
      seen[key] = value;
      try { localStorage.setItem(TOUR_KEY, JSON.stringify(seen)); } catch (error) { /* storage blocked */ }
    };
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    let layer = null, ring = null, sheet = null, active = null, index = 0, returnFocus = null;

    function build() {
      if (layer) return;
      layer = document.createElement("div");
      layer.className = "allen-tour";
      layer.innerHTML = '<div class="allen-tour-ring" hidden></div>' +
        '<section class="allen-tour-sheet" role="dialog" aria-modal="true" aria-labelledby="allen-tour-title"></section>';
      ring = layer.querySelector(".allen-tour-ring");
      sheet = layer.querySelector(".allen-tour-sheet");
      layer.addEventListener("click", onClick);
      document.addEventListener("keydown", event => { if (layer.isConnected && event.key === "Escape") close(true); });
      window.addEventListener("resize", () => placeRing());
      window.addEventListener("scroll", () => placeRing(), { passive: true });
    }
    function show() {
      build();
      if (!layer.isConnected) { returnFocus = document.activeElement; document.body.appendChild(layer); }
      root.classList.add("allen-tour-open");
    }
    function close(skipped) {
      const home = active && MODES[active].home;
      if (active) remember(active, skipped ? "skipped" : "done");
      // Skipping the welcome means no automatic tours later; Configuración can replay them.
      else if (skipped) Object.keys(MODES).forEach(mode => { if (mode !== "fair" && !seen[mode]) remember(mode, "skipped"); });
      remember("chooser", true);
      active = null;
      if (home) openPage(home);
      if (layer && layer.isConnected) layer.remove();
      root.classList.remove("allen-tour-open");
      if (returnFocus && returnFocus.isConnected) returnFocus.focus();
    }
    const esc = text => String(text).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const skipButton = '<button type="button" class="allen-tour-skip" data-tour="skip">Saltar recorrido</button>';

    function availableModes() {
      // Every workspace mode the app offers, in the order of its own switch.
      return [...document.querySelectorAll("#nav [data-workspace-mode]")]
        .map(button => button.dataset.workspaceMode).filter(mode => MODES[mode]);
    }
    function openChooser(force) {
      if (active || (!force && seen.chooser)) return;
      const modes = availableModes();
      if (!modes.length) return;
      show();
      ring.hidden = true;
      sheet.className = "allen-tour-sheet allen-tour-bottom";
      sheet.innerHTML =
        '<div class="allen-tour-head"><span class="allen-tour-count">Bienvenida</span>' + skipButton + "</div>" +
        '<div class="allen-tour-body"><img src="' + art("allen-brand") + '" alt=""><div>' +
        '<h2 id="allen-tour-title">¿Cómo vas a usar ALLEN?</h2>' +
        "<p>Elige un modo y te muestro lo que puedes hacer en él. Puedes cambiarlo después.</p></div></div>" +
        '<div class="allen-tour-modes">' + modes.map(mode =>
          '<button type="button" data-tour-mode="' + mode + '"><img src="' + art(MODES[mode].image) + '" alt="">' +
          "<span><b>" + esc(MODES[mode].label) + "</b><small>" + esc(MODES[mode].hint) + "</small></span></button>").join("") +
        "</div>";
      sheet.querySelector("[data-tour-mode]").focus();
    }
    async function start(mode) {
      if (!MODES[mode]) return;
      active = mode;
      index = 0;
      show();
      await render();
    }
    async function render() {
      const steps = MODES[active].steps, step = steps[index];
      const last = index === steps.length - 1;
      if (step.page) await openPage(step.page);
      const lists = step.can
        ? '<div class="allen-tour-lists"><div class="allen-tour-can"><h3>Puedes</h3><ul>' +
          step.can.map(item => "<li>" + esc(item) + "</li>").join("") + '</ul></div><div class="allen-tour-cannot"><h3>No puedes</h3><ul>' +
          step.cannot.map(item => "<li>" + esc(item) + "</li>").join("") + "</ul></div></div>"
        : "";
      sheet.innerHTML =
        '<div class="allen-tour-head"><span class="allen-tour-count">' + esc(MODES[active].label) + " · " +
        (index + 1) + " de " + steps.length + "</span>" + (last ? "" : skipButton) + "</div>" +
        '<div class="allen-tour-body"><img src="' + art(step.image) + '" alt=""><div>' +
        '<h2 id="allen-tour-title">' + esc(step.title) + "</h2>" + (step.text ? "<p>" + esc(step.text) + "</p>" : "") +
        "</div></div>" + lists +
        '<div class="allen-tour-actions">' +
        (index ? '<button type="button" data-tour="back">Atrás</button>' : "<span></span>") +
        '<button type="button" class="primary" data-tour="next">' + (last ? "Empezar" : "Siguiente") + "</button></div>";
      placeRing();
      sheet.querySelector('[data-tour="next"]').focus();
    }
    async function openPage(page) {
      const content = document.getElementById("content");
      const button = document.querySelector('#nav [data-page="' + page + '"]');
      if (!content || !button) return;
      const breadcrumb = document.getElementById("breadcrumb");
      const current = breadcrumb && breadcrumb.textContent === (page === "Inicio" ? "Tu espacio de aprendizaje" : page);
      if (!current) {
        button.click();
        await sleep(60);
      }
      for (let i = 0; i < 50 && content.getAttribute("aria-busy") === "true"; i++) await sleep(100);
      window.scrollTo(0, 0);
      await sleep(120);
    }
    function placeRing() {
      if (!active || !layer || !layer.isConnected) return;
      const step = MODES[active].steps[index];
      const target = step.target && document.querySelector(step.target);
      const box = target && target.getBoundingClientRect();
      const visible = box && box.width > 0 && box.height > 0;
      ring.hidden = !visible;
      layer.classList.toggle("allen-tour-dim", !visible);
      if (visible) {
        const pad = 6;
        ring.style.setProperty("--x", Math.max(4, box.left - pad) + "px");
        ring.style.setProperty("--y", Math.max(4, box.top - pad) + "px");
        ring.style.setProperty("--w", Math.min(innerWidth - 8, box.width + pad * 2) + "px");
        ring.style.setProperty("--h", box.height + pad * 2 + "px");
      }
      // Keep the sheet away from what it points at.
      const low = visible && box.top + box.height / 2 > innerHeight / 2;
      sheet.className = "allen-tour-sheet " + (low ? "allen-tour-top" : "allen-tour-bottom");
    }
    async function onClick(event) {
      const action = event.target.closest("[data-tour], [data-tour-mode]");
      if (!action) return;
      if (action.dataset.tourMode) {
        const mode = action.dataset.tourMode;
        remember("chooser", true);
        const current = document.body.dataset.workspaceMode;
        active = mode;  // set first so the mode-change observer does not start a second tour
        if (current !== mode) {
          const button = document.querySelector('#nav [data-workspace-mode="' + mode + '"]');
          if (button) button.click();
          for (let i = 0; i < 30 && document.body.dataset.workspaceMode !== mode; i++) await sleep(100);
          if (document.body.dataset.workspaceMode !== mode) { active = null; close(false); return; }
        }
        await start(mode);
        return;
      }
      const kind = action.dataset.tour;
      if (kind === "skip") close(true);
      else if (kind === "back" && index > 0) { index--; await render(); }
      else if (kind === "next") {
        if (index === MODES[active].steps.length - 1) close(false);
        else { index++; await render(); }
      }
    }
    return {
      openChooser,
      start,
      isActive: () => Boolean(active) || Boolean(layer && layer.isConnected),
      seen: mode => Boolean(seen[mode]),
    };
  })();

  function watchMainApp(content) {
    const ready = () =>
      !document.getElementById("allen-android-boot") && content.getAttribute("aria-busy") === "false" &&
      !content.querySelector("#welcome-form") && document.querySelector("#nav [data-workspace-mode]");
    const check = () => {
      addUpdateOption(content);
      addTourOption(content);
      if (ready() && !tour.isActive()) tour.openChooser(false);
    };
    new MutationObserver(check).observe(content, { childList: true, attributes: true, attributeFilter: ["aria-busy"] });
    // Switching to a mode for the first time shows that mode's tour.
    let mode = document.body.dataset.workspaceMode;
    new MutationObserver(() => {
      const next = document.body.dataset.workspaceMode;
      if (next === mode) return;
      mode = next;
      if (tour.seen("chooser") && !tour.seen(next) && !tour.isActive()) tour.start(next);
    }).observe(document.body, { attributes: true, attributeFilter: ["data-workspace-mode"] });
  }
  function watchFair(main) {
    const check = () => {
      if (tour.seen("fair") || tour.isActive() || document.getElementById("allen-android-boot")) return;
      if (main.querySelector("button, a")) tour.start("fair");
    };
    new MutationObserver(check).observe(main, { childList: true });
    ready.then(check, () => {});
  }

  document.addEventListener("DOMContentLoaded", () => {
    const content = document.getElementById("content");
    if (content) watchMainApp(content);
    const fair = document.getElementById("fair-main");
    if (fair) watchFair(fair);
  });
})();
