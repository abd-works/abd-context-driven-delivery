---
rule: tests-shape
kind: shape
fidelity: [engineering]
artifact: tests/**/*.test.{ts,js} | tests/**/test_*.py
scanner: tests-shape-scanner.py
---

# tests-shape

Each test file MUST have the fundamental structural elements of an executable
BDD test: a `describe`/class block that names the behaviour, and at least one
`it`/`test_` case inside it.

## The rule

- TypeScript / JavaScript (`*.test.ts`, `*.test.js`, `*.spec.ts`):
  - MUST contain a `describe(...)` block
  - MUST contain at least one `it(...)` (or `test(...)`) inside it
- Python (`test_*.py`, `*_test.py`):
  - MUST contain either a `class Test...` block or module-level `def test_...`
  - MUST contain at least one `def test_...` case

## DO

- Group behaviours by `describe` / test class.
- Name each case with an `it` / `test_` sentence.

## DON'T

- Do not commit test files with no `describe`/class + `it`/test_ pair.
- Do not use bare assertion scripts — always wrap in test-runner primitives.

## Cross-references

- `tests-implement-specification` — enforces that these test names match
  scenario titles verbatim.
