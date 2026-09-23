/**
 * Evilginx 2.3.0 phishlet schema validator
 */

import Ajv from 'ajv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load schema
const schemaPath = path.join(__dirname, '../testdata/phishlet-schema-2.3.0.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

const ajv = new Ajv({ strict: false, allErrors: true });
const validate = ajv.compile(schema);

/**
 * Validate phishlet against Evilginx 2.3.0 schema
 */
export function validatePhishlet(phishlet) {
  const valid = validate(phishlet);

  if (!valid) {
    console.error('Schema validation errors:');
    for (const error of validate.errors) {
      console.error(`  ${error.instancePath} ${error.message}`);
      if (error.params) {
        console.error(`    Params:`, JSON.stringify(error.params));
      }
    }
    return false;
  }

  return true;
}

/**
 * Get validation errors (for testing)
 */
export function getValidationErrors(phishlet) {
  const valid = validate(phishlet);
  return valid ? [] : validate.errors;
}
