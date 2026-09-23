"use strict";
function generateTrafficStub(session) {
  if (!session || !Array.isArray(session.events) || !session.events.length) throw new Error("Capture must contain events");
  const patterns = new Map();
  for (const event of session.events) {
    let url;
    try { url = new URL(event.url); } catch (_) { continue; }
    if (!/^https?:$/.test(url.protocol)) continue;
    const key = `${String(event.method || "GET").toUpperCase()} ${url.origin}${url.pathname}`;
    patterns.set(key, (patterns.get(key) || 0) + 1);
  }
  if (!patterns.size) throw new Error("Capture contains no HTTP(S) URL patterns");
  const lines = ["# AUTHORIZED LAB DOCUMENTATION SKELETON", "# Observed patterns only; not a production implant or evasion profile.",
    "# Review scope and sanitize paths before sharing.", "", "patterns:"];
  for (const [pattern, count] of patterns) lines.push(`  # observed ${count} time(s)`, `  - ${JSON.stringify(pattern)}`);
  return `${lines.join("\n")}\n`;
}
module.exports = { generateTrafficStub };
