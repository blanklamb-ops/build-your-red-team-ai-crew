(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LabFormCapture = api;
  if (typeof document !== "undefined" && typeof chrome !== "undefined" && chrome.runtime && !root.__labFormCaptureSent) {
    root.__labFormCaptureSent = true;
    const form_fields = api.captureFormMetadata(document, location.href);
    chrome.runtime.sendMessage({ type: "FORM_METADATA", payload: { url: location.href, form_fields } }).catch(() => {});
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  function captureFormMetadata(doc, pageUrl) {
    return Array.from(doc.querySelectorAll("form")).map((form) => {
      const fields = Array.from(form.querySelectorAll("input[name], button[name]"))
        .map((field) => ({ name: String(field.getAttribute("name")), type: String(field.getAttribute("type") ||
          (String(field.tagName).toLowerCase() === "button" ? "submit" : "text")).toLowerCase() }));
      const submit = form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
      let submitLabel = "";
      if (submit) submitLabel = String(submit.textContent || submit.getAttribute("aria-label") || submit.getAttribute("title") || "").trim().slice(0, 120);
      let formAction;
      try { formAction = new URL(form.getAttribute("action") || pageUrl, pageUrl).href; } catch (_) { formAction = pageUrl; }
      return { url: pageUrl, form_action: formAction, fields, ...(submitLabel ? { submit_label: submitLabel } : {}) };
    });
  }
  return { captureFormMetadata };
});
