# Instructions

Fill BDD signature files with **Arrange-Act-Assert** test bodies, then drive **minimum production code** until every test is green. Follow every rule in `rules/`.

---
# Concepts

## RED-GREEN-REFACTOR

- **`red-then-green`** — Write the test body so it fails for the right reason (missing import, unmet assertion) **before** touching production code. A test that passes with no production code is a false signal.
- **`minimum-green`** — Write the least production code that makes the failing test pass. No extra parameters, properties, error paths, or configuration.
- **`refactor-only-when-green`** — Refactor after the test is green and stays green. Never refactor during RED.
- **`one-signature-at-a-time`** — Replace one `// BDD: SIGNATURE` (or `# BDD: SIGNATURE`), drive it to green, then move to the next. **Do not** implement every test body before writing any production code.

## Arrange-Act-Assert

- **`aaa-body`** — Every test body has three parts: **Arrange** (preconditions), **Act** (call production code), **Assert** (check outcome). Label them with comments.
- **`one-assertion-per-test`** — Each `it` verifies one observable outcome. If you need multiple `expect`s on unrelated things, split the test.

## Mock boundaries

- **`mock-at-architecture-boundaries`** — Mock only at boundaries defined by the architecture (external services, adapters, framework integration). Domain classes under test are **never** mocked.
- **`do-not-mock-subject`** — Mocking the class under test tests the mock, not the code.

## Code minimalism

- **`no-untested-code-paths`** — Every branch, parameter, property, and error path must be driven by a failing test. Anything else is unverified scope.
- **`grow-per-test`** — Production code grows one failing test at a time. Design decisions come from tests, not anticipation.

## Shared setup

- **`beforeeach-when-three-siblings`** — Extract shared object construction to `beforeEach` / `with before.each:` the moment three or more sibling `it` blocks share the same arrangement.
- **`factories-for-test-data`** — Shared test-data objects go in factory functions (`defaultStats()`, `makeVoucher()`) with sensible defaults.

---
# Generate

1. Read § Concepts and every file in `rules/`.
2. Read `examples/examples.md` for the signature → tests → production shape.
3. Scan the signature file — list every `it` still holding `// BDD: SIGNATURE` and report the count.
4. Pick one signature. Fill it from the matching template:
   - `formats/python/bdd-template.py` — Mamba/Python
   - `formats/typescript/bdd-template.ts` — Jest/TypeScript
   - `formats/java/bdd-template.java` — JUnit 5/Java
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until the test is GREEN.
7. Refactor only while green. Move to the next signature.
8. Repeat until zero signature markers remain, then run **validate**.

**Do not:** add params/properties/branches no test drives, mock the subject, batch multiple test bodies before any production code, or fix a spinning test more than twice without a hypothesis — stop and diagnose.
