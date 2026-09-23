"use strict";
const { assert, expectThrow } = require("./helpers");
const shared = require("../extension/shared");
module.exports = async function originsTest() {
  for (const input of ["https://example.test", "example.test", "https://example.test/a?b=1", "https://example.test/*"])
    assert.equal(shared.normalizeOrigin(input), "https://example.test/*");
  assert.equal(shared.normalizeOrigin(shared.normalizeOrigin("https://example.test/path")), "https://example.test/*");
  expectThrow(() => shared.normalizeOrigin("ftp://example.test/a"), /HTTP/);
  expectThrow(() => shared.normalizeOrigin("https://user@example.test"), /Userinfo/);
  const compared = shared.comparePermissions(["https://a.test/*", "http://b.test/*"], ["https://*/*"]);
  assert.deepEqual(compared.granted, ["https://a.test/*"]);
  assert.deepEqual(compared.missing, ["http://b.test/*"]);
};
