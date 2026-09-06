---
name: framework-syntax
---

# Rule: Framework Syntax Consistency

Use the correct syntax for the confirmed framework throughout the file. Do not mix Jest and Mamba constructs.

## DO

**Jest/TypeScript:**
- `describe('…', () => { … })`
- `it('should …', () => { … })`
- Nested describes inside the parent describe callback

**Mamba/Python:**
- `with description('…'):`
- `with context('…'):` for state blocks
- `with it('should …'):`
- Python indentation for nesting (no closing braces)

## DO NOT

- Mix `describe()` with `with description()` in the same file.
- Use `test()` instead of `it()` in BDD signature files (BDD convention is `it` for "it should").
- Write `describe` without a callback in Jest.
- Use Python indentation style in a TypeScript file.

```typescript
// WRONG — using `test` instead of `it` (breaks BDD convention)
describe('Character', () => {
  test('should have initial stats', () => {
    // BDD: SIGNATURE
  });
});

// CORRECT
describe('Character', () => {
  it('should have initial stats', () => {
    // BDD: SIGNATURE
  });
});
```

**Example (pass):**
Entire file uses `describe`/`it` (Jest) or `with description`/`with context`/`with it` (Mamba) consistently. PASS.

**Example (fail):**
File mixes `describe()` and `with description()`, or uses `test()` for behavior blocks. FAIL.
