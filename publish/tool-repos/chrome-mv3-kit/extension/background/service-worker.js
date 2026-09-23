/**
 * MV3 Service Worker - Auth flow recorder
 * Persists state to chrome.storage to survive worker suspension
 */

import { extractOriginFromUrl, isOriginCovered } from '../shared/origin-utils.js';

// State keys in chrome.storage.local
const STORAGE_KEYS = {
  RECORDING: 'isRecording',
  EVENTS: 'capturedEvents',
  SESSION_ID: 'sessionId',
  STARTED_AT: 'startedAt',
  STOPPED_AT: 'stoppedAt',
  REQUESTED_ORIGINS: 'requestedOrigins',
  EVENT_COUNTS: 'eventCounts',
  OBSERVED_ORIGINS: 'observedOrigins'
};

// Initialize on startup
chrome.runtime.onStartup.addListener(() => {
  console.log('[Lab Kit] Service worker started');
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('[Lab Kit] Extension installed/updated');
});

/**
 * Persist state to storage
 */
async function saveState(key, value) {
  await chrome.storage.local.set({ [key]: value });
}

/**
 * Load state from storage
 */
async function loadState(key, defaultValue = null) {
  const result = await chrome.storage.local.get(key);
  return result[key] !== undefined ? result[key] : defaultValue;
}

/**
 * Start recording session
 */
async function startRecording(requestedOrigins = []) {
  const sessionId = crypto.randomUUID();
  const now = new Date().toISOString();

  await saveState(STORAGE_KEYS.SESSION_ID, sessionId);
  await saveState(STORAGE_KEYS.STARTED_AT, now);
  await saveState(STORAGE_KEYS.STOPPED_AT, null);
  await saveState(STORAGE_KEYS.RECORDING, true);
  await saveState(STORAGE_KEYS.EVENTS, []);
  await saveState(STORAGE_KEYS.REQUESTED_ORIGINS, requestedOrigins);
  await saveState(STORAGE_KEYS.EVENT_COUNTS, {
    webRequest_request: 0,
    webRequest_response: 0,
    webNavigation: 0
  });
  await saveState(STORAGE_KEYS.OBSERVED_ORIGINS, []);

  console.log('[Lab Kit] Recording started:', sessionId);
  return { sessionId, startedAt: now };
}

/**
 * Stop recording session
 */
async function stopRecording() {
  const now = new Date().toISOString();
  await saveState(STORAGE_KEYS.STOPPED_AT, now);
  await saveState(STORAGE_KEYS.RECORDING, false);

  console.log('[Lab Kit] Recording stopped');
  return { stoppedAt: now };
}

/**
 * Add event to capture log
 */
async function addEvent(event) {
  const events = await loadState(STORAGE_KEYS.EVENTS, []);
  events.push(event);
  await saveState(STORAGE_KEYS.EVENTS, events);

  // Track observed origins
  const origin = extractOriginFromUrl(event.url);
  if (origin) {
    const observedOrigins = await loadState(STORAGE_KEYS.OBSERVED_ORIGINS, []);
    if (!observedOrigins.includes(origin)) {
      observedOrigins.push(origin);
      await saveState(STORAGE_KEYS.OBSERVED_ORIGINS, observedOrigins);
    }
  }

  // Update counts
  const counts = await loadState(STORAGE_KEYS.EVENT_COUNTS, {});
  const countKey = event.source === 'webNavigation' ? 'webNavigation' :
                   (event.status ? 'webRequest_response' : 'webRequest_request');
  counts[countKey] = (counts[countKey] || 0) + 1;
  await saveState(STORAGE_KEYS.EVENT_COUNTS, counts);
}

/**
 * Get current session data
 */
async function getSessionData() {
  const [
    isRecording,
    events,
    sessionId,
    startedAt,
    stoppedAt,
    requestedOrigins,
    eventCounts,
    observedOrigins
  ] = await Promise.all([
    loadState(STORAGE_KEYS.RECORDING, false),
    loadState(STORAGE_KEYS.EVENTS, []),
    loadState(STORAGE_KEYS.SESSION_ID),
    loadState(STORAGE_KEYS.STARTED_AT),
    loadState(STORAGE_KEYS.STOPPED_AT),
    loadState(STORAGE_KEYS.REQUESTED_ORIGINS, []),
    loadState(STORAGE_KEYS.EVENT_COUNTS, {}),
    loadState(STORAGE_KEYS.OBSERVED_ORIGINS, [])
  ]);

  return {
    isRecording,
    events,
    sessionId,
    startedAt,
    stoppedAt,
    requestedOrigins,
    eventCounts,
    observedOrigins
  };
}

/**
 * WebRequest listener - captures request metadata
 * Must use extraHeaders to see Set-Cookie headers in MV3
 */
chrome.webRequest.onBeforeRequest.addListener(
  async (details) => {
    const isRecording = await loadState(STORAGE_KEYS.RECORDING, false);
    if (!isRecording) return;

    const origin = extractOriginFromUrl(details.url);
    if (!origin) return; // Skip non-HTTP(S)

    const event = {
      url: details.url,
      method: details.method,
      source: 'webRequest',
      timestamp: new Date().toISOString(),
      resourceType: details.type
    };

    await addEvent(event);
  },
  { urls: ['<all_urls>'] }
);

/**
 * WebRequest onCompleted - captures response headers and Set-Cookie names
 * MUST use extraHeaders to see Set-Cookie in Chrome MV3
 */
chrome.webRequest.onCompleted.addListener(
  async (details) => {
    const isRecording = await loadState(STORAGE_KEYS.RECORDING, false);
    if (!isRecording) return;

    const origin = extractOriginFromUrl(details.url);
    if (!origin) return;

    // Extract Set-Cookie names from response headers
    const setCookieNames = [];
    if (details.responseHeaders) {
      for (const header of details.responseHeaders) {
        if (header.name.toLowerCase() === 'set-cookie' && header.value) {
          // Extract cookie name (everything before =)
          const cookieName = header.value.split('=')[0].trim();
          if (cookieName && !setCookieNames.includes(cookieName)) {
            setCookieNames.push(cookieName);
          }
        }
      }
    }

    const event = {
      url: details.url,
      method: details.method,
      status: details.statusCode,
      source: 'webRequest',
      timestamp: new Date().toISOString(),
      set_cookie_names: setCookieNames,
      resourceType: details.type
    };

    await addEvent(event);
  },
  { urls: ['<all_urls>'] },
  ['responseHeaders', 'extraHeaders'] // extraHeaders required for Set-Cookie
);

/**
 * WebNavigation listener - fallback for main frame loads
 */
chrome.webNavigation.onCompleted.addListener(async (details) => {
  const isRecording = await loadState(STORAGE_KEYS.RECORDING, false);
  if (!isRecording) return;

  // Only record main frame navigations
  if (details.frameId !== 0) return;

  const origin = extractOriginFromUrl(details.url);
  if (!origin) return;

  const event = {
    url: details.url,
    method: 'GET',
    source: 'webNavigation',
    timestamp: new Date().toISOString(),
    frameId: details.frameId
  };

  await addEvent(event);
});

/**
 * Message handler for popup communication
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message.action === 'startRecording') {
        const result = await startRecording(message.requestedOrigins || []);
        sendResponse({ success: true, ...result });
      } else if (message.action === 'stopRecording') {
        const result = await stopRecording();
        sendResponse({ success: true, ...result });
      } else if (message.action === 'getSessionData') {
        const data = await getSessionData();
        sendResponse({ success: true, data });
      } else if (message.action === 'exportSession') {
        const data = await getSessionData();
        const exportData = await buildExport(data);
        sendResponse({ success: true, export: exportData });
      } else if (message.action === 'addFormFields') {
        // Content script sends form field data
        const events = await loadState(STORAGE_KEYS.EVENTS, []);
        // Find the most recent event for this URL and add form_fields
        for (let i = events.length - 1; i >= 0; i--) {
          if (events[i].url === message.url && !events[i].form_fields) {
            events[i].form_fields = message.formFields;
            await saveState(STORAGE_KEYS.EVENTS, events);
            break;
          }
        }
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('[Lab Kit] Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    }
  })();

  return true; // Keep channel open for async response
});

/**
 * Build export data with diagnostics
 */
async function buildExport(sessionData) {
  const {
    sessionId,
    startedAt,
    stoppedAt,
    events,
    requestedOrigins,
    eventCounts,
    observedOrigins
  } = sessionData;

  // Check for granted permissions
  const granted = await chrome.permissions.getAll();
  const grantedOrigins = granted.origins || [];

  // Determine coverage completeness
  const hasNonFallback = (eventCounts.webRequest_request || 0) + (eventCounts.webRequest_response || 0) > 0;
  const missingOrigins = observedOrigins.filter(origin => !isOriginCovered(origin, grantedOrigins));
  const coverage = (hasNonFallback && missingOrigins.length === 0) ? 'complete' : 'incomplete';

  // Filter out non-HTTP(S) events from export
  const httpEvents = events.filter(e => extractOriginFromUrl(e.url) !== null);

  // Build origin stats
  const originStats = {};
  for (const event of httpEvents) {
    const origin = extractOriginFromUrl(event.url);
    if (origin) {
      if (!originStats[origin]) {
        originStats[origin] = { count: 0, sources: new Set() };
      }
      originStats[origin].count++;
      originStats[origin].sources.add(event.source);
    }
  }

  const originStatsArray = Object.entries(originStats).map(([origin, stats]) => ({
    origin,
    count: stats.count,
    sources: Array.from(stats.sources)
  }));

  return {
    session_id: sessionId,
    started_at: startedAt,
    stopped_at: stoppedAt || new Date().toISOString(),
    coverage,
    diagnostics: {
      requested_origins: requestedOrigins,
      granted_origins: grantedOrigins,
      missing_origins: missingOrigins,
      event_counts: eventCounts,
      origin_stats: originStatsArray
    },
    events: httpEvents
  };
}
