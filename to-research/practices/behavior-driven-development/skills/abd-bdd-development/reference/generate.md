# Generate — abd-bdd-development

Follow every file in `rules/`; fill templates exactly.

## When to use

- Test file with `// BDD: SIGNATURE` markers ready for implementation
- RED-GREEN-REFACTOR cycle — production code driven by failing tests
- Module implementation with test coverage matching the BDD hierarchy

**Not this skill when:** signatures not written (`abd-bdd-specification` first), tests from scratch without BDD hierarchy (`abd-story-acceptance-test`), or E2E acceptance tests (Playwright template via `abd-story-acceptance-test`).

## Read context

- **`../../../reference/bdd-concepts.md`** — shared BDD theory.
- **`reference/concepts.md`** — RED-GREEN-REFACTOR, Arrange-Act-Assert, mock boundaries, code minimalism.
- **`reference/examples.md`** — worked test-to-code examples.
- **`reference/diagnose.md`** — flip to diagnose mode when a test keeps failing after 2 fix attempts.
- Existing signature file — scan all `// BDD: SIGNATURE` markers for scope.

## Implement tests

**Before writing any test body:**

1. **Confirm framework** — inherit from the signature file.
2. **Scan signatures** — list all `it` blocks still containing `// BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` or factory before implementing.

**Build rules:**

- Replace `// BDD: SIGNATURE` with Arrange-Act-Assert body.
- **One assertion per behavior** — each `it` tests one observable outcome.
- Call production code directly — let tests fail naturally (RED phase).
- Mock **only at module boundaries** — not domain classes under test.
- Extract shared setup to `beforeEach` when the same arrangement appears in three or more sibling tests.
- Extract helpers to `{domain-name}-helper.ts` when reused across describe blocks.

| Template | Deliverable |
| --- | --- |
| `templates/tests.ts` | Jest/TypeScript test implementation |
| `templates/tests.py` | Mamba/Python test implementation |

## Implement production code

After all test bodies are written and tests are RED:

1. Write **minimal code** that makes each failing test GREEN.
2. Start with functions before classes; let tests drive when a class is needed.
3. Follow `abd-clean-code` rules for production modules.

| Template | Deliverable |
| --- | --- |
| `templates/code.ts` | Minimal TypeScript production module |
| `templates/code.py` | Minimal Python production module |

**Do not add** properties, parameters, behaviors, configuration, or error paths that no test demands.

## Diagnose

If a test fails after **2 or more consecutive fix attempts** — stop. Read **`reference/diagnose.md`** immediately. Do not attempt a third fix without a hypothesis.

**Do not move to the next test until the spinning test is GREEN.**

## Quality bar

Zero signature markers remain. Tests were RED before production code. Assertions check observable behavior. Mocks at architecture boundaries only. Production code minimal — nothing without a passing test.
