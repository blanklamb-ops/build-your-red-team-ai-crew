// chrome-mv3-kit popup controller (R3: JSON + markdown export via chrome.downloads).

import { sessionToJson, sessionToMarkdown, assertValidSession } from "./lib/session_export.js";

const statusEl = document.getElementById("status");
const targetLabelEl = document.getElementById("targetLabel");

function send(message) {
  return chrome.runtime.sendMessage(message);
}

function renderStatus({ recording, session, host_access }) {
  const lines = [];
  lines.push(`Host access: ${host_access ? "granted" : "NOT granted — recorder will see 0 events"}`);
  lines.push(`Recording: ${recording ? "ON" : "off"}`);
  if (session) {
    lines.push(`Session: ${session.session_id}`);
    lines.push(`Target: ${session.target_label}`);
    lines.push(`Events captured: ${session.events?.length ?? 0}`);
  } else {
    lines.push("No session yet.");
  }
  statusEl.textContent = lines.join("\n");
}

async function refresh() {
  const status = await send({ type: "GET_STATUS" });
  renderStatus(status);
  return status;
}

function downloadText(filename, text, mime) {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  chrome.downloads.download({ url, filename, saveAs: true }, () => {
    // Revoke shortly after; download has already started reading the blob.
    setTimeout(() => URL.revokeObjectURL(url), 10_000);
  });
}

document.getElementById("grantAccess").addEventListener("click", async () => {
  const granted = await chrome.permissions.request({
    origins: ["http://*/*", "https://*/*"],
  });
  statusEl.textContent = granted
    ? "Lab host access granted. Reload the extension on chrome://extensions, then Start recording and browse."
    : "Host access not granted — recorder will not observe any requests (you will get 0 events).";
});

document.getElementById("start").addEventListener("click", async () => {
  const res = await send({ type: "START_RECORDING", targetLabel: targetLabelEl.value });
  if (res?.error) {
    statusEl.textContent = res.error;
    return;
  }
  renderStatus({ recording: true, session: res.session, host_access: res.host_access });
});

document.getElementById("stop").addEventListener("click", async () => {
  const { session } = await send({ type: "STOP_RECORDING" });
  const status = await send({ type: "GET_STATUS" });
  renderStatus({
    recording: false,
    session: session || status.session,
    host_access: status.host_access,
  });
});

document.getElementById("clear").addEventListener("click", async () => {
  await send({ type: "CLEAR_SESSION" });
  await refresh();
});

document.getElementById("exportJson").addEventListener("click", async () => {
  const { session } = await send({ type: "GET_STATUS" });
  if (!session) {
    statusEl.textContent = "Nothing to export — no session recorded yet.";
    return;
  }
  assertValidSession(session);
  downloadText(`chrome-mv3-kit-session-${session.session_id}.json`, sessionToJson(session), "application/json");
});

document.getElementById("exportMd").addEventListener("click", async () => {
  const { session } = await send({ type: "GET_STATUS" });
  if (!session) {
    statusEl.textContent = "Nothing to export — no session recorded yet.";
    return;
  }
  assertValidSession(session);
  downloadText(`chrome-mv3-kit-session-${session.session_id}.md`, sessionToMarkdown(session), "text/markdown");
});

refresh();
