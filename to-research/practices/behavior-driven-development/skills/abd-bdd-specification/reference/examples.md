# Examples — BDD Specification Signatures

## Input scaffold → Output signatures

**Input scaffold (`character-hierarchy.txt`):**
```
Character
  that has been created
    should have initial stats assigned
    should have zero starting wounds
  that is in combat
    should track current wounds
    should apply damage from attacks
  Attack
    that has targeted an enemy
      should calculate hit chance using character stats
      should consume one action from the active turn
    that has missed
      should deal no damage
      should still consume one action
  that has been defeated
    should be removed from the initiative order
```

---

### Jest/TypeScript output (`character.test.ts`)

```typescript
describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // BDD: SIGNATURE
    });
    it('should have zero starting wounds', () => {
      // BDD: SIGNATURE
    });
  });

  describe('that is in combat', () => {
    it('should track current wounds', () => {
      // BDD: SIGNATURE
    });
    it('should apply damage from attacks', () => {
      // BDD: SIGNATURE
    });
  });

  describe('Attack', () => {
    describe('that has targeted an enemy', () => {
      it('should calculate hit chance using character stats', () => {
        // BDD: SIGNATURE
      });
      it('should consume one action from the active turn', () => {
        // BDD: SIGNATURE
      });
    });

    describe('that has missed', () => {
      it('should deal no damage', () => {
        // BDD: SIGNATURE
      });
      it('should still consume one action', () => {
        // BDD: SIGNATURE
      });
    });
  });

  describe('that has been defeated', () => {
    it('should be removed from the initiative order', () => {
      // BDD: SIGNATURE
    });
  });
});
```

---

### Mamba/Python output (`character_spec.py`)

```python
from mamba import description, context, it

with description('Character'):
    with context('that has been created'):
        with it('should have initial stats assigned'):
            # BDD: SIGNATURE
        with it('should have zero starting wounds'):
            # BDD: SIGNATURE

    with context('that is in combat'):
        with it('should track current wounds'):
            # BDD: SIGNATURE
        with it('should apply damage from attacks'):
            # BDD: SIGNATURE

    with description('Attack'):
        with context('that has targeted an enemy'):
            with it('should calculate hit chance using character stats'):
                # BDD: SIGNATURE
            with it('should consume one action from the active turn'):
                # BDD: SIGNATURE

        with context('that has missed'):
            with it('should deal no damage'):
                # BDD: SIGNATURE
            with it('should still consume one action'):
                # BDD: SIGNATURE

    with context('that has been defeated'):
        with it('should be removed from the initiative order'):
            # BDD: SIGNATURE
```

---

## What to notice

- Scaffold has 9 `should` lines → signature has 9 `it` blocks. Count matches exactly.
- 4 nesting levels in scaffold (Character → state → Attack → state → behavior) → 4 levels in code.
- Every body contains `// BDD: SIGNATURE` (Jest) or `# BDD: SIGNATURE` (Mamba) and nothing else.
- No imports, no assertions, no mocks, no `beforeEach`.
- `it('should …')` matches the scaffold text verbatim — no paraphrasing.

## Batch processing for large scaffolds

When a scaffold has more than ~18 describe blocks, process in batches:

1. First batch: top-level concept and its first 2-3 state blocks (~18 describes).
2. Subsequent batches: remaining state blocks and sub-concepts.
3. Confirm after each batch that the hierarchy count matches the scaffold for that slice.
