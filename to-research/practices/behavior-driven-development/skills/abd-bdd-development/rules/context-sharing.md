---
name: context-sharing
---

# Rule: Context Sharing

Shared object setup belongs in `beforeEach`; shared test data belongs in factory functions. Never duplicate arrangement code across sibling tests — three or more sibling tests with the same setup is the trigger to extract.

## DO

- Use `beforeEach` to instantiate the object under test once per context block.
- Use factory functions (`defaultStats()`, `makeVoucher()`) for test data objects with sensible defaults.
- Extract helpers to a `{domain-name}-helper.ts` file when they are reused across describe blocks or test files.

```typescript
describe('Character that is in combat', () => {
  let character: Character;

  beforeEach(() => {
    character = new Character({ name: 'Test', stats: defaultStats() });
  });

  it('should track current wounds', () => {
    character.applyDamage(2);
    expect(character.wounds).toBe(2);
  });

  it('should apply damage from attacks', () => {
    character.applyDamage(5);
    expect(character.wounds).toBe(5);
  });
});
```

## DO NOT

- Duplicate the same `new Object(...)` call in every `it` body within the same describe block.
- Hard-code the same literal values across multiple tests — use a factory.
- Share mutable state between tests without a `beforeEach` reset.

```typescript
// WRONG — duplicated arrangement
it('should track current wounds', () => {
  const character = new Character({ name: 'Test', stats: defaultStats() }); // duplicate
  character.applyDamage(2);
  expect(character.wounds).toBe(2);
});

it('should apply damage from attacks', () => {
  const character = new Character({ name: 'Test', stats: defaultStats() }); // duplicate
  character.applyDamage(5);
  expect(character.wounds).toBe(5);
});
```

**Example (pass):**
No describe block contains three or more `it` bodies that each instantiate the same object independently. Shared setup is in `beforeEach`. PASS.

**Example (fail):**
Same constructor call appears in 3+ sibling `it` blocks with no `beforeEach`. FAIL — extract to `beforeEach`.
