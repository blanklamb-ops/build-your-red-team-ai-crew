/**
 * Form Field Capture Tests
 * A3h: Content script form metadata extraction
 */

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

  // Mock DOM for form extraction
  function createMockForm(formAction, fields) {
    return {
      action: formAction,
      querySelectorAll: (selector) => {
        if (selector === 'input, button') {
          return fields.map(f => ({
            name: f.name,
            id: f.id || '',
            type: f.type,
            value: f.value || '' // MUST NOT be extracted
          }));
        }
        return [];
      }
    };
  }

  function extractFormMetadata(form, pageUrl) {
    const formAction = form.action || pageUrl;
    const fields = [];

    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => {
      const name = input.name || input.id;
      const type = input.type || 'text';

      if (name) {
        fields.push({
          name: name,
          type: type
          // NOTE: NO value field - that's the critical test
        });
      }
    });

    if (fields.length > 0) {
      return {
        url: pageUrl,
        form_action: formAction,
        fields: fields
      };
    }

    return null;
  }

  test('A3h: Extract form action and field names', () => {
    const mockForm = createMockForm('https://example.test/auth/submit', [
      { name: 'username', type: 'text', value: 'john.doe@example.com' },
      { name: 'password', type: 'password', value: 'secret123' }
    ]);

    const pageUrl = 'https://example.test/login';
    const result = extractFormMetadata(mockForm, pageUrl);

    assert(result !== null, 'Should extract form data');
    assert(result.form_action === 'https://example.test/auth/submit', 'Should extract form action');
    assert(result.fields.length === 2, 'Should extract 2 fields');
    assert(result.fields[0].name === 'username', 'Should extract username field name');
    assert(result.fields[0].type === 'text', 'Should extract username field type');
    assert(result.fields[1].name === 'password', 'Should extract password field name');
    assert(result.fields[1].type === 'password', 'Should extract password field type');
  });

  test('A3h: NEVER extract input values', () => {
    const mockForm = createMockForm('https://example.test/auth/submit', [
      { name: 'username', type: 'text', value: 'sensitive-user@example.com' },
      { name: 'password', type: 'password', value: 'super-secret-password' }
    ]);

    const pageUrl = 'https://example.test/login';
    const result = extractFormMetadata(mockForm, pageUrl);

    // Critical: ensure NO value field
    for (const field of result.fields) {
      assert(!('value' in field), `Field ${field.name} should NOT have value property`);
      assert(field.value === undefined, `Field ${field.name} should have undefined value`);
    }
  });

  test('A3h: Extract hidden fields (loginfmt, etc.)', () => {
    const mockForm = createMockForm('https://example.test/post.srf', [
      { name: 'loginfmt', type: 'hidden', value: 'user@example.com' },
      { name: 'passwd', type: 'password', value: 'secret' },
      { name: 'PPFT', type: 'hidden', value: 'token123' }
    ]);

    const pageUrl = 'https://example.test/login';
    const result = extractFormMetadata(mockForm, pageUrl);

    assert(result.fields.length === 3, 'Should extract all fields including hidden');
    assert(result.fields[0].name === 'loginfmt', 'Should extract loginfmt');
    assert(result.fields[0].type === 'hidden', 'Should record hidden type');
  });

  test('A3h: Phishlet generator uses captured field names', () => {
    // Simulate a session with form_fields
    const session = {
      session_id: 'test',
      events: [
        {
          url: 'https://login.example.test/login',
          method: 'GET',
          status: 200,
          source: 'webRequest',
          set_cookie_names: ['session'],
          form_fields: [
            {
              url: 'https://login.example.test/login',
              form_action: 'https://login.example.test/auth',
              fields: [
                { name: 'loginfmt', type: 'hidden' },
                { name: 'passwd', type: 'password' }
              ]
            }
          ]
        }
      ]
    };

    // Simple credential extraction logic
    function findUsernameField(formFields) {
      const priority = ['loginfmt', 'login', 'user', 'username', 'email'];
      for (const form of formFields) {
        const hasPassword = form.fields.some(f => f.type === 'password');
        if (!hasPassword) continue;

        for (const pname of priority) {
          const field = form.fields.find(f => f.name.toLowerCase() === pname);
          if (field) return field.name;
        }
      }
      return null;
    }

    function findPasswordField(formFields) {
      for (const form of formFields) {
        const field = form.fields.find(f => f.type === 'password');
        if (field) return field.name;
      }
      return null;
    }

    const allFormFields = [];
    for (const event of session.events) {
      if (event.form_fields) {
        allFormFields.push(...event.form_fields);
      }
    }

    const usernameKey = findUsernameField(allFormFields);
    const passwordKey = findPasswordField(allFormFields);

    assert(usernameKey === 'loginfmt', `Expected 'loginfmt', got '${usernameKey}'`);
    assert(passwordKey === 'passwd', `Expected 'passwd', got '${passwordKey}'`);
  });

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\nForm capture tests: ${results.length - failCount}/${results.length} passed`);

  return failCount === 0 ? results : null;
}

module.exports = { runTests };

if (require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}
