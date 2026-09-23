(function (root, factory) {
  const shared = typeof module === "object" && module.exports ? require("./shared") : root.LabShared;
  const api = factory(shared);
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LabState = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (shared) {
  "use strict";
  const KEY = "captureState";

  function freshState() {
    return { version: 1, session_id: null, requested_origins: [], granted_origins: [],
      recording: false, events: [], started_at: null, stopped_at: null, diagnostics: {} };
  }

  function uuid() {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") return globalThis.crypto.randomUUID();
    return `lab-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function createController(chromeApi, clock = () => new Date().toISOString()) {
    if (!chromeApi || !chromeApi.storage || !chromeApi.storage.local) throw new Error("chrome.storage.local is required");
    let queue = Promise.resolve();
    const transact = (operation) => {
      queue = queue.then(operation, operation);
      return queue;
    };
    const load = async () => {
      const result = await chromeApi.storage.local.get(KEY);
      return Object.assign(freshState(), result[KEY] || {});
    };
    const save = async (state) => {
      await chromeApi.storage.local.set({ [KEY]: state });
      return state;
    };
    const granted = async () => {
      const result = await chromeApi.permissions.getAll();
      return shared.normalizeOrigins(result.origins || []);
    };
    return {
      load,
      setOrigins(origins) {
        return transact(async () => {
          const state = await load();
          state.requested_origins = shared.normalizeOrigins(origins);
          state.diagnostics = shared.buildDiagnostics(state, await granted());
          return save(state);
        });
      },
      start() {
        return transact(async () => {
          const state = await load();
          if (!state.requested_origins.length) throw new Error("Enable lab access or approve the complete origin set before recording");
          const allGranted = await granted();
          const comparison = shared.comparePermissions(state.requested_origins, allGranted);
          if (comparison.missing.length) throw new Error(`Missing host access: ${comparison.missing.join(", ")}`);
          const next = Object.assign(freshState(), state, { session_id: uuid(), recording: true,
            events: [], started_at: clock(), stopped_at: null, granted_origins: allGranted });
          next.diagnostics = shared.buildDiagnostics(next, allGranted);
          return save(next);
        });
      },
      stop() {
        return transact(async () => {
          const state = await load();
          state.recording = false;
          state.stopped_at = clock();
          state.granted_origins = await granted();
          state.diagnostics = shared.buildDiagnostics(state, state.granted_origins);
          return save(state);
        });
      },
      addEvent(raw) {
        return transact(async () => {
          const state = await load();
          if (!state.recording) return state;
          state.events = shared.mergeEvents(state.events, raw);
          state.granted_origins = await granted();
          state.diagnostics = shared.buildDiagnostics(state, state.granted_origins);
          return save(state);
        });
      },
      export() {
        return transact(async () => shared.exportSession(await load(), await granted()));
      }
    };
  }
  return { KEY, freshState, createController };
});
