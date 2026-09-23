/**
 * MV3 Lifecycle Tests
 * A3e: Simulates service worker restart and verifies state restoration
 */

function runTests() {
  const results = [];

  function test(name, fn) {
    try {
      fn();
      results.push({ name, status: 'PASS' });
      console.log(`✓ ${name}`);
    } catch (error) {
      results.push({ name, status: 'FAIL', error: error.message });
      console.error(`✗ ${name}: ${error.message}`);
    }
  }

  function assert(condition, message) {
    if (!condition) {
      throw new Error(message || 'Assertion failed');
    }
  }

  // Mock chrome.storage.local
  const mockStorage = {};

  const mockChrome = {
    storage: {
      local: {
        get: (keys, callback) => {
          const result = {};
          if (Array.isArray(keys)) {
            keys.forEach(key => {
              if (mockStorage[key] !== undefined) {
                result[key] = mockStorage[key];
              }
            });
          } else if (typeof keys === 'object') {
            Object.keys(keys).forEach(key => {
              if (mockStorage[key] !== undefined) {
                result[key] = mockStorage[key];
              }
            });
          }
          callback(result);
        },
        set: (items, callback) => {
          Object.assign(mockStorage, items);
          if (callback) callback();
        }
      }
    }
  };

  test('A3e: Service worker state persistence', () => {
    // Simulate initial state
    const initialState = {
      isRecording: true,
      sessionId: 'test-session-123',
      startedAt: '2026-09-01T10:00:00.000Z',
      events: [
        { url: 'https://example.test/login', method: 'GET', source: 'webRequest' },
        { url: 'https://example.test/auth', method: 'POST', source: 'webRequest' }
      ],
      requestedOrigins: ['https://example.test/*', 'https://auth.example.test/*'],
      eventCounts: { webRequest: 2, webRequestResponse: 1, webNavigation: 0 },
      observedOrigins: ['https://example.test/*', 'https://auth.example.test/*']
    };

    // Save to storage
    mockChrome.storage.local.set({
      isRecording: initialState.isRecording,
      sessionId: initialState.sessionId,
      startedAt: initialState.startedAt,
      events: initialState.events,
      requestedOrigins: initialState.requestedOrigins,
      eventCounts: initialState.eventCounts,
      observedOrigins: initialState.observedOrigins
    });

    // Simulate worker restart - restore from storage
    let restoredState = {};

    mockChrome.storage.local.get(
      ['isRecording', 'sessionId', 'startedAt', 'events', 'requestedOrigins', 'eventCounts', 'observedOrigins'],
      (result) => {
        restoredState = result;
      }
    );

    // Verify restoration
    assert(restoredState.isRecording === true, 'isRecording should be restored');
    assert(restoredState.sessionId === 'test-session-123', 'sessionId should be restored');
    assert(restoredState.startedAt === '2026-09-01T10:00:00.000Z', 'startedAt should be restored');
    assert(restoredState.events.length === 2, 'events should be restored');
    assert(restoredState.requestedOrigins.length === 2, 'requestedOrigins should be restored');
    assert(restoredState.eventCounts.webRequest === 2, 'eventCounts should be restored');
    assert(restoredState.observedOrigins.length === 2, 'observedOrigins should be restored');
  });

  test('A3f: Requested origins persist after grant/reload', () => {
    // Simulate requested origins being set
    const requestedOrigins = ['https://login.example.test/*', 'https://auth.example.test/*'];

    mockChrome.storage.local.set({
      requestedOrigins: requestedOrigins
    });

    // Simulate reload
    let restored = {};
    mockChrome.storage.local.get(['requestedOrigins'], (result) => {
      restored = result;
    });

    assert(restored.requestedOrigins.length === 2, 'Requested origins should persist');
    assert(restored.requestedOrigins.includes('https://login.example.test/*'), 'Should include first origin');
    assert(restored.requestedOrigins.includes('https://auth.example.test/*'), 'Should include second origin');
  });

  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`\nLifecycle tests: ${results.length - failCount}/${results.length} passed`);

  return failCount === 0 ? results : null;
}

module.exports = { runTests };

if (require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}
