// Popup UI controller

let state = {
  recording: false,
  requestedOrigins: [],
  grantedOrigins: [],
  eventCount: 0
};

async function updateUI() {
  // Load state from storage
  const stored = await chrome.storage.local.get(['requestedOrigins', 'recordingState', 'capturedEvents']);
  state.requestedOrigins = stored.requestedOrigins || [];
  state.recording = stored.recordingState?.isRecording || false;
  state.eventCount = (stored.capturedEvents || []).length;

  // Check granted permissions
  state.grantedOrigins = [];
  for (const origin of state.requestedOrigins) {
    const granted = await chrome.permissions.contains({ origins: [origin] });
    if (granted) {
      state.grantedOrigins.push(origin);
    }
  }

  // Update access status
  const accessStatus = document.getElementById('accessStatus');
  const originsList = document.getElementById('originsList');

  if (state.grantedOrigins.length === 0) {
    accessStatus.textContent = 'Host access: Not granted';
    accessStatus.className = 'status stopped';
    originsList.style.display = 'none';
  } else if (state.grantedOrigins.length < state.requestedOrigins.length) {
    accessStatus.textContent = `Host access: Partial (${state.grantedOrigins.length}/${state.requestedOrigins.length})`;
    accessStatus.className = 'status warning';
    showOriginsList();
  } else {
    accessStatus.textContent = `Host access: Granted (${state.grantedOrigins.length} origins)`;
    accessStatus.className = 'status info';
    showOriginsList();
  }

  // Update recording status
  const recordingStatus = document.getElementById('recordingStatus');
  const startBtn = document.getElementById('startRecording');
  const stopBtn = document.getElementById('stopRecording');
  const eventCountDiv = document.getElementById('eventCount');

  if (state.recording) {
    recordingStatus.textContent = '🔴 Recording in progress';
    recordingStatus.className = 'status recording';
    startBtn.disabled = true;
    stopBtn.disabled = false;
    eventCountDiv.textContent = `Events captured: ${state.eventCount}`;
  } else {
    recordingStatus.textContent = 'Recorder: Stopped';
    recordingStatus.className = 'status stopped';
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (state.eventCount > 0) {
      eventCountDiv.textContent = `Last session: ${state.eventCount} events`;
    } else {
      eventCountDiv.textContent = '';
    }
  }

  // Populate origins textarea if empty
  const originsTextarea = document.getElementById('origins');
  if (originsTextarea.value.trim() === '' && state.requestedOrigins.length > 0) {
    originsTextarea.value = state.requestedOrigins.join('\n');
  }
}

function showOriginsList() {
  const originsList = document.getElementById('originsList');
  originsList.style.display = 'block';
  originsList.innerHTML = '';

  for (const origin of state.requestedOrigins) {
    const div = document.createElement('div');
    const granted = state.grantedOrigins.includes(origin);
    div.className = granted ? 'granted' : 'missing';
    div.textContent = `${granted ? '✓' : '✗'} ${origin}`;
    originsList.appendChild(div);
  }
}

document.getElementById('enableAccess').addEventListener('click', async () => {
  const originsText = document.getElementById('origins').value;
  const { normalized, errors } = parseOrigins(originsText);

  if (errors.length > 0) {
    alert('Origin parsing errors:\n' + errors.join('\n'));
    return;
  }

  if (normalized.length === 0) {
    // Default: request http and https wildcard
    normalized.push('http://*/*', 'https://*/*');
  }

  try {
    const granted = await chrome.permissions.request({
      origins: normalized
    });

    if (granted) {
      // Store requested origins
      state.requestedOrigins = normalized;
      await chrome.storage.local.set({ requestedOrigins: normalized });
      await updateUI();
      alert('✓ Host access granted!\n\nIMPORTANT: If you just granted new permissions, reload this extension (chrome://extensions → Reload) before starting recording.');
    } else {
      alert('Host access denied. Cannot record without permissions.');
    }
  } catch (error) {
    alert(`Error requesting permissions: ${error.message}`);
  }
});

document.getElementById('startRecording').addEventListener('click', async () => {
  // Verify we have permissions for all requested origins
  let hasAllPermissions = false;

  if (state.requestedOrigins.length === 0) {
    alert('ERROR: No origins configured.\n\n1. Enter authorized origins in the text area above\n2. Click "Enable Lab Access"\n3. Grant permissions\n4. Reload extension if needed\n5. Click "Start Recording"');
    return;
  }

  hasAllPermissions = state.grantedOrigins.length === state.requestedOrigins.length;

  if (!hasAllPermissions) {
    alert(`ERROR: Cannot start recording without host access.\n\nRequested: ${state.requestedOrigins.length} origins\nGranted: ${state.grantedOrigins.length} origins\n\nMissing permissions for:\n${state.requestedOrigins.filter(o => !state.grantedOrigins.includes(o)).join('\n')}\n\nClick "Enable Lab Access" and grant permissions, then reload the extension.`);
    return;
  }

  // Start recording
  await chrome.runtime.sendMessage({ type: 'START_RECORDING' });
  await updateUI();
});

document.getElementById('stopRecording').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'STOP_RECORDING' });
  await updateUI();
});

document.getElementById('exportJson').addEventListener('click', async () => {
  const response = await chrome.runtime.sendMessage({ type: 'EXPORT_JSON' });
  if (response.error) {
    alert(`Export error: ${response.error}`);
    return;
  }

  const blob = new Blob([response.json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  await chrome.downloads.download({
    url: url,
    filename: `session-${Date.now()}.json`,
    saveAs: true
  });
});

document.getElementById('exportMarkdown').addEventListener('click', async () => {
  const response = await chrome.runtime.sendMessage({ type: 'EXPORT_MARKDOWN' });
  if (response.error) {
    alert(`Export error: ${response.error}`);
    return;
  }

  const blob = new Blob([response.markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);

  await chrome.downloads.download({
    url: url,
    filename: `session-${Date.now()}.md`,
    saveAs: true
  });
});

document.getElementById('clearSession').addEventListener('click', async () => {
  if (state.recording) {
    alert('Stop recording before clearing session.');
    return;
  }

  if (confirm('Clear all captured events?')) {
    await chrome.runtime.sendMessage({ type: 'CLEAR_SESSION' });
    await updateUI();
  }
});

// Initialize UI
updateUI();

// Listen for storage changes
chrome.storage.onChanged.addListener(() => {
  updateUI();
});
