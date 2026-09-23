#!/usr/bin/env node
"use strict";
const fs = require("fs");
const { generateYaml } = require("./phishlet");
const { sessionToMarkdown } = require("./capture");
const { generateTrafficStub } = require("./traffic_stub");
const { validateYaml } = require("./validate");

function usage() {
  throw new Error("Usage: node generators/cli.js <phishlet|markdown|traffic|validate> <input> [output] [--author NAME] [--include-host HOST]");
}
function main(argv) {
  const [command, input, output, ...flags] = argv;
  if (!command || !input) usage();
  if (command === "validate") {
    const result = validateYaml(fs.readFileSync(input, "utf8"));
    if (!result.valid) throw new Error(result.errors.join("\n"));
    process.stdout.write("Valid Evilginx 2.3.0 phishlet YAML\n");
    return;
  }
  if (!output) usage();
  const session = JSON.parse(fs.readFileSync(input, "utf8"));
  let content;
  if (command === "phishlet") {
    const options = { includeHosts: [] };
    for (let i = 0; i < flags.length; i += 2) {
      if (flags[i] === "--author") options.author = flags[i + 1];
      else if (flags[i] === "--include-host") options.includeHosts.push(flags[i + 1]);
      else throw new Error(`Unknown option: ${flags[i]}`);
    }
    content = generateYaml(session, options).yaml;
  } else if (command === "markdown") content = sessionToMarkdown(session);
  else if (command === "traffic") content = generateTrafficStub(session);
  else usage();
  fs.writeFileSync(output, content, "utf8");
}
if (require.main === module) {
  try { main(process.argv.slice(2)); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
module.exports = { main };
