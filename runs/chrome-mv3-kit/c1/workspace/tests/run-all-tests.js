#!/usr/bin/env node
/**
 * Master test runner - executes all test suites
 * Child test modules must return/throw rather than call process.exit
 */

import { runOriginTests } from './test-origin-normalization.js';
import { runLifecycleTests } from './test-lifecycle-persistence.js';
import { runFormCaptureTests } from './test-form-capture.js';
import { runPhishletGeneratorTests } from './test-phishlet-generator.js';
import { runSchemaValidationTests } from './test-schema-validation.js';
import { runRegressionTests } from './test-regression-a5e.js';

let totalTests = 0;
let totalPassed = 0;
let totalFailed = 0;

async function runTestSuite(name, testFn) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`Running: ${name}`);
  console.log('='.repeat(60));

  try {
    const result = await testFn();
    totalTests += result.total;
    totalPassed += result.passed;
    totalFailed += result.failed;

    if (result.failed === 0) {
      console.log(`✓ ${name}: ALL PASSED (${result.passed}/${result.total})`);
    } else {
      console.log(`✗ ${name}: FAILED (${result.failed}/${result.total} failures)`);
    }
  } catch (error) {
    console.error(`✗ ${name}: SUITE ERROR - ${error.message}`);
    totalFailed++;
  }
}

async function main() {
  console.log('Chrome MV3 Lab Kit - Full Test Suite\n');

  await runTestSuite('Origin Normalization Tests', runOriginTests);
  await runTestSuite('Lifecycle Persistence Tests', runLifecycleTests);
  await runTestSuite('Form Capture Tests', runFormCaptureTests);
  await runTestSuite('Phishlet Generator Tests', runPhishletGeneratorTests);
  await runTestSuite('Schema Validation Tests', runSchemaValidationTests);
  await runTestSuite('Regression Tests (A5e)', runRegressionTests);

  console.log(`\n${'='.repeat(60)}`);
  console.log('TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total tests: ${totalTests}`);
  console.log(`Passed: ${totalPassed}`);
  console.log(`Failed: ${totalFailed}`);

  if (totalFailed === 0) {
    console.log('\n✓ ALL TESTS PASSED');
    process.exit(0);
  } else {
    console.log(`\n✗ ${totalFailed} TEST(S) FAILED`);
    process.exit(1);
  }
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
