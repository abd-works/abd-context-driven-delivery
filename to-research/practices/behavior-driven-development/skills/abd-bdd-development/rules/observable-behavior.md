---
name: observable-behavior
scanner: javascript/observable_behavior_scanner.py
severity: warning
---

# Rule: Observable Behavior

Tests prove what the system does, not how it is built internally. Assertions target outputs and state changes accessible through the public API.

## DO

- Assert on return values: `expect(result.email).toBe('test@example.com')`
- Assert on state changes visible via getters or public properties: `expect(character.wounds).toBe(3)`
- Assert on side effects by checking the boundary mock: `expect(repo.save).toHaveBeenCalledWith(expectedEntity)`

```typescript
it('should apply damage to character', () => {
  const character = new Character({ wounds: 0 });
  character.applyDamage(3);
  expect(character.wounds).toBe(3); // observable through public property
});
```

## DO NOT

- Access private fields: `character._wounds`, `service._cache`.
- Spy on the object under test: `jest.spyOn(character, 'applyDamage')`.
- Assert on internal method call counts for domain logic.

```typescript
// WRONG — accessing private internal field
it('should apply damage to character', () => {
  const character = new Character({ wounds: 0 });
  character.applyDamage(3);
  expect((character as any)._wounds).toBe(3); // private field — not observable
});
```

**Example (pass):**
Every `expect()` in the test file targets a return value, a public property, or a mock at an architecture boundary. PASS.

**Example (fail):**
Any assertion accesses a private/internal property via casting or `_`-prefixed access. FAIL.
