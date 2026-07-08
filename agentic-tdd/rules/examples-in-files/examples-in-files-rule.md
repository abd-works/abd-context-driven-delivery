---
rule: examples-in-files
kind: shape
fidelity: [engineering]
artifact: test_*.py
---

# Rule: Examples in Files

Pass and fail example artifacts must live in files alongside the test, not hardcoded as strings in the test code. Tests must be parametrized to run over multiple examples. Prompts and rubrics may live in the test.

## DO

- Load artifacts from `examples/{scenario}/context/` and check against `examples/{scenario}/expected/`
- Use `@pytest.mark.parametrize` over all discovered examples

## DON'T

- Hardcode artifact text as a string literal in the test method body
- Write a single hardcoded scenario with no parametrization
