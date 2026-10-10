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

})();
