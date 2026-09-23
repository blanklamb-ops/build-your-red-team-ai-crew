"use strict";
const { assert } = require("./helpers");
const { createController, KEY } = require("../extension/state");
module.exports = async function lifecycleTest() {
  const disk = {};
  const chromeMock = {
    storage: { local: {
      async get(key) { return { [key]: disk[key] }; },
      async set(value) { Object.assign(disk, JSON.parse(JSON.stringify(value))); }
    } },
    permissions: { async getAll() { return { origins: ["https://*/*"] }; } }
  };
  const first = createController(chromeMock, () => "2026-01-01T00:00:00.000Z");
  await first.setOrigins(["https://login.alpha.test", "https://account.beta.test/*"]);
  const started = await first.start();
  await first.addEvent({ request_id: "r1", url: "https://login.alpha.test/login", method: "GET", source: "webRequest_request" });
  await first.addEvent({ request_id: "r1", url: "https://login.alpha.test/login", method: "GET", status: 200, source: "webRequest_response", set_cookie_names: ["sid"] });
  assert.equal(started.recording, true);
  const restarted = createController(chromeMock, () => "2026-01-01T00:01:00.000Z");
  const restored = await restarted.load();
  assert.deepEqual(restored.requested_origins, ["https://login.alpha.test/*", "https://account.beta.test/*"]);
  assert.equal(restored.recording, true);
  assert.equal(restored.events.length, 2);
  assert.equal(restored.started_at, "2026-01-01T00:00:00.000Z");
  assert.ok(restored.diagnostics.counts_by_source.webRequest_request);
  await restarted.stop();
  assert.equal(disk[KEY].stopped_at, "2026-01-01T00:01:00.000Z");
  const deniedMock = JSON.parse(JSON.stringify(chromeMock));
  deniedMock.storage.local = chromeMock.storage.local;
  deniedMock.permissions = { async getAll() { return { origins: [] }; } };
  await assert.rejects(createController(deniedMock).start(), /Missing host access/);
};
