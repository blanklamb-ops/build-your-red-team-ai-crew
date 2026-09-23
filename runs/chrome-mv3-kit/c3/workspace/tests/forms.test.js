"use strict";
const { assert } = require("./helpers");
const { captureFormMetadata } = require("../extension/form_capture");
function field(name, type, value) {
  return { tagName: "INPUT", value, getAttribute(key) { return key === "name" ? name : key === "type" ? type : null; } };
}
module.exports = async function formsTest() {
  const fields = [field("loginfmt", "hidden", "person@lab.test"), field("passwd", "password", "DO-NOT-CAPTURE")];
  const submit = { textContent: "Sign in", getAttribute() { return null; } };
  const form = {
    getAttribute(name) { return name === "action" ? "/ppsecure/post.srf" : null; },
    querySelectorAll() { return fields; },
    querySelector() { return submit; }
  };
  const doc = { querySelectorAll(selector) { assert.equal(selector, "form"); return [form]; } };
  const result = captureFormMetadata(doc, "https://login.wallet.test/login.srf");
  assert.equal(result[0].form_action, "https://login.wallet.test/ppsecure/post.srf");
  assert.deepEqual(result[0].fields, [{ name: "loginfmt", type: "hidden" }, { name: "passwd", type: "password" }]);
  assert.equal(JSON.stringify(result).includes("DO-NOT-CAPTURE"), false);
  assert.equal(Object.prototype.hasOwnProperty.call(result[0].fields[0], "value"), false);
};
