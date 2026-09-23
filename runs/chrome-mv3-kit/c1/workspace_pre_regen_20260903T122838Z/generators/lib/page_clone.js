// Page-clone LAB utility.
//
// Saves a static HTML snapshot of a source (local file or a URL the operator
// is authorized to fetch, e.g. a lab target) plus a structural report
// (form count, external script count). This is for lab review of a page's
// structure — it does not rewrite forms to point at a collector, inject
// credential-harvesting JS, or beacon anywhere.
//
// Optional "unsafe" lab modules (clickjack / file-prompt) are separate,
// off by default, and only run when explicitly enabled — see
// lab_modules/index.js and config/lab.config.json.

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";

/**
 * @param {string} source - local file path or http(s) URL
 * @returns {Promise<string>} raw HTML
 */
export async function fetchSource(source) {
  if (/^https?:\/\//i.test(source)) {
    const res = await fetch(source);
    if (!res.ok) {
      throw new Error(`Page-clone error: fetch of "${source}" returned HTTP ${res.status}`);
    }
    return await res.text();
  }
  if (!existsSync(source)) {
    throw new Error(`Page-clone error: local source "${source}" does not exist`);
  }
  return await readFile(source, "utf8");
}

/**
 * Very small structural analysis — no external HTML parser dependency.
 * @param {string} html
 */
export function analyzeHtml(html) {
  const formCount = (html.match(/<form\b/gi) || []).length;
  const scriptTags = html.match(/<script\b[^>]*>/gi) || [];
  const externalScriptCount = scriptTags.filter((tag) => /\bsrc\s*=/i.test(tag)).length;
  return { formCount, externalScriptCount };
}

/**
 * @param {string} source
 * @param {string} outDir
 * @param {object} [opts]
 * @param {boolean} [opts.labUnsafeModulesEnabled]
 * @param {string[]} [opts.modulesRun]
 * @param {string[]} [opts.warnings]
 */
export async function writeCloneArtifacts(source, outDir, opts = {}) {
  const html = await fetchSource(source);
  const analysis = analyzeHtml(html);

  await mkdir(outDir, { recursive: true });
  const snapshotFile = path.join(outDir, "snapshot.html");
  await writeFile(snapshotFile, html, "utf8");

  const report = {
    source,
    captured_at_iso: new Date().toISOString(),
    snapshot_file: path.relative(process.cwd(), snapshotFile),
    form_count: analysis.formCount,
    external_script_count: analysis.externalScriptCount,
    lab_unsafe_modules_enabled: Boolean(opts.labUnsafeModulesEnabled),
    modules_run: opts.modulesRun || [],
    warnings: opts.warnings || [],
  };

  const reportFile = path.join(outDir, "clone_report.json");
  await writeFile(reportFile, JSON.stringify(report, null, 2), "utf8");

  return { html, report, snapshotFile, reportFile };
}
