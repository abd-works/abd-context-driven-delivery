/**
 * {{subEpicSlug}}.base.ts — Scenario vocabulary and test data constants.
 *
 * Abstract base: tier helpers (server, client, e2e) extend this class
 * and implement the abstract seed/cleanup methods for their tier.
 */

export abstract class {{SubEpicName}}BaseHelper {
  protected abstract seed(): Promise<void>;
  abstract cleanup(): Promise<void>;

  // Given steps — shared across all tiers
  // When steps — shared across all tiers
  // Then steps — shared across all tiers
}
