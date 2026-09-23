"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(ROOT, relative), "utf8"));
function expectThrow(fn, pattern) {
  assert.throws(fn, pattern);
}
module.exports = { assert, fs, path, ROOT, readJson, expectThrow };
