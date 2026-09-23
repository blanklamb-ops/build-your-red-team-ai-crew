#!/usr/bin/env node

/**
 * Traffic Pattern Stub Generator
 * Generates a commented skeleton for lab documentation
 * Not a production implant - documentation aid only
 */

const fs = require('fs');

function generateTrafficPattern(sessionData) {
  if (!sessionData || !sessionData.events) {
    throw new Error('Invalid session data');
  }

  const events = sessionData.events;
  const urlPatterns = new Map(); // URL pattern -> count

  for (const event of events) {
    try {
      const url = new URL(event.url);
      const pattern = `${event.method || 'GET'} ${url.pathname}`;
      urlPatterns.set(pattern, (urlPatterns.get(pattern) || 0) + 1);
    } catch (e) {
      // Skip invalid URLs
    }
  }

  // Sort by frequency
  const sorted = Array.from(urlPatterns.entries()).sort((a, b) => b[1] - a[1]);

  let output = '# Traffic Pattern Skeleton\n\n';
  output += '**Lab documentation only** - not a production profile\n\n';
  output += `Generated from ${events.length} captured events\n\n`;
  output += '## Observed URL Patterns\n\n';

  for (const [pattern, count] of sorted) {
    output += `- \`${pattern}\` (${count}x)\n`;
  }

  output += '\n## Operator Notes\n\n';
  output += '- Review patterns for auth-relevant endpoints\n';
  output += '- Correlate with timing and redirect chains\n';
  output += '- Adapt for lab documentation needs\n';

  return output;
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node traffic-pattern.js <session.json> [--output <file.md>]');
    process.exit(1);
  }

  const inputFile = args[0];
  let outputFile = null;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--output' && args[i + 1]) {
      outputFile = args[i + 1];
      i++;
    }
  }

  try {
    const sessionJson = fs.readFileSync(inputFile, 'utf-8');
    const sessionData = JSON.parse(sessionJson);

    const pattern = generateTrafficPattern(sessionData);

    if (outputFile) {
      fs.writeFileSync(outputFile, pattern);
      console.log(`✓ Traffic pattern written to ${outputFile}`);
    } else {
      console.log(pattern);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { generateTrafficPattern };
