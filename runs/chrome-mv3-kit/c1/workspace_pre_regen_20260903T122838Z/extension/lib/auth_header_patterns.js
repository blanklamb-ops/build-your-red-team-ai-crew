// Shared list of header-name patterns considered "auth-related" for
// recording purposes. Only NAMES are ever inspected/stored — this module
// never reads or stores header VALUES.

export const AUTH_HEADER_NAME_PATTERNS = [
  /^authorization$/i,
  /^cookie$/i,
  /^set-cookie$/i,
  /^www-authenticate$/i,
  /^proxy-authenticate$/i,
  /^proxy-authorization$/i,
  /^x-csrf-token$/i,
  /^x-xsrf-token$/i,
  /^x-auth-token$/i,
  /^x-session-token$/i,
  /^x-api-key$/i,
];

/**
 * @param {string} headerName
 * @returns {boolean}
 */
export function isAuthRelatedHeaderName(headerName) {
  return AUTH_HEADER_NAME_PATTERNS.some((re) => re.test(headerName));
}

/**
 * Extracts cookie NAMES (never values) from a raw Set-Cookie header string.
 * @param {string} setCookieHeaderValue
 * @returns {string[]}
 */
export function extractCookieNamesFromSetCookie(setCookieHeaderValue) {
  if (!setCookieHeaderValue) return [];
  const namePart = setCookieHeaderValue.split(";")[0] || "";
  const eq = namePart.indexOf("=");
  if (eq <= 0) return [];
  return [namePart.slice(0, eq).trim()];
}
