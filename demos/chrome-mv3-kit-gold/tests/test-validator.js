// Test phishlet YAML validator

const fs = require('fs');
const path = require('path');
const { validatePhishlet } = require('../generators/validator.js');

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function testValidator() {
  console.log('Testing YAML validator...');

  const schemaPath = path.join(__dirname, '../schemas/phishlet-schema.json');

  // Valid phishlet
  const validYaml = `
name: 'test-phishlet'
min_ver: '3.0.0'
proxy_hosts:
  - phish_sub: 'login'
    orig_sub: 'login'
    domain: 'example.test'
    session: true
    is_landing: true
    auto_filter: true
auth_tokens:
  - domain: 'example.test'
    keys:
      - 'session_id'
      - 'csrf_token'
auth_urls:
  - '/auth/login'
  - '/oauth/authorize'
login:
  domain: 'example.test'
  path: '/auth/login'
  username: 'login'
  password: 'passwd'
credentials:
  - key: 'login'
    search: '{{PLACEHOLDER}}'
    type: 'username'
  - key: 'passwd'
    search: '{{PLACEHOLDER}}'
    type: 'password'
sub_filters:
  - '{{PLACEHOLDER}}'
`;

  try {
    validatePhishlet(validYaml, schemaPath);
    console.log('  ✓ Valid phishlet passes');
  } catch (e) {
    throw new Error(`Valid phishlet should pass: ${e.message}`);
  }

  // Missing required property
  const missingName = validYaml.replace("name: 'test-phishlet'", "removed_name: 'test-phishlet'");
  try {
    validatePhishlet(missingName, schemaPath);
    throw new Error('Should fail on missing name');
  } catch (e) {
    assert(e.message.includes('validation failed') || e.message.includes('required'), 'Rejects missing name');
    console.log('  ✓ Rejects missing required property');
  }

  // Forbidden property
  const forbiddenProp = validYaml + "\nforbidden_field: 'value'\n";
  try {
    validatePhishlet(forbiddenProp, schemaPath);
    throw new Error('Should fail on forbidden property');
  } catch (e) {
    assert(e.message.includes('validation failed') || e.message.includes('additional'), 'Rejects forbidden property');
    console.log('  ✓ Rejects forbidden top-level property');
  }

  // Cookie value key (forbidden)
  const cookieValue = `
name: 'test'
min_ver: '3.0.0'
proxy_hosts:
  - phish_sub: 'login'
    orig_sub: 'login'
    domain: 'example.test'
    session: true
    is_landing: true
    auto_filter: true
auth_tokens:
  - domain: 'example.test'
    keys:
      - 'session_id'
    value: 'abc123'
auth_urls: []
login:
  domain: 'example.test'
  path: '/'
credentials: []
sub_filters:
  - '{{PLACEHOLDER}}'
`;

  try {
    validatePhishlet(cookieValue, schemaPath);
    throw new Error('Should fail on cookie value key');
  } catch (e) {
    assert(e.message.includes('value') || e.message.includes('additional properties'), 'Rejects cookie value key');
    console.log('  ✓ Rejects cookie value key');
  }

  // Wrong auth_tokens shape (map instead of list)
  const wrongShape = `
name: 'test'
min_ver: '3.0.0'
proxy_hosts:
  - phish_sub: 'login'
    orig_sub: 'login'
    domain: 'example.test'
    session: true
    is_landing: true
    auto_filter: true
auth_tokens:
  example.test:
    - name: 'session_id'
auth_urls: []
login:
  domain: 'example.test'
  path: '/'
credentials: []
sub_filters:
  - '{{PLACEHOLDER}}'
`;

  try {
    validatePhishlet(wrongShape, schemaPath);
    throw new Error('Should fail on wrong auth_tokens shape');
  } catch (e) {
    assert(e.message.includes('validation failed'), 'Rejects wrong auth_tokens shape');
    console.log('  ✓ Rejects wrong auth_tokens shape');
  }

  // Non-placeholder credential pattern
  const nonPlaceholder = `
name: 'test'
min_ver: '3.0.0'
proxy_hosts:
  - phish_sub: 'login'
    orig_sub: 'login'
    domain: 'example.test'
    session: true
    is_landing: true
    auto_filter: true
auth_tokens: []
auth_urls: []
login:
  domain: 'example.test'
  path: '/'
credentials:
  - key: 'username'
    search: '(.+)'
    type: 'username'
sub_filters:
  - '{{PLACEHOLDER}}'
`;

  try {
    validatePhishlet(nonPlaceholder, schemaPath);
    throw new Error('Should fail on non-placeholder credential');
  } catch (e) {
    assert(e.message.includes('Non-placeholder'), 'Rejects non-placeholder credential pattern');
    console.log('  ✓ Rejects non-placeholder credential pattern');
  }

  // Malformed YAML
  const malformed = "name: 'test'\nbroken yaml: [unclosed";
  try {
    validatePhishlet(malformed, schemaPath);
    throw new Error('Should fail on malformed YAML');
  } catch (e) {
    assert(e.message.includes('parse error') || e.message.includes('YAML'), 'Rejects malformed YAML');
    console.log('  ✓ Rejects malformed YAML');
  }

  // Null auth_tokens (should fail - must be array)
  const nullTokens = validYaml.replace('auth_tokens:\n  - domain:', 'auth_tokens: null\nignored:\n  - domain:');
  try {
    validatePhishlet(nullTokens, schemaPath);
    throw new Error('Should fail on null auth_tokens');
  } catch (e) {
    assert(e.message.includes('validation failed'), 'Rejects null auth_tokens');
    console.log('  ✓ Rejects null auth_tokens (must be array)');
  }

  console.log('✓ All validator tests passed');
}

module.exports = { testValidator };

if (require.main === module) {
  testValidator();
}
