/**
 * Host classification and domain extraction (R4g gold-kit rules)
 * Filters out telemetry, CDN, storage, and junk hosts
 */

// Deny-list patterns (R4g)
const DENY_PATTERNS = {
  prefixes: [
    'graph.',
    'admin.',
    'monitor.',
    'storage.',
    'blob.',
    'fpt.',
  ],
  contains: [
    'wcpstatic',
    'uhf',
    'amcdn',
    'office.net',
    'sharepointonline',
    'cdn.office',
    'lifecycle.office',
    'copilot',
    'clarity.ms',
    'OneCollector',
    'telemetry',
    'metrics',
  ],
  suffixes: [
    'azurefd.net',
    'azureedge.net',
    'cloudfront.net',
    'akamaihd.net',
    'edgecdn.test',
    'trafficmanager.net',
  ]
};

// Auth-relevant patterns
const AUTH_PATTERNS = {
  subdomains: ['login', 'auth', 'account', 'msauth', 'authcdn'],
  paths: ['login', 'password', 'checkpassword', 'post.srf', 'GetCredentialType', 'oauth', 'saml']
};

/**
 * Extract eTLD+1 (registrable domain) from hostname
 * Simplified PSL logic for common cases
 */
export function extractDomain(hostname) {
  if (!hostname) return null;

  const parts = hostname.toLowerCase().split('.');

  // Check for edge/CDN suffixes first (multi-part)
  for (const suffix of DENY_PATTERNS.suffixes) {
    if (hostname.endsWith(suffix)) {
      // Reject hosts on edge networks
      return null;
    }
  }

  // Reject hex-like labels (≥12 chars, mostly hex)
  for (const part of parts) {
    if (part.length >= 12 && /^[a-f0-9]{12,}$/i.test(part)) {
      return null;
    }
  }

  // Extract eTLD+1
  if (parts.length < 2) return null;

  // Handle common TLDs
  const tld = parts[parts.length - 1];
  const sld = parts[parts.length - 2];

  // Handle .co.uk, .com.au style TLDs
  if (parts.length >= 3 && ['co', 'com', 'net', 'org', 'gov', 'edu'].includes(sld)) {
    return parts.slice(-3).join('.');
  }

  // Standard TLD
  return `${sld}.${tld}`;
}

/**
 * Check if host is on deny-list
 */
function isDenied(hostname) {
  const lower = hostname.toLowerCase();

  // Check prefixes
  for (const prefix of DENY_PATTERNS.prefixes) {
    if (lower.startsWith(prefix)) return true;
  }

  // Check contains
  for (const pattern of DENY_PATTERNS.contains) {
    if (lower.includes(pattern)) return true;
  }

  // Check suffixes (already handled in extractDomain, but double-check)
  for (const suffix of DENY_PATTERNS.suffixes) {
    if (lower.endsWith(suffix)) return true;
  }

  return false;
}

/**
 * Check if host/event is auth-relevant (R4g)
 * Auth-relevant = NOT denied AND (has cookies OR credential path OR auth CDN)
 */
export function isAuthRelevantHost(hostname, domain, event, allEvents) {
  if (!domain) return false;

  // First check deny-list
  if (isDenied(hostname)) return false;

  const lower = hostname.toLowerCase();

  // Check if has Set-Cookie
  if (event.set_cookie_names && event.set_cookie_names.length > 0) {
    return true;
  }

  // Check for credential/login paths
  try {
    const url = new URL(event.url);
    const path = url.pathname.toLowerCase();

    for (const pattern of AUTH_PATTERNS.paths) {
      if (path.includes(pattern)) {
        return true;
      }
    }
  } catch (e) {
    // Invalid URL
  }

  // Check if any event from this domain has form_fields with password
  const domainEvents = allEvents.filter(e => {
    try {
      const u = new URL(e.url);
      return extractDomain(u.hostname) === domain;
    } catch (err) {
      return false;
    }
  });

  for (const e of domainEvents) {
    if (e.form_fields) {
      for (const form of e.form_fields) {
        const hasPassword = form.fields.some(f => f.type === 'password');
        if (hasPassword) return true;
      }
    }
  }

  // Check for auth CDN (no cookies but auth-related subdomain)
  if (!event.set_cookie_names || event.set_cookie_names.length === 0) {
    for (const pattern of AUTH_PATTERNS.subdomains) {
      if (lower.includes(pattern)) {
        // Auth CDN - session: false
        return true;
      }
    }
  }

  return false;
}
