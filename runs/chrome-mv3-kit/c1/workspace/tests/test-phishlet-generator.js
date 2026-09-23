/**
 * Tests for phishlet generator (A5c)
 * Tests secret rejection, fixture generation, and basic structure
 */

import { generatePhishlet, exportPhishletYaml, validateNoPlaceholders } from '../generators/phishlet-generator.js';
import { validatePhishlet } from '../generators/phishlet-validator.js';

export function runPhishletGeneratorTests() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // Create test fixture
  function createTestCapture(events) {
    return {
      session_id: '00000000-0000-4000-8000-000000000001',
      started_at: '2026-09-05T12:00:00.000Z',
      stopped_at: '2026-09-05T12:05:00.000Z',
      coverage: 'complete',
      events: events
    };
  }

  test('Generates valid phishlet from simple capture', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session']
      },
      {
        url: 'https://login.example.test/post.srf',
        method: 'POST',
        status: 302,
        source: 'webRequest',
        set_cookie_names: ['auth'],
        form_fields: [{
          url: 'https://login.example.test/login',
          form_action: 'https://login.example.test/post.srf',
          fields: [
            { name: 'username', type: 'text' },
            { name: 'password', type: 'password' }
          ]
        }]
      }
    ]);

    const phishlet = generatePhishlet(capture);

    if (!phishlet.author) {
      throw new Error('Missing author');
    }
    if (phishlet.min_ver !== '2.3.0') {
      throw new Error('Wrong min_ver');
    }
    if (!Array.isArray(phishlet.proxy_hosts) || phishlet.proxy_hosts.length === 0) {
      throw new Error('Missing proxy_hosts');
    }
    if (!Array.isArray(phishlet.auth_tokens)) {
      throw new Error('auth_tokens must be array');
    }
    if (!phishlet.login || !phishlet.login.domain || !phishlet.login.path) {
      throw new Error('Invalid login structure');
    }
    if (!phishlet.credentials || typeof phishlet.credentials !== 'object') {
      throw new Error('credentials must be object/map');
    }
    if (!phishlet.credentials.username || !phishlet.credentials.password) {
      throw new Error('credentials must have username and password');
    }
  });

  test('Credentials use captured field names from password form', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: [],
        form_fields: [{
          url: 'https://login.example.test/login',
          form_action: 'https://login.example.test/post.srf',
          fields: [
            { name: 'loginfmt', type: 'hidden' },
            { name: 'passwd', type: 'password' }
          ]
        }]
      }
    ]);

    const phishlet = generatePhishlet(capture);

    if (phishlet.credentials.username.key !== 'loginfmt') {
      throw new Error(`Expected username.key=loginfmt, got ${phishlet.credentials.username.key}`);
    }
    if (phishlet.credentials.password.key !== 'passwd') {
      throw new Error(`Expected password.key=passwd, got ${phishlet.credentials.password.key}`);
    }
  });

  test('Credentials have non-placeholder search patterns', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'POST',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session']
      }
    ]);

    const phishlet = generatePhishlet(capture);

    if (!phishlet.credentials.username.search || phishlet.credentials.username.search === '{{PLACEHOLDER}}') {
      throw new Error('credentials.username.search is placeholder or empty');
    }
    if (!phishlet.credentials.password.search || phishlet.credentials.password.search === '{{PLACEHOLDER}}') {
      throw new Error('credentials.password.search is placeholder or empty');
    }

    // Default should be (.*)
    if (phishlet.credentials.username.search !== '(.*)') {
      throw new Error(`Expected default search (.*), got ${phishlet.credentials.username.search}`);
    }
  });

  test('sub_filters is non-empty array of objects', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session']
      }
    ]);

    const phishlet = generatePhishlet(capture);

    if (!Array.isArray(phishlet.sub_filters)) {
      throw new Error('sub_filters must be array');
    }
    if (phishlet.sub_filters.length === 0) {
      throw new Error('sub_filters must not be empty');
    }

    const filter = phishlet.sub_filters[0];
    if (typeof filter !== 'object' || Array.isArray(filter)) {
      throw new Error('sub_filters items must be objects, not strings');
    }

    const required = ['triggers_on', 'domain', 'search', 'replace', 'mimes'];
    for (const field of required) {
      if (!filter[field]) {
        throw new Error(`sub_filter missing required field: ${field}`);
      }
    }
  });

  test('No {{PLACEHOLDER}} in exported YAML', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session']
      }
    ]);

    const phishlet = generatePhishlet(capture);
    const yaml = exportPhishletYaml(phishlet);

    validateNoPlaceholders(yaml); // Throws if found
  });

  test('Generated phishlet validates against schema', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session'],
        form_fields: [{
          url: 'https://login.example.test/login',
          form_action: 'https://login.example.test/auth',
          fields: [
            { name: 'user', type: 'text' },
            { name: 'pass', type: 'password' }
          ]
        }]
      }
    ]);

    const phishlet = generatePhishlet(capture);
    const isValid = validatePhishlet(phishlet);

    if (!isValid) {
      throw new Error('Generated phishlet failed schema validation');
    }
  });

  test('Cookie names are captured in auth_tokens', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['MSPAuth', 'MSPProf', 'MSPOK']
      }
    ]);

    const phishlet = generatePhishlet(capture);

    if (phishlet.auth_tokens.length === 0) {
      throw new Error('No auth_tokens generated from cookies');
    }

    const tokens = phishlet.auth_tokens[0];
    if (!tokens.domain || !tokens.keys) {
      throw new Error('auth_tokens structure invalid');
    }

    if (tokens.keys.length !== 3) {
      throw new Error(`Expected 3 cookies, got ${tokens.keys.length}`);
    }
  });

  test('Empty auth_tokens is [] not null', () => {
    const capture = createTestCapture([
      {
        url: 'https://login.example.test/login',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: []
      }
    ]);

    const phishlet = generatePhishlet(capture);

    if (!Array.isArray(phishlet.auth_tokens)) {
      throw new Error('auth_tokens must be array even when empty');
    }
  });

  test('Telemetry hosts are excluded (copilot)', () => {
    const capture = createTestCapture([
      {
        url: 'https://copilot.example.test/api',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['tracking']
      },
      {
        url: 'https://login.example.test/auth',
        method: 'POST',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session']
      }
    ]);

    const phishlet = generatePhishlet(capture);

    // copilot.example.test should be filtered out
    const hasCopilot = phishlet.proxy_hosts.some(h =>
      h.domain.includes('copilot') || h.orig_sub.includes('copilot')
    );

    if (hasCopilot) {
      throw new Error('Copilot host should be excluded');
    }
  });

  test('Graph API hosts are excluded', () => {
    const capture = createTestCapture([
      {
        url: 'https://graph.example.test/v1.0/me',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['api_token']
      },
      {
        url: 'https://login.example.test/auth',
        method: 'POST',
        status: 200,
        source: 'webRequest',
        set_cookie_names: ['session']
      }
    ]);

    const phishlet = generatePhishlet(capture);

    const hasGraph = phishlet.proxy_hosts.some(h =>
      h.domain.includes('graph') || h.orig_sub === 'graph'
    );

    if (hasGraph) {
      throw new Error('Graph API host should be excluded');
    }
  });

  test('Throws on no auth-relevant hosts', () => {
    const capture = createTestCapture([
      {
        url: 'https://graph.example.test/api',
        method: 'GET',
        status: 200,
        source: 'webRequest',
        set_cookie_names: []
      }
    ]);

    try {
      generatePhishlet(capture);
      throw new Error('Should have thrown on no auth hosts');
    } catch (e) {
      if (!e.message.includes('no auth-relevant hosts')) {
        throw new Error(`Wrong error: ${e.message}`);
      }
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
