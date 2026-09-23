// chrome-mv3-kit — auth-flow recorder service worker (R1/R2).
//
// Records HTTP request/response METADATA ONLY for the currently-open
// recording session: URL, method, status code, resource type, and the
// NAMES of any auth-related headers observed (never header/cookie values,
// never bodies). Everything is written to chrome.storage.local. This
// worker makes no network requests of its own and never sends captured
// data anywhere off-host — there is no fetch()/XHR call in this file.
//
// Recording is OFF by default and only observes hosts the user has
// explicitly granted via the optional_host_permissions runtime prompt
// (see popup.js "Grant lab host access").
//
// v0.1.1: record ALL requests while recording (not only those that already
// carry auth header names), plus webNavigation main_frame fallback so a
// simple page load is never a silent zero-event session when host access
// was granted.

import { isAuthRelatedHeaderName, extractCookieNamesFromSetCookie } from "./auth_header_patterns.js";

const STORAGE_KEY_SESSION = "chrome_mv3_kit_current_session";
const STORAGE_KEY_RECORDING = "chrome_mv3_kit_recording";

function nowIso() {
  return new Date().toISOString();
}

function newSessionId() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : `sess-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function getRecordingState() {
  const { [STORAGE_KEY_RECORDING]: recording } = await chrome.storage.local.get(
    STORAGE_KEY_RECORDING
  );
  return Boolean(recording);
}

async function getSession() {
  const { [STORAGE_KEY_SESSION]: session } = await chrome.storage.local.get(
    STORAGE_KEY_SESSION
  );
  return session || null;
}

async function setSession(session) {
  await chrome.storage.local.set({ [STORAGE_KEY_SESSION]: session });
}

async function startRecording(targetLabel) {
  const session = {
    session_id: newSessionId(),
    started_at_iso: nowIso(),
    ended_at_iso: null,
    target_label: targetLabel || "(unlabeled lab session)",
    notes: "",
    events: [],
  };
  await setSession(session);
  await chrome.storage.local.set({ [STORAGE_KEY_RECORDING]: true });
  return session;
}

async function stopRecording() {
  const session = await getSession();
  if (session && !session.ended_at_iso) {
    session.ended_at_iso = nowIso();
    await setSession(session);
  }
  await chrome.storage.local.set({ [STORAGE_KEY_RECORDING]: false });
  return session;
}

async function recordEvent(partialEvent) {
  const recording = await getRecordingState();
  if (!recording) return;
  const session = await getSession();
  if (!session) return;

  session.events.push({
    timestamp_iso: nowIso(),
    url: partialEvent.url,
    method: partialEvent.method || "GET",
    status_code: partialEvent.status_code ?? null,
    type: partialEvent.type || "unknown",
    auth_header_names: partialEvent.auth_header_names || [],
    set_cookie_names: partialEvent.set_cookie_names || [],
  });
  await setSession(session);
}

async function hostAccessGranted() {
  return chrome.permissions.contains({
    origins: ["http://*/*", "https://*/*"],
  });
}

// --- webRequest listeners: metadata only, never header VALUES stored ------
// While recording, log every matching request/response (not only auth-tagged
// ones). Auth header *names* are still extracted when present.

try {
  chrome.webRequest.onBeforeSendHeaders.addListener(
    (details) => {
      const authHeaderNames = (details.requestHeaders || [])
        .filter((h) => isAuthRelatedHeaderName(h.name))
        .map((h) => h.name);

      recordEvent({
        url: details.url,
        method: details.method,
        type: details.type,
        auth_header_names: authHeaderNames,
      });
    },
    { urls: ["http://*/*", "https://*/*"] },
    ["requestHeaders", "extraHeaders"]
  );

  chrome.webRequest.onHeadersReceived.addListener(
    (details) => {
      const responseHeaders = details.responseHeaders || [];
      const authHeaderNames = responseHeaders
        .filter((h) => isAuthRelatedHeaderName(h.name))
        .map((h) => h.name);
      const setCookieNames = responseHeaders
        .filter((h) => /^set-cookie$/i.test(h.name))
        .flatMap((h) => extractCookieNamesFromSetCookie(h.value));

      recordEvent({
        url: details.url,
        method: details.method,
        type: details.type,
        status_code: details.statusCode,
        auth_header_names: authHeaderNames,
        set_cookie_names: setCookieNames,
      });
    },
    { urls: ["http://*/*", "https://*/*"] },
    ["responseHeaders", "extraHeaders"]
  );
} catch (err) {
  console.error("chrome-mv3-kit: failed to register webRequest listeners", err);
}

// Fallback: main-frame navigations (works even when header listeners are flaky).
if (chrome.webNavigation?.onCompleted) {
  chrome.webNavigation.onCompleted.addListener((details) => {
    if (details.frameId !== 0) return;
    recordEvent({
      url: details.url,
      method: "GET",
      type: "main_frame",
      status_code: null,
      auth_header_names: [],
      set_cookie_names: [],
    });
  });
}

// --- Message API for popup.js ---------------------------------------------

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  (async () => {
    switch (message?.type) {
      case "GET_STATUS": {
        sendResponse({
          recording: await getRecordingState(),
          session: await getSession(),
          host_access: await hostAccessGranted(),
        });
        break;
      }
      case "START_RECORDING": {
        const access = await hostAccessGranted();
        if (!access) {
          sendResponse({
            error:
              "Host access not granted. Click “Grant lab host access” and Allow, then Start again.",
            session: null,
          });
          break;
        }
        const session = await startRecording(message.targetLabel);
        sendResponse({ session, host_access: true });
        break;
      }
      case "STOP_RECORDING": {
        const session = await stopRecording();
        sendResponse({ session });
        break;
      }
      case "CLEAR_SESSION": {
        await chrome.storage.local.remove(STORAGE_KEY_SESSION);
        sendResponse({ ok: true });
        break;
      }
      default:
        sendResponse({ error: `unknown message type: ${message?.type}` });
    }
  })();
  return true; // keep the message channel open for the async response
});
