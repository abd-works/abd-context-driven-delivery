// =============================================================================
// BDD Development Template — Jest/TypeScript Test Implementation
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {DomainEntity} with the class or module under test.
//   2. Import only the entity under test and its dependency types.
//   3. Add a factory function for each shared test-data object.
//   4. Use `beforeEach` for shared object setup when 3+ sibling `it` blocks need it.
//   5. Each `it` body uses Arrange / Act / Assert comments.
//   6. One assertion per behavior (or a tight group describing the same outcome).
//   7. Replace `// BDD: SIGNATURE` markers — do not leave any in the final file.
//   8. Delete this instruction block before committing the file.
// =============================================================================

import { {DomainEntity} } from '../{DomainEntity}';

// Factory — returns a minimal valid instance of {RelatedType} for tests
function default{RelatedType}(): {RelatedType} {
  return {
    // populate only fields tests assert on
  };
}

describe('{DomainEntity}', () => {
  describe('that has been created', () => {
    it('should have {initial property} assigned', () => {
      // Arrange
      const input = default{RelatedType}();

      // Act
      const entity = new {DomainEntity}(input);

      // Assert
      expect(entity.{property}).toBe({expectedValue});
    });
  });

  describe('that is {active state}', () => {
    let entity: {DomainEntity};

    beforeEach(() => {
      entity = new {DomainEntity}(default{RelatedType}());
    });

    it('should {behavior description}', () => {
      // Act
      entity.{action}({input});

      // Assert
      expect(entity.{property}).toBe({expectedValue});
    });

    it('should {second behavior}', () => {
      // Arrange
      const {localSetup} = {value};

      // Act
      entity.{action}({localSetup});

      // Assert
      expect(entity.{property}).toBe({expectedValue});
    });
  });
});
