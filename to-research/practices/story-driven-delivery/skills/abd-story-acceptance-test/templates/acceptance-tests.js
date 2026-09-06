/**
 * ## Instructions (for skill maintainers — do NOT paste this block into project test files)
 *
 * This template defines the required structure for acceptance test files produced by the
 * abd-story-acceptance-test skill using Node.js built-in test runner
 * (node:test + node:assert/strict).  When writing test files for a project, omit this
 * Instructions block and emit only the sections below.
 *
 * ### Inputs
 * Work from whatever behavioral context is available:
 * - Spec-by-example scenarios (ideal) — encode Given/When/Then steps directly.
 * - Acceptance criteria (WHEN/THEN) — convert THEN to assertions, derive Given from preconditions.
 * - Stories + notes — identify normal, edge, and failure behaviors; make them concrete in tests.
 * - Unstructured context — extract observable behaviors, name them, then encode as tests.
 *
 * ### Layout
 * 1. File header comment — one-line summary + list of behaviors covered in this file.
 * 2. Imports             — node:test, node:assert, then third-party, then local; all at top.
 * 3. HELPER FUNCTIONS    — reusable setup/action/assertion functions (each under 20 lines).
 * 4. SETUP / TEARDOWN    — before() / after() at describe-block level for shared state.
 * 5. DESCRIBE BLOCKS     — one describe() per behavior cluster (story, flow, feature area).
 *    Named after the exact behavior name from source context.
 *    Each it() maps to one scenario or condition.
 *    Every it() uses // Given / // When / // Then comments and calls helper functions.
 *
 * ### Naming
 * | source level        | test artifact    | example                              |
 * |---------------------|------------------|--------------------------------------|
 * | Area / flow / group | File name        | <area-kebab-case>.test.js            |
 * | Behavior / story    | describe() label | 'Place Order'                        |
 * | Scenario / condition| it() label       | 'order is confirmed for available items' |
 */

// =============================================================================
// {Area Name} Tests
//
// Behaviors covered:
// - {Story / Behavior Name 1}
// - {Story / Behavior Name 2}
// =============================================================================

import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
// import { DomainEntity } from '../src/{domain-entity}.js';

// =============================================================================
// HELPER FUNCTIONS -- reusable operations (each under 20 lines)
// =============================================================================

/**
 * Helper: Create {domain entity} with {description}.
 * @param {string} name
 * @param {object} options
 * @returns {DomainEntity}
 */
function create{DomainEntity}(name, options = {}) {
  // ... setup ...
  return new {DomainEntity}(name, options);
}

/**
 * Helper: Verify {domain entity} is in {expected state}.
 * @param {DomainEntity} entity
 * @param {*} expected
 */
function verify{DomainState}(entity, expected) {
  assert.equal(entity.{observableProperty}, expected);
}

// =============================================================================
// STORY: {Story Name 1}
// =============================================================================

describe('{Story Name 1}', () => {
  let {sharedState};

  before(() => {
    // Shared setup for all scenarios in this story
    {sharedState} = create{DomainEntity}('{name}');
  });

  after(() => {
    // Cleanup if needed
  });

  it('{outcome of scenario in plain English}', () => {
    // SCENARIO: {Scenario Name}
    // GIVEN: {precondition}
    // WHEN: {action}
    // THEN: {observable outcome}

    // Given
    const {entity} = create{DomainEntity}('{arg}');

    // When
    const result = {entity}.{domainOperation}();

    // Then
    verify{DomainState}({entity}, {expectedValue});
  });

  it('throws when {edge condition}', () => {
    // SCENARIO: {Edge Case Scenario Name}
    // GIVEN: {edge condition}
    // WHEN: {action}
    // THEN: {failure or edge outcome}

    // Given
    const {entity} = create{DomainEntity}With{EdgeCondition}();

    // When / Then
    assert.throws(
      () => {entity}.{domainOperation}(),
      { name: '{ExpectedErrorName}' }
    );
  });
});

// =============================================================================
// STORY: {Story Name 2}
// =============================================================================

describe('{Story Name 2}', () => {
  it('{outcome of scenario in plain English}', () => {
    // SCENARIO: {Scenario Name}
    // GIVEN: {precondition}
    // WHEN: {action}
    // THEN: {observable outcome}

    // Given
    const {entity} = create{DomainEntity}('{arg}');

    // When
    const result = {entity}.{domainOperation}();

    // Then
    assert.deepEqual(result, {expectedValue});
  });
});
