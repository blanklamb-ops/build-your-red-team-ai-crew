// Malleable-C2-style profile stub exporter.
//
// Produces a DRAFT, heavily commented skeleton derived from operator-supplied
// "observed URL patterns" (e.g. from an auth-flow recording session). This is
// explicitly NOT a complete or working malleable profile — no working
// http-get/http-post transaction blocks, jitter, or crypto config are
// filled in. It exists to save an operator time turning field notes into a
// starting skeleton for their own authorized tooling.

/**
 * @param {object} input - matches schemas/profile_stub_input.schema.json
 * @returns {string} commented profile-stub text
 */
export function buildProfileStub(input) {
  assertValidProfileStubInput(input);

  const { profile_label, observed_patterns, notes = "" } = input;

  const patternBlocks = observed_patterns
    .map((p, i) => {
      const method = p.method || "GET";
      const contentType = p.content_type || "__REPLACE_CONTENT_TYPE__";
      return `    # Observed pattern #${i + 1}${p.note ? " — " + p.note : ""}
    # uri      "${p.uri_path}"
    # method   "${method}"
    # NOTE: This is a draft comment block, not an active transaction.
    #       Fill in client/server blocks per your C2 framework's profile
    #       language before use, with content-type "${contentType}".`;
    })
    .join("\n\n");

  return `# Malleable-profile STUB — draft skeleton, not a production profile
# label: ${profile_label}
# generated_at: ${new Date().toISOString()}
# tool: chrome-mv3-kit / generators/lib/profile_stub.js
#
# This file is intentionally incomplete. It captures *shape* observed during
# an authorized engagement (URL paths, methods, content types) so an operator
# can hand-author a real profile in their own C2 framework's syntax. It is
# not parseable by any specific C2 product as-is, and ships with no jitter,
# sleep, indicator, or crypto configuration.
#
# Non-goal: this tool does not guarantee detection bypass of any control.

set sleeptime "__REPLACE_SLEEPTIME_MS__";
set jitter    "__REPLACE_JITTER_PERCENT__";

# --- Observed URL patterns (informational only) --------------------------
#
${patternBlocks}
#
# ---------------------------------------------------------------------------

# notes:
# ${notes || "(no operator notes provided)"}
`;
}

/**
 * @param {object} input
 */
export function assertValidProfileStubInput(input) {
  if (!input || typeof input !== "object") {
    throw new Error("Profile-stub input error: expected a JSON object");
  }
  if (!input.profile_label || typeof input.profile_label !== "string") {
    throw new Error('Profile-stub input error: "profile_label" is required and must be a non-empty string');
  }
  if (!Array.isArray(input.observed_patterns) || input.observed_patterns.length === 0) {
    throw new Error('Profile-stub input error: "observed_patterns" is required and must be a non-empty array');
  }
  input.observed_patterns.forEach((p, i) => {
    if (!p || typeof p !== "object" || !p.uri_path) {
      throw new Error(`Profile-stub input error: observed_patterns[${i}] is missing required "uri_path"`);
    }
  });
}
