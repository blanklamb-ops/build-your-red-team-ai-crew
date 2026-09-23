/**
 * Markdown report exporter
 */

/**
 * Generate human-readable markdown report from capture data
 */
export function generateMarkdownReport(captureData) {
  const lines = [];

  lines.push('# Lab Capture Report\n');
  lines.push(`**Session ID:** ${captureData.session_id}  `);
  lines.push(`**Started:** ${captureData.started_at}  `);
  lines.push(`**Stopped:** ${captureData.stopped_at}  `);
  lines.push(`**Coverage:** ${captureData.coverage.toUpperCase()}\n`);

  if (captureData.coverage === 'incomplete') {
    lines.push('⚠️ **Warning:** This capture is marked incomplete. See diagnostics below.\n');
  }

  if (captureData.diagnostics) {
    lines.push('## Diagnostics\n');
    const diag = captureData.diagnostics;

    if (diag.requested_origins) {
      lines.push(`- **Requested origins:** ${diag.requested_origins.length}`);
    }
    if (diag.granted_origins) {
      lines.push(`- **Granted origins:** ${diag.granted_origins.length}`);
    }
    if (diag.missing_origins && diag.missing_origins.length > 0) {
      lines.push(`- **Missing origins:** ${diag.missing_origins.length}`);
      lines.push('\n**Missing permissions for:**');
      diag.missing_origins.forEach(o => lines.push(`  - ${o}`));
    }

    if (diag.event_counts) {
      lines.push('\n**Event counts:**');
      const counts = diag.event_counts;
      lines.push(`  - WebRequest (request): ${counts.webRequest_request || 0}`);
      lines.push(`  - WebRequest (response): ${counts.webRequest_response || 0}`);
      lines.push(`  - WebNavigation (fallback): ${counts.webNavigation || 0}`);
    }

    if (diag.origin_stats) {
      lines.push('\n**Events by origin:**');
      diag.origin_stats.forEach(stat => {
        lines.push(`  - ${stat.origin}: ${stat.count} events (sources: ${stat.sources.join(', ')})`);
      });
    }
  }

  lines.push('\n## Captured Events\n');
  lines.push(`Total: ${captureData.events.length} events\n`);

  captureData.events.forEach((event, idx) => {
    lines.push(`### Event ${idx + 1}`);
    lines.push(`- **URL:** ${event.url}`);
    lines.push(`- **Method:** ${event.method}`);
    if (event.status) lines.push(`- **Status:** ${event.status}`);
    lines.push(`- **Source:** ${event.source}`);
    if (event.timestamp) lines.push(`- **Timestamp:** ${event.timestamp}`);
    if (event.set_cookie_names && event.set_cookie_names.length > 0) {
      lines.push(`- **Set-Cookie names:** ${event.set_cookie_names.join(', ')}`);
    }
    if (event.form_fields && event.form_fields.length > 0) {
      lines.push(`- **Form fields captured:** ${event.form_fields.length} form(s)`);
      event.form_fields.forEach((form, formIdx) => {
        lines.push(`  - Form ${formIdx + 1}: action=${form.form_action}`);
        form.fields.forEach(field => {
          lines.push(`    - ${field.name} (${field.type})`);
        });
      });
    }
    lines.push('');
  });

  return lines.join('\n');
}
