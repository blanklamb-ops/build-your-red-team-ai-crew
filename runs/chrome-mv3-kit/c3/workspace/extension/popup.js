"use strict";
const byId = (id) => document.getElementById(id);

function show(message, error = false) {
  byId("status").textContent = message;
  byId("status").className = error ? "error" : "";
}

async function send(type, payload = {}) {
  const response = await chrome.runtime.sendMessage({ type, payload });
  if (!response || !response.ok) throw new Error(response && response.error || "Extension service worker did not respond");
  return response.data;
}

async function render() {
  const state = await send("STATE_GET");
  const diagnostics = state.diagnostics || {};
  byId("origins").value = (state.requested_origins || []).join("\n");
  byId("requested").textContent = (diagnostics.requested_origins || []).join(", ") || "none";
  byId("granted").textContent = (diagnostics.granted_origins || []).join(", ") || "none";
  byId("missing").textContent = (diagnostics.missing_origins || []).join(", ") || "none";
  byId("access").textContent = diagnostics.missing_origins && diagnostics.missing_origins.length ? "Host access incomplete" :
    (diagnostics.granted_origins && diagnostics.granted_origins.length ? "Host access granted" : "Host access not granted");
  show(state.recording ? `Recording ${state.events.length} event(s)` : `Stopped; ${state.events.length} event(s); coverage ${state.coverage || diagnostics.coverage || "incomplete"}`);
}

async function requestAndStore(origins) {
  const normalized = LabShared.normalizeOrigins(origins);
  const allowed = await chrome.permissions.request({ origins: normalized });
  if (!allowed) throw new Error("Host access was not granted; recording remains off");
  await send("ORIGINS_SET", { origins: normalized });
  await render();
}

function download(filename, mime, content) {
  const url = `data:${mime};charset=utf-8,${encodeURIComponent(content)}`;
  return chrome.downloads.download({ url, filename, saveAs: true });
}

byId("enable").addEventListener("click", () => requestAndStore(["http://*/*", "https://*/*"]).catch((e) => show(e.message, true)));
byId("approve").addEventListener("click", () => {
  const origins = byId("origins").value.split(/[\n,]+/).map((x) => x.trim()).filter(Boolean);
  requestAndStore(origins).catch((e) => show(e.message, true));
});
byId("start").addEventListener("click", () => send("START").then(render).catch((e) => show(e.message, true)));
byId("stop").addEventListener("click", () => send("STOP").then(render).catch((e) => show(e.message, true)));
byId("json").addEventListener("click", () => send("EXPORT_JSON").then((data) => download("lab-auth-flow.json", "application/json", JSON.stringify(data, null, 2))).catch((e) => show(e.message, true)));
byId("markdown").addEventListener("click", () => send("EXPORT_MARKDOWN").then((data) => download("lab-auth-flow.md", "text/markdown", data)).catch((e) => show(e.message, true)));
byId("snapshot").addEventListener("click", async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const result = await chrome.tabs.sendMessage(tab.id, { type: "SNAPSHOT_PAGE" });
    if (!result || !result.ok) throw new Error("Snapshot content script unavailable on this page");
    await download("lab-page-snapshot.html", "text/html", result.html);
    await download("lab-page-snapshot-report.json", "application/json", JSON.stringify(result.report, null, 2));
  } catch (error) { show(error.message, true); }
});

const unsafeEnabled = LabConfig.lab_unsafe_modules === true;
byId("training").hidden = !unsafeEnabled;
if (unsafeEnabled) {
  byId("overlay-demo").addEventListener("click", () => alert("Training demo: verify browser chrome and origin before trusting page overlays."));
  byId("picker-demo").addEventListener("click", () => alert("Training demo: inspect the requesting origin before selecting a local file."));
}
render().catch((e) => show(e.message, true));
