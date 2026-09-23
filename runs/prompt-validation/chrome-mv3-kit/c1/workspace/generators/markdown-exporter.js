#!/usr/bin/env node

/**
 * Markdown Export Generator
 * Creates human-readable markdown summary from session JSON
 */

const fs = require('fs');

function generateMarkdown(session) {
  let md = `# Auth Flow Capture Report\n\n`;
  md += `**Session ID:** ${session.session_id}\n`;
  md += `**Started:** ${session.started_at}\n`;
  md += `**Stopped:** ${session.stopped_at}\n`;
  md += `**Coverage:** ${session.coverage}\n\n`;

  if (session.diagnostics) {
    md += `## Diagnostics\n\n`;

    if (session.diagnostics.event_counts) {
      md += `**Event Counts:**\n`;
      md += `- webRequest: ${session.diagnostics.event_counts.webRequest || 0}\n`;
      md += `- webRequestResponse: ${session.diagnostics.event_counts.webRequestResponse || 0}\n`;
      md += `- webNavigation: ${session.diagnostics.event_counts.webNavigation || 0}\n\n`;
    }

    if (session.diagnostics.requested_origins) {
      md += `**Requested Origins:** ${session.diagnostics.requested_origins.length}\n`;
      session.diagnostics.requested_origins.forEach(o => md += `- ${o}\n`);
      md += `\n`;
    }

    if (session.diagnostics.granted_origins) {
      md += `**Granted Origins:** ${session.diagnostics.granted_origins.length}\n`;
      session.diagnostics.granted_origins.forEach(o => md += `- ${o}\n`);
      md += `\n`;
    }

    if (session.diagnostics.missing_origins && session.diagnostics.missing_origins.length > 0) {
      md += `**⚠️ Missing Permissions:** ${session.diagnostics.missing_origins.length}\n`;
      session.diagnostics.missing_origins.forEach(o => md += `- ${o}\n`);
      md += `\n`;
    }

    if (session.diagnostics.observed_origins) {
      md += `**Observed Origins:** ${session.diagnostics.observed_origins.length}\n`;
      session.diagnostics.observed_origins.forEach(o => md += `- ${o}\n`);
      md += `\n`;
    }
  }

  md += `## Captured Events (${session.events.length})\n\n`;

  session.events.forEach((event, i) => {
    md += `### Event ${i + 1}\n`;
    md += `- **URL:** ${event.url}\n`;
    md += `- **Method:** ${event.method || 'GET'}\n`;

    if (event.status) {
      md += `- **Status:** ${event.status}\n`;
    }

    md += `- **Source:** ${event.source}\n`;

    if (event.set_cookie_names && event.set_cookie_names.length > 0) {
      md += `- **Set-Cookie Names:** ${event.set_cookie_names.join(', ')}\n`;
    }

    if (event.form_fields && event.form_fields.length > 0) {
      md += `- **Form Fields:**\n`;
      event.form_fields.forEach(form => {
        md += `  - **Action:** ${form.form_action}\n`;
        md += `    **Fields:** ${form.fields.map(f => `${f.name} (${f.type})`).join(', ')}\n`;
      });
    }

    md += `\n`;
  });

  return md;
}

// CLI
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: markdown-exporter.js <session.json> [--output <file>]');
    process.exit(1);
  }

  const sessionFile = args[0];
  let outputFile = null;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--output' && i + 1 < args.length) {
      outputFile = args[++i];
    }
  }

  try {
    const session = JSON.parse(fs.readFileSync(sessionFile, 'utf8'));
    const markdown = generateMarkdown(session);

    if (outputFile) {
      fs.writeFileSync(outputFile, markdown, 'utf8');
      console.log(`✓ Markdown written to ${outputFile}`);
    } else {
      console.log(markdown);
    }

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generateMarkdown
  };
}

// Run CLI if invoked directly
if (require.main === module) {
  main();
}
