# Examples — BDD fidelities

## Behavior hierarchy input (prerequisite)

Approved plain-English hierarchy (`character-behavior.md`) used as input to **behavior** fidelity:

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

## Behavior fidelity — signatures

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

### What to notice

- Behavior hierarchy has 9 `should` lines → signature has 9 `it` blocks. Count matches exactly.
- 4 nesting levels in scaffold → 4 levels in code.
- Every body contains `// BDD: SIGNATURE` (Jest) or `# BDD: SIGNATURE` (Mamba) and nothing else.
- No imports, no assertions, no mocks, no `beforeEach`.
- `it('should …')` matches the behavior hierarchy text verbatim — no paraphrasing.

### Batch processing for large behavior hierarchies

When a behavior hierarchy has more than ~18 describe blocks, process in batches:

1. First batch: top-level concept and its first 2-3 state blocks (~18 describes).
2. Subsequent batches: remaining state blocks and sub-concepts.
3. Confirm after each batch that the hierarchy count matches the behavior hierarchy for that slice.

---

## Development fidelity — tests + code

### Phase 1: Signature → Test implementation

**Input (signature)**

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
});
```

**Output (test implementation — Jest/TypeScript)**

```typescript
import { Character } from '../Character';

function defaultStats() {
  return { strength: 10, agility: 8, endurance: 6 };
}

describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // Arrange
      const stats = defaultStats();
      // Act
      const character = new Character({ name: 'Test', stats });
      // Assert
      expect(character.stats.strength).toBe(10);
      expect(character.stats.agility).toBe(8);
    });

    it('should have zero starting wounds', () => {
      // Arrange / Act
      const character = new Character({ name: 'Test', stats: defaultStats() });
      // Assert
      expect(character.wounds).toBe(0);
    });
  });

  describe('that is in combat', () => {
    let character: Character;

    beforeEach(() => {
      character = new Character({ name: 'Test', stats: defaultStats() });
    });

    it('should track current wounds', () => {
      // Act
      character.applyDamage(3);
      // Assert
      expect(character.wounds).toBe(3);
    });

    it('should apply damage from attacks', () => {
      // Arrange
      character.applyDamage(2);
      // Act
      character.applyDamage(4);
      // Assert
      expect(character.wounds).toBe(6);
    });
  });
});
```

### Phase 2: Failing tests → Minimal production code

Tests above are RED — `Character` does not exist.

**Output (minimal production code — TypeScript)**

```typescript
// Character.ts

interface Stats {
  strength: number;
  agility: number;
  endurance: number;
}

interface CharacterProps {
  name: string;
  stats: Stats;
}

export class Character {
  readonly name: string;
  readonly stats: Stats;
  wounds = 0;

  constructor({ name, stats }: CharacterProps) {
    this.name = name;
    this.stats = stats;
  }

  applyDamage(amount: number): void {
    this.wounds += amount;
  }
}
```

**What to notice:**
- Only properties tests assert on: `stats`, `wounds`. No `createdAt`, `id`, etc.
- Only methods tests call: `applyDamage`. No `heal()`, `die()`, etc.
- `wounds` starts at `0` because the test asserts `expect(character.wounds).toBe(0)`.
- Class used (not function) because `wounds` is mutable state that accumulates across calls.

### Mamba/Python equivalent

**Test implementation**

```python
from mamba import description, context, it, before
from expects import equal, expect
from character import Character

def default_stats():
    return {'strength': 10, 'agility': 8, 'endurance': 6}

with description('Character'):
    with context('that has been created'):
        with it('should have initial stats assigned'):
            # Arrange / Act
            character = Character(name='Test', stats=default_stats())
            # Assert
            expect(character.stats['strength']).to(equal(10))
            expect(character.stats['agility']).to(equal(8))

        with it('should have zero starting wounds'):
            # Arrange / Act
            character = Character(name='Test', stats=default_stats())
            # Assert
            expect(character.wounds).to(equal(0))

    with context('that is in combat'):
        with before.each:
            self.character = Character(name='Test', stats=default_stats())

        with it('should track current wounds'):
            self.character.apply_damage(3)
            expect(self.character.wounds).to(equal(3))

        with it('should apply damage from attacks'):
            self.character.apply_damage(2)
            self.character.apply_damage(4)
            expect(self.character.wounds).to(equal(6))
```

**Minimal production code (Python)**

```python
# character.py

class Character:
    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = stats
        self.wounds = 0

    def apply_damage(self, amount: int) -> None:
        self.wounds += amount
```

### Layer boundary mocking example (service layer)

When testing a service that depends on a repository:

```typescript
import { VoucherService } from '../VoucherService';
import { VoucherRepository } from '../VoucherRepository';

describe('VoucherService', () => {
  describe('that is creating a voucher', () => {
    let service: VoucherService;
    let mockRepo: jest.Mocked<Pick<VoucherRepository, 'save'>>;

    beforeEach(() => {
      mockRepo = { save: jest.fn().mockResolvedValue(undefined) };
      service = new VoucherService(mockRepo as VoucherRepository);
    });

    it('should persist the voucher when input is valid', async () => {
      // Arrange
      const input = { code: 'ABC-001', campaignId: 'camp-1' };
      // Act
      await service.create(input);
      // Assert
      expect(mockRepo.save).toHaveBeenCalledWith(
        expect.objectContaining({ code: 'ABC-001' })
      );
    });
  });
});
```

**Mock is at the boundary** (repository) — the service is fully tested; the repository mock is not the thing under test.
