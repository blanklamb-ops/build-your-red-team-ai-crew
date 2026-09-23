"use strict";
const crypto = require("crypto");
const { assert, fs, path, ROOT, readJson } = require("./helpers");
const { generateYaml } = require("../generators/phishlet");
const { validateYaml } = require("../generators/validate");
module.exports = async function regressionTest() {
  const study = fs.readFileSync(path.join(ROOT, "study-fixtures/regression-mixed-capture.json"));
  const shipped = fs.readFileSync(path.join(ROOT, "testdata/regression-mixed-capture.json"));
  assert.deepEqual(shipped, study);
  assert.equal(crypto.createHash("sha256").update(shipped).digest("hex"), "eddf034a05b205d7c2018e088f55a54a520c12c4c02b0463e46f869fe7b2a95f");
  const { phishlet, yaml } = generateYaml(readJson("testdata/regression-mixed-capture.json"));
  const allowed = new Set(["idp.test", "wallet.test", "authcdn.test", "corp.test"]);
  assert.ok(phishlet.proxy_hosts.every((host) => allowed.has(host.domain)));
  for (const required of ["idp.test", "wallet.test", "corp.test"]) assert.ok(phishlet.proxy_hosts.some((host) => host.domain === required));
  assert.ok(phishlet.proxy_hosts.length >= 3 && phishlet.proxy_hosts.length <= 4);
  const forbidden = /graph|admin|monitor|metrics|wcpstatic|uhf|edgecdn|storage|blob|amcdn|fpt|copilot|clarity/i;
  assert.ok(phishlet.proxy_hosts.every((host) => !forbidden.test(`${host.orig_sub} ${host.domain}`) && !/[a-f0-9]{12,}/i.test(`${host.orig_sub} ${host.domain}`)));
  assert.equal(new Set(phishlet.auth_tokens.map((item) => item.domain)).size, phishlet.auth_tokens.length);
  assert.ok(phishlet.auth_tokens.every((item) => item.domain.split(".").length === 2));
  assert.deepEqual(phishlet.login, { domain: "wallet.test", path: "/ppsecure/post.srf" });
  assert.deepEqual(phishlet.credentials, {
    username: { key: "loginfmt", search: "(.*)", type: "post" },
    password: { key: "passwd", search: "(.*)", type: "post" }
  });
  assert.ok(phishlet.auth_urls.includes("/checkpassword.srf"));
  assert.ok(phishlet.auth_urls.includes("/common/GetCredentialType"));
  assert.ok(phishlet.sub_filters.length && phishlet.sub_filters.every((item) => item && typeof item === "object" &&
    ["triggers_on", "orig_sub", "domain", "search", "replace", "mimes"].every((key) => Object.prototype.hasOwnProperty.call(item, key))));
  assert.equal(phishlet.min_ver, "2.3.0");
  assert.ok(phishlet.author);
  assert.equal(yaml.includes("{{PLACEHOLDER}}"), false);
  assert.equal(validateYaml(yaml).valid, true);
};
