/**
 * Origin normalization utilities shared between popup and service worker.
 * Must be idempotent and reject userinfo/non-HTTP(S) schemes.
 */

/**
 * Normalizes an origin/URL to Chrome match pattern format: https://example.test/*
 * @param {string} input - Bare origin, full URL, or match pattern
 * @returns {string} Normalized match pattern
 * @throws {Error} If input contains userinfo or non-HTTP(S) scheme
 */
export function normalizeOrigin(input) {
  if (!input || typeof input !== 'string') {
    throw new Error('Input must be a non-empty string');
  }

  const trimmed = input.trim();

  // Already normalized - idempotent check
  if (/^https?:\/\/[^/]+\/\*$/.test(trimmed)) {
    return trimmed;
  }

  // Check for obvious non-HTTP(S) schemes before URL parsing
  if (/^[a-z][a-z0-9+.-]*:/i.test(trimmed)) {
    // Has a scheme
    const scheme = trimmed.split(':')[0].toLowerCase();
    if (scheme !== 'http' && scheme !== 'https') {
      throw new Error(`Non-HTTP(S) scheme not allowed: ${scheme}:`);
    }
  }

  // Parse URL
  let url;
  try {
    // Handle bare host or host:port by adding scheme if missing
    if (!/^https?:\/\//i.test(trimmed)) {
      url = new URL(`https://${trimmed}`);
    } else {
      url = new URL(trimmed);
    }
  } catch (e) {
    throw new Error(`Invalid URL/origin: ${trimmed}`);
  }

  // Double-check protocol after parsing
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new Error(`Non-HTTP(S) scheme not allowed: ${url.protocol}`);
  }

  // Reject userinfo
  if (url.username || url.password) {
    throw new Error('Userinfo (username/password) in URL is not allowed');
  }

  // Build match pattern: protocol://host/*
  const origin = `${url.protocol}//${url.host}/*`;
  return origin;
}

/**
 * Checks if a set of granted origins covers a target origin.
 * Treats http://*\/* and https://*\/* as covering all HTTP(S) origins.
 */
export function isOriginCovered(target, grantedSet) {
  if (!grantedSet || grantedSet.length === 0) return false;

  // Check for wildcard coverage
  const hasHttpWildcard = grantedSet.includes('http://*/*');
  const hasHttpsWildcard = grantedSet.includes('https://*/*');

  if (target.startsWith('https://') && hasHttpsWildcard) return true;
  if (target.startsWith('http://') && hasHttpWildcard) return true;

  // Check for exact match
  return grantedSet.includes(target);
}

/**
 * Extract origin from a URL, returning null for non-HTTP(S).
 */
export function extractOriginFromUrl(urlString) {
  try {
    const url = new URL(urlString);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return null;
    }
    return `${url.protocol}//${url.host}/*`;
  } catch (e) {
    return null;
  }
}
