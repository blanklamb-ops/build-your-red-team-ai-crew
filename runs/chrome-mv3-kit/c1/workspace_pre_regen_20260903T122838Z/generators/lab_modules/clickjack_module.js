// LAB MODULE — clickjacking structural review.
// Gated: only invoked by lab_modules/index.js when both the config flag and
// the CLI --lab-unsafe flag are set. See lab_modules/README.md.
//
// This module does NOT frame or attack a third-party site. It:
//   1. inspects headers/HTML the operator already captured for
//      framing-protection signals (X-Frame-Options / CSP frame-ancestors),
//   2. emits a labeled, static "framing_review.html" artifact that frames
//      the operator's OWN local snapshot.html (not a live target) inside an
//      iframe, purely so a defender/report reader can see what an
//      un-protected clone would look like when framed.

import { writeFile } from "node:fs/promises";
import path from "node:path";

/**
 * @param {string} html - snapshot HTML previously saved by page_clone.js
 * @param {object} headers - optional observed response headers (name: value)
 */
export function assessFramingProtections(html, headers = {}) {
  const lowerHeaders = Object.fromEntries(Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v]));
  const hasXfo = "x-frame-options" in lowerHeaders;
  const csp = lowerHeaders["content-security-policy"] || "";
  const hasFrameAncestors = /frame-ancestors/i.test(csp);
  return {
    x_frame_options_present: hasXfo,
    csp_frame_ancestors_present: hasFrameAncestors,
    likely_frameable: !hasXfo && !hasFrameAncestors,
  };
}

/**
 * @param {string} outDir - same directory as the page-clone snapshot
 * @param {object} assessment - result of assessFramingProtections
 */
export async function writeFramingReviewArtifact(outDir, assessment) {
  const artifactPath = path.join(outDir, "framing_review.html");
  const html = `<!doctype html>
<!--
  LAB REVIEW ARTIFACT — clickjack module (chrome-mv3-kit)
  Frames the LOCAL snapshot.html captured alongside this file for review
  purposes only. Do not repoint the iframe "src" at a third-party origin;
  doing so against systems you are not authorized to test is out of scope
  and prohibited by AUTHORIZED_USE.md.
-->
<html>
<head><meta charset="utf-8"><title>LAB REVIEW: framing susceptibility</title></head>
<body>
  <h1 style="font-family:sans-serif">LAB REVIEW — clickjack structural check</h1>
  <p style="font-family:sans-serif">
    Framing protections observed: X-Frame-Options=${assessment.x_frame_options_present},
    CSP frame-ancestors=${assessment.csp_frame_ancestors_present}.
    Likely frameable (from observed headers): <b>${assessment.likely_frameable}</b>.
  </p>
  <iframe src="./snapshot.html" width="800" height="600"
          style="border:2px dashed red"></iframe>
</body>
</html>
`;
  await writeFile(artifactPath, html, "utf8");
  return artifactPath;
}
