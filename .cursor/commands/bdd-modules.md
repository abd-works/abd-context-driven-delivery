# bdd-modules

Use bdd guidance at `modules` fidelity only.

# Contexts

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

## Hierarchy shape (required)

```
describe {subject — domain thing, state, or observable condition}
  that {event or condition that sets the subject up}
    with {narrower condition}
      it should {observable outcome}
```

Read top-down as a **usage / storytelling sequence**: what the user or system does first, then what is true, then what is observed. Nest by the **real events and conditions** that make the next observation possible — not by package, class role, or test fixture type.

| Line | Names | Never names |
| --- | --- | --- |
| **describe** | Subject under observation in plain English (thing, state, condition) | Manager / hub / runner / service / internal class; decorator symbol (`@log`); marker name |
| **that …** | Past or present event/condition on that subject (`that has been logged`, `that is invoked`) | `when …` |
| **with …** | Narrower standing condition (`with no session name given`, `with verbose off`) | `when …`; implementation knobs phrased as API flags |
| **it should …** | One stakeholder-visible outcome | Internals, private fields, call counts on mocks of the subject |

**Pass (storytelling / usage order):**
```
an action that is annotated with log
  that is invoked
    it should record a run event on the session trail
  that has been logged
    with no session name given
      it should use the default session
    with a given session name
      it should keep events under that session
    with verbose off
      it should write a summary line and keep the last payload
      with full logging requested
        it should flush the last payload
    with verbose on
      it should write payload files for later events

an action that is not annotated
  that is invoked
    it should leave the session trail empty
```

**Fail:**
```
@log marker                          ← mechanism / symbol, not a subject
ToolsetRunner                        ← manager / internal
a logged tool                        ← splits the same subject; use one action story
when no session name is given        ← never "when" for state — use "with …"
```

**Shared Rules:**

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …).
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`full-surface-coverage`** — When generating or satisfying tests for a module that already exists, scan the production source for every public method, property, class, and constant. Each must have at least one `it should` covering its observable behavior. Any gap is a violation. Private and underscore-prefixed members are excluded unless they are part of a documented public contract.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

---

This skill operates at **multiple levels of fidelity**. Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity. Least detail → most detail below.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **development** | Implemented tests + production code |

## behavior

**Default format:** Python

**Goal:** map observation to a real test before implementation. Lock the sketched hierarchy as framework `describe` / `it` nesting. Every `it` body is exactly one `BDD: SIGNATURE` marker — nothing else.

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed 
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

### Framework syntax

| Construct | Jest (TypeScript) | Mamba (Python) | JUnit 5 (Java) |
| --- | --- | --- | --- |
| Top-level concept | `describe('Context', () => {` | `with description('Context'):` | `@Nested class Context` |
| Nested state/context | `describe('that has…', () => {` | `with context('that has…'):` | `@Nested class ThatHas…` |
| Behavior | `it('should …', () => {` | `with it('should …'):` | `@Test void should…()` |
| Marker | `// BDD: SIGNATURE` | `# BDD: SIGNATURE` | `// BDD: SIGNATURE` |

### Rules

- **`hierarchy-preservation`** — 1:1 from sketch nesting to code. Nothing added, removed, or flattened. Same depth, same `it` count.
- **`signature-markers`** — Every `it` body is exactly `// BDD: SIGNATURE` or `# BDD: SIGNATURE`.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

## development

**Default format:** Python

**Goal:** Replace `BDD: SIGNATURE` markers one at a time with it shgould /expect bodies, then minimum production code until green. Inherit the framework from the **behavior** artifactif already completed.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

### Coverage scan (existing code)

When generating or satisfying against a module that already exists, read the production source before touching the spec:

1. List every public method, property, class, and constant (exclude `_`-prefixed members unless publicly documented).
2. Compare against the existing spec to find members with no `it should` entry.
3. Add `it should` entries (at behavior fidelity) or full test bodies (at development fidelity) for every gap — do not skip any public member.
4. Only then proceed with RED-GREEN-REFACTOR for the new or updated tests.

### The RED-GREEN-REFACTOR cycle

**RED** — fail for the right reason before production code exists.  
**GREEN** — least production code that makes this assertion pass.  
**REFACTOR** — clean up while green. One test, one production change, one green — do not batch all bodies first.

### Arrange-Act-Assert

Label Arrange / Act / Assert; one observable outcome per `it` (`observable-behavior` above). Split unrelated expects. Shared construction → `beforeEach` / factory at three sibling dupes.

### Rules

- **`red-then-green`** — Fail for the right reason before production code changes.
- **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass.
- **`refactor-only-when-green`** — Refactor only while green.
- **`one-signature-at-a-time`** — One marker → green → next. Do not batch all bodies first.
- **`one-assertion-per-test`** —  one outcome per `it`. tighly connects `expects`
- **`layer-isolation`** — Mock only at architecture boundaries; never the subject under test.
- **`no-remaining-signatures`** — Zero `BDD: SIGNATURE` markers when done.
- **`full-surface-coverage`** — Before generating or satisfying, scan the production source for all public members. Add `it should` entries for every uncovered public method, property, or class. Complete coverage is required; no public surface may be left untested.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.
- **`roundtrip-parity-is-required`** — Adapter parse/render seams assert `counts(parse(render(canonical))) == counts(canonical)`.
- **`code-source-of-truth-guard`** — Tests reject unsafe regeneration when generation can overwrite hand-edited code.
- **`impl-must-carry-bdd-manifest`** — Impl paired with `*_spec.py` carries `# @toolset-manifest … context_tools.bdd.bdd:Bdd`.
- **`observable-behavior`** — Assert public outcomes only.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

---

## examples.md

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
2. Subsequent batches: remaining state blocks and sub-context_tools.
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

// =============================================================================
// BDD Development Template — JUnit 5 / Java Test Implementation
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {DomainEntity} with the class or module under test.
//   2. Import only the entity under test and its dependency types.
//   3. Add a private static factory for each shared test-data object.
//   4. Use @BeforeEach for shared object setup when 3+ sibling @Test methods need it.
//   5. Each @Test body uses // Arrange / // Act / // Assert comments.
//   6. One assertion per behavior (or a tight group describing the same outcome).
//   7. Replace `// BDD: SIGNATURE` markers — do not leave any in the final file.
//   8. Delete this instruction block before committing the file.
// =============================================================================

package {com.example.domain.area};

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

// import {com.example.domain.DomainEntity};

@DisplayName("{DomainEntity}")
class {DomainEntity}Spec {

    // ------------------------------------------------------------------------
    // Factories — minimal valid test data (populate only fields tests assert on)
    // ------------------------------------------------------------------------

    private static {RelatedType} default{RelatedType}() {
        return new {RelatedType}(/* populate only fields tests assert on */);
    }

    // ------------------------------------------------------------------------

    @Nested
    @DisplayName("that has been created")
    class ThatHasBeenCreated {

        @Test
        @DisplayName("should have {initial property} assigned")
        void shouldHave{InitialPropertyPascalCase}Assigned() {
            // Arrange
            {RelatedType} input = default{RelatedType}();

            // Act
            {DomainEntity} entity = new {DomainEntity}(input);

            // Assert
            assertEquals({expectedValue}, entity.get{PropertyPascalCase}());
        }
    }

    @Nested
    @DisplayName("that is {active state}")
    class ThatIs{ActiveStatePascalCase} {

        private {DomainEntity} entity;

        @BeforeEach
        void setUp() {
            entity = new {DomainEntity}(default{RelatedType}());
        }

        @Test
        @DisplayName("should {behavior description}")
        void should{BehaviorDescriptionPascalCase}() {
            // Act
            entity.{action}({input});

            // Assert
            assertEquals({expectedValue}, entity.get{PropertyPascalCase}());
        }

        @Test
        @DisplayName("should {second behavior}")
        void should{SecondBehaviorPascalCase}() {
            // Arrange
            {LocalSetupType} {localSetup} = {value};

            // Act
            entity.{action}({localSetup});

            // Assert
            assertEquals({expectedValue}, entity.get{PropertyPascalCase}());
        }
    }
}