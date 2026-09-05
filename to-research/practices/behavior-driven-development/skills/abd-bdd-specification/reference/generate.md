# Generate — abd-bdd-specification

Follow every file in `rules/`; fill templates exactly.

## When to use

- Approved BDD scaffold (`*-behavior.md`) ready for code structure
- Phase 1 of BDD workflow — lock hierarchy before assertions
- Review that every scaffold behavior maps to a real test slot

**Not this skill when:** no scaffold yet (`abd-bdd-behavior` first), adding assertions (`abd-bdd-development`), or writing tests directly from AC (`abd-story-acceptance-test`).

## Read context

- **`../../../reference/bdd-concepts.md`** — shared BDD theory.
- **`reference/concepts.md`** — signature phase: BDD: SIGNATURE marker, hierarchy preservation, framework syntax.
- **`reference/examples.md`** — worked signature examples in Jest and Mamba.
- Behavior hierarchy: `{stem}-behavior.md` beside the target test file.

## Before writing

1. **Confirm framework** — ask if not stated. Default: Jest/TypeScript; Mamba/Python for Python projects.
2. **Confirm scaffold** — read and confirm scaffold file path.
3. **Declare hierarchy** — state full describe/it nesting in chat before writing.

## Build rules

- Convert every scaffold line to its framework equivalent:
  - Describe-level line → `describe()` (Jest) or `with description()` / `with context()` (Mamba)
  - Behavior line (`should …`) → `it()` (Jest) or `with it()` (Mamba)
- Preserve **all nesting levels** from the scaffold exactly — do not flatten.
- Every test body contains **only** the signature marker:
  - Jest: `// BDD: SIGNATURE`
  - Mamba: `# BDD: SIGNATURE`
- **No mocks, stubs, helpers, or assertions** in this phase.
- Process in batches of ~18 describe blocks when the scaffold is large.
- Update the test file directly; do not create a duplicate.

## Framework syntax

| Construct | Jest (TypeScript) | Mamba (Python) |
| --- | --- | --- |
| Top-level concept | `describe('Concept', () => {` | `with description('Concept'):` |
| Nested state/context | `describe('that has been created', () => {` | `with context('that has been created'):` |
| Behavior | `it('should have initial stats', () => {` | `with it('should have initial stats'):` |
| Signature marker | `// BDD: SIGNATURE` | `# BDD: SIGNATURE` |
| Body close | `});` | *(indentation only)* |

## Output shape

| Template | Deliverable |
| --- | --- |
| `templates/signatures.ts` | Jest/TypeScript signature skeleton |
| `templates/signatures.py` | Mamba/Python signature skeleton |

## Quality bar

1:1 scaffold-to-code hierarchy. Every `it` body has exactly one signature marker. No implementation. Single file — no duplicates.
