/**
 * Traffic pattern stub exporter
 * Generates commented skeleton from URL patterns - documentation aid only
 */

/**
 * Generate traffic pattern skeleton
 */
export function generateTrafficPattern(captureData) {
  const lines = [];

  lines.push('# Traffic Pattern Skeleton');
  lines.push('# Generated from lab capture - documentation aid only');
  lines.push('# NOT a production implant profile\n');

  lines.push(`Session: ${captureData.session_id}`);
  lines.push(`Captured: ${captureData.started_at} to ${captureData.stopped_at}\n`);

  // Group by origin
  const originMap = new Map();

  for (const event of captureData.events) {
    try {
      const url = new URL(event.url);
      const origin = `${url.protocol}//${url.host}`;

      if (!originMap.has(origin)) {
        originMap.set(origin, []);
      }

      originMap.get(origin).push(event);
    } catch (e) {
      // Invalid URL
    }
  }

  lines.push('## URL Patterns by Origin\n');

  for (const [origin, events] of originMap.entries()) {
    lines.push(`### ${origin}`);
    lines.push(`Events: ${events.length}\n`);

    // Extract unique path patterns
    const pathSet = new Set();
    const methodMap = new Map();

    for (const event of events) {
      try {
        const url = new URL(event.url);
        const path = url.pathname;
        pathSet.add(path);

        const key = `${event.method} ${path}`;
        if (!methodMap.has(key)) {
          methodMap.set(key, {
            method: event.method,
            path: path,
            count: 0,
            hasCookies: false
          });
        }
        const entry = methodMap.get(key);
        entry.count++;
        if (event.set_cookie_names && event.set_cookie_names.length > 0) {
          entry.hasCookies = true;
        }
      } catch (e) {
        // Invalid URL
      }
    }

    lines.push('Observed paths:');
    for (const [key, data] of methodMap.entries()) {
      const cookies = data.hasCookies ? ' [sets cookies]' : '';
      lines.push(`  ${data.method} ${data.path} (${data.count}x)${cookies}`);
    }

    lines.push('');
  }

  lines.push('\n## Notes\n');
  lines.push('- Review paths for auth-relevant patterns (login, password, oauth, etc.)');
  lines.push('- Cookie-setting paths may indicate session establishment');
  lines.push('- Form submissions (POST) are credential submission candidates');
  lines.push('- This is a documentation skeleton only - not a production profile');

  return lines.join('\n');
}
