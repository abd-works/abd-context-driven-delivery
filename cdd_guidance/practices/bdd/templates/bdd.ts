/**
 * Conceptual BDD reference (TypeScript / Vitest).
 * Refer to practices/language-tools.md for tool recommendations.
 *
 * BEHAVIOR (SIGNATURE) — every `it` body is exactly `// BDD: SIGNATURE`.
 *
 * describe('{DomainEntity}', () => {
 *   describe('that has been created', () => {
 *     it('should have {initial property} assigned', () => {
 *       // BDD: SIGNATURE
 *     });
 *   });
 * });
 */
import { describe, it } from "vitest";

describe("{DomainEntity}", () => {
  describe("that has been created", () => {
    it("should have {initial property} assigned", () => {
      // BDD: SIGNATURE
    });
  });
});
