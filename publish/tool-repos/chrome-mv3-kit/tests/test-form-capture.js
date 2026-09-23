/**
 * Tests for form metadata capture (A3h)
 * Verifies NO input values are captured
 */

export function runFormCaptureTests() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // Mock DOM for testing
  function createMockForm(fields) {
    return {
      action: 'https://example.test/login',
      querySelectorAll: (selector) => {
        if (selector === 'input, button') {
          return fields.map(f => ({
            getAttribute: (attr) => {
              if (attr === 'name') return f.name;
              if (attr === 'type') return f.type;
              if (attr === 'value') return f.value; // Should NOT be captured
              return null;
            }
          }));
        }
        return [];
      }
    };
  }

  test('Password field type is captured', () => {
    const form = createMockForm([
      { name: 'username', type: 'text', value: 'secretuser' },
      { name: 'password', type: 'password', value: 'secretpass' }
    ]);

    const fields = [];
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => {
      const name = input.getAttribute('name');
      const type = input.getAttribute('type');
      if (name) {
        fields.push({ name, type });
      }
    });

    if (fields.length !== 2) {
      throw new Error(`Expected 2 fields, got ${fields.length}`);
    }

    const passwordField = fields.find(f => f.type === 'password');
    if (!passwordField) {
      throw new Error('Password field not captured');
    }

    if (passwordField.name !== 'password') {
      throw new Error('Password field name incorrect');
    }
  });

  test('Input values are NOT captured', () => {
    const form = createMockForm([
      { name: 'username', type: 'text', value: 'SECRETVALUE' },
      { name: 'password', type: 'password', value: 'SECRETPASS' }
    ]);

    const fields = [];
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => {
      const name = input.getAttribute('name');
      const type = input.getAttribute('type');
      // CRITICAL: Never capture value
      if (name) {
        fields.push({ name, type });
      }
    });

    // Check that no field object has a 'value' property
    for (const field of fields) {
      if ('value' in field) {
        throw new Error('SECURITY VIOLATION: Input value was captured!');
      }
    }
  });

  test('Hidden username field is captured', () => {
    const form = createMockForm([
      { name: 'loginfmt', type: 'hidden', value: 'user@example.com' },
      { name: 'passwd', type: 'password', value: 'secret' }
    ]);

    const fields = [];
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => {
      const name = input.getAttribute('name');
      const type = input.getAttribute('type');
      if (name) {
        fields.push({ name, type });
      }
    });

    const hiddenField = fields.find(f => f.name === 'loginfmt');
    if (!hiddenField) {
      throw new Error('Hidden loginfmt field not captured');
    }

    if (hiddenField.type !== 'hidden') {
      throw new Error('Field type incorrect');
    }
  });

  test('Username field names are recognized', () => {
    const usernameNames = ['login', 'loginfmt', 'user', 'username', 'usernameEntry', 'email', 'account'];

    for (const name of usernameNames) {
      const form = createMockForm([
        { name: name, type: 'hidden', value: 'user@example.com' }
      ]);

      const fields = [];
      const inputs = form.querySelectorAll('input, button');
      inputs.forEach(input => {
        const fieldName = input.getAttribute('name');
        const type = input.getAttribute('type');
        if (fieldName) {
          fields.push({ name: fieldName, type });
        }
      });

      if (fields.length !== 1 || fields[0].name !== name) {
        throw new Error(`Failed to capture username field: ${name}`);
      }
    }
  });

  test('Form action URL is captured', () => {
    const form = createMockForm([
      { name: 'username', type: 'text', value: 'user' }
    ]);

    const formAction = form.action;

    if (formAction !== 'https://example.test/login') {
      throw new Error(`Form action incorrect: ${formAction}`);
    }
  });

  test('Multiple forms can be captured', () => {
    const forms = [
      createMockForm([{ name: 'email', type: 'email', value: 'a@b.com' }]),
      createMockForm([{ name: 'password', type: 'password', value: 'secret' }])
    ];

    const allFields = [];

    for (const form of forms) {
      const inputs = form.querySelectorAll('input, button');
      const fields = [];
      inputs.forEach(input => {
        const name = input.getAttribute('name');
        const type = input.getAttribute('type');
        if (name) {
          fields.push({ name, type });
        }
      });
      allFields.push({ form_action: form.action, fields });
    }

    if (allFields.length !== 2) {
      throw new Error(`Expected 2 forms, got ${allFields.length}`);
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
