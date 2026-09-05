# Language and Tooling Recommendations

This document defines the recommended tools, libraries, and idiomatic patterns for each supported language in the `context_tools` framework. 

Use this guidance to adapt conceptual templates (e.g., in TypeScript or Python) to the specific requirements of the target stack.

---

## TypeScript / JavaScript

- **Test Runner**: [Jest](https://jestjs.io/) or [Vitest](https://vitest.dev/).
- **Assertion Library**: Built-in `expect`.
- **Style**: Jasmine-style `describe` / `it` / `beforeEach` blocks.
- **Mocking**: `jest.mock()` or `vi.mock()`.
- **Idioms**: 
    - Use `camelCase` for properties and operations.
    - Favour `interface` for seams.
    - Use `async/await` for I/O and interaction points.

## Python

- **Test Runner**: [Pytest](https://docs.pytest.org/) or [Mamba](https://github.com/nestorsalceda/mamba).
- **Assertion Library**: `pytest` assertions or [Expects](https://github.com/jaimegildesagredo/expects).
- **Style**: 
    - For BDD: Mamba `description` / `it` blocks.
    - For unit: Standard `test_*` functions.
- **Mocking**: `unittest.mock`.
- **Idioms**:
    - Use `snake_case` for properties and operations.
    - Use `typing.Protocol` for structural typing/interfaces.
    - Use `@property` for simple accessors.

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
