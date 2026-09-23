/**
 * Popup UI controller
 */

import { normalizeOrigin, isOriginCovered } from '../shared/origin-utils.js';

const DEFAULT_ORIGINS = ['http://*/*', 'https://*/*'];

let currentRequestedOrigins = [];

// Initialize UI
document.addEventListener('DOMContentLoaded', async () => {
  await updateAccessStatus();
  await updateRecordingStatus();

  // Load requested origins from storage
  const result = await chrome.storage.local.get('requestedOrigins');
  currentRequestedOrigins = result.requestedOrigins || [];

  // Event listeners
  document.getElementById('enableDefaultAccess').addEventListener('click', enableDefaultAccess);
  document.getElementById('enableCustomAccess').addEventListener('click', showCustomOrigins);
  document.getElementById('requestCustom').addEventListener('click', requestCustomOrigins);
  document.getElementById('cancelCustom').addEventListener('click', hideCustomOrigins);
  document.getElementById('startRecording').addEventListener('click', startRecording);
  document.getElementById('stopRecording').addEventListener('click', stopRecording);
  document.getElementById('exportJson').addEventListener('click', exportJson);
  document.getElementById('exportMarkdown').addEventListener('click', exportMarkdown);

  // Poll for updates while popup is open
  setInterval(updateRecordingStatus, 1000);
});

async function updateAccessStatus() {
  const permissions = await chrome.permissions.getAll();
  const grantedOrigins = permissions.origins || [];

  const accessStatus = document.getElementById('accessStatus');
  const originList = document.getElementById('originList');

  if (grantedOrigins.length === 0) {
    accessStatus.className = 'status warning';
    accessStatus.textContent = '⚠️ No host access granted - recording will fail';
    originList.style.display = 'none';
  } else {
    const hasWildcard = grantedOrigins.includes('http://*/*') || grantedOrigins.includes('https://*/*');
    accessStatus.className = 'status success';
    accessStatus.textContent = `✓ Access granted to ${grantedOrigins.length} origin${grantedOrigins.length > 1 ? 's' : ''}`;

    // Show origin list
    originList.style.display = 'block';
    originList.innerHTML = '<strong>Granted:</strong><br>' +
      grantedOrigins.map(o => `<div class="origin-item granted">✓ ${o}</div>`).join('');

    // Show requested vs granted
    if (currentRequestedOrigins.length > 0) {
      const missing = currentRequestedOrigins.filter(o => !isOriginCovered(o, grantedOrigins));
      if (missing.length > 0) {
        originList.innerHTML += '<br><strong>Requested but missing:</strong><br>' +
          missing.map(o => `<div class="origin-item missing">✗ ${o}</div>`).join('');
      }
    }
  }
}

async function updateRecordingStatus() {
  const response = await chrome.runtime.sendMessage({ action: 'getSessionData' });
  if (!response.success) return;

  const data = response.data;
  const recordingStatus = document.getElementById('recordingStatus');
  const startBtn = document.getElementById('startRecording');
  const stopBtn = document.getElementById('stopRecording');

  if (data.isRecording) {
    recordingStatus.className = 'status success';
    const eventCount = data.events.length;
    const duration = data.startedAt ? Math.floor((Date.now() - new Date(data.startedAt)) / 1000) : 0;
    recordingStatus.textContent = `🔴 Recording: ${eventCount} events (${duration}s)`;
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } else if (data.events.length > 0) {
    recordingStatus.className = 'status info';
    recordingStatus.textContent = `Session complete: ${data.events.length} events captured`;
    startBtn.disabled = false;
    stopBtn.disabled = true;
  } else {
    recordingStatus.className = 'status info';
    recordingStatus.textContent = 'Ready to record';
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

async function enableDefaultAccess() {
  try {
    const granted = await chrome.permissions.request({
      origins: DEFAULT_ORIGINS
    });

    if (granted) {
      currentRequestedOrigins = DEFAULT_ORIGINS;
      await chrome.storage.local.set({ requestedOrigins: currentRequestedOrigins });
      await updateAccessStatus();
      showStatus('exportStatus', 'success', '✓ Access granted! You may need to reload the extension.');
    } else {
      showStatus('exportStatus', 'warning', 'Access request denied by user');
    }
  } catch (error) {
    showStatus('exportStatus', 'error', `Error: ${error.message}`);
  }
}

function showCustomOrigins() {
  document.getElementById('customOriginsSection').style.display = 'block';
  document.getElementById('customOriginsInput').value = currentRequestedOrigins.join('\n');
}

function hideCustomOrigins() {
  document.getElementById('customOriginsSection').style.display = 'none';
}

async function requestCustomOrigins() {
  const input = document.getElementById('customOriginsInput').value;
  const lines = input.split('\n').map(l => l.trim()).filter(l => l.length > 0);

  try {
    // Normalize all origins
    const normalized = [];
    for (const line of lines) {
      const norm = normalizeOrigin(line);
      if (!normalized.includes(norm)) {
        normalized.push(norm);
      }
    }

    // Request permissions
    const granted = await chrome.permissions.request({
      origins: normalized
    });

    if (granted) {
      currentRequestedOrigins = normalized;
      await chrome.storage.local.set({ requestedOrigins: currentRequestedOrigins });
      await updateAccessStatus();
      hideCustomOrigins();
      showStatus('exportStatus', 'success', `✓ Access granted to ${normalized.length} origins`);
    } else {
      showStatus('exportStatus', 'warning', 'Access request denied by user');
    }
  } catch (error) {
    showStatus('exportStatus', 'error', `Error: ${error.message}`);
  }
}

async function startRecording() {
  // Check if we have any permissions
  const permissions = await chrome.permissions.getAll();
  const grantedOrigins = permissions.origins || [];

  if (grantedOrigins.length === 0) {
    showStatus('exportStatus', 'error', '❌ Cannot start: No host access granted. Click "Enable Lab Access" first.');
    return;
  }

  // Verify we have the requested origins
  if (currentRequestedOrigins.length > 0) {
    const missing = currentRequestedOrigins.filter(o => !isOriginCovered(o, grantedOrigins));
    if (missing.length > 0) {
      showStatus('exportStatus', 'error', `❌ Cannot start: Missing permissions for ${missing.length} origin(s). Reload extension or re-request access.`);
      return;
    }
  }

  const response = await chrome.runtime.sendMessage({
    action: 'startRecording',
    requestedOrigins: currentRequestedOrigins
  });

  if (response.success) {
    showStatus('exportStatus', 'success', '✓ Recording started - browse your lab flows now');
    await updateRecordingStatus();
  } else {
    showStatus('exportStatus', 'error', `Error: ${response.error}`);
  }
}

async function stopRecording() {
  const response = await chrome.runtime.sendMessage({ action: 'stopRecording' });

  if (response.success) {
    showStatus('exportStatus', 'success', '✓ Recording stopped');
    await updateRecordingStatus();
  } else {
    showStatus('exportStatus', 'error', `Error: ${response.error}`);
  }
}

async function exportJson() {
  const response = await chrome.runtime.sendMessage({ action: 'exportSession' });

  if (!response.success) {
    showStatus('exportStatus', 'error', `Error: ${response.error}`);
    return;
  }

  const data = response.export;
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const filename = `lab-capture-${data.session_id}.json`;

  await chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });

  showStatus('exportStatus', 'success', `✓ Exported ${filename}`);
}

async function exportMarkdown() {
  const response = await chrome.runtime.sendMessage({ action: 'exportSession' });

  if (!response.success) {
    showStatus('exportStatus', 'error', `Error: ${response.error}`);
    return;
  }

  const data = response.export;
  const markdown = generateMarkdown(data);
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);

  const filename = `lab-capture-${data.session_id}.md`;

  await chrome.downloads.download({
    url: url,
    filename: filename,
    saveAs: true
  });

  showStatus('exportStatus', 'success', `✓ Exported ${filename}`);
}

function generateMarkdown(data) {
  const lines = [];

  lines.push('# Lab Capture Report\n');
  lines.push(`**Session ID:** ${data.session_id}  `);
  lines.push(`**Started:** ${data.started_at}  `);
  lines.push(`**Stopped:** ${data.stopped_at}  `);
  lines.push(`**Coverage:** ${data.coverage.toUpperCase()}\n`);

  if (data.coverage === 'incomplete') {
    lines.push('⚠️ **Warning:** This capture is marked incomplete. See diagnostics below.\n');
  }

  lines.push('## Diagnostics\n');
  lines.push(`- **Requested origins:** ${data.diagnostics.requested_origins.length}`);
  lines.push(`- **Granted origins:** ${data.diagnostics.granted_origins.length}`);
  lines.push(`- **Missing origins:** ${data.diagnostics.missing_origins.length}`);

  if (data.diagnostics.missing_origins.length > 0) {
    lines.push('\n**Missing permissions for:**');
    data.diagnostics.missing_origins.forEach(o => lines.push(`  - ${o}`));
  }

  lines.push('\n**Event counts:**');
  lines.push(`  - WebRequest (request): ${data.diagnostics.event_counts.webRequest_request || 0}`);
  lines.push(`  - WebRequest (response): ${data.diagnostics.event_counts.webRequest_response || 0}`);
  lines.push(`  - WebNavigation (fallback): ${data.diagnostics.event_counts.webNavigation || 0}`);

  lines.push('\n**Events by origin:**');
  data.diagnostics.origin_stats.forEach(stat => {
    lines.push(`  - ${stat.origin}: ${stat.count} events (sources: ${stat.sources.join(', ')})`);
  });

  lines.push('\n## Captured Events\n');
  lines.push(`Total: ${data.events.length} events\n`);

  data.events.forEach((event, idx) => {
    lines.push(`### Event ${idx + 1}`);
    lines.push(`- **URL:** ${event.url}`);
    lines.push(`- **Method:** ${event.method}`);
    if (event.status) lines.push(`- **Status:** ${event.status}`);
    lines.push(`- **Source:** ${event.source}`);
    if (event.set_cookie_names && event.set_cookie_names.length > 0) {
      lines.push(`- **Set-Cookie names:** ${event.set_cookie_names.join(', ')}`);
    }
    if (event.form_fields && event.form_fields.length > 0) {
      lines.push(`- **Form fields captured:** ${event.form_fields.length} form(s)`);
      event.form_fields.forEach((form, formIdx) => {
        lines.push(`  - Form ${formIdx + 1}: action=${form.form_action}`);
        form.fields.forEach(field => {
          lines.push(`    - ${field.name} (${field.type})`);
        });
      });
    }
    lines.push('');
  });

  return lines.join('\n');
}

function showStatus(elementId, type, message) {
  const el = document.getElementById(elementId);
  el.className = `status ${type}`;
  el.textContent = message;
  setTimeout(() => {
    el.textContent = '';
    el.className = '';
  }, 5000);
}
