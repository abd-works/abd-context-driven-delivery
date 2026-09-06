# Testing Architecture — abd-architecture-specification

Two artefacts carry testing architecture. The central spec holds a one-paragraph pointer; everything else lives in the test-helpers context file alongside the test code. Quality contract: [testing-architecture-names-pattern-and-seam](../rules/testing-architecture-names-pattern-and-seam.md).

## Central spec section

One paragraph maximum. State the pattern name, what exercises the real stack, what is stubbed at the boundary, and a single link to the test-helpers context file. No principles, no code snippets, no tables.

## Test-helpers context file

Place at `tests/<helpers-folder>/architecture-context.md`. Use the package-tier template as the base. The content it must carry:

**Pattern and stub boundary** — name the testing pattern (e.g. Sandbox, Integration, Unit+Integration split) and state exactly what is stubbed and at which interface boundary (e.g. "outbound HTTP calls and identity checks stubbed via Jest mocks at the axios boundary"). This is the one fact the central spec paragraph quotes.

**Layer-to-tech mapping** — a table mapping each test layer or concern to its tooling:

| Layer | Tool | Notes |
|---|---|---|
| Test runner | e.g. Jest | version, config file location |
| HTTP exercise | e.g. Supertest | drives the real Express app |
| Stubs / mocks | e.g. jest.mock, sinon | stub boundary and how stubs are registered |
| Fixtures / factories | e.g. domain test objects | where they live, naming convention |
| Coverage | e.g. Istanbul/c8 | threshold, report location |

**Folder structure** — annotated tree showing where test files live relative to source, the naming convention for spec files, and where shared helpers and fixtures are kept:

```
tests/
+-- <helpers>/         <- shared test objects, fixtures, and spec-alignment table
+-- <feature-a>/       <- spec files for feature A (named <story>.spec.ts or similar)
+-- <feature-b>/
src/
+-- <feature-a>/       <- source sits here; spec files mirror this tree under tests/
```

**Epic / sub-epic map** — a table or bulleted list showing which test files (or test describe blocks) cover which epics and sub-epics. Keeps the test suite navigable when story count grows.

**Spec-alignment table** — a row per acceptance-criteria story mapped to the spec file and describe block that covers it. Format:

| Story | Spec file | Describe / context block |
|---|---|---|
| AC-01 | tests/feature-a/create.spec.ts | `describe("Create Feature A")` |

**Principles** — a short bulleted list of the test design rules the team enforces (e.g. "helpers own mechanics; spec files own scenarios", "one stub registration point per external system"). These live here, NOT in the central spec.

## Authoring order

Author the test-helpers context file as part of Phase 2 alongside the other context files. Classify the test-helpers folder as a **package-tier** context file and list it under the **Testing** category in Package Context. Write the central spec's `## Testing Architecture` paragraph last, after the test-helpers file exists to link to.
