// Service worker for chrome-mv3-kit
// Handles webRequest/webNavigation recording with MV3 lifecycle persistence

importScripts('shared/utils.js');

// State keys for chrome.storage.local
const STORAGE_KEYS = {
  RECORDING: 'isRecording',
  SESSION_ID: 'sessionId',
  STARTED_AT: 'startedAt',
  EVENTS: 'events',
  REQUESTED_ORIGINS: 'requestedOrigins',
  EVENT_COUNTS: 'eventCounts',
  OBSERVED_ORIGINS: 'observedOrigins'
};

// Restore state on service worker start
let state = {
  isRecording: false,
  sessionId: null,
  startedAt: null,
  events: [],
  requestedOrigins: [],
  eventCounts: { webRequest: 0, webRequestResponse: 0, webNavigation: 0 },
  observedOrigins: new Set()
};

// Restore from storage
chrome.storage.local.get(Object.values(STORAGE_KEYS), (result) => {
  if (result.isRecording) state.isRecording = result.isRecording;
  if (result.sessionId) state.sessionId = result.sessionId;
  if (result.startedAt) state.startedAt = result.startedAt;
  if (result.events) state.events = result.events;
  if (result.requestedOrigins) state.requestedOrigins = result.requestedOrigins;
  if (result.eventCounts) state.eventCounts = result.eventCounts;
  if (result.observedOrigins) {
    state.observedOrigins = new Set(result.observedOrigins);
  }
});

// Persist state to storage
function saveState() {
  chrome.storage.local.set({
    [STORAGE_KEYS.RECORDING]: state.isRecording,
    [STORAGE_KEYS.SESSION_ID]: state.sessionId,
    [STORAGE_KEYS.STARTED_AT]: state.startedAt,
    [STORAGE_KEYS.EVENTS]: state.events,
    [STORAGE_KEYS.REQUESTED_ORIGINS]: state.requestedOrigins,
    [STORAGE_KEYS.EVENT_COUNTS]: state.eventCounts,
    [STORAGE_KEYS.OBSERVED_ORIGINS]: Array.from(state.observedOrigins)
  });
}

// Message handler from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startRecording') {
    handleStartRecording(message.origins || [])
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // async response
  }

  if (message.action === 'stopRecording') {
    handleStopRecording()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (message.action === 'getState') {
    sendResponse({
      isRecording: state.isRecording,
      sessionId: state.sessionId,
      startedAt: state.startedAt,
      eventCount: state.events.length,
      requestedOrigins: state.requestedOrigins,
      eventCounts: state.eventCounts
    });
    return true;
  }

  if (message.action === 'exportSession') {
    handleExportSession()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (message.action === 'setRequestedOrigins') {
    state.requestedOrigins = message.origins || [];
    saveState();
    sendResponse({ success: true });
    return true;
  }

  if (message.action === 'recordFormFields') {
    handleFormFields(message.data);
    sendResponse({ success: true });
    return true;
  }
});

async function handleStartRecording(origins) {
  // Verify all requested origins have permission
  const permissions = await chrome.permissions.getAll();
  const granted = permissions.origins || [];

  const normalized = origins.map(o => normalizeOrigin(o));

  for (const origin of normalized) {
    if (!hasPermission(granted, origin)) {
      return {
        success: false,
        error: `Missing permission for ${origin}. Grant access first.`
      };
    }
  }

  // Start new session
  state.isRecording = true;
  state.sessionId = generateUUID();
  state.startedAt = new Date().toISOString();
  state.events = [];
  state.requestedOrigins = normalized;
  state.eventCounts = { webRequest: 0, webRequestResponse: 0, webNavigation: 0 };
  state.observedOrigins = new Set();

  saveState();

  return { success: true, sessionId: state.sessionId };
}

async function handleStopRecording() {
  state.isRecording = false;
  saveState();
  return { success: true };
}

async function handleExportSession() {
  const permissions = await chrome.permissions.getAll();
  const granted = permissions.origins || [];

  // Compute missing permissions
  const missing = [];
  for (const origin of state.observedOrigins) {
    if (!hasPermission(granted, origin)) {
      missing.push(origin);
    }
  }

  // Determine coverage
  let coverage = 'complete';
  const hasWebRequestEvents = state.eventCounts.webRequest > 0 || state.eventCounts.webRequestResponse > 0;
  const hasOnlyNavEvents = state.eventCounts.webNavigation > 0 && !hasWebRequestEvents;

  if (hasOnlyNavEvents || missing.length > 0) {
    coverage = 'incomplete';
  }

  const session = {
    session_id: state.sessionId || 'unknown',
    started_at: state.startedAt,
    stopped_at: new Date().toISOString(),
    coverage: coverage,
    diagnostics: {
      event_counts: state.eventCounts,
      requested_origins: state.requestedOrigins,
      granted_origins: granted,
      missing_origins: missing,
      observed_origins: Array.from(state.observedOrigins)
    },
    events: state.events
  };

  return { success: true, session };
}

function handleFormFields(data) {
  if (!state.isRecording || !data) return;

  // Find or create event for this URL
  const existingEvent = state.events.find(e => e.url === data.url);
  if (existingEvent) {
    // Add form_fields if not already present
    if (!existingEvent.form_fields) {
      existingEvent.form_fields = [];
    }
    // Merge form data
    for (const form of data.forms) {
      existingEvent.form_fields.push(form);
    }
  } else {
    // Create new event from content script
    const origin = extractOrigin(data.url);
    if (origin) {
      state.observedOrigins.add(origin);
    }

    state.events.push({
      url: data.url,
      method: 'GET',
      status: 200,
      source: 'contentScript',
      form_fields: data.forms
    });
  }

  saveState();
}

// WebRequest listeners
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (!state.isRecording) return;

    const origin = extractOrigin(details.url);
    if (!origin) return; // Skip non-HTTP(S)

    state.observedOrigins.add(origin);

    // Track request
    const eventId = `${details.requestId}-${details.method}`;
    const existing = state.events.find(e => e._eventId === eventId);

    if (!existing) {
      state.events.push({
        _eventId: eventId,
        url: details.url,
        method: details.method,
        source: 'webRequest',
        timestamp: details.timeStamp
      });
      state.eventCounts.webRequest++;
    }
  },
  { urls: ['<all_urls>'] }
);

chrome.webRequest.onCompleted.addListener(
  (details) => {
    if (!state.isRecording) return;

    const origin = extractOrigin(details.url);
    if (!origin) return;

    state.observedOrigins.add(origin);

    const eventId = `${details.requestId}-${details.method}`;
    const existing = state.events.find(e => e._eventId === eventId);

    // Extract Set-Cookie names
    const setCookieNames = [];
    if (details.responseHeaders) {
      for (const header of details.responseHeaders) {
        if (header.name.toLowerCase() === 'set-cookie' && header.value) {
          const cookieName = header.value.split('=')[0];
          if (cookieName) {
            setCookieNames.push(cookieName);
          }
        }
      }
    }

    if (existing) {
      existing.status = details.statusCode;
      existing.set_cookie_names = setCookieNames;
      delete existing._eventId;
      state.eventCounts.webRequestResponse++;
    } else {
      state.events.push({
        url: details.url,
        method: details.method,
        status: details.statusCode,
        source: 'webRequest',
        set_cookie_names: setCookieNames
      });
      state.eventCounts.webRequestResponse++;
    }

    saveState();
  },
  { urls: ['<all_urls>'] },
  ['responseHeaders', 'extraHeaders'] // MUST include extraHeaders for Set-Cookie
);

// WebNavigation fallback
chrome.webNavigation.onCompleted.addListener((details) => {
  if (!state.isRecording) return;
  if (details.frameId !== 0) return; // Main frame only

  const origin = extractOrigin(details.url);
  if (!origin) return;

  state.observedOrigins.add(origin);

  // Check if already captured via webRequest
  const alreadyCaptured = state.events.some(e =>
    e.url === details.url && e.source === 'webRequest'
  );

  if (!alreadyCaptured) {
    state.events.push({
      url: details.url,
      method: 'GET',
      source: 'webNavigation',
      timestamp: details.timeStamp
    });
    state.eventCounts.webNavigation++;
    saveState();
  }
});

console.log('chrome-mv3-kit service worker loaded');
