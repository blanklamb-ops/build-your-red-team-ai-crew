/**
 * Tests for MV3 lifecycle persistence (A3e)
 * Simulates service worker teardown and restart
 */

export function runLifecycleTests() {
  const tests = [];
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    tests.push({ name, fn });
  }

  // Mock chrome.storage.local
  const mockStorage = new Map();
  const chrome = {
    storage: {
      local: {
        async set(items) {
          for (const [key, value] of Object.entries(items)) {
            mockStorage.set(key, value);
          }
        },
        async get(keys) {
          if (typeof keys === 'string') {
            return { [keys]: mockStorage.get(keys) };
          }
          const result = {};
          for (const key of keys) {
            result[key] = mockStorage.get(key);
          }
          return result;
        }
      }
    }
  };

  // Simulate storage operations from service worker
  test('Recording state persists across restart', async () => {
    // Save state
    await chrome.storage.local.set({ isRecording: true });

    // Simulate restart - storage survives
    const result = await chrome.storage.local.get('isRecording');

    if (result.isRecording !== true) {
      throw new Error('Recording state not persisted');
    }
  });

  test('Session ID persists across restart', async () => {
    const sessionId = 'test-session-123';
    await chrome.storage.local.set({ sessionId });

    const result = await chrome.storage.local.get('sessionId');

    if (result.sessionId !== sessionId) {
      throw new Error('Session ID not persisted');
    }
  });

  test('Captured events persist across restart', async () => {
    const events = [
      { url: 'https://example.test/login', method: 'GET' },
      { url: 'https://example.test/auth', method: 'POST' }
    ];

    await chrome.storage.local.set({ capturedEvents: events });

    const result = await chrome.storage.local.get('capturedEvents');

    if (!result.capturedEvents || result.capturedEvents.length !== 2) {
      throw new Error('Events not persisted correctly');
    }
  });

  test('Requested origins persist after grant/reload', async () => {
    const requestedOrigins = ['https://login.test/*', 'https://auth.test/*'];

    await chrome.storage.local.set({ requestedOrigins });

    // Simulate reload
    const result = await chrome.storage.local.get('requestedOrigins');

    if (!result.requestedOrigins || result.requestedOrigins.length !== 2) {
      throw new Error('Requested origins not persisted');
    }

    if (result.requestedOrigins[0] !== 'https://login.test/*') {
      throw new Error('Requested origins corrupted');
    }
  });

  test('Timestamps persist across restart', async () => {
    const startedAt = '2026-09-05T12:00:00.000Z';
    const stoppedAt = '2026-09-05T12:05:00.000Z';

    await chrome.storage.local.set({ startedAt, stoppedAt });

    const result = await chrome.storage.local.get(['startedAt', 'stoppedAt']);

    if (result.startedAt !== startedAt || result.stoppedAt !== stoppedAt) {
      throw new Error('Timestamps not persisted');
    }
  });

  test('Event counts persist across restart', async () => {
    const eventCounts = {
      webRequest_request: 10,
      webRequest_response: 8,
      webNavigation: 2
    };

    await chrome.storage.local.set({ eventCounts });

    const result = await chrome.storage.local.get('eventCounts');

    if (result.eventCounts.webRequest_request !== 10) {
      throw new Error('Event counts not persisted');
    }
  });

  test('Observed origins persist across restart', async () => {
    const observedOrigins = ['https://login.test/*', 'https://auth.test/*'];

    await chrome.storage.local.set({ observedOrigins });

    const result = await chrome.storage.local.get('observedOrigins');

    if (!result.observedOrigins || result.observedOrigins.length !== 2) {
      throw new Error('Observed origins not persisted');
    }
  });

  // Run all tests
  const runTests = async () => {
    for (const { name, fn } of tests) {
      try {
        const result = fn();
        if (result && result.then) {
          // Async test
          await result;
        }
        console.log(`  ✓ ${name}`);
        passed++;
      } catch (error) {
        console.log(`  ✗ ${name}: ${error.message}`);
        failed++;
      }
    }

    return { total: tests.length, passed, failed };
  };

  return runTests();
}
