# Language and Tooling Recommendations

This document defines the recommended tools, libraries, and idiomatic patterns for each supported language in the `context_tools` framework. 

Use this guidance to adapt conceptual templates (e.g., in TypeScript or Python) to the specific requirements of the target stack.

---

## TypeScript / JavaScript

- **Test Runner**: [Vitest](https://vitest.dev/) (or Jest).
- **Assertion Library**: Vitest `expect` (including `expect.poll` for async UI state).
- **Story file shape**: One `{story}.{tier}.ts` per story — `beforeAll`/`afterAll` for `{App}E2e.initialize(config)` / `.close()`; `background(({ given }) => { … scenario() … })` for shared Given + all scenarios; `./givens`, `./whens`, `./examples/*` modules for step bodies.
- **Style**: `story` / `background` / `scenario` from `story-test.ts`; chain `when(…).and(…)`; first `then(…)` then `.and(…)` for additional outcomes; domain operations in When, observable assertions in Then.

## Python

- **Test Runner**: [Mamba](https://github.com/nestorsalceda/mamba) (RSpec-style `description` / `context` / `it`).
- **Assertion Library**: [Expects](https://github.com/jaimegildesagredo/expects).
- **Story file shape**: Same layout as TypeScript — `story_test.background` wrapping scenarios, `before.all`/`after.all` for boot/teardown, sibling `givens.py`, `whens.py`, `examples/*` modules.
- **Style**: `story` / `background` / `scenario` from `story_test.py`; `when(…).and_(…)` chains; separate `it` blocks emitted for Then/And steps.

## Java

- **Test Runner**: [JUnit 5](https://junit.org/junit5/).
- **Assertion Library**: [AssertJ](https://assertj.github.io/doc/) or built-in `Assertions.assertAll`.
- **Style**: `@Nested` classes to mirror `describe` hierarchies; `@Test` methods for behaviors.
- **Mocking**: [Mockito](https://site.mockito.org/).
- **Idioms**:
    - Use `camelCase` for properties and methods.
    - Use `interface` for public seams.
    - Concatenate tier names onto class names (e.g., `SubmitOrderStoryTestHelperServer`) to comply with Java's file-naming rules.

---

## Universal Concepts

Regardless of language, follow these core Clean Engineering and Story Mapping principles:

1. **Arrange / Act / Assert**: Every test behavior should clearly separate these three phases.
2. **One Assertion per Behavior**: Each `it` or `@Test` block should verify one specific outcome.
3. **Example Factories**: Isolate test data generation into sibling `*_example_factory` files.
4. **Behavioral Outcomes**: Assertions must be in domain-observable terms, not internal state.
5. **One-Way Dependencies**: Modules and packages must have a clear, acyclic build order.
