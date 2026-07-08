---
rule: rubric-is-verifiable
kind: quality
fidelity: [engineering]
artifact: test_*.py
---

# Rule: Rubric Is Verifiable

The `rubric` passed to `ai_judge` must describe a concrete, observable outcome — not a vague quality.

## DO

- State exactly what must appear: `"Output must contain the word PASS on its own line. It must not mention FAIL."`

## DON'T

- Write vague rubrics like `"The response should be good."` or `"The agent should behave correctly."`
