// test/{{domain}}/{{domain}}_test.ts — shared behaviour test base
import { describe, it, expect, beforeEach } from 'vitest';
import type { I{{Domain}} } from '../../src/{{domain}}/{{domain}}.js';

/**
 * Shared test base (Template Method pattern).
 * All tiers (domain, server domain, server view) run registerTests().
 * Each tier overrides createEntity() and optionally assertState() to add
 * tier-specific assertions (persistence reload, postMessage, DOM state).
 */
export abstract class {{Domain}}Test {
  protected abstract createEntity(): I{{Domain}};

  protected assertState(entity: I{{Domain}}, expected: unknown): void {
    // TODO: default assertion — adapt to your domain's state shape
    // expect(entity.total).toBe(expected);
  }

  registerTests(): void {
    describe('Given a new {{domain}}', () => {
      let entity: I{{Domain}};
      beforeEach(() => { entity = this.createEntity(); });

      // TODO: add scenarios that match specification-by-example.md
      // it('starts at zero', () => this.assertState(entity, 0));
      // it('counts by integer', () => { entity.count(3); this.assertState(entity, 3); });
      // it('resets to zero', () => { entity.count(5); entity.reset(); this.assertState(entity, 0); });
    });
  }
}
