/**
 * Content script for form metadata capture
 * Captures form structure (action URLs, field names/types) - NEVER values
 */

// Priority username field names (exact match, case-insensitive)
const USERNAME_FIELD_NAMES = [
  'login',
  'loginfmt',
  'user',
  'username',
  'usernameEntry',
  'email',
  'account'
];

/**
 * Capture form metadata on page load
 */
function captureFormMetadata() {
  const forms = document.querySelectorAll('form');
  if (forms.length === 0) return;

  const formFields = [];

  forms.forEach(form => {
    const formAction = form.action || window.location.href;
    const fields = [];

    // Capture all input and button elements with name attributes
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => {
      const name = input.getAttribute('name');
      const type = input.getAttribute('type') || 'text';

      if (name) {
        fields.push({
          name: name,
          type: type
        });
      }
    });

    if (fields.length > 0) {
      formFields.push({
        url: window.location.href,
        form_action: formAction,
        fields: fields
      });
    }
  });

  // Send to service worker
  if (formFields.length > 0) {
    chrome.runtime.sendMessage({
      action: 'addFormFields',
      url: window.location.href,
      formFields: formFields
    }).catch(err => {
      // Service worker may not be ready, ignore errors
      console.debug('[Form Capture] Could not send form fields:', err);
    });
  }
}

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', captureFormMetadata);
} else {
  // Already loaded
  captureFormMetadata();
}

// Also capture on dynamic form changes (with debounce)
let captureTimeout;
const observer = new MutationObserver(() => {
  clearTimeout(captureTimeout);
  captureTimeout = setTimeout(captureFormMetadata, 500);
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});
