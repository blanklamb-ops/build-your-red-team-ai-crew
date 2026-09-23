// Service worker for MV3 extension

// State persisted in chrome.storage
let recordingState = {
  isRecording: false,
  sessionStartTime: null,
  sessionStopTime: null
};

let capturedEvents = [];
let requestedOrigins = [];
let formFieldsData = [];

// Restore state on startup
chrome.runtime.onStartup.addListener(restoreState);
chrome.runtime.onInstalled.addListener(restoreState);

async function restoreState() {
  const stored = await chrome.storage.local.get(['recordingState', 'capturedEvents', 'requestedOrigins', 'formFieldsData']);

  if (stored.recordingState) {
    recordingState = stored.recordingState;
  }
  if (stored.capturedEvents) {
    capturedEvents = stored.capturedEvents;
  }
  if (stored.requestedOrigins) {
    requestedOrigins = stored.requestedOrigins;
  }
  if (stored.formFieldsData) {
    formFieldsData = stored.formFieldsData;
  }

  // Re-register listeners if we were recording
  if (recordingState.isRecording) {
    registerListeners();
  }
}

async function persistState() {
  await chrome.storage.local.set({
    recordingState,
    capturedEvents,
    requestedOrigins,
    formFieldsData
  });
}

function registerListeners() {
  // webRequest listeners for request/response metadata
  if (!chrome.webRequest.onBeforeRequest.hasListener(onBeforeRequest)) {
    chrome.webRequest.onBeforeRequest.addListener(
      onBeforeRequest,
      { urls: ['<all_urls>'] },
      []
    );
  }

  if (!chrome.webRequest.onCompleted.hasListener(onCompleted)) {
    chrome.webRequest.onCompleted.addListener(
      onCompleted,
      { urls: ['<all_urls>'] },
      ['responseHeaders', 'extraHeaders']
    );
  }

  if (!chrome.webRequest.onErrorOccurred.hasListener(onErrorOccurred)) {
    chrome.webRequest.onErrorOccurred.addListener(
      onErrorOccurred,
      { urls: ['<all_urls>'] }
    );
  }

  // webNavigation fallback
  if (!chrome.webNavigation.onCompleted.hasListener(onNavigationCompleted)) {
    chrome.webNavigation.onCompleted.addListener(onNavigationCompleted);
  }
}

function unregisterListeners() {
  if (chrome.webRequest.onBeforeRequest.hasListener(onBeforeRequest)) {
    chrome.webRequest.onBeforeRequest.removeListener(onBeforeRequest);
  }
  if (chrome.webRequest.onCompleted.hasListener(onCompleted)) {
    chrome.webRequest.onCompleted.removeListener(onCompleted);
  }
  if (chrome.webRequest.onErrorOccurred.hasListener(onErrorOccurred)) {
    chrome.webRequest.onErrorOccurred.removeListener(onErrorOccurred);
  }
  if (chrome.webNavigation.onCompleted.hasListener(onNavigationCompleted)) {
    chrome.webNavigation.onCompleted.removeListener(onNavigationCompleted);
  }
}

function onBeforeRequest(details) {
  if (!recordingState.isRecording) return;

  const url = new URL(details.url);

  capturedEvents.push({
    event_source: 'webRequest.onBeforeRequest',
    timestamp: new Date().toISOString(),
    url: details.url,
    origin: `${url.protocol}//${url.host}`,
    method: details.method,
    type: details.type,
    frame_type: details.frameType || null,
    request_id: details.requestId
  });

  persistState();
}

function onCompleted(details) {
  if (!recordingState.isRecording) return;

  const url = new URL(details.url);
  const setCookieNames = [];

  // Extract Set-Cookie header names (cookie names, not values)
  if (details.responseHeaders) {
    for (const header of details.responseHeaders) {
      if (header.name.toLowerCase() === 'set-cookie' && header.value) {
        const cookieName = header.value.split('=')[0].trim();
        if (cookieName) {
          setCookieNames.push(cookieName);
        }
      }
    }
  }

  // Check if we already have a request event for this request ID
  const existingIndex = capturedEvents.findIndex(
    e => e.request_id === details.requestId && e.event_source === 'webRequest.onBeforeRequest'
  );

  if (existingIndex >= 0) {
    // Merge with existing request event
    capturedEvents[existingIndex] = {
      ...capturedEvents[existingIndex],
      event_source: 'webRequest.onBeforeRequest+onCompleted',
      status_code: details.statusCode,
      set_cookie_names: setCookieNames.length > 0 ? setCookieNames : undefined,
      response_headers: details.responseHeaders ? details.responseHeaders.map(h => h.name) : []
    };
  } else {
    // Add as separate response event
    capturedEvents.push({
      event_source: 'webRequest.onCompleted',
      timestamp: new Date().toISOString(),
      url: details.url,
      origin: `${url.protocol}//${url.host}`,
      method: details.method,
      type: details.type,
      status_code: details.statusCode,
      set_cookie_names: setCookieNames.length > 0 ? setCookieNames : undefined,
      response_headers: details.responseHeaders ? details.responseHeaders.map(h => h.name) : [],
      request_id: details.requestId
    });
  }

  persistState();
}

function onErrorOccurred(details) {
  if (!recordingState.isRecording) return;

  const url = new URL(details.url);

  capturedEvents.push({
    event_source: 'webRequest.onErrorOccurred',
    timestamp: new Date().toISOString(),
    url: details.url,
    origin: `${url.protocol}//${url.host}`,
    method: details.method,
    type: details.type,
    error: details.error,
    request_id: details.requestId
  });

  persistState();
}

function onNavigationCompleted(details) {
  if (!recordingState.isRecording) return;
  if (details.frameId !== 0) return; // Main frame only

  const url = new URL(details.url);

  capturedEvents.push({
    event_source: 'webNavigation.onCompleted',
    timestamp: new Date().toISOString(),
    url: details.url,
    origin: `${url.protocol}//${url.host}`,
    frame_id: details.frameId,
    tab_id: details.tabId
  });

  persistState();

  // Request form fields capture from content script
  chrome.tabs.sendMessage(details.tabId, { type: 'CAPTURE_FORM_FIELDS' }).catch(() => {
    // Content script might not be ready, ignore
  });
}

// Listen for form fields data from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'FORM_FIELDS_CAPTURED') {
    if (recordingState.isRecording && message.data) {
      formFieldsData.push({
        url: message.data.url,
        timestamp: new Date().toISOString(),
        form_fields: message.data.form_fields
      });
      persistState();
    }
    return;
  }

  if (message.type === 'START_RECORDING') {
    recordingState.isRecording = true;
    recordingState.sessionStartTime = new Date().toISOString();
    recordingState.sessionStopTime = null;
    registerListeners();
    persistState();
    sendResponse({ success: true });
    return;
  }

  if (message.type === 'STOP_RECORDING') {
    recordingState.isRecording = false;
    recordingState.sessionStopTime = new Date().toISOString();
    unregisterListeners();
    persistState();
    sendResponse({ success: true });
    return;
  }

  if (message.type === 'EXPORT_JSON') {
    const exportData = generateExport();
    sendResponse({ json: JSON.stringify(exportData, null, 2) });
    return true;
  }

  if (message.type === 'EXPORT_MARKDOWN') {
    const exportData = generateExport();
    const markdown = generateMarkdownSummary(exportData);
    sendResponse({ markdown });
    return true;
  }

  if (message.type === 'CLEAR_SESSION') {
    capturedEvents = [];
    formFieldsData = [];
    recordingState.sessionStartTime = null;
    recordingState.sessionStopTime = null;
    persistState();
    sendResponse({ success: true });
    return;
  }
});

function generateExport() {
  // Calculate diagnostics
  const eventsBySource = {};
  const eventsByOrigin = {};
  const observedOrigins = new Set();

  for (const event of capturedEvents) {
    // Count by source
    eventsBySource[event.event_source] = (eventsBySource[event.event_source] || 0) + 1;

    // Count by origin
    if (event.origin) {
      observedOrigins.add(event.origin);
      eventsByOrigin[event.origin] = (eventsByOrigin[event.origin] || 0) + 1;
    }
  }

  // Check coverage
  const hasWebRequestEvents = capturedEvents.some(e => e.event_source.startsWith('webRequest.'));
  const onlyFallbackEvents = !hasWebRequestEvents && capturedEvents.some(e => e.event_source === 'webNavigation.onCompleted');

  // Check permission gaps
  const missingOrigins = [];
  for (const origin of observedOrigins) {
    // Convert origin to match pattern for comparison
    let matchPattern = origin;
    if (!matchPattern.endsWith('/*')) {
      matchPattern = matchPattern.replace(/\/$/, '') + '/*';
    }
    if (!requestedOrigins.includes(matchPattern)) {
      missingOrigins.push(origin);
    }
  }

  const coverage = (onlyFallbackEvents || missingOrigins.length > 0) ? 'incomplete' : 'complete';

  // Merge form fields data into events
  const eventsWithFormData = capturedEvents.map(event => {
    const matchingFormData = formFieldsData.find(f => f.url === event.url);
    if (matchingFormData && matchingFormData.form_fields.length > 0) {
      return {
        ...event,
        form_fields: matchingFormData.form_fields
      };
    }
    return event;
  });

  return {
    session: {
      start_time: recordingState.sessionStartTime,
      stop_time: recordingState.sessionStopTime,
      requested_origins: requestedOrigins,
      observed_origins: Array.from(observedOrigins),
      missing_origins: missingOrigins
    },
    diagnostics: {
      total_events: capturedEvents.length,
      events_by_source: eventsBySource,
      events_by_origin: eventsByOrigin,
      coverage: coverage,
      has_webRequest_events: hasWebRequestEvents,
      only_fallback: onlyFallbackEvents
    },
    events: eventsWithFormData
  };
}

function generateMarkdownSummary(exportData) {
  let md = '# Lab Session Summary\n\n';

  md += `**Session Start:** ${exportData.session.start_time || 'N/A'}\n`;
  md += `**Session Stop:** ${exportData.session.stop_time || 'N/A'}\n`;
  md += `**Coverage:** ${exportData.diagnostics.coverage}\n\n`;

  md += '## Diagnostics\n\n';
  md += `- Total events: ${exportData.diagnostics.total_events}\n`;
  md += `- Has webRequest events: ${exportData.diagnostics.has_webRequest_events}\n`;
  md += `- Only fallback events: ${exportData.diagnostics.only_fallback}\n\n`;

  if (exportData.diagnostics.only_fallback) {
    md += '⚠️ **WARNING:** This capture contains only webNavigation fallback events. No detailed request/response metadata was captured.\n\n';
  }

  md += '### Events by Source\n\n';
  for (const [source, count] of Object.entries(exportData.diagnostics.events_by_source)) {
    md += `- ${source}: ${count}\n`;
  }

  md += '\n### Events by Origin\n\n';
  for (const [origin, count] of Object.entries(exportData.diagnostics.events_by_origin)) {
    md += `- ${origin}: ${count}\n`;
  }

  md += '\n## Origins\n\n';
  md += `**Requested:** ${exportData.session.requested_origins.length}\n`;
  md += `**Observed:** ${exportData.session.observed_origins.length}\n`;

  if (exportData.session.missing_origins.length > 0) {
    md += `\n⚠️ **Missing permissions for observed origins:**\n`;
    for (const origin of exportData.session.missing_origins) {
      md += `- ${origin}\n`;
    }
  }

  md += '\n## Sample Events\n\n';
  const sampleEvents = exportData.events.slice(0, 10);
  for (const event of sampleEvents) {
    md += `### ${event.event_source}\n`;
    md += `- URL: ${event.url}\n`;
    md += `- Time: ${event.timestamp}\n`;
    if (event.method) md += `- Method: ${event.method}\n`;
    if (event.status_code) md += `- Status: ${event.status_code}\n`;
    if (event.set_cookie_names && event.set_cookie_names.length > 0) {
      md += `- Set-Cookie names: ${event.set_cookie_names.join(', ')}\n`;
    }
    if (event.form_fields && event.form_fields.length > 0) {
      md += `- Form fields captured: ${event.form_fields.length}\n`;
    }
    md += '\n';
  }

  if (exportData.events.length > 10) {
    md += `\n*(${exportData.events.length - 10} more events omitted from summary)*\n`;
  }

  return md;
}

// Initialize on load
restoreState();
