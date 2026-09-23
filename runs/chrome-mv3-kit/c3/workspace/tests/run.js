#!/usr/bin/env node
"use strict";
const suites = ["structure", "origins", "lifecycle", "forms", "exports", "generator", "validation", "regression", "safety"];
(async () => {
  let failed = 0;
  for (const name of suites) {
    try { await require(`./${name}.test`)(); process.stdout.write(`PASS ${name}\n`); }
    catch (error) { failed++; process.stderr.write(`FAIL ${name}: ${error.stack || error.message}\n`); }
  }
  if (failed) process.exitCode = 1;
  else process.stdout.write(`PASS all ${suites.length} suites\n`);
})();
