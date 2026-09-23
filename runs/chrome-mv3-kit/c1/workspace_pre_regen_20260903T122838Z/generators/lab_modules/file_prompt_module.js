// LAB MODULE — file-prompt pretext structural review.
// Gated: only invoked by lab_modules/index.js when both the config flag and
// the CLI --lab-unsafe flag are set. See lab_modules/README.md.
//
// This module does NOT generate an executable, script, or macro-bearing
// document. It emits a labeled, static HTML artifact showing what a
// "download/open this file" social-engineering pretext overlay would look
// like on the cloned page, plus an inert placeholder text file (never an
// executable) so a report can reference "the operator clicked X" without
// ever shipping real payload logic.

import { writeFile } from "node:fs/promises";
import path from "node:path";

/**
 * @param {string} outDir - same directory as the page-clone snapshot
 */
export async function writeFilePromptReviewArtifact(outDir) {
  const decoyPath = path.join(outDir, "decoy_placeholder.txt");
  await writeFile(
    decoyPath,
    "This is an inert placeholder artifact generated for lab review only.\n" +
      "It contains no executable content, macros, or scripts.\n" +
      "chrome-mv3-kit / lab_modules/file_prompt_module.js\n",
    "utf8"
  );

  const artifactPath = path.join(outDir, "file_prompt_review.html");
  const html = `<!doctype html>
<!--
  LAB REVIEW ARTIFACT — file-prompt module (chrome-mv3-kit)
  Demonstrates a "you need to open this file" pretext overlay UI for
  awareness/report purposes. The linked file is an inert .txt placeholder,
  not an executable payload. Do not substitute a real executable or macro
  document — that is out of scope for this tool.
-->
<html>
<head><meta charset="utf-8"><title>LAB REVIEW: file-prompt pretext</title></head>
<body style="font-family:sans-serif">
  <h1>LAB REVIEW — file-prompt pretext overlay</h1>
  <div style="border:2px dashed red;padding:16px;max-width:420px">
    <p><b>Example pretext copy (operator-authored, redact before use):</b></p>
    <p>"Your document is ready — click below to open it."</p>
    <a href="./decoy_placeholder.txt" download>Open document (inert placeholder)</a>
  </div>
</body>
</html>
`;
  await writeFile(artifactPath, html, "utf8");
  return { artifactPath, decoyPath };
}
