// Shared utilities for chrome-mv3-kit
// Used in popup, service worker, and tests

/**
 * Normalize origin to Chrome permission pattern format
 * Must be idempotent: normalizeOrigin(normalizeOrigin(x)) === normalizeOrigin(x)
 *
 * @param {string} input - Bare origin, URL, or already-canonical pattern
 * @returns {string} - Canonical pattern like "https://example.test/*"
 * @throws {Error} - For userinfo, non-HTTP(S) schemes
 */
function normalizeOrigin(input) {
  if (!input || typeof input !== 'string') {
    throw new Error('Invalid input: must be a non-empty string');
  }

  const trimmed = input.trim();

  // Already canonical pattern (idempotent)
  if (/^https?:\/\/[^/]+\/\*$/.test(trimmed)) {
    const url = new URL(trimmed.replace('/*', '/'));
    if (url.username || url.password) {
      throw new Error('Userinfo not allowed in origins');
    }
    return trimmed;
  }

  // Check for existing non-HTTP(S) protocol
  if (trimmed.match(/^[a-z][a-z0-9+.-]*:\/\//i) && !trimmed.match(/^https?:\/\//i)) {
    throw new Error(`Only HTTP(S) schemes allowed, got ${trimmed.split(':')[0]}:`);
  }

  // Add protocol if missing
  let urlString = trimmed;
  if (!urlString.match(/^https?:\/\//)) {
    urlString = 'https://' + urlString;
  }

  // Remove trailing path but keep for URL parsing
  urlString = urlString.replace(/\/\*$/, '/');

  let url;
  try {
    url = new URL(urlString);
  } catch (e) {
    throw new Error(`Invalid URL: ${e.message}`);
  }

  // Reject non-HTTP(S) (double-check)
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new Error(`Only HTTP(S) schemes allowed, got ${url.protocol}`);
  }

  // Reject userinfo
  if (url.username || url.password) {
    throw new Error('Userinfo not allowed in origins');
  }

  // Return canonical pattern
  return `${url.protocol}//${url.host}/*`;
}

/**
 * Extract origin from URL for permission comparison
 * Returns null for non-HTTP(S) URLs (chrome-extension:// etc)
 */
function extractOrigin(url) {
  if (!url || typeof url !== 'string') {
    return null;
  }

  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return null;
    }
    return `${parsed.protocol}//${parsed.host}/*`;
  } catch (e) {
    return null;
  }
}

/**
 * Check if granted permissions cover the required origin
 * Treats http://*\/* and https://*\/* as covering all HTTP(S) origins
 */
function hasPermission(grantedPatterns, requiredOrigin) {
  if (!Array.isArray(grantedPatterns) || !requiredOrigin) {
    return false;
  }

  // Direct match
  if (grantedPatterns.includes(requiredOrigin)) {
    return true;
  }

  // Check wildcard coverage
  const isHttp = requiredOrigin.startsWith('http://');
  const isHttps = requiredOrigin.startsWith('https://');

  if (isHttp && grantedPatterns.includes('http://*/*')) {
    return true;
  }
  if (isHttps && grantedPatterns.includes('https://*/*')) {
    return true;
  }

  return false;
}

/**
 * Generate a UUID v4 for session IDs
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Export for Node.js tests if in that environment
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    normalizeOrigin,
    extractOrigin,
    hasPermission,
    generateUUID
  };
}
