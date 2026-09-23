#!/usr/bin/env node
// chrome-mv3-kit headless generator CLI.
//
// Usage:
//   node generators/cli.js session:export-md   <session.json> [out.md]
//   node generators/cli.js session:export-json <session.json> [out.json]
//   node generators/cli.js phishlet:generate    <input.json> [out.yaml]
//   node generators/cli.js profile:generate     <input.json> [out.txt]
//   node generators/cli.js clone:run            <sourcePathOrUrl> <outDir> [--lab-unsafe] [--config <path>]
//
// All commands fail with a non-zero exit code and a clear stderr message on
// missing/invalid input rather than emitting silent garbage (ACCEPTANCE M3).

import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { sessionToJson, sessionToMarkdown, assertValidSession } from "./lib/session_export.js";
import { buildPhishletTemplate, assertValidPhishletInput } from "./lib/phishlet_template.js";
import { buildProfileStub, assertValidProfileStubInput } from "./lib/profile_stub.js";
import { writeCloneArtifacts } from "./lib/page_clone.js";
import { maybeRunUnsafeLabModules } from "./lab_modules/index.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
}

async function readJson(filePath, label) {
  let raw;
  try {
    raw = await readFile(filePath, "utf8");
  } catch (err) {
    fail(`could not read ${label} at "${filePath}": ${err.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    fail(`${label} at "${filePath}" is not valid JSON: ${err.message}`);
  }
}

async function cmdSessionExportMd(args) {
  const [inPath, outPath = "out/session_summary.md"] = args;
  if (!inPath) fail('session:export-md requires <session.json>');
  const session = await readJson(inPath, "session JSON");
  try {
    assertValidSession(session);
  } catch (err) {
    fail(err.message);
  }
  const md = sessionToMarkdown(session);
  await mkdirFor(outPath);
  await writeFile(outPath, md, "utf8");
  console.log(`wrote ${outPath}`);
}

async function cmdSessionExportJson(args) {
  const [inPath, outPath = "out/session_export.json"] = args;
  if (!inPath) fail('session:export-json requires <session.json>');
  const session = await readJson(inPath, "session JSON");
  try {
    assertValidSession(session);
  } catch (err) {
    fail(err.message);
  }
  await mkdirFor(outPath);
  await writeFile(outPath, sessionToJson(session), "utf8");
  console.log(`wrote ${outPath}`);
}

async function cmdPhishletGenerate(args) {
  const [inPath, outPath = "out/phishlet_template.yaml"] = args;
  if (!inPath) fail('phishlet:generate requires <input.json>');
  const input = await readJson(inPath, "phishlet input JSON");
  try {
    assertValidPhishletInput(input);
  } catch (err) {
    fail(err.message);
  }
  const template = buildPhishletTemplate(input);
  await mkdirFor(outPath);
  await writeFile(outPath, template, "utf8");
  console.log(`wrote ${outPath}`);
}

async function cmdProfileGenerate(args) {
  const [inPath, outPath = "out/profile_stub.txt"] = args;
  if (!inPath) fail('profile:generate requires <input.json>');
  const input = await readJson(inPath, "profile-stub input JSON");
  try {
    assertValidProfileStubInput(input);
  } catch (err) {
    fail(err.message);
  }
  const stub = buildProfileStub(input);
  await mkdirFor(outPath);
  await writeFile(outPath, stub, "utf8");
  console.log(`wrote ${outPath}`);
}

async function cmdCloneRun(args) {
  const positional = args.filter((a) => !a.startsWith("--"));
  const labUnsafeCli = args.includes("--lab-unsafe");
  const configIdx = args.indexOf("--config");
  const configPath = configIdx >= 0 ? args[configIdx + 1] : path.join(__dirname, "..", "config", "lab.config.json");

  const [source, outDir = "out/clone"] = positional;
  if (!source) fail('clone:run requires <sourcePathOrUrl> [outDir]');

  const config = await readJson(configPath, "lab config JSON");
  const configFlag = config.lab_unsafe_modules === true;

  let result;
  try {
    result = await writeCloneArtifacts(source, outDir, {
      labUnsafeModulesEnabled: configFlag && labUnsafeCli,
    });
  } catch (err) {
    fail(err.message);
  }

  const modulesResult = await maybeRunUnsafeLabModules({
    configFlag,
    cliOptIn: labUnsafeCli,
    outDir,
    html: result.html,
  });

  // Re-write the report with final module info now that modules have run.
  const finalReport = {
    ...result.report,
    lab_unsafe_modules_enabled: modulesResult.enabled,
    modules_run: modulesResult.modulesRun,
    warnings: modulesResult.warnings,
  };
  await writeFile(result.reportFile, JSON.stringify(finalReport, null, 2), "utf8");

  console.log(`wrote ${result.snapshotFile}`);
  console.log(`wrote ${result.reportFile}`);
  if (modulesResult.warnings.length) {
    modulesResult.warnings.forEach((w) => console.log(`note: ${w}`));
  }
  if (modulesResult.enabled) {
    console.log(`lab_unsafe_modules ran: ${modulesResult.modulesRun.join(", ")}`);
  }
}

async function mkdirFor(filePath) {
  const dir = path.dirname(filePath);
  const { mkdir } = await import("node:fs/promises");
  await mkdir(dir, { recursive: true });
}

async function main() {
  const [, , command, ...args] = process.argv;

  const commands = {
    "session:export-md": cmdSessionExportMd,
    "session:export-json": cmdSessionExportJson,
    "phishlet:generate": cmdPhishletGenerate,
    "profile:generate": cmdProfileGenerate,
    "clone:run": cmdCloneRun,
  };

  if (!command || !commands[command]) {
    console.error("chrome-mv3-kit generator CLI");
    console.error("");
    console.error("commands:");
    Object.keys(commands).forEach((c) => console.error(`  ${c}`));
    process.exit(command ? 1 : 0);
  }

  await commands[command](args);
}

main().catch((err) => fail(err.stack || String(err)));
