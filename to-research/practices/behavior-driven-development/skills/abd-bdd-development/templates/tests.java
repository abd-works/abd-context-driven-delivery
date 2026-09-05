// =============================================================================
// BDD Development Template — JUnit 5 / Java Test Implementation
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {DomainEntity} with the class or module under test.
//   2. Import only the entity under test and its dependency types.
//   3. Add a private static factory for each shared test-data object.
//   4. Use @BeforeEach for shared object setup when 3+ sibling @Test methods need it.
//   5. Each @Test body uses // Arrange / // Act / // Assert comments.
//   6. One assertion per behavior (or a tight group describing the same outcome).
//   7. Replace `// BDD: SIGNATURE` markers — do not leave any in the final file.
//   8. Delete this instruction block before committing the file.
// =============================================================================

package {com.example.domain.area};

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

// import {com.example.domain.DomainEntity};

@DisplayName("{DomainEntity}")
class {DomainEntity}Spec {

    // ------------------------------------------------------------------------
    // Factories — minimal valid test data (populate only fields tests assert on)
    // ------------------------------------------------------------------------

    private static {RelatedType} default{RelatedType}() {
        return new {RelatedType}(/* populate only fields tests assert on */);
    }

    // ------------------------------------------------------------------------

    @Nested
    @DisplayName("that has been created")
    class ThatHasBeenCreated {

        @Test
        @DisplayName("should have {initial property} assigned")
        void shouldHave{InitialPropertyPascalCase}Assigned() {
            // Arrange
            {RelatedType} input = default{RelatedType}();

            // Act
            {DomainEntity} entity = new {DomainEntity}(input);

            // Assert
            assertEquals({expectedValue}, entity.get{PropertyPascalCase}());
        }
    }

    @Nested
    @DisplayName("that is {active state}")
    class ThatIs{ActiveStatePascalCase} {

        private {DomainEntity} entity;

        @BeforeEach
        void setUp() {
            entity = new {DomainEntity}(default{RelatedType}());
        }

        @Test
        @DisplayName("should {behavior description}")
        void should{BehaviorDescriptionPascalCase}() {
            // Act
            entity.{action}({input});

            // Assert
            assertEquals({expectedValue}, entity.get{PropertyPascalCase}());
        }

        @Test
        @DisplayName("should {second behavior}")
        void should{SecondBehaviorPascalCase}() {
            // Arrange
            {LocalSetupType} {localSetup} = {value};

            // Act
            entity.{action}({localSetup});

            // Assert
            assertEquals({expectedValue}, entity.get{PropertyPascalCase}());
        }
    }
}
