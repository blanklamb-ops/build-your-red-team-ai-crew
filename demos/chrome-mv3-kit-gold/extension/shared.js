// Shared utility functions for extension

function normalizeOrigin(input) {
  if (!input || typeof input !== 'string') {
    throw new Error('Invalid origin input');
  }

  input = input.trim();
  if (!input) {
    throw new Error('Empty origin input');
  }

  // Already canonical Chrome match pattern
  if (input.match(/^https?:\/\/[^/]+\/\*$/)) {
    return input;
  }

  let url;
  try {
    // Try parsing as full URL
    url = new URL(input);
  } catch (e) {
    // Try as bare origin
    if (input.match(/^[a-z0-9.-]+$/i)) {
      // Host only, add https://
      url = new URL(`https://${input}`);
    } else if (input.match(/^https?:\/\/[a-z0-9.-]+(:\d+)?$/i)) {
      // Looks like origin without path
      url = new URL(input + '/');
    } else {
      throw new Error(`Cannot parse origin: ${input}`);
    }
  }

  // Reject non-HTTP(S) schemes
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new Error(`Non-HTTP(S) scheme rejected: ${url.protocol}`);
  }

  // Reject userinfo
  if (url.username || url.password) {
    throw new Error('userinfo in URL rejected');
  }

  // Return canonical Chrome match pattern: protocol://host/*
  return `${url.protocol}//${url.host}/*`;
}

function parseOrigins(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
  const normalized = [];
  const errors = [];

  for (const line of lines) {
    try {
      normalized.push(normalizeOrigin(line));
    } catch (e) {
      errors.push(`${line}: ${e.message}`);
    }
  }

  return { normalized: [...new Set(normalized)], errors };
}

// Make functions available globally
if (typeof window !== 'undefined') {
  window.normalizeOrigin = normalizeOrigin;
  window.parseOrigins = parseOrigins;
}

// For Node.js testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { normalizeOrigin, parseOrigins };
}
