// Content script for form field metadata capture
// Records form actions and input names (NEVER values) for phishlet credential mapping

(function() {
  'use strict';

  // Check if this is an auth-relevant page
  function isAuthRelevantPage() {
    const url = window.location.href.toLowerCase();
    const keywords = [
      'login', 'signin', 'auth', 'oauth', 'saml',
      'password', 'credential', 'account', 'sso'
    ];
    return keywords.some(kw => url.includes(kw));
  }

  // Extract form metadata
  function extractFormMetadata() {
    const forms = document.querySelectorAll('form');
    const formData = [];

    forms.forEach(form => {
      const formAction = form.action || window.location.href;
      const fields = [];

      // Get all input and button elements
      const inputs = form.querySelectorAll('input, button');
      inputs.forEach(input => {
        const name = input.name || input.id;
        const type = input.type || 'text';

        if (name) {
          fields.push({
            name: name,
            type: type
          });
        }
      });

      if (fields.length > 0) {
        formData.push({
          url: window.location.href,
          form_action: formAction,
          fields: fields
        });
      }
    });

    return formData;
  }

  // Send form metadata to service worker
  function sendFormMetadata() {
    const forms = extractFormMetadata();

    if (forms.length > 0) {
      chrome.runtime.sendMessage({
        action: 'recordFormFields',
        data: {
          url: window.location.href,
          forms: forms
        }
      }).catch(() => {
        // Service worker might not be ready, ignore
      });
    }
  }

  // Run on auth-relevant pages
  if (isAuthRelevantPage()) {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', sendFormMetadata);
    } else {
      sendFormMetadata();
    }
  }
})();
