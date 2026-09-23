(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LabShared = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const HTTP_PATTERN = /^(https?):\/\/([^/]+)\/\*$/i;

  function normalizeOrigin(input) {
    if (typeof input !== "string" || !input.trim()) throw new Error("Origin is required");
    const raw = input.trim();
    if (raw === "http://*/*" || raw === "https://*/*") return raw.toLowerCase();
    const match = raw.match(HTTP_PATTERN);
    if (match) {
      if (match[2].includes("@")) throw new Error("Userinfo is not allowed");
      return `${match[1].toLowerCase()}://${match[2].toLowerCase()}/*`;
    }
    const candidate = /^[a-z][a-z0-9+.-]*:\/\//i.test(raw) ? raw : `https://${raw}`;
    let parsed;
    try { parsed = new URL(candidate); } catch (_) { throw new Error(`Invalid origin: ${raw}`); }
    if (!/^https?:$/.test(parsed.protocol)) throw new Error("Only HTTP(S) origins are allowed");
    if (parsed.username || parsed.password) throw new Error("Userinfo is not allowed");
    if (!parsed.hostname) throw new Error(`Invalid origin: ${raw}`);
    return `${parsed.protocol}//${parsed.host.toLowerCase()}/*`;
  }

  function normalizeOrigins(values) {
    return [...new Set(values.map(normalizeOrigin))];
  }

  function isHttpUrl(value) {
    try { return /^https?:$/.test(new URL(value).protocol); } catch (_) { return false; }
  }

  function permissionCovers(grant, requested) {
    const g = normalizeOrigin(grant);
    const r = normalizeOrigin(requested);
    if (g === r) return true;
    return (g === "https://*/*" && r.startsWith("https://")) ||
      (g === "http://*/*" && r.startsWith("http://"));
  }

  function comparePermissions(requested, granted) {
    const wanted = normalizeOrigins(requested || []);
    const have = normalizeOrigins(granted || []);
    const covered = wanted.filter((item) => have.some((grant) => permissionCovers(grant, item)));
    return { granted: covered, missing: wanted.filter((item) => !covered.includes(item)) };
  }

  function uniqueNames(values) {
    return [...new Set((values || []).filter((v) => typeof v === "string" && v).map((v) => v.toLowerCase()))];
  }

  function sanitizeForms(forms) {
    if (!Array.isArray(forms)) return [];
    return forms.map((form) => ({
      url: String(form.url || ""),
      form_action: String(form.form_action || ""),
      fields: Array.isArray(form.fields) ? form.fields
        .filter((field) => field && typeof field.name === "string")
        .map((field) => ({ name: field.name, type: String(field.type || "text").toLowerCase() })) : [],
      ...(form.submit_label ? { submit_label: String(form.submit_label).slice(0, 120) } : {})
    }));
  }

  function sanitizeEvent(raw) {
    if (!raw || !isHttpUrl(raw.url)) return null;
    const event = {
      url: String(raw.url),
      source: String(raw.source || "unknown"),
      timestamp: String(raw.timestamp || new Date().toISOString())
    };
    if (raw.request_id !== undefined) event.request_id = String(raw.request_id);
    if (raw.method) event.method = String(raw.method).toUpperCase();
    if (Number.isFinite(raw.status)) event.status = raw.status;
    if (raw.resource_type) event.resource_type = String(raw.resource_type);
    if (raw.request_header_names) event.request_header_names = uniqueNames(raw.request_header_names);
    if (raw.response_header_names) event.response_header_names = uniqueNames(raw.response_header_names);
    if (raw.set_cookie_names) event.set_cookie_names = uniqueNames(raw.set_cookie_names);
    if (raw.form_fields) event.form_fields = sanitizeForms(raw.form_fields);
    return event;
  }

  function mergeEvents(events, raw) {
    const event = sanitizeEvent(raw);
    if (!event) return events.slice();
    const next = events.slice();
    const index = event.request_id ? next.findIndex((old) =>
      old.request_id === event.request_id && old.source === event.source) : -1;
    if (index < 0) next.push(event);
    else next[index] = Object.assign({}, next[index], event, {
      request_header_names: uniqueNames([...(next[index].request_header_names || []), ...(event.request_header_names || [])]),
      response_header_names: uniqueNames([...(next[index].response_header_names || []), ...(event.response_header_names || [])]),
      set_cookie_names: uniqueNames([...(next[index].set_cookie_names || []), ...(event.set_cookie_names || [])])
    });
    return next;
  }

  function buildDiagnostics(state, grantedOrigins) {
    const events = (state.events || []).map(sanitizeEvent).filter(Boolean);
    const bySource = {};
    const byOrigin = {};
    for (const event of events) {
      bySource[event.source] = (bySource[event.source] || 0) + 1;
      const origin = new URL(event.url).origin;
      byOrigin[origin] = (byOrigin[origin] || 0) + 1;
    }
    const requested = normalizeOrigins(state.requested_origins || []);
    const granted = normalizeOrigins(grantedOrigins || state.granted_origins || []);
    const observed = Object.keys(byOrigin).map(normalizeOrigin);
    const requestedCheck = comparePermissions(requested, granted);
    const observedCheck = comparePermissions(observed, granted);
    const missing = [...new Set([...requestedCheck.missing, ...observedCheck.missing])];
    const webRequestCount = Object.entries(bySource)
      .filter(([key]) => key.startsWith("webRequest"))
      .reduce((sum, [, value]) => sum + value, 0);
    const incomplete = webRequestCount === 0 || missing.length > 0;
    const warnings = [];
    if (webRequestCount === 0) warnings.push("Only navigation/form fallback evidence was captured.");
    if (missing.length) warnings.push(`Missing permission for: ${missing.join(", ")}`);
    return {
      counts_by_source: bySource,
      counts_by_origin: byOrigin,
      requested_origins: requested,
      granted_origins: granted,
      missing_origins: missing,
      session_started_at: state.started_at || null,
      session_stopped_at: state.stopped_at || null,
      coverage: incomplete ? "incomplete" : "complete",
      warnings
    };
  }

  function exportSession(state, grantedOrigins) {
    const clean = Object.assign({}, state, { events: (state.events || []).map(sanitizeEvent).filter(Boolean) });
    clean.diagnostics = buildDiagnostics(clean, grantedOrigins);
    clean.coverage = clean.diagnostics.coverage;
    clean.granted_origins = clean.diagnostics.granted_origins;
    return clean;
  }

  function sessionToMarkdown(state, grantedOrigins) {
    const session = exportSession(state, grantedOrigins);
    const d = session.diagnostics;
    const lines = [
      "# Lab authentication-flow capture",
      "",
      `**Coverage: ${d.coverage.toUpperCase()}**`,
      "",
      `- Session: ${session.session_id || "unknown"}`,
      `- Started: ${session.started_at || "unknown"}`,
      `- Stopped: ${session.stopped_at || "not stopped"}`,
      `- Events: ${session.events.length}`,
      `- Requested origins: ${d.requested_origins.join(", ") || "none"}`,
      `- Granted origins: ${d.granted_origins.join(", ") || "none"}`,
      `- Missing origins: ${d.missing_origins.join(", ") || "none"}`,
      "",
      "## Counts by source",
      ""
    ];
    for (const [name, count] of Object.entries(d.counts_by_source)) lines.push(`- ${name}: ${count}`);
    lines.push("", "## Counts by origin", "");
    for (const [name, count] of Object.entries(d.counts_by_origin)) lines.push(`- ${name}: ${count}`);
    lines.push("", "## Events", "", "| Time | Source | Method | Status | URL |", "|---|---|---|---:|---|");
    for (const e of session.events) lines.push(`| ${e.timestamp || ""} | ${e.source} | ${e.method || ""} | ${e.status || ""} | ${e.url.replace(/\|/g, "%7C")} |`);
    if (d.warnings.length) lines.push("", "## Warnings", "", ...d.warnings.map((w) => `- ${w}`));
    return `${lines.join("\n")}\n`;
  }

  return { normalizeOrigin, normalizeOrigins, isHttpUrl, permissionCovers, comparePermissions,
    sanitizeEvent, mergeEvents, buildDiagnostics, exportSession, sessionToMarkdown };
});
