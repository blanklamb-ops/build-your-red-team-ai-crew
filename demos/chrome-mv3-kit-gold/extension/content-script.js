// Content script for capturing form field metadata (names only, never values)

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_FORM_FIELDS') {
    const formFields = captureFormFieldMetadata();
    chrome.runtime.sendMessage({
      type: 'FORM_FIELDS_CAPTURED',
      data: {
        url: window.location.href,
        form_fields: formFields
      }
    });
  }
});

function captureFormFieldMetadata() {
  const forms = document.querySelectorAll('form');
  const formData = [];

  for (const form of forms) {
    const formAction = form.action || window.location.href;
    const fields = [];

    // Capture input fields
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
