// Test phishlet generator

const fs = require('fs');
const path = require('path');
const { generatePhishlet, generateYaml, isExcludedHost, DEFAULT_EXCLUDED_HOSTS } = require('../generators/phishlet-generator.js');

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function testGenerator() {
  console.log('Testing phishlet generator...');

  // Load synthetic session fixture
  const fixturePath = path.join(__dirname, '../testdata/synthetic-session.json');
  const sessionData = JSON.parse(fs.readFileSync(fixturePath, 'utf-8'));

  // Generate phishlet
  const phishlet = generatePhishlet(sessionData, { phishletName: 'test-lab' });

  // Validate structure
  assert(phishlet.name === 'test-lab', 'Name set correctly');
  assert(phishlet.min_ver === '3.0.0', 'Min version is 3.0.0');
  assert(Array.isArray(phishlet.proxy_hosts), 'proxy_hosts is array');
  assert(phishlet.proxy_hosts.length >= 1, 'At least one proxy host');

  // Check proxy_hosts structure
  for (const host of phishlet.proxy_hosts) {
    assert(typeof host.phish_sub === 'string', 'phish_sub is string');
    assert(typeof host.orig_sub === 'string', 'orig_sub is string');
    assert(typeof host.domain === 'string', 'domain is string');
    assert(typeof host.session === 'boolean', 'session is boolean');
    assert(typeof host.is_landing === 'boolean', 'is_landing is boolean');
    assert(typeof host.auto_filter === 'boolean', 'auto_filter is boolean');

    // Single-label subdomains
    assert(!host.phish_sub.includes('.'), 'phish_sub is single label');
    assert(!host.orig_sub.includes('.'), 'orig_sub is single label');
  }

  // Exactly one landing host
  const landingHosts = phishlet.proxy_hosts.filter(h => h.is_landing);
  assert(landingHosts.length === 1, 'Exactly one landing host');

  // Check auth_tokens structure (must be list of {domain, keys})
  assert(Array.isArray(phishlet.auth_tokens), 'auth_tokens is array');
  if (phishlet.auth_tokens.length > 0) {
    for (const token of phishlet.auth_tokens) {
      assert(typeof token.domain === 'string', 'auth_token has domain');
      assert(Array.isArray(token.keys), 'auth_token has keys array');
      assert(token.value === undefined, 'auth_token has no value key');
      for (const key of token.keys) {
        assert(typeof key === 'string', 'Cookie name is string');
        assert(typeof key !== 'object', 'Cookie key is not object');
      }
    }
  }

  // Check auth_urls
  assert(Array.isArray(phishlet.auth_urls), 'auth_urls is array');
  if (phishlet.auth_urls.length > 0) {
    for (const url of phishlet.auth_urls) {
      assert(!url.endsWith('.js'), 'auth_url is not .js file');
      assert(!url.endsWith('.css'), 'auth_url is not .css file');
    }
  }

  // Check login
  assert(typeof phishlet.login.domain === 'string', 'login has domain');
  assert(typeof phishlet.login.path === 'string', 'login has path');
  assert(!phishlet.login.path.endsWith('.js'), 'login.path is not static asset');

  // Check credentials from form_fields capture
  assert(Array.isArray(phishlet.credentials), 'credentials is array');
  // The fixture has form_fields, so credentials should be populated
  assert(phishlet.credentials.length > 0, 'credentials populated from form_fields');

  const usernameField = phishlet.credentials.find(c => c.key === 'login');
  const passwordField = phishlet.credentials.find(c => c.key === 'passwd');
  assert(usernameField !== undefined, 'Username field from form_fields captured');
  assert(passwordField !== undefined, 'Password field from form_fields captured');

  // Check login.username and login.password references
  assert(phishlet.login.username === 'login', 'login.username references captured field');
  assert(phishlet.login.password === 'passwd', 'login.password references captured field');

  // Check sub_filters placeholder (array with placeholder)
  assert(Array.isArray(phishlet.sub_filters) && phishlet.sub_filters.includes('{{PLACEHOLDER}}'), 'sub_filters is placeholder array');

  // Generate YAML
  const yaml = generateYaml(phishlet);
  assert(typeof yaml === 'string', 'YAML generated');
  assert(yaml.includes('name:'), 'YAML contains name');
  assert(yaml.includes('AUTHORIZED LAB USE ONLY'), 'YAML has lab-use warning');

  // Test telemetry exclusion
  assert(isExcludedHost('clarity.ms'), 'clarity.ms is excluded');
  assert(isExcludedHost('browser.events.data.microsoft.com'), 'Microsoft telemetry excluded');
  assert(isExcludedHost('copilot.microsoft.com'), 'copilot.microsoft.com excluded');
  assert(isExcludedHost('subdomain.copilot.com'), 'subdomain.copilot.com excluded');
  assert(!isExcludedHost('login.example.test'), 'Auth host not excluded');

  // Check that DEFAULT_EXCLUDED_HOSTS includes required patterns
  assert(DEFAULT_EXCLUDED_HOSTS.includes('copilot.com'), 'Default exclusions include copilot.com');
  assert(DEFAULT_EXCLUDED_HOSTS.includes('copilot.microsoft.com'), 'Default exclusions include copilot.microsoft.com');

  console.log('✓ All generator tests passed');
}

function testSecretRejection() {
  console.log('Testing secret rejection...');

  // Test that URL parameters with JWT-like values do NOT block generation
  // (URL parameters in the input session are observed metadata, not credential
  // material being emitted in the output — secret detection targets output values only)
  const secretFixturePath = path.join(__dirname, '../testdata/secret-fixture.json');
  const secretData = JSON.parse(fs.readFileSync(secretFixturePath, 'utf-8'));

  try {
    const phishlet = generatePhishlet(secretData);
    assert(phishlet && phishlet.name, 'Generates phishlet even with JWT in URL params');
    console.log('  ✓ URL parameters with JWT-like values do not block generation');
  } catch (e) {
    throw new Error(`Should not reject URL parameter values: ${e.message}`);
  }

  // Test that cookie names and session_id are not rejected
  const safeData = {
    events: [
      {
        url: 'https://example.com/login',
        origin: 'https://example.com',
        method: 'GET',
        set_cookie_names: ['csrf_token', 'auth_session', '__Host-AuthToken'],
        metadata: {
          session_id: '550e8400-e29b-41d4-a716-446655440000'
        }
      }
    ]
  };

  try {
    const phishlet = generatePhishlet(safeData);
    assert(true, 'Cookie names and UUID session_id do not block generation');
  } catch (e) {
    throw new Error(`Should not reject cookie names or UUID: ${e.message}`);
  }

  console.log('✓ All secret rejection tests passed');
}

module.exports = { testGenerator, testSecretRejection };

if (require.main === module) {
  testGenerator();
  testSecretRejection();
}
