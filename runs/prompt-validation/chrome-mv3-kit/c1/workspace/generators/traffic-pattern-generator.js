#!/usr/bin/env node

/**
 * Traffic Pattern Stub Generator
 * Creates a commented HTTP traffic-pattern skeleton for lab documentation
 * NOT a production implant
 */

const fs = require('fs');

function generateTrafficPattern(session) {
  const events = session.events || [];

  if (events.length === 0) {
    throw new Error('No events in session');
  }

  let output = `# HTTP Traffic Pattern Skeleton\n`;
  output += `# Lab Documentation Aid - NOT a production profile\n\n`;
  output += `Session ID: ${session.session_id}\n`;
  output += `Captured: ${session.started_at} to ${session.stopped_at}\n`;
  output += `Coverage: ${session.coverage}\n\n`;
  output += `## Observed Flow Pattern\n\n`;

  // Group by domain
  const byDomain = new Map();

  for (const event of events) {
    try {
      const url = new URL(event.url);
      const domain = url.hostname;

      if (!byDomain.has(domain)) {
        byDomain.set(domain, []);
      }

      byDomain.get(domain).push(event);
    } catch (e) {
      // Skip invalid URLs
    }
  }

  // Output pattern
  for (const [domain, domainEvents] of byDomain.entries()) {
    output += `### ${domain}\n\n`;

    for (const event of domainEvents) {
      const url = new URL(event.url);
      output += `- **${event.method}** ${url.pathname}${url.search}\n`;

      if (event.status) {
        output += `  - Status: ${event.status}\n`;
      }

      if (event.set_cookie_names && event.set_cookie_names.length > 0) {
        output += `  - Set-Cookie: ${event.set_cookie_names.join(', ')}\n`;
      }

      if (event.form_fields && event.form_fields.length > 0) {
        output += `  - Form fields detected:\n`;
        for (const form of event.form_fields) {
          output += `    - Action: ${form.form_action}\n`;
          output += `      Fields: ${form.fields.map(f => f.name).join(', ')}\n`;
        }
      }

      output += `\n`;
    }
  }

  output += `## Summary\n\n`;
  output += `Total requests: ${events.length}\n`;
  output += `Unique domains: ${byDomain.size}\n\n`;

  output += `**Note:** This is a URL pattern skeleton for lab documentation.\n`;
  output += `It does not include request bodies, headers, or timing.\n`;

  return output;
}

// CLI
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: traffic-pattern-generator.js <session.json> [--output <file>]');
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
    const pattern = generateTrafficPattern(session);

    if (outputFile) {
      fs.writeFileSync(outputFile, pattern, 'utf8');
      console.log(`✓ Traffic pattern written to ${outputFile}`);
    } else {
      console.log(pattern);
    }

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generateTrafficPattern
  };
}

// Run CLI if invoked directly
if (require.main === module) {
  main();
}
