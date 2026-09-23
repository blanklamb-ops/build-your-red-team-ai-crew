// Test form field metadata capture (no values)

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function testFormCapture() {
  console.log('Testing form field capture...');

  // Mock DOM
  const mockForm = {
    action: 'https://example.test/auth/login',
    querySelectorAll: (selector) => {
      if (selector === 'input, button') {
        return [
          {
            getAttribute: (attr) => {
              if (attr === 'name') return 'username';
              if (attr === 'type') return 'text';
            }
          },
          {
            getAttribute: (attr) => {
              if (attr === 'name') return 'password';
              if (attr === 'type') return 'password';
            }
          },
          {
            getAttribute: (attr) => {
              if (attr === 'name') return null; // No name
              if (attr === 'type') return 'submit';
            }
          }
        ];
      }
      return [];
    }
  };

  global.document = {
    querySelectorAll: (selector) => {
      if (selector === 'form') {
        return [mockForm];
      }
      return [];
    }
  };

  global.window = {
    location: {
      href: 'https://example.test/login'
    }
  };

  // Import and execute the content script logic inline
  function captureFormFieldMetadata() {
    const forms = document.querySelectorAll('form');
    const formData = [];

    for (const form of forms) {
      const formAction = form.action || window.location.href;
      const fields = [];

      const inputs = form.querySelectorAll('input, button');
      for (const input of inputs) {
        const name = input.getAttribute('name');
        const type = input.getAttribute('type') || 'text';

        if (name) {
          fields.push({
            name: name,
            type: type
          });
        }
      }

      if (fields.length > 0) {
        formData.push({
          form_action: formAction,
          fields: fields
        });
      }
    }

    return formData;
  }

  const captured = captureFormFieldMetadata();

  assert(captured.length === 1, 'Captured one form');
  assert(captured[0].form_action === 'https://example.test/auth/login', 'Form action captured');
  assert(captured[0].fields.length === 2, 'Captured two named fields (skipped unnamed submit)');
  assert(captured[0].fields[0].name === 'username', 'Username field captured');
  assert(captured[0].fields[0].type === 'text', 'Username type captured');
  assert(captured[0].fields[1].name === 'password', 'Password field captured');
  assert(captured[0].fields[1].type === 'password', 'Password type captured');

  // Verify no values captured
  for (const formData of captured) {
    for (const field of formData.fields) {
      assert(field.value === undefined, 'No field values captured');
      assert(field.defaultValue === undefined, 'No default values captured');
    }
  }

  console.log('✓ All form capture tests passed');
}

module.exports = { testFormCapture };

if (require.main === module) {
  testFormCapture();
}
