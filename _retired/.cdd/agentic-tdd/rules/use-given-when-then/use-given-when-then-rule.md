---
rule: use-given-when-then
kind: shape
fidelity: [engineering]
artifact: test_*.py
scanner: use-given-when-then-scanner.py
---

# Rule: Use Given / When / Then

Every agent test must be structured as Given / When / Then using the `AgentTest` helpers: `given_guidance`, `when_agent_invoked`, and either `ai_judge` or a direct assertion on `result.stdout`.

## DO

- Subclass `AgentTest`
- Call `given_guidance()` and `given_context()` in the Given step
- Call `when_agent_invoked(...)` in the When step
- Assert on `ai_judge(...)` or `result.stdout` in the Then step

## DON'T

- Call `cursor-agent` directly via `subprocess`
- Use no `AgentTest` base class
- Assert only on `result.exit_code` with no content check
