---
rule: judge-session-is-separate
kind: shape
fidelity: [engineering]
artifact: test_*.py
scanner: judge-session-is-separate-scanner.py
---

# Rule: Judge Session Is Separate

The `ai_judge` call must use a different `session_file` from the one used in `when_agent_invoked`. Judge state must not bleed into agent state.

## DO

- Agent: `session_file=SESSION_DIR / "my-rule.json"`
- Judge: `session_file=SESSION_DIR / "my-rule-judge.json"`

## DON'T

- Pass the same `session_file` path to both `when_agent_invoked` and `ai_judge`
