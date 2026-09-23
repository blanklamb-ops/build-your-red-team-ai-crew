// Test origin normalization (production code)

const { normalizeOrigin } = require('../extension/shared.js');

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function testNormalization() {
  console.log('Testing origin normalization...');

  // Idempotent: already canonical
  assert(
    normalizeOrigin('https://example.test/*') === 'https://example.test/*',
    'Idempotent: canonical pattern unchanged'
  );

  // Bare origin
  assert(
    normalizeOrigin('https://example.test') === 'https://example.test/*',
    'Bare origin gets /* suffix'
  );

  // Full URL
  assert(
    normalizeOrigin('https://example.test/path/to/page') === 'https://example.test/*',
    'Full URL extracts origin'
  );

  // Host-only
  assert(
    normalizeOrigin('example.test') === 'https://example.test/*',
    'Host-only gets https:// prefix'
  );

  // HTTP protocol
  assert(
    normalizeOrigin('http://example.test') === 'http://example.test/*',
    'HTTP protocol preserved'
  );

  // Double normalization (idempotent)
  const once = normalizeOrigin('https://example.test/some/path');
  const twice = normalizeOrigin(once);
  assert(once === twice, 'Normalization is idempotent');

  // Reject userinfo
  try {
    normalizeOrigin('https://user:pass@example.test');
    throw new Error('Should have rejected userinfo');
  } catch (e) {
    assert(e.message.includes('userinfo'), 'Rejects userinfo');
  }

  // Reject non-HTTP(S)
  try {
    normalizeOrigin('ftp://example.test');
    throw new Error('Should have rejected FTP');
  } catch (e) {
    assert(e.message.includes('Non-HTTP'), 'Rejects non-HTTP(S) schemes');
  }

  console.log('✓ All normalization tests passed');
}

module.exports = { testNormalization };

if (require.main === module) {
  testNormalization();
}
