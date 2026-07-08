---
rule: sessions-are-isolated
kind: shape
fidelity: [engineering]
artifact: test_*.py
---

# Rule: Sessions Are Isolated

Each test scenario must use its own `session_file` path. Never share a session file between two different test methods.

## DO

- Use a unique path per scenario: `session_file=SESSION_DIR / "validate-heading-pass.json"`

## DON'T

- Reuse the same `session_file` path in multiple test methods
