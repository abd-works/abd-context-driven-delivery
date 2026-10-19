# Language and Tooling Recommendations

This document defines the recommended tools, libraries, and idiomatic patterns for each supported language in the `context_tools` framework. 

Use this guidance to adapt conceptual templates (e.g., in TypeScript or Python) to the specific requirements of the target stack.

---

## TypeScript / JavaScript

- **Test Runner**: [Vitest](https://vitest.dev/) (or Jest).
- **Assertion Library**: Vitest `expect` (including `expect.poll` for async UI state).
- **Machinery**: Copy `practices/stories/templates/ts/story-test.ts` → `tests/story-test.ts` once per tests tree if missing — not inlined in deploy templates.
- **Story file shape**: One `{epic}/{sub-epic}/{story}/{story_snake}_story.test.ts` per story — `beforeAll` / `afterAll`, `background(({ given }) => { … scenario() … })`. The scenarios markdown for that story is the same stem with `.md`. Do not emit front-end / back-end / e2e files, and do not use `.spec.` (that name is for BDD describe/it). Template is **structure only** (`// test code goes here` in each step); replace when implementing.
- **Style**: `story` / `background` / `scenario` from `story-test.ts`; chain `when(…).and(…)`; first `then(…)` then `.and(…)` for additional outcomes.

## Python

- **Test Runner (BDD unit specs)**: [Mamba](https://github.com/nestorsalceda/mamba) with `description` / `context` / `it` / `before`.
- **Test Runner (story acceptance)**: Same Mamba stack via **`story_test.py`** — extends Mamba like **`story-test.ts`** extends Vitest (`story`, `background`, `scenario`, `given`, `when`, `then`).
- **Assertion Library**: [Expects](https://github.com/jaimegildesagredo/expects).
- **Machinery**: Copy `practices/stories/templates/py/story_test.py` → `tests/story_test.py` once per tests tree if missing — not inlined in deploy templates. Run stories with `python -m story_test`.
- **Story file shape**: One `{epic}/{sub-epic}/{story}/{story_snake}_story.test.py` per story — `with story` / `background` / `given` / `when` / `then`. The scenarios markdown for that story is the same stem with `.md`. Do not emit front-end / back-end / e2e files, and do not use `_spec.py` (that name is for BDD). Template is **structure only** (`pass  # test code goes here` under each block); you replace with real code when implementing. Boot/teardown in `with before.all` / `with after.all`.
- **Runner**: `python -m story_test tests/...` (patches Mamba AST loader). Assertions use `expects` inside **then** bodies like unit specs.

## Java

- **Test Runner**: [JUnit 5](https://junit.org/junit5/).
- **Assertion Library**: [AssertJ](https://assertj.github.io/doc/) or built-in `Assertions.assertAll`.
- **Style**: `@Nested` classes to mirror `describe` hierarchies; `@Test` methods for behaviors.
- **Mocking**: [Mockito](https://site.mockito.org/).
- **Idioms**:
    - Use `camelCase` for properties and methods.
    - Use `interface` for public seams.
    - Name the story test `{Story}StoryTest.java` (same `{story}_story.test` idea; Java cannot use a `.test.` infix). Markdown scenarios stay `{story_snake}_story.test.md`.

## Markdown

- **Story file shape**: One `{epic}/{sub-epic}/{story}/{story_snake}_story.test.md` per story — GWT and Examples tables. Same stem as the TypeScript or Python acceptance test; only the extension is `md`.

---

## Universal Concepts

1. **Arrange / Act / Assert**: Every test behavior should clearly separate these three phases.
2. **One Assertion per Behavior**: Each `it` or `@Test` block should verify one specific outcome.
3. **Example Factories**: Isolate test data generation into sibling `*_example_factory` files.
4. **Behavioral Outcomes**: Assertions must be in domain-observable terms, not internal state.
5. **One-Way Dependencies**: Modules and packages must have a clear, acyclic build order.
