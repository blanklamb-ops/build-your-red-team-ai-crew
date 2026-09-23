/**
 * Schema Validation Tests
 * A5d: JSON Schema validation with mutation testing
 */

const fs = require('fs');
const yaml = require('js-yaml');
const Ajv = require('ajv');

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

  const schemaPath = 'schemas/phishlet-schema-2.3.0.json';
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

  function validatePhishlet(phishlet) {
    const ajv = new Ajv();
    const validate = ajv.compile(schema);
    const valid = validate(phishlet);

    if (!valid) {
      return { valid: false, errors: validate.errors };
    }

    // Additional substring check
    const yamlText = yaml.dump(phishlet);
    if (yamlText.includes('{{PLACEHOLDER}}')) {
      return { valid: false, errors: [{ message: 'Contains {{PLACEHOLDER}}' }] };
    }

    return { valid: true };
  }

  // Load a valid phishlet
  const phishletGen = require('../generators/phishlet-generator.js');
  const session = JSON.parse(fs.readFileSync('testdata/example-simple.json', 'utf8'));
  const validPhishlet = phishletGen.generatePhishlet(session);

  test('A5d: Valid phishlet passes schema', () => {
    const result = validatePhishlet(validPhishlet);
    assert(result.valid, `Valid phishlet should pass: ${JSON.stringify(result.errors)}`);
  });

  test('A5d: Missing author fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    delete invalid.author;

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail without author');
  });

  test('A5d: Wrong min_ver fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.min_ver = '3.0.0';

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with wrong min_ver');
  });

  test('A5d: Top-level name fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.name = 'my-phishlet';

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with top-level name');
  });

  test('A5d: Cookie with value key fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    if (invalid.auth_tokens.length > 0) {
      invalid.auth_tokens[0].value = 'some-value';
    }

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with cookie value key');
  });

  test('A5d: credentials as list fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.credentials = [
      { key: 'username', search: '(.*)', type: 'post' },
      { key: 'password', search: '(.*)', type: 'post' }
    ];

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with credentials as list');
  });

  test('A5d: sub_filters as string list fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.sub_filters = ['{{PLACEHOLDER}}'];

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with sub_filters as string list');
  });

  test('A5d: login with username key fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.login.username = 'some-key';

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with login.username');
  });

  test('A5d: login with password key fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.login.password = 'some-key';

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with login.password');
  });

  test('A5d: {{PLACEHOLDER}} in search fails', () => {
    const invalid = JSON.parse(JSON.stringify(validPhishlet));
    invalid.credentials.username.search = '{{PLACEHOLDER}}';

    const result = validatePhishlet(invalid);
    assert(!result.valid, 'Should fail with {{PLACEHOLDER}} in search');
  });

  test('A5d: Malformed YAML fails to parse', () => {
    let threw = false;
    try {
      yaml.load('invalid: yaml: content: [');
    } catch (e) {
      threw = true;
    }
    assert(threw, 'Should fail to parse malformed YAML');
  });

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\nSchema validation tests: ${results.length - failCount}/${results.length} passed`);

  return failCount === 0 ? results : null;
}

module.exports = { runTests };

if (require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}
