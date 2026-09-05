---
name: no-implementation
---

# Rule: No Implementation in Signatures

The signature phase locks structure, not logic. No assertions, no mocks, no production-code imports, no helper calls, no `beforeEach` blocks belong in a signature file.

## DO

- Import only the test framework if the project requires explicit imports.
- Write only `describe`, `it`, and the `// BDD: SIGNATURE` marker.

## DO NOT

- Import production code (`import { Character } from '../Character'`).
- Import mock utilities (`jest.mock`, `vi.mock`).
- Write `expect()` assertions.
- Set up `beforeEach()`, `afterEach()`, or factory functions.
- Call helper functions.

```typescript
// WRONG — production import in signature phase
import { Character } from '../Character';

describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      const c = new Character();      // WRONG — implementation
      expect(c.stats).toBeDefined();  // WRONG — assertion
    });
  });
});
```

```typescript
// CORRECT — pure signature
describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // BDD: SIGNATURE
    });
  });
});
```

**Example (pass):**
Signature file has zero `import` statements for production code, zero `expect` calls, zero `beforeEach` blocks, zero mock calls. PASS.

**Example (fail):**
Any assertion, mock setup, production import, or helper call present in the file. FAIL.
