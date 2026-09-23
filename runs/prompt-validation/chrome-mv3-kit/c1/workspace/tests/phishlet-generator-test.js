/**
 * Phishlet Generator Tests
 * Includes A5, A5b, A5c, A5d, and critical A5e regression test
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const phishletGen = require('../generators/phishlet-generator.js');

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

  // A5c: Secret rejection
  test('A5c: Reject JWT in session', () => {
    const session = {
      session_id: 'test',
      events: [
        {
          url: 'https://example.com/auth?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U',
          method: 'GET',
          status: 200,
          source: 'webRequest',
          set_cookie_names: []
        }
      ]
    };

    let threw = false;
    try {
      phishletGen.generatePhishlet(session);
    } catch (e) {
      threw = true;
      assert(e.message.includes('secret'), 'Should mention secret in error');
    }

    assert(threw, 'Should reject JWT in URL');
  });

  test('A5c: Allow canonical UUID', () => {
    const session = {
      session_id: '00000000-0000-4000-8000-000000000001',
      events: [
        {
          url: 'https://login.example.com/auth',
          method: 'GET',
          status: 200,
          source: 'webRequest',
          set_cookie_names: ['session_id']
        }
      ]
    };

    const phishlet = phishletGen.generatePhishlet(session);
    assert(phishlet !== null, 'Should allow canonical UUID');
  });

  test('A5c: Allow cookie names', () => {
    const session = {
      session_id: 'test',
      events: [
        {
          url: 'https://login.example.com/auth',
          method: 'GET',
          status: 200,
          source: 'webRequest',
          set_cookie_names: ['MSPAuth', 'fpc', 'session_id']
        }
      ]
    };

    const phishlet = phishletGen.generatePhishlet(session);
    assert(phishlet !== null, 'Should allow cookie names');
    assert(phishlet.auth_tokens.length > 0, 'Should extract cookie names');
  });

  // A5b: Basic structure
  test('A5b: Generated phishlet has required top-level keys', () => {
    const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert('author' in phishlet, 'Should have author');
    assert('min_ver' in phishlet, 'Should have min_ver');
    assert('proxy_hosts' in phishlet, 'Should have proxy_hosts');
    assert('auth_tokens' in phishlet, 'Should have auth_tokens');
    assert('auth_urls' in phishlet, 'Should have auth_urls');
    assert('login' in phishlet, 'Should have login');
    assert('credentials' in phishlet, 'Should have credentials');
    assert('sub_filters' in phishlet, 'Should have sub_filters');

    assert(!('name' in phishlet), 'Should NOT have top-level name');
  });

  test('A5b: min_ver is 2.3.0', () => {
    const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.min_ver === '2.3.0', `Expected '2.3.0', got '${phishlet.min_ver}'`);
  });

  test('A5b: credentials is a MAP not list', () => {
    const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(typeof phishlet.credentials === 'object', 'credentials should be object');
    assert(!Array.isArray(phishlet.credentials), 'credentials should NOT be array');
    assert('username' in phishlet.credentials, 'Should have username');
    assert('password' in phishlet.credentials, 'Should have password');
  });

  test('A5b: credentials has key/search/type', () => {
    const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.credentials.username.key, 'username should have key');
    assert(phishlet.credentials.username.search, 'username should have search');
    assert(phishlet.credentials.username.type, 'username should have type');

    assert(phishlet.credentials.password.key, 'password should have key');
    assert(phishlet.credentials.password.search, 'password should have search');
    assert(phishlet.credentials.password.type, 'password should have type');
  });

  test('A5b: sub_filters is non-empty list of objects', () => {
    const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(Array.isArray(phishlet.sub_filters), 'sub_filters should be array');
    assert(phishlet.sub_filters.length > 0, 'sub_filters should not be empty');

    for (const filter of phishlet.sub_filters) {
      assert(typeof filter === 'object', 'Each filter should be object');
      assert(!Array.isArray(filter), 'Filter should not be array');
      assert(filter.triggers_on, 'Filter should have triggers_on');
      assert('orig_sub' in filter, 'Filter should have orig_sub');
      assert(filter.domain, 'Filter should have domain');
      assert(filter.search, 'Filter should have search');
      assert(filter.replace, 'Filter should have replace');
      assert(Array.isArray(filter.mimes), 'Filter should have mimes array');
    }
  });

  test('A5: No {{PLACEHOLDER}} in YAML', () => {
    const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);
    const yamlText = yaml.dump(phishlet);

    assert(!yamlText.includes('{{PLACEHOLDER}}'), 'YAML should not contain {{PLACEHOLDER}}');
  });

  // A5e: CRITICAL regression test
  test('A5e: Regression mixed-capture - proxy_hosts domains', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    const domains = phishlet.proxy_hosts.map(h => h.domain);
    const allowedDomains = ['idp.test', 'wallet.test', 'authcdn.test', 'corp.test'];

    for (const domain of domains) {
      assert(allowedDomains.includes(domain),
        `Domain '${domain}' not in allowed set: ${allowedDomains.join(', ')}`);
    }

    assert(domains.includes('idp.test'), 'Should include idp.test');
    assert(domains.includes('wallet.test'), 'Should include wallet.test');
    assert(domains.includes('corp.test'), 'Should include corp.test');

    assert(domains.length >= 3 && domains.length <= 4,
      `Expected 3-4 domains, got ${domains.length}`);
  });

  test('A5e: Regression mixed-capture - no junk domains', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    const junkKeywords = [
      'graph', 'admin', 'monitor', 'metrics', 'wcpstatic',
      'uhf', 'edgecdn', 'storage', 'blob', 'amcdn',
      'fpt', 'copilot', 'clarity'
    ];

    for (const host of phishlet.proxy_hosts) {
      const combined = `${host.orig_sub}.${host.domain}`.toLowerCase();

      for (const kw of junkKeywords) {
        assert(!combined.includes(kw),
          `Should not include '${kw}' in ${combined}`);
      }

      // No hex-like orig_sub/domain
      if (host.orig_sub.length >= 12) {
        assert(!/^[0-9a-f]+$/.test(host.orig_sub),
          `orig_sub '${host.orig_sub}' looks like hex junk`);
      }
    }
  });

  test('A5e: Regression mixed-capture - login.domain and login.path', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.login.domain === 'wallet.test',
      `Expected login.domain 'wallet.test', got '${phishlet.login.domain}'`);

    assert(phishlet.login.path === '/ppsecure/post.srf',
      `Expected login.path '/ppsecure/post.srf', got '${phishlet.login.path}'`);

    assert(!('username' in phishlet.login), 'login should NOT have username key');
    assert(!('password' in phishlet.login), 'login should NOT have password key');
  });

  test('A5e: Regression mixed-capture - credentials from form_fields', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.credentials.username.key === 'loginfmt',
      `Expected username.key 'loginfmt', got '${phishlet.credentials.username.key}'`);

    assert(phishlet.credentials.password.key === 'passwd',
      `Expected password.key 'passwd', got '${phishlet.credentials.password.key}'`);

    assert(phishlet.credentials.username.type === 'post' || phishlet.credentials.username.type === 'json',
      `Expected type 'post' or 'json', got '${phishlet.credentials.username.type}'`);

    assert(phishlet.credentials.username.search !== '{{PLACEHOLDER}}',
      'username.search should not be {{PLACEHOLDER}}');
    assert(phishlet.credentials.password.search !== '{{PLACEHOLDER}}',
      'password.search should not be {{PLACEHOLDER}}');
  });

  test('A5e: Regression mixed-capture - auth_urls includes required paths', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.auth_urls.includes('/checkpassword.srf') ||
           phishlet.auth_urls.some(u => u.includes('checkpassword')),
      'auth_urls should include checkpassword.srf');

    assert(phishlet.auth_urls.includes('/common/GetCredentialType') ||
           phishlet.auth_urls.some(u => u.includes('GetCredentialType')),
      'auth_urls should include GetCredentialType');
  });

  test('A5e: Regression mixed-capture - sub_filters non-empty with no placeholders', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.sub_filters.length > 0, 'sub_filters should not be empty');

    for (const filter of phishlet.sub_filters) {
      assert(filter.triggers_on !== '{{PLACEHOLDER}}', 'triggers_on should not be {{PLACEHOLDER}}');
      assert(filter.search !== '{{PLACEHOLDER}}', 'search should not be {{PLACEHOLDER}}');
      assert(filter.replace !== '{{PLACEHOLDER}}', 'replace should not be {{PLACEHOLDER}}');

      // Should match a proxy_hosts entry
      const matchesHost = phishlet.proxy_hosts.some(h =>
        h.domain === filter.domain &&
        h.orig_sub === filter.orig_sub
      );
      assert(matchesHost, `Filter domain/orig_sub should match a proxy_hosts entry`);
    }
  });

  test('A5e: Regression mixed-capture - YAML contains no {{PLACEHOLDER}}', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);
    const yamlText = yaml.dump(phishlet);

    assert(!yamlText.includes('{{PLACEHOLDER}}'),
      'Full YAML text must not contain {{PLACEHOLDER}}');
  });

  test('A5e: Regression mixed-capture - author and min_ver', () => {
    const session = JSON.parse(fs.readFileSync('testdata/regression-mixed-capture.json', 'utf8'));
    const phishlet = phishletGen.generatePhishlet(session);

    assert(phishlet.author && phishlet.author.length > 0, 'author should be non-empty');
    assert(phishlet.min_ver === '2.3.0', `min_ver should be '2.3.0', got '${phishlet.min_ver}'`);
  });

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\nPhishlet generator tests: ${results.length - failCount}/${results.length} passed`);

  return failCount === 0 ? results : null;
}

module.exports = { runTests };

if (require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}
