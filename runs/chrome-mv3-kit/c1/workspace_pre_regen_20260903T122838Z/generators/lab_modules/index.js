// Gatekeeper for lab_unsafe_modules. Both the persisted config flag AND an
// explicit per-run CLI opt-in are required before any unsafe module runs.
// This is intentional defense-in-depth for R5/A6: a stray config file
// change alone should not silently activate these modules.

import { assessFramingProtections, writeFramingReviewArtifact } from "./clickjack_module.js";
import { writeFilePromptReviewArtifact } from "./file_prompt_module.js";

/**
 * @param {object} params
 * @param {boolean} params.configFlag - config/lab.config.json -> lab_unsafe_modules
 * @param {boolean} params.cliOptIn - CLI --lab-unsafe flag was passed
 * @param {string} params.outDir - clone output directory
 * @param {string} params.html - snapshot HTML
 * @param {object} [params.headers] - observed response headers, if any
 * @returns {Promise<{enabled: boolean, modulesRun: string[], warnings: string[]}>}
 */
export async function maybeRunUnsafeLabModules({ configFlag, cliOptIn, outDir, html, headers }) {
  const enabled = Boolean(configFlag) && Boolean(cliOptIn);
  const modulesRun = [];
  const warnings = [];

  if (!enabled) {
    warnings.push(
      configFlag && !cliOptIn
        ? "lab_unsafe_modules=true in config but --lab-unsafe was not passed; unsafe modules skipped."
        : "lab_unsafe_modules is false (default); unsafe modules skipped."
    );
    return { enabled: false, modulesRun, warnings };
  }

  const assessment = assessFramingProtections(html, headers || {});
  await writeFramingReviewArtifact(outDir, assessment);
  modulesRun.push("clickjack_overlay_report");

  await writeFilePromptReviewArtifact(outDir);
  modulesRun.push("file_prompt_report");

  return { enabled: true, modulesRun, warnings };
}
