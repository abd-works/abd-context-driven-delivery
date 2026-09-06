---
scanner: test_structure_scanner.py
---

# Rule: Test Each Tier Independently with a Shared Behaviour Base

Tests are organised by domain root, not by tier. Each domain root has a `test/<domain>/` folder. Tier variation is expressed through a **shared test base class** that defines the behaviour contract, with each tier providing its own `createCounter()` factory.

This pattern means the persistence guarantee (state survives reload) and the view guarantee (postMessage is called after mutation) are verified by the same behaviour suite, not by separate tests that can drift apart.

## DO

- Create `test/<domain>/<domain>_test.ts` as the shared test base class with `registerTests()`.
- Have each tier create its own `describe` block and subclass that overrides `createCounter()`.
- Override `assertTotal()` in each tier to add tier-specific assertions (persistence reload, postMessage, DOM state).
- Use `vitest` as the test runner (`describe`, `beforeEach`, `expect`).
- Mock the VS Code API with a `test/__mocks__/vscode.ts` that the view tests import.

```typescript
// test/counter/counter_test.ts — shared behaviour base
export abstract class CounterTest {
  protected abstract createCounter(): ICounter;

  protected assertTotal(counter: ICounter, expected: number): void {
    expect(counter.total).toBe(expected);
  }

  registerTests(): void {
    let counter: ICounter;
    beforeEach(() => { counter = this.createCounter(); });

    it('starts at zero', () => this.assertTotal(counter, 0));
    it('counts by integer', () => { counter.count(3); this.assertTotal(counter, 3); });
    it('resets to zero', () => { counter.count(5); counter.reset(); this.assertTotal(counter, 0); });
  }
}
```

```typescript
// test/counter/counter.test.ts — domain + server domain tier variations
describe('Counter', () => {
  class DomainCounterTest extends CounterTest {
    protected createCounter(): ICounter { return new Counter(); }
  }
  new DomainCounterTest().registerTests();
});

describe('CounterServer', () => {
  class ServerCounterTest extends CounterTest {
    protected createCounter(): ICounter { return new CounterServer(filePath); }

    protected override assertTotal(counter: ICounter, expected: number): void {
      super.assertTotal(counter, expected);
      const reloaded = new CounterServer(filePath);
      expect(reloaded.total).toBe(expected);   // persistence guarantee
    }
  }
  new ServerCounterTest().registerTests();
});
```

## DON'T

- Don't write separate test suites for domain and server that test overlapping behaviour independently — they will drift.
- Don't put view tests in the same file as domain tests — view tests require the VS Code mock and have different setup.
- Don't skip the persistence reload assertion in server domain tests.

```typescript
// WRONG — separate suites duplicating behaviour tests
describe('Counter', () => {
  it('counts', () => { ... });        // WRONG: duplicated in CounterServer tests
  it('resets', () => { ... });
});

describe('CounterServer', () => {
  it('counts', () => { ... });        // WRONG: same test, different instance
  it('resets', () => { ... });
  // Missing: persistence reload check
});
```
