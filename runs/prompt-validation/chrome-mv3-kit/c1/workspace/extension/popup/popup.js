// Popup UI controller for chrome-mv3-kit

// DOM elements
const accessStatus = document.getElementById('accessStatus');
const enableAccessBtn = document.getElementById('enableAccessBtn');
const customOrigins = document.getElementById('customOrigins');
const requestCustomBtn = document.getElementById('requestCustomBtn');
const recordingStatus = document.getElementById('recordingStatus');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const requestedOrigins = document.getElementById('requestedOrigins');
const eventCount = document.getElementById('eventCount');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const exportMarkdownBtn = document.getElementById('exportMarkdownBtn');

let currentState = {
  grantedOrigins: [],
  requestedOrigins: [],
  isRecording: false
};

// Initialize
async function init() {
  await updatePermissionStatus();
  await updateRecordingStatus();

  // Set up event listeners
  enableAccessBtn.addEventListener('click', handleEnableAccess);
  requestCustomBtn.addEventListener('click', handleRequestCustom);
  startBtn.addEventListener('click', handleStart);
  stopBtn.addEventListener('click', handleStop);
  exportJsonBtn.addEventListener('click', () => handleExport('json'));
  exportMarkdownBtn.addEventListener('click', () => handleExport('markdown'));

  // Refresh status periodically
  setInterval(updateRecordingStatus, 2000);
}

async function updatePermissionStatus() {
  const permissions = await chrome.permissions.getAll();
  const granted = permissions.origins || [];
  currentState.grantedOrigins = granted;

  const hasHttpAccess = granted.includes('http://*/*');
  const hasHttpsAccess = granted.includes('https://*/*');

  if (hasHttpAccess && hasHttpsAccess) {
    accessStatus.className = 'status info';
    accessStatus.textContent = '✓ Lab access granted (all HTTP/HTTPS)';
  } else if (granted.length > 0) {
    accessStatus.className = 'status info';
    accessStatus.textContent = `✓ Access granted to ${granted.length} origin(s)`;
  } else {
    accessStatus.className = 'status error';
    accessStatus.textContent = '✗ No host access granted';
  }

  updateStartButtonState();
}

async function updateRecordingStatus() {
  const response = await chrome.runtime.sendMessage({ action: 'getState' });

  currentState.isRecording = response.isRecording;
  currentState.requestedOrigins = response.requestedOrigins || [];

  if (response.isRecording) {
    recordingStatus.className = 'status recording';
    recordingStatus.textContent = `🔴 Recording (session: ${response.sessionId.slice(0, 8)}...)`;
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } else {
    recordingStatus.className = 'status stopped';
    recordingStatus.textContent = '⚫ Not recording';
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }

  eventCount.textContent = response.eventCount || 0;

  // Update requested origins display
  if (currentState.requestedOrigins.length > 0) {
    requestedOrigins.textContent = currentState.requestedOrigins.join('\n');
  } else {
    requestedOrigins.textContent = 'None (will use all granted origins)';
  }

  updateStartButtonState();
}

function updateStartButtonState() {
  // Enable start button only if we have some granted origins and not recording
  const hasAnyAccess = currentState.grantedOrigins.length > 0;
  startBtn.disabled = currentState.isRecording || !hasAnyAccess;
}

async function handleEnableAccess() {
  try {
    const granted = await chrome.permissions.request({
      origins: ['http://*/*', 'https://*/*']
    });

    if (granted) {
      accessStatus.className = 'status info';
      accessStatus.textContent = '✓ Lab access granted! Reload extension if needed, then start recording.';

      // Store as requested origins
      const origins = ['http://*/*', 'https://*/*'];
      await chrome.runtime.sendMessage({
        action: 'setRequestedOrigins',
        origins: origins
      });

      await updatePermissionStatus();
      await updateRecordingStatus();
    } else {
      accessStatus.className = 'status error';
      accessStatus.textContent = '✗ Access denied by user';
    }
  } catch (error) {
    accessStatus.className = 'status error';
    accessStatus.textContent = `Error: ${error.message}`;
  }
}

async function handleRequestCustom() {
  const input = customOrigins.value.trim();
  if (!input) {
    alert('Please enter at least one origin');
    return;
  }

  const parts = input.split(',').map(s => s.trim()).filter(s => s);
  const normalized = [];

  try {
    for (const part of parts) {
      const norm = normalizeOrigin(part);
      normalized.push(norm);
    }

    const granted = await chrome.permissions.request({
      origins: normalized
    });

    if (granted) {
      // Store requested origins
      await chrome.runtime.sendMessage({
        action: 'setRequestedOrigins',
        origins: normalized
      });

      accessStatus.className = 'status info';
      accessStatus.textContent = `✓ Custom origins granted: ${normalized.length}`;
      await updatePermissionStatus();
      await updateRecordingStatus();
    } else {
      accessStatus.className = 'status error';
      accessStatus.textContent = '✗ Custom access denied';
    }
  } catch (error) {
    accessStatus.className = 'status error';
    accessStatus.textContent = `Error: ${error.message}`;
  }
}

async function handleStart() {
  // Use requested origins if set, otherwise all granted
  const origins = currentState.requestedOrigins.length > 0
    ? currentState.requestedOrigins
    : currentState.grantedOrigins;

  if (origins.length === 0) {
    recordingStatus.className = 'status error';
    recordingStatus.textContent = '✗ No origins available. Grant access first.';
    return;
  }

  const response = await chrome.runtime.sendMessage({
    action: 'startRecording',
    origins: origins
  });

  if (response.success) {
    recordingStatus.className = 'status recording';
    recordingStatus.textContent = `🔴 Recording started`;
    await updateRecordingStatus();
  } else {
    recordingStatus.className = 'status error';
    recordingStatus.textContent = `✗ ${response.error}`;
  }
}

async function handleStop() {
  const response = await chrome.runtime.sendMessage({
    action: 'stopRecording'
  });

  if (response.success) {
    recordingStatus.className = 'status stopped';
    recordingStatus.textContent = '⚫ Recording stopped';
    await updateRecordingStatus();
  }
}

async function handleExport(format) {
  const response = await chrome.runtime.sendMessage({
    action: 'exportSession'
  });

  if (!response.success) {
    alert(`Export failed: ${response.error}`);
    return;
  }

  const session = response.session;

  if (format === 'json') {
    downloadJSON(session);
  } else if (format === 'markdown') {
    downloadMarkdown(session);
  }
}

function downloadJSON(session) {
  const json = JSON.stringify(session, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const filename = `auth-flow-${session.session_id.slice(0, 8)}.json`;

  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
}

function downloadMarkdown(session) {
  let md = `# Auth Flow Capture Report\n\n`;
  md += `**Session ID:** ${session.session_id}\n`;
  md += `**Started:** ${session.started_at}\n`;
  md += `**Stopped:** ${session.stopped_at}\n`;
  md += `**Coverage:** ${session.coverage}\n\n`;

  md += `## Diagnostics\n\n`;
  md += `**Event Counts:**\n`;
  md += `- webRequest: ${session.diagnostics.event_counts.webRequest}\n`;
  md += `- webRequestResponse: ${session.diagnostics.event_counts.webRequestResponse}\n`;
  md += `- webNavigation: ${session.diagnostics.event_counts.webNavigation}\n\n`;

  md += `**Requested Origins:** ${session.diagnostics.requested_origins.length}\n`;
  session.diagnostics.requested_origins.forEach(o => md += `- ${o}\n`);
  md += `\n`;

  md += `**Granted Origins:** ${session.diagnostics.granted_origins.length}\n`;
  session.diagnostics.granted_origins.forEach(o => md += `- ${o}\n`);
  md += `\n`;

  if (session.diagnostics.missing_origins.length > 0) {
    md += `**⚠️ Missing Permissions:** ${session.diagnostics.missing_origins.length}\n`;
    session.diagnostics.missing_origins.forEach(o => md += `- ${o}\n`);
    md += `\n`;
  }

  md += `## Captured Events (${session.events.length})\n\n`;
  session.events.forEach((event, i) => {
    md += `### Event ${i + 1}\n`;
    md += `- **URL:** ${event.url}\n`;
    md += `- **Method:** ${event.method}\n`;
    if (event.status) md += `- **Status:** ${event.status}\n`;
    md += `- **Source:** ${event.source}\n`;
    if (event.set_cookie_names && event.set_cookie_names.length > 0) {
      md += `- **Set-Cookie Names:** ${event.set_cookie_names.join(', ')}\n`;
    }
    if (event.form_fields && event.form_fields.length > 0) {
      md += `- **Form Fields:**\n`;
      event.form_fields.forEach(form => {
        md += `  - Action: ${form.form_action}\n`;
        md += `    Fields: ${form.fields.map(f => `${f.name}(${f.type})`).join(', ')}\n`;
      });
    }
    md += `\n`;
  });

  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);

  const filename = `auth-flow-${session.session_id.slice(0, 8)}.md`;

  chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });
}

// Initialize on load
init();
