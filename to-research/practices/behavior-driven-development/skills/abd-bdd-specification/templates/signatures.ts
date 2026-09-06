// =============================================================================
// BDD Signature Template — Jest/TypeScript
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {ConceptName} with the top-level domain concept (noun).
//   2. Replace {state description} with the lifecycle state (linking-word phrase).
//   3. Replace {behavior description} with the "should ..." behavior from the scaffold.
//   4. Add nesting levels to match every level in the scaffold hierarchy.
//   5. Every `it` body must contain exactly `// BDD: SIGNATURE` and nothing else.
//   6. Delete this instruction block before committing the file.
// =============================================================================

describe('{ConceptName}', () => {
  describe('that has been {state description}', () => {
    it('should {behavior description}', () => {
      // BDD: SIGNATURE
    });
    it('should {second behavior description}', () => {
      // BDD: SIGNATURE
    });
  });

  describe('that is {active state description}', () => {
    it('should {behavior description}', () => {
      // BDD: SIGNATURE
    });
  });

  describe('{SubConceptName}', () => {
    describe('that has {sub-concept state}', () => {
      it('should {sub-concept behavior}', () => {
        // BDD: SIGNATURE
      });
    });
  });

  describe('that has been {completed state}', () => {
    it('should {outcome behavior}', () => {
      // BDD: SIGNATURE
    });
  });
});
