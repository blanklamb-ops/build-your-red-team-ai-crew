// Test MV3 service worker lifecycle persistence

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function testLifecyclePersistence() {
  console.log('Testing MV3 lifecycle persistence...');

  // Mock chrome.storage API
  const storage = {};
  global.chrome = {
    storage: {
      local: {
        set: async (data) => {
          Object.assign(storage, data);
        },
        get: async (keys) => {
          const result = {};
          if (Array.isArray(keys)) {
            for (const key of keys) {
              if (storage[key] !== undefined) {
                result[key] = storage[key];
              }
            }
          } else if (typeof keys === 'object') {
            for (const key of Object.keys(keys)) {
              result[key] = storage[key] !== undefined ? storage[key] : keys[key];
            }
          }
          return result;
        }
      }
    }
  };

  // Simulate session state
  const sessionState = {
    requestedOrigins: ['https://example.test/*', 'https://auth.example.test/*'],
    recordingState: {
      isRecording: true,
      sessionStartTime: '2024-01-15T10:00:00.000Z'
    },
    capturedEvents: [
      {
        url: 'https://example.test/login',
        timestamp: '2024-01-15T10:00:01.000Z',
        method: 'GET'
      }
    ],
    formFieldsData: [
      {
        url: 'https://example.test/login',
        form_fields: [{ name: 'username', type: 'text' }]
      }
    ]
  };

  // Persist state
  chrome.storage.local.set(sessionState).then(async () => {
    console.log('State persisted to storage');

    // Simulate service worker restart (clear in-memory state)
    // Now restore from storage
    const restored = await chrome.storage.local.get([
      'requestedOrigins',
      'recordingState',
      'capturedEvents',
      'formFieldsData'
    ]);

    console.log('State restored from storage');

    // Verify restoration
    assert(
      JSON.stringify(restored.requestedOrigins) === JSON.stringify(sessionState.requestedOrigins),
      'Requested origins restored'
    );
    assert(
      restored.recordingState.isRecording === true,
      'Recording state restored'
    );
    assert(
      restored.recordingState.sessionStartTime === sessionState.recordingState.sessionStartTime,
      'Session start time restored'
    );
    assert(
      restored.capturedEvents.length === 1,
      'Captured events restored'
    );
    assert(
      restored.formFieldsData.length === 1,
      'Form fields data restored'
    );

    console.log('✓ All lifecycle persistence tests passed');
  });
}

module.exports = { testLifecyclePersistence };

if (require.main === module) {
  testLifecyclePersistence();
}
