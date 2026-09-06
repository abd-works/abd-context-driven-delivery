// =============================================================================
// BDD Signature Template — JUnit 5 / Java
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {ConceptName} with the top-level domain concept (noun).
//   2. Replace {state description} with the lifecycle state (linking-word phrase).
//   3. Replace {behavior description} with the "should ..." behavior from the scaffold.
//   4. Add @Nested classes to match every level in the scaffold hierarchy.
//   5. Every @Test body must contain exactly `// BDD: SIGNATURE` and nothing else.
//   6. The outer class carries @DisplayName for the top-level concept; every
//      @Nested class carries @DisplayName for its state/sub-concept; every
//      @Test carries @DisplayName for the "should ..." behavior.
//   7. Delete this instruction block before committing the file.
// =============================================================================

package {com.example.domain.area};

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@DisplayName("{ConceptName}")
class {ConceptName}Spec {

    @Nested
    @DisplayName("that has been {state description}")
    class ThatHasBeen{StateDescriptionPascalCase} {

        @Test
        @DisplayName("should {behavior description}")
        void should{BehaviorDescriptionPascalCase}() {
            // BDD: SIGNATURE
        }

        @Test
        @DisplayName("should {second behavior description}")
        void should{SecondBehaviorDescriptionPascalCase}() {
            // BDD: SIGNATURE
        }
    }

    @Nested
    @DisplayName("that is {active state description}")
    class ThatIs{ActiveStateDescriptionPascalCase} {

        @Test
        @DisplayName("should {behavior description}")
        void should{BehaviorDescriptionPascalCase}() {
            // BDD: SIGNATURE
        }
    }

    @Nested
    @DisplayName("{SubConceptName}")
    class {SubConceptName}Spec {

        @Nested
        @DisplayName("that has {sub-concept state}")
        class ThatHas{SubConceptStatePascalCase} {

            @Test
            @DisplayName("should {sub-concept behavior}")
            void should{SubConceptBehaviorPascalCase}() {
                // BDD: SIGNATURE
            }
        }
    }

    @Nested
    @DisplayName("that has been {completed state}")
    class ThatHasBeen{CompletedStatePascalCase} {

        @Test
        @DisplayName("should {outcome behavior}")
        void should{OutcomeBehaviorPascalCase}() {
            // BDD: SIGNATURE
        }
    }
}
