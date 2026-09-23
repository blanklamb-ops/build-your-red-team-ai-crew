#!/usr/bin/env node

/**
 * Master test runner
 * Executes all test suites
 */

const { testNormalization } = require('./test-normalization.js');
const { testLifecyclePersistence } = require('./test-lifecycle.js');
const { testFormCapture } = require('./test-form-capture.js');
const { testGenerator, testSecretRejection } = require('./test-generator.js');
const { testValidator } = require('./test-validator.js');

async function runAllTests() {
  console.log('=== Running All Tests ===\n');

  let passed = 0;
  let failed = 0;

  const tests = [
    { name: 'Origin Normalization', fn: testNormalization },
    { name: 'MV3 Lifecycle Persistence', fn: testLifecyclePersistence },
    { name: 'Form Field Capture', fn: testFormCapture },
    { name: 'Phishlet Generator', fn: testGenerator },
    { name: 'Secret Rejection', fn: testSecretRejection },
    { name: 'YAML Validator', fn: testValidator }
  ];

  for (const test of tests) {
    try {
      console.log(`\n--- ${test.name} ---`);
      await test.fn();
      passed++;
    } catch (error) {
      console.error(`\n✗ ${test.name} FAILED:`);
      console.error(error.message);
      console.error(error.stack);
      failed++;
    }
  }

  console.log('\n=== Test Summary ===');
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    process.exit(1);
  }

  console.log('\n✓ All tests passed!');
  process.exit(0);
}

if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests };
