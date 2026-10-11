// ALLEN Android demo: Python runs in this Web Worker so the page stays responsive to touch
// while Pyodide starts up or the backend handles a request.
importScripts("/pyodide/pyodide.js");

const PACKAGES = ["fastapi", "httpx", "pydantic", "cryptography", "micropip", "sqlite3", "hashlib", "ssl"];
const mutating = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const step = text => postMessage({ type: "step", text });

function syncfs(populate, py) {
  return new Promise((resolve, reject) => py.FS.syncfs(populate, err => (err ? reject(err) : resolve())));
}

const ready = (async () => {
  const py = await loadPyodide({ indexURL: "/pyodide/" });
  step("Cargando tus datos guardados");
  py.FS.mkdirTree("/data");
  py.FS.mount(py.FS.filesystems.IDBFS, {}, "/data");
  await syncfs(true, py);
  step("Cargando módulos de aprendizaje");
  await py.loadPackage(PACKAGES, { messageCallback: () => {} });
  const manifest = await (await fetch("/allen-manifest.json")).json();
  py.FS.mkdirTree("/wheels");
  for (const wheel of manifest.wheels) {
    py.FS.writeFile("/wheels/" + wheel, new Uint8Array(await (await fetch("/wheels/" + wheel)).arrayBuffer()));
  }
  await py.pyimport("micropip").install(manifest.wheels.map(w => "emfs:/wheels/" + w), { deps: false });
  py.unpackArchive(await (await fetch("/allen-src.zip")).arrayBuffer(), "zip", { extractDir: "/app" });
  py.runPython("import sys; sys.path.insert(0, '/app')");
  step("Abriendo ALLEN");
  const bridge = py.pyimport("allen_bridge");
  await syncfs(false, py);
  return { py, bridge };
})();

ready.then(
  () => postMessage({ type: "ready" }),
  error => postMessage({ type: "failed", message: String((error && error.message) || error) })
);

// Serialize ASGI requests and acknowledge writes only after durable filesystem sync.
let requests = Promise.resolve();
onmessage = ({ data }) => {
  if (data.type !== "request") return;
  requests = requests.then(async () => {
    try {
      const { py, bridge } = await ready;
      const raw = await bridge.handle(data.method, data.url, data.headers, data.body);
      if (mutating.has(data.method)) await syncfs(false, py);
      postMessage({ type: "response", id: data.id, raw });
    } catch (error) {
      postMessage({ type: "response", id: data.id, error: String((error && error.message) || error) });
    }
  });
};
