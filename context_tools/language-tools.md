# Language and Tooling Recommendations

This document defines the recommended tools, libraries, and idiomatic patterns for each supported language in the `context_tools` framework. 

Use this guidance to adapt conceptual templates (e.g., in TypeScript or Python) to the specific requirements of the target stack.

---

## TypeScript / JavaScript

- **Test Runner**: [Vitest](https://vitest.dev/) (or Jest).
- **Assertion Library**: Vitest `expect` (including `expect.poll` for async UI state).
- **Story file shape**: One `{story}.{tier}.ts` per story — `beforeAll`/`afterAll` for `{App}E2e.initialize(config)` / `.close()`; `background(({ given }) => { … scenario() … })` for shared Given + all scenarios; step bodies inline in `given` / `when` / `then`.
- **Style**: `story` / `background` / `scenario` from `story-test.ts`; chain `when(…).and(…)`; first `then(…)` then `.and(…)` for additional outcomes; domain operations in When, observable assertions in Then.

## Python

- **Test Runner (BDD unit specs)**: [Mamba](https://github.com/nestorsalceda/mamba) with `description` / `context` / `it` / `before`.
- **Test Runner (story acceptance)**: Same Mamba stack via **`story_test.py`** — extends Mamba like **`story-test.ts`** extends Vitest (`story`, `background`, `scenario`, `given`, `when`, `then`).
- **Assertion Library**: [Expects](https://github.com/jaimegildesagredo/expects).
- **Story file shape**: `story(name, body)`, `background(given)`, `scenario(name, ({ when, then }) => …)` from `story_test.py`; `before_all()` / `after_all()` for boot/teardown; inline step bodies in `given` / `when` / `then` callbacks.
- **Style**: `when(…).and_(…)` and `then(…).and_(…)` — mirrors TS `when().and()` / `then().and()`.

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
