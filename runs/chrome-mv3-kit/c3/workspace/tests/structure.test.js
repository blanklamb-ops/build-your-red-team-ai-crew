"use strict";
const { assert, fs, path, ROOT, readJson } = require("./helpers");
const { validateSchema } = require("../generators/validate");
module.exports = async function structureTest() {
  const manifest = readJson("extension/manifest.json");
  assert.equal(manifest.manifest_version, 3);
  for (const permission of ["webRequest", "webNavigation", "storage", "downloads"]) assert.ok(manifest.permissions.includes(permission));
  assert.deepEqual(manifest.optional_host_permissions, ["http://*/*", "https://*/*"]);
  assert.equal(Object.prototype.hasOwnProperty.call(manifest, "host_permissions"), false);
  assert.ok(manifest.content_scripts.some((entry) => entry.js.includes("form_capture.js")));
  const background = fs.readFileSync(path.join(ROOT, "extension/background.js"), "utf8");
  assert.match(background, /\["responseHeaders", "extraHeaders"\]/);
  const popup = fs.readFileSync(path.join(ROOT, "extension/popup.html"), "utf8");
  assert.ok(popup.indexOf('src="shared.js"') < popup.indexOf('src="popup.js"'));
  const formCode = fs.readFileSync(path.join(ROOT, "extension/form_capture.js"), "utf8");
  assert.equal(/\.value\b/.test(formCode), false);
  assert.deepEqual(validateSchema(readJson("testdata/session-fixture.json"), readJson("schemas/capture-session.schema.json")), []);
  const readme = fs.readFileSync(path.join(ROOT, "README.md"), "utf8");
  for (const phrase of ["npm test", "Enable/Grant → Reload", "Authorized lab", "2.3.0", "placeholder-free", "domain and lures"])
    assert.ok(readme.includes(phrase), `README is missing ${phrase}`);
};
