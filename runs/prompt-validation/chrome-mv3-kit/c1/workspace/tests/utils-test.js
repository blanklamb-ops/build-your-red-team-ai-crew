/**
 * Tests for shared utilities (origin normalization, permission checks)
 * A3g: idempotent normalization tests
 */

const utils = require('../extension/shared/utils.js');

function runTests() {
  const results = [];

  function test(name, fn) {
    try {
      fn();
      results.push({ name, status: 'PASS' });
      console.log(`✓ ${name}`);
    } catch (error) {
      results.push({ name, status: 'FAIL', error: error.message });
      console.error(`✗ ${name}: ${error.message}`);
    }
  }

  function assert(condition, message) {
    if (!condition) {
      throw new Error(message || 'Assertion failed');
    }
  }

  // A3g: Idempotent normalization
  test('normalizeOrigin: bare HTTPS origin', () => {
    const result = utils.normalizeOrigin('https://example.test');
    assert(result === 'https://example.test/*', `Expected 'https://example.test/*', got '${result}'`);
  });

  test('normalizeOrigin: full URL', () => {
    const result = utils.normalizeOrigin('https://example.test/path/to/page');
    assert(result === 'https://example.test/*', `Expected 'https://example.test/*', got '${result}'`);
  });

  test('normalizeOrigin: already canonical', () => {
    const result = utils.normalizeOrigin('https://example.test/*');
    assert(result === 'https://example.test/*', `Expected 'https://example.test/*', got '${result}'`);
  });

  test('normalizeOrigin: idempotent (apply twice)', () => {
    const first = utils.normalizeOrigin('https://example.test/some/path');
    const second = utils.normalizeOrigin(first);
    assert(first === second, `Not idempotent: '${first}' !== '${second}'`);
  });

  test('normalizeOrigin: bare host (no protocol)', () => {
    const result = utils.normalizeOrigin('example.test');
    assert(result === 'https://example.test/*', `Expected 'https://example.test/*', got '${result}'`);
  });

  test('normalizeOrigin: HTTP scheme', () => {
    const result = utils.normalizeOrigin('http://example.test');
    assert(result === 'http://example.test/*', `Expected 'http://example.test/*', got '${result}'`);
  });

  test('normalizeOrigin: rejects userinfo', () => {
    let threw = false;
    try {
      utils.normalizeOrigin('https://user:pass@example.test');
    } catch (e) {
      threw = true;
      assert(e.message.includes('userinfo') || e.message.includes('Userinfo'), 'Wrong error message');
    }
    assert(threw, 'Should reject userinfo');
  });

  test('normalizeOrigin: rejects non-HTTP(S)', () => {
    let threw = false;
    try {
      utils.normalizeOrigin('chrome-extension://abcdef/page.html');
    } catch (e) {
      threw = true;
    }
    assert(threw, 'Should reject non-HTTP(S) schemes');
  });

  test('extractOrigin: valid HTTPS URL', () => {
    const result = utils.extractOrigin('https://example.test/path');
    assert(result === 'https://example.test/*', `Expected 'https://example.test/*', got '${result}'`);
  });

  test('extractOrigin: non-HTTP(S) returns null', () => {
    const result = utils.extractOrigin('chrome-extension://abcdef/page.html');
    assert(result === null, `Expected null, got '${result}'`);
  });

  test('hasPermission: direct match', () => {
    const granted = ['https://example.test/*'];
    const result = utils.hasPermission(granted, 'https://example.test/*');
    assert(result === true, 'Should have permission');
  });

  test('hasPermission: wildcard HTTP coverage', () => {
    const granted = ['http://*/*'];
    const result = utils.hasPermission(granted, 'http://example.test/*');
    assert(result === true, 'Should have permission via http://*/*');
  });

  test('hasPermission: wildcard HTTPS coverage', () => {
    const granted = ['https://*/*'];
    const result = utils.hasPermission(granted, 'https://example.test/*');
    assert(result === true, 'Should have permission via https://*/*');
  });

  test('hasPermission: no match', () => {
    const granted = ['https://other.test/*'];
    const result = utils.hasPermission(granted, 'https://example.test/*');
    assert(result === false, 'Should not have permission');
  });

  test('generateUUID: valid format', () => {
    const uuid = utils.generateUUID();
    const pattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
    assert(pattern.test(uuid), `Invalid UUID format: ${uuid}`);
  });

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\nUtils tests: ${results.length - failCount}/${results.length} passed`);

  return failCount === 0 ? results : null;
}

module.exports = { runTests };

if (require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}
