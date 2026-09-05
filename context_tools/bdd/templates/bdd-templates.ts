// Conceptual BDD Reference (TypeScript/Jest style)
// Refer to context_tools/language-tools.md for tool recommendations.
// =============================================================================

import { {DomainEntity} } from '../{DomainEntity}';

describe('{DomainEntity}', () => {
  describe('that has been created', () => {
    it('should have {initial property} assigned', () => {
      // Arrange / Act
      const entity = new {DomainEntity}(defaultData());

      // Assert
      expect(entity.property).toBe(expectedValue);
    });
  });
});
