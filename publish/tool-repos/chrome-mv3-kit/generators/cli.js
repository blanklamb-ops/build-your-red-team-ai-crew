#!/usr/bin/env node
/**
 * CLI for running generators on fixtures
 */

import fs from 'fs';
import path from 'path';
import { generatePhishlet, exportPhishletYaml, validateNoPlaceholders } from './phishlet-generator.js';
import { validatePhishlet } from './phishlet-validator.js';
import { generateMarkdownReport } from './markdown-exporter.js';
import { generateTrafficPattern } from './traffic-pattern-exporter.js';

const command = process.argv[2];
const inputFile = process.argv[3];

if (!command) {
  console.log('Usage:');
  console.log('  node cli.js generate <capture.json>  - Generate all outputs');
  console.log('  node cli.js validate <phishlet.yaml> - Validate phishlet');
  process.exit(1);
}

if (command === 'generate') {
  if (!inputFile) {
    console.error('Error: Input file required');
    process.exit(1);
  }

  try {
    const captureData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

    // Generate phishlet
    const phishlet = generatePhishlet(captureData);
    const yamlContent = exportPhishletYaml(phishlet);

    // Validate no placeholders
    validateNoPlaceholders(yamlContent);

    // Validate against schema
    const isValid = validatePhishlet(phishlet);
    if (!isValid) {
      console.error('Error: Generated phishlet failed schema validation');
      process.exit(1);
    }

    // Write outputs
    const baseName = path.basename(inputFile, '.json');
    const outputDir = path.dirname(inputFile);

    const phishletPath = path.join(outputDir, `${baseName}-phishlet.yaml`);
    const markdownPath = path.join(outputDir, `${baseName}-report.md`);
    const trafficPath = path.join(outputDir, `${baseName}-traffic-pattern.txt`);

    fs.writeFileSync(phishletPath, yamlContent);
    console.log(`✓ Generated phishlet: ${phishletPath}`);

    // Generate markdown report
    const markdown = generateMarkdownReport(captureData);
    fs.writeFileSync(markdownPath, markdown);
    console.log(`✓ Generated markdown: ${markdownPath}`);

    // Generate traffic pattern
    const traffic = generateTrafficPattern(captureData);
    fs.writeFileSync(trafficPath, traffic);
    console.log(`✓ Generated traffic pattern: ${trafficPath}`);

    console.log('\nPhishlet validation: PASS');
    console.log('No {{PLACEHOLDER}} tokens found: PASS');

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

if (command === 'validate') {
  if (!inputFile) {
    console.error('Error: Input file required');
    process.exit(1);
  }

  try {
    const content = fs.readFileSync(inputFile, 'utf8');

    // Check for placeholders
    validateNoPlaceholders(content);

    // Parse and validate
    const yaml = await import('js-yaml');
    const phishlet = yaml.load(content);

    const isValid = validatePhishlet(phishlet);

    if (isValid) {
      console.log('✓ Phishlet validation: PASS');
      console.log('✓ No {{PLACEHOLDER}} tokens found');
    } else {
      console.error('✗ Phishlet validation: FAIL');
      process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}
