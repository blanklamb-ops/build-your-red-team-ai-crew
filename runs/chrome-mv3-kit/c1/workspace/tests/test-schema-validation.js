/**
 * Tests for schema validation (A5d)
 * Tests that mutations fail validation
 */

import { validatePhishlet, getValidationErrors } from '../generators/phishlet-validator.js';

export function runSchemaValidationTests() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // Valid baseline phishlet
  const validPhishlet = {
    author: 'lab-operator',
    min_ver: '2.3.0',
    proxy_hosts: [
      {
        phish_sub: 'login',
        orig_sub: 'login',
        domain: 'example.test',
        session: true,
        is_landing: true,
        auto_filter: true
      }
    ],
    auth_tokens: [
      {
        domain: 'example.test',
        keys: ['session', 'auth']
      }
    ],
    auth_urls: ['/oauth/authorize'],
    login: {
      domain: 'example.test',
      path: '/login'
    },
    credentials: {
      username: {
        key: 'login',
        search: '(.*)',
        type: 'post'
      },
      password: {
        key: 'passwd',
        search: '(.*)',
        type: 'post'
      }
    },
    sub_filters: [
      {
        triggers_on: 'login.example.test',
        orig_sub: 'login',
        domain: 'example.test',
        search: 'https://{hostname}/',
        replace: 'https://{hostname}/',
        mimes: ['text/html']
      }
    ]
  };

  test('Valid phishlet passes validation', () => {
    const valid = validatePhishlet({ ...validPhishlet });
    if (!valid) {
      throw new Error('Valid phishlet failed validation');
    }
  });

  test('Missing author fails', () => {
    const invalid = { ...validPhishlet };
    delete invalid.author;

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail without author');
    }
  });

  test('Wrong min_ver fails', () => {
    const invalid = { ...validPhishlet, min_ver: '3.0.0' };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with wrong min_ver');
    }
  });

  test('Top-level name key fails (forbidden)', () => {
    const invalid = { ...validPhishlet, name: 'example' };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with top-level name key');
    }
  });

  test('login.username key fails (forbidden)', () => {
    const invalid = {
      ...validPhishlet,
      login: {
        domain: 'example.test',
        path: '/login',
        username: 'user' // Forbidden in 2.3.0
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with login.username');
    }
  });

  test('login.password key fails (forbidden)', () => {
    const invalid = {
      ...validPhishlet,
      login: {
        domain: 'example.test',
        path: '/login',
        password: 'pass' // Forbidden in 2.3.0
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with login.password');
    }
  });

  test('credentials as array fails (must be map)', () => {
    const invalid = {
      ...validPhishlet,
      credentials: [
        { key: 'login', search: '(.*)', type: 'post' }
      ]
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with credentials as array');
    }
  });

  test('Empty credentials fails', () => {
    const invalid = {
      ...validPhishlet,
      credentials: {}
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with empty credentials');
    }
  });

  test('Missing credentials.username fails', () => {
    const invalid = {
      ...validPhishlet,
      credentials: {
        password: {
          key: 'passwd',
          search: '(.*)',
          type: 'post'
        }
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail without credentials.username');
    }
  });

  test('Missing credentials.password fails', () => {
    const invalid = {
      ...validPhishlet,
      credentials: {
        username: {
          key: 'login',
          search: '(.*)',
          type: 'post'
        }
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail without credentials.password');
    }
  });

  test('Missing credentials.*.search fails', () => {
    const invalid = {
      ...validPhishlet,
      credentials: {
        username: {
          key: 'login',
          type: 'post'
          // Missing search
        },
        password: {
          key: 'passwd',
          search: '(.*)',
          type: 'post'
        }
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail without credentials.username.search');
    }
  });

  test('Empty sub_filters array fails', () => {
    const invalid = {
      ...validPhishlet,
      sub_filters: []
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with empty sub_filters');
    }
  });

  test('sub_filters as string array fails', () => {
    const invalid = {
      ...validPhishlet,
      sub_filters: ['{{PLACEHOLDER}}']
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with string array sub_filters');
    }
  });

  test('Missing sub_filter required fields fails', () => {
    const invalid = {
      ...validPhishlet,
      sub_filters: [
        {
          domain: 'example.test',
          search: 'x',
          replace: 'y'
          // Missing triggers_on, orig_sub, mimes
        }
      ]
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with incomplete sub_filter');
    }
  });

  test('auth_tokens with value key fails (only keys array allowed)', () => {
    const invalid = {
      ...validPhishlet,
      auth_tokens: [
        {
          domain: 'example.test',
          keys: ['session'],
          value: 'secret123' // Forbidden
        }
      ]
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with value in auth_tokens');
    }
  });

  test('Empty proxy_hosts fails', () => {
    const invalid = {
      ...validPhishlet,
      proxy_hosts: []
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with empty proxy_hosts');
    }
  });

  test('Missing login.domain fails', () => {
    const invalid = {
      ...validPhishlet,
      login: {
        path: '/login'
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail without login.domain');
    }
  });

  test('Missing login.path fails', () => {
    const invalid = {
      ...validPhishlet,
      login: {
        domain: 'example.test'
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail without login.path');
    }
  });

  test('Invalid credential type fails', () => {
    const invalid = {
      ...validPhishlet,
      credentials: {
        username: {
          key: 'login',
          search: '(.*)',
          type: 'invalid' // Must be post or json
        },
        password: {
          key: 'passwd',
          search: '(.*)',
          type: 'post'
        }
      }
    };

    const valid = validatePhishlet(invalid);
    if (valid) {
      throw new Error('Should fail with invalid credential type');
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
