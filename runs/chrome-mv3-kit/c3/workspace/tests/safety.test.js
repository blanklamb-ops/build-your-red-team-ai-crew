"use strict";
const { assert, readJson } = require("./helpers");
const { generatePhishlet } = require("../generators/phishlet");
module.exports = async function safetyTest() {
  const secret = readJson("testdata/session-fixture.json");
  secret.note = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsYWItdXNlciJ9.signaturevalue123456";
  assert.throws(() => generatePhishlet(secret), /Secret-looking value/);
  const uuidAndCookie = readJson("testdata/session-fixture.json");
  assert.doesNotThrow(() => generatePhishlet(uuidAndCookie));
  assert.throws(() => generatePhishlet({ events: [] }), /non-empty events/);
  const config = readJson("config/default.json");
  assert.equal(config.lab_unsafe_modules, false);
  assert.equal(config.ui_overlay_awareness, false);
  assert.equal(config.file_picker_awareness, false);
};
