"use strict";
const { assert, readJson } = require("./helpers");
const { generatePhishlet } = require("../generators/phishlet");
const { serializeYaml } = require("../generators/yaml");
const { validateYaml } = require("../generators/validate");
module.exports = async function validationTest() {
  const base = generatePhishlet(readJson("testdata/session-fixture.json")).phishlet;
  const mutate = (fn) => { const copy = JSON.parse(JSON.stringify(base)); fn(copy); return validateYaml(serializeYaml(copy)); };
  assert.equal(mutate((x) => delete x.author).valid, false);
  assert.equal(mutate((x) => { x.min_ver = "3.0.0"; }).valid, false);
  assert.equal(mutate((x) => { x.name = "forbidden"; }).valid, false);
  assert.equal(mutate((x) => { x.auth_tokens[0].value = "forbidden"; }).valid, false);
  assert.equal(mutate((x) => { x.auth_tokens = { "alpha.test": { keys: ["sid"] } }; }).valid, false);
  assert.equal(mutate((x) => { x.credentials = []; }).valid, false);
  assert.equal(mutate((x) => { x.sub_filters = ["{{PLACEHOLDER}}"] ; }).valid, false);
  assert.equal(mutate((x) => { x.login.username = "bad"; }).valid, false);
  assert.equal(mutate((x) => { x.credentials.username.search = "{{PLACEHOLDER}}"; }).valid, false);
  assert.equal(validateYaml("author: \"x\"\n bad: [broken\n").valid, false);
};
