/**
 * A5e Regression Test - Mixed Capture
 * Tests production generator against testdata/regression-mixed-capture.json
 * This is the CRITICAL acceptance test that must pass
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { generatePhishlet, exportPhishletYaml, validateNoPlaceholders } from '../generators/phishlet-generator.js';
import { validatePhishlet } from '../generators/phishlet-validator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function runRegressionTests() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // Load regression fixture
  const fixturePath = path.join(__dirname, '../testdata/regression-mixed-capture.json');
  const captureData = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

  // Generate phishlet from fixture
  let phishlet;
  let yamlContent;

  test('A5e: Generate phishlet from regression fixture', () => {
    phishlet = generatePhishlet(captureData);
    if (!phishlet) {
      throw new Error('Failed to generate phishlet');
    }
  });

  test('A5e: Export to YAML without errors', () => {
    yamlContent = exportPhishletYaml(phishlet);
    if (!yamlContent) {
      throw new Error('Failed to export YAML');
    }
  });

  test('A5e-1: proxy_hosts domains are subset of expected', () => {
    const allowedDomains = ['idp.test', 'wallet.test', 'authcdn.test', 'corp.test'];
    const domains = phishlet.proxy_hosts.map(h => h.domain);

    for (const domain of domains) {
      if (!allowedDomains.includes(domain)) {
        throw new Error(`Unexpected domain in proxy_hosts: ${domain}`);
      }
    }

    // Must include these core domains
    if (!domains.includes('idp.test')) {
      throw new Error('Missing required domain: idp.test');
    }
    if (!domains.includes('wallet.test')) {
      throw new Error('Missing required domain: wallet.test');
    }
    if (!domains.includes('corp.test')) {
      throw new Error('Missing required domain: corp.test');
    }

    if (domains.length < 3 || domains.length > 4) {
      throw new Error(`Expected 3-4 domains, got ${domains.length}`);
    }
  });

  test('A5e-2: No junk hosts (graph/admin/monitor/telemetry/CDN)', () => {
    const junkPatterns = [
      'graph', 'admin', 'monitor', 'metrics', 'wcpstatic',
      'uhf', 'edgecdn', 'storage', 'blob', 'amcdn',
      'fpt', 'copilot', 'clarity'
    ];

    for (const host of phishlet.proxy_hosts) {
      const domainLower = host.domain.toLowerCase();
      const origSubLower = host.orig_sub.toLowerCase();

      for (const pattern of junkPatterns) {
        if (domainLower.includes(pattern) || origSubLower.includes(pattern)) {
          throw new Error(`Junk host found: ${host.domain} (${host.orig_sub})`);
        }
      }

      // Check for hex-like orig_sub
      if (host.orig_sub.length >= 12 && /^[a-f0-9]{12,}$/i.test(host.orig_sub)) {
        throw new Error(`Hex-like orig_sub found: ${host.orig_sub}`);
      }
    }
  });

  test('A5e-3: auth_tokens domains are registrable', () => {
    for (const token of phishlet.auth_tokens) {
      if (!token.domain) {
        throw new Error('auth_token missing domain');
      }

      // Domain should be eTLD+1, not full hostname
      const parts = token.domain.split('.');
      if (parts.length !== 2) {
        // Allow for .co.uk style (3 parts)
        if (parts.length !== 3 || !['co', 'com'].includes(parts[1])) {
          throw new Error(`auth_token domain not registrable: ${token.domain}`);
        }
      }

      if (!token.keys || !Array.isArray(token.keys)) {
        throw new Error('auth_token missing or invalid keys array');
      }
    }
  });

  test('A5e-4: login.domain is wallet.test, login.path is /ppsecure/post.srf', () => {
    if (phishlet.login.domain !== 'wallet.test') {
      throw new Error(`Expected login.domain=wallet.test, got ${phishlet.login.domain}`);
    }

    if (phishlet.login.path !== '/ppsecure/post.srf') {
      throw new Error(`Expected login.path=/ppsecure/post.srf, got ${phishlet.login.path}`);
    }

    // No login.username or login.password
    if ('username' in phishlet.login) {
      throw new Error('login.username should not exist in 2.3.0');
    }
    if ('password' in phishlet.login) {
      throw new Error('login.password should not exist in 2.3.0');
    }
  });

  test('A5e-5: credentials is map with correct keys from form_fields', () => {
    if (Array.isArray(phishlet.credentials)) {
      throw new Error('credentials must be map/object, not array');
    }

    if (!phishlet.credentials.username || !phishlet.credentials.password) {
      throw new Error('credentials must have username and password');
    }

    // Check captured field names
    if (phishlet.credentials.username.key !== 'loginfmt') {
      throw new Error(`Expected username.key=loginfmt, got ${phishlet.credentials.username.key}`);
    }

    if (phishlet.credentials.password.key !== 'passwd') {
      throw new Error(`Expected password.key=passwd, got ${phishlet.credentials.password.key}`);
    }

    // Check type
    if (phishlet.credentials.username.type !== 'post' && phishlet.credentials.username.type !== 'json') {
      throw new Error(`Invalid username.type: ${phishlet.credentials.username.type}`);
    }
    if (phishlet.credentials.password.type !== 'post' && phishlet.credentials.password.type !== 'json') {
      throw new Error(`Invalid password.type: ${phishlet.credentials.password.type}`);
    }

    // Check search is not placeholder
    if (!phishlet.credentials.username.search || phishlet.credentials.username.search === '{{PLACEHOLDER}}') {
      throw new Error('credentials.username.search is placeholder or empty');
    }
    if (!phishlet.credentials.password.search || phishlet.credentials.password.search === '{{PLACEHOLDER}}') {
      throw new Error('credentials.password.search is placeholder or empty');
    }

    // Default should be (.*)
    if (phishlet.credentials.username.search !== '(.*)') {
      console.warn(`  Note: username.search is ${phishlet.credentials.username.search}, expected (.*) for post type`);
    }
  });

  test('A5e-6: auth_urls includes checkpassword and GetCredentialType', () => {
    if (!Array.isArray(phishlet.auth_urls)) {
      throw new Error('auth_urls must be array');
    }

    const hasCheckPassword = phishlet.auth_urls.some(url =>
      url.toLowerCase().includes('checkpassword')
    );
    const hasGetCredentialType = phishlet.auth_urls.some(url =>
      url.toLowerCase().includes('getcredentialtype')
    );

    if (!hasCheckPassword) {
      throw new Error('auth_urls should include checkpassword.srf');
    }
    if (!hasGetCredentialType) {
      throw new Error('auth_urls should include GetCredentialType');
    }
  });

  test('A5e-7: sub_filters is non-empty object array with no placeholders', () => {
    if (!Array.isArray(phishlet.sub_filters)) {
      throw new Error('sub_filters must be array');
    }

    if (phishlet.sub_filters.length === 0) {
      throw new Error('sub_filters must not be empty');
    }

    for (const filter of phishlet.sub_filters) {
      if (typeof filter !== 'object' || Array.isArray(filter)) {
        throw new Error('sub_filters items must be objects, not strings');
      }

      const required = ['triggers_on', 'orig_sub', 'domain', 'search', 'replace', 'mimes'];
      for (const field of required) {
        if (!(field in filter)) {
          throw new Error(`sub_filter missing ${field}`);
        }
        if (typeof filter[field] === 'string' && filter[field].includes('{{PLACEHOLDER}}')) {
          throw new Error(`sub_filter.${field} contains {{PLACEHOLDER}}`);
        }
      }
    }

    // At least one filter should match a proxy_hosts entry
    const domains = phishlet.proxy_hosts.map(h => h.domain);
    const matchesHost = phishlet.sub_filters.some(f => domains.includes(f.domain));

    if (!matchesHost) {
      throw new Error('sub_filters should derive from proxy_hosts');
    }
  });

  test('A5e-8: min_ver is 2.3.0 and author is non-empty', () => {
    if (phishlet.min_ver !== '2.3.0') {
      throw new Error(`Expected min_ver=2.3.0, got ${phishlet.min_ver}`);
    }

    if (!phishlet.author || phishlet.author.trim() === '') {
      throw new Error('author must be non-empty string');
    }
  });

  test('A5e-9: Full YAML text contains no {{PLACEHOLDER}}', () => {
    if (yamlContent.includes('{{PLACEHOLDER}}')) {
      throw new Error('YAML contains {{PLACEHOLDER}} tokens');
    }
  });

  test('A5e: Schema validation passes', () => {
    const isValid = validatePhishlet(phishlet);
    if (!isValid) {
      throw new Error('Phishlet failed schema validation');
    }
  });

  // Run all tests
  for (const { name, fn } of tests) {
    try {
      fn();
      console.log(`  ✓ ${name}`);
      passed++;
    } catch (error) {
      console.log(`  ✗ ${name}: ${error.message}`);
      failed++;
    }
  }

  return { total: tests.length, passed, failed };
}
