/**
 * Shared behaviors for BDD (Vitest and Playwright). The TypeScript form of `shared_examples` and
 * `it_behaves_like` in the BDD practice: one describe tree, run on every tier through that tier's driver.
 * The blocks keep the names `describe` and `it`, so the BDD practice reads a shared behavior as it reads any spec.
 *
 * ```
 * file: test-utils/behavior-test/behavior-test.ts
 * ```
 */

export type Block = (name: string, body: () => void | Promise<void>) => void

type Matchers = { toEqual: (expected: unknown) => unknown; toContain: (expected: unknown) => unknown }

export type Tier<Driver> = {
  describe: (name: string, body: () => void) => void
  it: Block
  before: (body: () => void | Promise<void>) => void
  expect: (actual: unknown) => Matchers
  driver: () => Driver
}

export type SharedBehavior<Driver> = (tier: Tier<Driver>) => void

export function shareBehavior<Driver>(behavior: SharedBehavior<Driver>): SharedBehavior<Driver> {
  return behavior
}

export function itBehavesLike<Driver>(behavior: SharedBehavior<Driver>, tier: Tier<Driver>): void {
  behavior(tier)
}
