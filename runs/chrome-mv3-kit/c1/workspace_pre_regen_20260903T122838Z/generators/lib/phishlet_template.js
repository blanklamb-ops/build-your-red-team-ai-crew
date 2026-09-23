// Phishlet-oriented template generator.
//
// This produces a STRUCTURAL template file (YAML) with clearly marked
// placeholders, intended to seed an operator's own phishing-proxy tooling
// (e.g. an Evilginx-style phishlet) for an AUTHORIZED engagement. It does
// not contain working attack logic, TLS material, or transparent-proxy
// config — those are the operator's responsibility to fill in under their
// own authorization and tooling.

const PLACEHOLDER = (label) => `__REPLACE_${label}__`;

/**
 * @param {object} input - matches schemas/phishlet_input.schema.json
 * @returns {string} YAML template text
 */
export function buildPhishletTemplate(input) {
  assertValidPhishletInput(input);

  const {
    target_name,
    landing_domain_placeholder = "REPLACE_ME.lab.invalid",
    login_paths,
    cookie_names,
    notes = "",
  } = input;

  const authUrlsYaml = login_paths
    .map((p) => `      - "${p}"  # ${PLACEHOLDER("PROXY_HOST_FOR_PATH")}`)
    .join("\n");

  const cookiesYaml = cookie_names
    .map(
      (name) =>
        `      - name: "${name}"\n        domain: "${PLACEHOLDER("COOKIE_DOMAIN")}"\n        path: "/"\n        is_session: true`
    )
    .join("\n");

  return `# Phishlet-oriented template — GENERATED, NOT PRODUCTION-READY
# Tool: chrome-mv3-kit / generators/lib/phishlet_template.js
# Authorized-use only. See ../../README.md and ../../OPSEC_CARD.md.
#
# Every "__REPLACE_*__" placeholder MUST be filled in by the operator
# before this template is usable, and only against systems covered by a
# signed authorization / rules of engagement.

name: "${target_name}"
author: "${PLACEHOLDER("OPERATOR_NAME")}"
min_ver: "0.0.0"

proxy_hosts:
  - phish_sub: "${PLACEHOLDER("PHISH_SUBDOMAIN")}"
    orig_sub: "${PLACEHOLDER("ORIGINAL_SUBDOMAIN")}"
    domain: "${landing_domain_placeholder}"
    session: true
    is_landing: true

auth_urls:
${authUrlsYaml}

credentials:
  username:
    key: "${PLACEHOLDER("USERNAME_FIELD_NAME")}"
  password:
    key: "${PLACEHOLDER("PASSWORD_FIELD_NAME")}"

cookies:
${cookiesYaml}

login:
  domain: "${landing_domain_placeholder}"
  path: "${PLACEHOLDER("LOGIN_LANDING_PATH")}"

notes: |
  ${notes || "(no operator notes provided)"}
  Generated at: ${new Date().toISOString()}
`;
}

/**
 * @param {object} input
 */
export function assertValidPhishletInput(input) {
  if (!input || typeof input !== "object") {
    throw new Error("Phishlet input error: expected a JSON object");
  }
  if (!input.target_name || typeof input.target_name !== "string") {
    throw new Error('Phishlet input error: "target_name" is required and must be a non-empty string');
  }
  if (!Array.isArray(input.login_paths) || input.login_paths.length === 0) {
    throw new Error('Phishlet input error: "login_paths" is required and must be a non-empty array');
  }
  if (!Array.isArray(input.cookie_names) || input.cookie_names.length === 0) {
    throw new Error('Phishlet input error: "cookie_names" is required and must be a non-empty array');
  }
}
