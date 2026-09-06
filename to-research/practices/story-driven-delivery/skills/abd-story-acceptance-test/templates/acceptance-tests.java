/**
 * ## Instructions (for skill maintainers — do NOT paste this block into project test files)
 *
 * This template defines the required structure for acceptance test files produced by the
 * abd-story-acceptance-test skill using JUnit 5 (Jupiter).
 * When writing test files for a project, omit this Instructions block and emit only the
 * sections below.
 *
 * ### Inputs
 * Work from whatever behavioral context is available:
 * - Spec-by-example scenarios (ideal) — encode Given/When/Then steps directly.
 * - Acceptance criteria (WHEN/THEN) — convert THEN to assertions, derive Given from preconditions.
 * - Stories + notes — identify normal, edge, and failure behaviors; make them concrete in tests.
 * - Unstructured context — extract observable behaviors, name them, then encode as tests.
 *
 * ### Layout
 * 1. Package declaration    — matches project source tree.
 * 2. Imports                — JUnit 5, then third-party, then local; all at top.
 * 3. @DisplayName           — human-readable label on the class (behavior cluster name from source).
 * 4. HELPER METHODS         — private static methods for setup/action/assertion (each under 20 lines).
 * 5. @BeforeEach / @AfterEach — shared setup / teardown for the class.
 * 6. @Test METHODS          — one per scenario or condition.
 *    @DisplayName on each @Test carries the scenario outcome in plain English.
 *    Every method uses // Given / // When / // Then comments and calls helper methods.
 *
 * ### Naming
 * | source level        | test artifact     | example                                    |
 * |---------------------|-------------------|--------------------------------------------|
 * | Area / flow / group | File name         | {AreaPascalCase}Test.java                  |
 * | Behavior / story    | @DisplayName(class)| "Place Order"                              |
 * | Scenario / condition| @DisplayName(method)| "order is confirmed for available items"  |
 * | Scenario / condition| Method name        | orderIsConfirmedForAvailableItems()        |
 */

package {com.example.domain.area};

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
// import {com.example.domain.DomainEntity};

// =============================================================================
// {Area Name} Tests
//
// Behaviors covered:
// - {Story / Behavior Name 1}
// - {Story / Behavior Name 2}
// =============================================================================

@DisplayName("{Area Name}")
class {AreaName}Test {

    // =========================================================================
    // HELPER METHODS -- reusable operations (each under 20 lines)
    // =========================================================================

    private static {DomainEntity} create{DomainEntity}(String name) {
        // Helper: Create domain entity with given name
        return new {DomainEntity}(name);
    }

    private static void verify{DomainState}({DomainEntity} entity, {ExpectedType} expected) {
        // Helper: Verify entity is in expected state
        assertEquals(expected, entity.get{ObservableProperty}());
    }

    // =========================================================================
    // STORY: {Story Name 1}
    // =========================================================================

    @Nested
    @DisplayName("{Story Name 1}")
    class {StoryName1}Tests {

        private {DomainEntity} {entity};

        @BeforeEach
        void setUp() {
            {entity} = create{DomainEntity}("{name}");
        }

        @AfterEach
        void tearDown() {
            // cleanup if needed
        }

        @Test
        @DisplayName("{outcome of scenario in plain English}")
        void {scenarioNameCamelCase}() {
            // SCENARIO: {Scenario Name}
            // GIVEN: {precondition}
            // WHEN: {action}
            // THEN: {observable outcome}

            // Given
            {DomainEntity} {setup} = create{DomainEntity}("{arg}");

            // When
            {ResultType} result = {setup}.{domainOperation}();

            // Then
            verify{DomainState}({setup}, {expectedValue});
        }

        @Test
        @DisplayName("throws {ExceptionName} when {edge condition}")
        void throws{ExceptionName}When{EdgeCondition}() {
            // SCENARIO: {Edge Case Scenario Name}
            // GIVEN: {edge condition}
            // WHEN: {action}
            // THEN: {failure or edge outcome}

            // Given
            {DomainEntity} {entity} = create{DomainEntity}With{EdgeCondition}();

            // When / Then
            assertThrows(
                {ExpectedException}.class,
                () -> {entity}.{domainOperation}()
            );
        }
    }

    // =========================================================================
    // STORY: {Story Name 2}
    // =========================================================================

    @Nested
    @DisplayName("{Story Name 2}")
    class {StoryName2}Tests {

        @Test
        @DisplayName("{outcome of scenario in plain English}")
        void {scenarioNameCamelCase}() {
            // SCENARIO: {Scenario Name}
            // GIVEN: {precondition}
            // WHEN: {action}
            // THEN: {observable outcome}

            // Given
            {DomainEntity} {entity} = create{DomainEntity}("{arg}");

            // When
            {ResultType} result = {entity}.{domainOperation}();

            // Then
            assertEquals({expectedValue}, result);
        }
    }
}
