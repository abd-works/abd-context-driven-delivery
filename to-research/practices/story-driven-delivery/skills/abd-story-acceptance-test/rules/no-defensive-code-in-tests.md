---
scanner: no_guard_clauses_scanner.py
---

# Rule: No Defensive Code in Tests

Tests must **never** contain guard clauses, defensive conditionals, `try/except`, or fallback paths. Tests control their own setup — if setup is wrong, the test **must fail immediately and clearly**. Guard clauses hide problems by silently skipping assertions.

## DO

- Assume correct setup; let the test fail if setup is not right.
- Call code directly without wrapping in conditionals.

```python
def test_behavior_loads_by_name(self, workspace_root):
    # Given — direct setup, no guard
    behavior = Behavior(name='shape', workspace_root=workspace_root)

    # When / Then — no if-check needed
    assert behavior.name == 'shape'
    assert behavior.instructions_path.exists()
```

## DON'T

- Wrap operations in `if`, `try/except`, or `hasattr` checks.
- Add fallback paths to paper over setup problems.

```python
# WRONG: defensive conditional hides a broken test
if behavior_file.exists():        # if it doesn't exist, test silently passes!
    behavior = load_behavior(behavior_file)
    assert behavior.name == 'shape'

# WRONG: exception swallowed
try:
    agent.initialize()
except Exception:
    pass  # hides the real failure
```
