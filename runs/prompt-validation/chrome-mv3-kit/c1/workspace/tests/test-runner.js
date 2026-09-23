#!/usr/bin/env node

/**
 * Test Runner - A11 requirement
 * Executes all test suites without child exit() calls terminating the runner
 */

const utilsTest = require('./utils-test.js');
const lifecycleTest = require('./lifecycle-test.js');
const formCaptureTest = require('./form-capture-test.js');
const phishletGeneratorTest = require('./phishlet-generator-test.js');
const schemaValidatorTest = require('./schema-validator-test.js');

function main() {
  console.log('='.repeat(60));
  console.log('chrome-mv3-kit Test Suite');
  console.log('='.repeat(60));
  console.log('');

  const suites = [
    { name: 'Utils Tests (A3g)', runner: utilsTest },
    { name: 'Lifecycle Tests (A3e, A3f)', runner: lifecycleTest },
    { name: 'Form Capture Tests (A3h)', runner: formCaptureTest },
    { name: 'Phishlet Generator Tests (A5, A5b, A5c, A5e)', runner: phishletGeneratorTest },
    { name: 'Schema Validation Tests (A5d)', runner: schemaValidatorTest }
  ];

  let totalPass = 0;
  let totalFail = 0;

  for (const suite of suites) {
    console.log('\n' + '='.repeat(60));
    console.log(`Running: ${suite.name}`);
    console.log('='.repeat(60));

    try {
      const results = suite.runner.runTests();

      if (results) {
        totalPass += results.length;
        console.log(`✓ ${suite.name} PASSED`);
      } else {
        // runTests returns null on failure
        totalFail++;
        console.log(`✗ ${suite.name} FAILED`);
      }
    } catch (error) {
      console.error(`✗ ${suite.name} crashed: ${error.message}`);
      totalFail++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('Test Summary');
  console.log('='.repeat(60));
  console.log(`Suites passed: ${totalPass}`);
  console.log(`Suites failed: ${totalFail}`);
  console.log('');

  if (totalFail === 0) {
    console.log('✓ ALL TESTS PASSED');
    process.exit(0);
  } else {
    console.log('✗ SOME TESTS FAILED');
    process.exit(1);
  }
}

// Run if invoked directly
if (require.main === module) {
  main();
}

module.exports = { main };
