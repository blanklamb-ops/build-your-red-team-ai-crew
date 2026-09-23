"use strict";
const { assert, readJson } = require("./helpers");
const shared = require("../extension/shared");
const { generateTrafficStub } = require("../generators/traffic_stub");
module.exports = async function exportsTest() {
  const fixture = readJson("testdata/session-fixture.json");
  fixture.events.push({ url: "chrome-extension://abc/popup.html", source: "webNavigation_fallback" });
  const exported = shared.exportSession(fixture, ["https://*/*"]);
  assert.equal(exported.events.some((e) => e.url.startsWith("chrome-extension:")), false);
  assert.equal(exported.coverage, "complete");
  assert.equal(exported.diagnostics.counts_by_origin["https://login.alpha.test"], 3);
  const markdown = shared.sessionToMarkdown(fixture, ["https://*/*"]);
  assert.match(markdown, /Coverage: COMPLETE/);
  assert.match(markdown, /Counts by source/);
  assert.match(generateTrafficStub(fixture), /AUTHORIZED LAB DOCUMENTATION SKELETON/);
  const fallback = shared.exportSession({ requested_origins: ["https://a.test/*"], events: [{ url: "https://a.test/", source: "webNavigation_fallback" }] }, ["https://*/*"]);
  assert.equal(fallback.coverage, "incomplete");
};
