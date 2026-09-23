(function () {
  "use strict";
  if (typeof chrome === "undefined" || !chrome.runtime || globalThis.__labSnapshotReady) return;
  globalThis.__labSnapshotReady = true;
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (!message || message.type !== "SNAPSHOT_PAGE") return false;
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll("script, iframe, object, embed, base").forEach((node) => node.remove());
    clone.querySelectorAll("*").forEach((node) => {
      for (const attribute of [...node.attributes]) {
        if (/^on/i.test(attribute.name) || ["src", "srcset", "integrity", "nonce"].includes(attribute.name.toLowerCase())) node.removeAttribute(attribute.name);
      }
    });
    clone.querySelectorAll("input, textarea, select").forEach((node) => {
      node.removeAttribute("value"); node.removeAttribute("checked"); node.removeAttribute("selected");
      if ("textContent" in node && node.tagName.toLowerCase() === "textarea") node.textContent = "";
    });
    clone.querySelectorAll("form").forEach((form) => { form.setAttribute("action", "about:blank"); form.setAttribute("method", "get"); });
    const html = `<!doctype html>\n<!-- Authorized lab snapshot; scripts, remote sources, handlers, and form values removed. -->\n${clone.outerHTML}`;
    sendResponse({ ok: true, html, report: { url: location.href, title: document.title, captured_at: new Date().toISOString(), sanitation: "active content and form values removed" } });
    return false;
  });
})();
