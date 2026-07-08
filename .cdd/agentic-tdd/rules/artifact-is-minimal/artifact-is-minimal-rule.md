---
rule: artifact-is-minimal
kind: quality
fidelity: [engineering]
artifact: test_*.py
---

# Rule: Artifact Is Minimal

The context (artifact) passed to the agent must contain only what is needed to exercise the behaviour under test. Do not paste entire real files.

## DO

- Provide a minimal snippet (5–15 lines) that exercises exactly one aspect of the behaviour under test

## DON'T

- Paste a 300-line file wholesale when only one heading or section is relevant
