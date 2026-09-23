#!/usr/bin/env node

/**
 * Phishlet YAML Validator
 * Uses YAML parser + JSON Schema validation
 */

const fs = require('fs');
const yaml = require('js-yaml');
const Ajv = require('ajv');

function validatePhishlet(yamlContent, schemaPath) {
  // Parse YAML
  let phishlet;
  try {
    phishlet = yaml.load(yamlContent);
  } catch (error) {
    throw new Error(`YAML parse error: ${error.message}`);
  }

  // Load schema
  const schemaJson = fs.readFileSync(schemaPath, 'utf-8');
  const schema = JSON.parse(schemaJson);

  // Validate with JSON Schema
  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema);
  const valid = validate(phishlet);

  if (!valid) {
    const errors = validate.errors.map(e => `${e.instancePath} ${e.message}`).join('\n');
    throw new Error(`Schema validation failed:\n${errors}`);
  }

  // Additional custom validations
  // Check for forbidden cookie value keys in auth_tokens
  if (phishlet.auth_tokens && Array.isArray(phishlet.auth_tokens)) {
    for (const token of phishlet.auth_tokens) {
      if (token.value !== undefined) {
        throw new Error('Forbidden property: auth_tokens must not contain "value" keys');
      }
      if (token.keys && Array.isArray(token.keys)) {
        for (const item of token.keys) {
          if (typeof item === 'object' && item.value !== undefined) {
            throw new Error('Forbidden property: auth_tokens.keys must not contain objects with "value"');
          }
        }
      }
    }
  }

  // Check for non-placeholder credentials when no evidence
  if (phishlet.credentials && Array.isArray(phishlet.credentials)) {
    for (const cred of phishlet.credentials) {
      if (cred.search && cred.search !== '{{PLACEHOLDER}}' && cred.search.match(/^\(.*\)$/)) {
        // Looks like a real regex, not a placeholder
        throw new Error(`Non-placeholder credential search pattern found: ${cred.key}. Use {{PLACEHOLDER}} unless form field names were captured.`);
      }
    }
  }

  return { valid: true, phishlet };
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node validator.js <phishlet.yaml> [--schema <schema.json>]');
    process.exit(1);
  }

  const inputFile = args[0];
  let schemaPath = '../schemas/phishlet-schema.json';

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--schema' && args[i + 1]) {
      schemaPath = args[i + 1];
      i++;
    }
  }

  try {
    const yamlContent = fs.readFileSync(inputFile, 'utf-8');

    // Resolve schema path relative to this script
    const resolvedSchemaPath = require('path').resolve(__dirname, schemaPath);

    const result = validatePhishlet(yamlContent, resolvedSchemaPath);

    console.log('✓ Phishlet validation passed');
    process.exit(0);
  } catch (error) {
    console.error(`✗ Validation failed: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { validatePhishlet };
