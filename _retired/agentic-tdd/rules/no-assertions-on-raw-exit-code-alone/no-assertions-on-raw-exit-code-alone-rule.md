---
rule: no-assertions-on-raw-exit-code-alone
kind: shape
fidelity: [engineering]
artifact: test_*.py
scanner: no-assertions-on-raw-exit-code-alone-scanner.py
---

# Rule: No Assertions on Raw Exit Code Alone

`result.exit_code == 0` is not a sufficient pass condition. Always also check the content of `result.stdout` or obtain a `JudgeResult`.

## DO

- `assert verdict.passed(), verdict.reason`
- `assert "PASS" in result.stdout`

## DON'T

- `assert result.exit_code == 0` with no further content check
