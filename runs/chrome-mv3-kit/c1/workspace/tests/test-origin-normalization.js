/**
 * Tests for origin normalization (A3g)
 * MUST import and test production normalizeOrigin function
 */

import { normalizeOrigin, isOriginCovered } from '../extension/shared/origin-utils.js';

export function runOriginTests() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // A3g: Idempotent normalization
  test('Bare HTTPS origin normalizes correctly', () => {
    const result = normalizeOrigin('https://example.test');
    if (result !== 'https://example.test/*') {
      throw new Error(`Expected https://example.test/*, got ${result}`);
    }
  });

  test('Full URL normalizes to match pattern', () => {
    const result = normalizeOrigin('https://login.example.test/path/to/login');
    if (result !== 'https://login.example.test/*') {
      throw new Error(`Expected https://login.example.test/*, got ${result}`);
    }
  });

  test('Already-canonical match pattern is idempotent', () => {
    const input = 'https://example.test/*';
    const result = normalizeOrigin(input);
    if (result !== input) {
      throw new Error(`Normalization not idempotent: ${input} -> ${result}`);
    }
  });

  test('Double normalization is idempotent', () => {
    const first = normalizeOrigin('https://example.test');
    const second = normalizeOrigin(first);
    if (first !== second) {
      throw new Error(`Not idempotent: ${first} -> ${second}`);
    }
  });

  test('HTTP origin normalizes correctly', () => {
    const result = normalizeOrigin('http://example.test');
    if (result !== 'http://example.test/*') {
      throw new Error(`Expected http://example.test/*, got ${result}`);
    }
  });

  test('Host-only input gets HTTPS', () => {
    const result = normalizeOrigin('example.test');
    if (result !== 'https://example.test/*') {
      throw new Error(`Expected https://example.test/*, got ${result}`);
    }
  });

  test('Host with port normalizes correctly', () => {
    const result = normalizeOrigin('https://example.test:8443');
    if (result !== 'https://example.test:8443/*') {
      throw new Error(`Expected https://example.test:8443/*, got ${result}`);
    }
  });

  // Reject userinfo
  test('Userinfo in URL is rejected', () => {
    try {
      normalizeOrigin('https://user:pass@example.test');
      throw new Error('Should have rejected userinfo');
    } catch (e) {
      if (!e.message.includes('Userinfo')) {
        throw new Error(`Wrong error: ${e.message}`);
      }
    }
  });

  test('Username-only userinfo is rejected', () => {
    try {
      normalizeOrigin('https://user@example.test');
      throw new Error('Should have rejected userinfo');
    } catch (e) {
      if (!e.message.includes('Userinfo')) {
        throw new Error(`Wrong error: ${e.message}`);
      }
    }
  });

  // Reject non-HTTP(S)
  test('chrome-extension:// scheme is rejected', () => {
    try {
      normalizeOrigin('chrome-extension://abcdef123456/popup.html');
      throw new Error('Should have rejected non-HTTP(S) scheme');
    } catch (e) {
      if (!e.message.includes('Non-HTTP')) {
        throw new Error(`Wrong error: ${e.message}`);
      }
    }
  });

  test('file:// scheme is rejected', () => {
    try {
      normalizeOrigin('file:///etc/passwd');
      throw new Error('Should have rejected file:// scheme');
    } catch (e) {
      if (!e.message.includes('Non-HTTP')) {
        throw new Error(`Wrong error: ${e.message}`);
      }
    }
  });

  test('data: scheme is rejected', () => {
    try {
      normalizeOrigin('data:text/html,<h1>Hi</h1>');
      throw new Error('Should have rejected data: scheme');
    } catch (e) {
      if (!e.message.includes('Non-HTTP')) {
        throw new Error(`Wrong error: ${e.message}`);
      }
    }
  });

  // Coverage tests
  test('Wildcard HTTPS covers specific origin', () => {
    const granted = ['https://*/*'];
    const covered = isOriginCovered('https://example.test/*', granted);
    if (!covered) {
      throw new Error('https://*/* should cover https://example.test/*');
    }
  });

  test('Wildcard HTTP covers HTTP origin', () => {
    const granted = ['http://*/*'];
    const covered = isOriginCovered('http://example.test/*', granted);
    if (!covered) {
      throw new Error('http://*/* should cover http://example.test/*');
    }
  });

  test('Exact match is covered', () => {
    const granted = ['https://login.example.test/*'];
    const covered = isOriginCovered('https://login.example.test/*', granted);
    if (!covered) {
      throw new Error('Exact match should be covered');
    }
  });

  test('Missing origin is not covered', () => {
    const granted = ['https://example.test/*'];
    const covered = isOriginCovered('https://other.test/*', granted);
    if (covered) {
      throw new Error('Different origin should not be covered');
    }
  });

  // Run all tests
  for (const { name, fn } of tests) {
    try {
      fn();
      console.log(`  ✓ ${name}`);
      passed++;
    } catch (error) {
      console.log(`  ✗ ${name}: ${error.message}`);
      failed++;
    }
  }

  return { total: tests.length, passed, failed };
}
