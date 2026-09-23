importScripts("shared.js", "state.js");

const controller = LabState.createController(chrome);

function cookieNames(headers) {
  const names = [];
  for (const header of headers || []) {
    if (String(header.name).toLowerCase() !== "set-cookie" || typeof header.value !== "string") continue;
    const name = header.value.split(";", 1)[0].split("=", 1)[0].trim();
    if (name) names.push(name);
  }
  return names;
}

chrome.webRequest.onBeforeRequest.addListener((details) => {
  controller.addEvent({
    request_id: details.requestId,
    url: details.url,
    method: details.method,
    resource_type: details.type,
    source: "webRequest_request",
    timestamp: new Date(details.timeStamp).toISOString()
  }).catch(() => {});
}, { urls: ["http://*/*", "https://*/*"] });

chrome.webRequest.onBeforeSendHeaders.addListener((details) => {
  controller.addEvent({
    request_id: details.requestId,
    url: details.url,
    method: details.method,
    resource_type: details.type,
    source: "webRequest_request",
    request_header_names: (details.requestHeaders || []).map((header) => header.name),
    timestamp: new Date(details.timeStamp).toISOString()
  }).catch(() => {});
}, { urls: ["http://*/*", "https://*/*"] }, ["requestHeaders", "extraHeaders"]);

chrome.webRequest.onCompleted.addListener((details) => {
  controller.addEvent({
    request_id: details.requestId,
    url: details.url,
    method: details.method,
    status: details.statusCode,
    resource_type: details.type,
    source: "webRequest_response",
    response_header_names: (details.responseHeaders || []).map((header) => header.name),
    set_cookie_names: cookieNames(details.responseHeaders),
    timestamp: new Date(details.timeStamp).toISOString()
  }).catch(() => {});
}, { urls: ["http://*/*", "https://*/*"] }, ["responseHeaders", "extraHeaders"]);

chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId !== 0 || !LabShared.isHttpUrl(details.url)) return;
  controller.addEvent({ url: details.url, resource_type: "main_frame", source: "webNavigation_fallback",
    timestamp: new Date(details.timeStamp).toISOString() }).catch(() => {});
  chrome.scripting.executeScript({ target: { tabId: details.tabId, frameIds: [0] }, files: ["form_capture.js"] })
    .catch(() => {});
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    switch (message && message.type) {
      case "STATE_GET": return controller.export();
      case "ORIGINS_SET": return controller.setOrigins(message.payload.origins);
      case "START": return controller.start();
      case "STOP": return controller.stop();
      case "FORM_METADATA":
        if (sender.frameId !== 0) return controller.load();
        return controller.addEvent({ url: message.payload.url, resource_type: "main_frame",
          source: "form_metadata", form_fields: message.payload.form_fields });
      case "EXPORT_JSON": return controller.export();
      case "EXPORT_MARKDOWN": return LabShared.sessionToMarkdown(await controller.export());
      default: throw new Error("Unknown extension message");
    }
  })().then((data) => sendResponse({ ok: true, data }), (error) => sendResponse({ ok: false, error: error.message }));
  return true;
});
