/**
 * Browser-safe assert helpers for story Then steps (Play soft-fail + node tests).
 * Avoid importing node:assert from story files that must load in the browser.
 */

function fail(message) {
  throw new Error(message);
}

export const assert = {
  ok(value, message = "expected value to be truthy") {
    if (!value) fail(message);
  },
  equal(actual, expected, message) {
    if (actual !== expected) {
      fail(message || `expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
  },
  deepEqual(actual, expected, message) {
    const a = JSON.stringify(actual);
    const b = JSON.stringify(expected);
    if (a !== b) {
      fail(message || `expected ${b}, got ${a}`);
    }
  },
};
