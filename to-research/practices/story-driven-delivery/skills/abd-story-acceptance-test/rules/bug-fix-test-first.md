---
scanner: bug_fix_test_first_scanner.py
---

# Rule: Bug-Fix Test First

When production code breaks, follow the **RED → GREEN → PRODUCTION** workflow. Write a failing test that reproduces the bug before touching any production code. Never fix bugs without a failing test first — a fix without a test may be incomplete and will not prevent regression.

## DO

1. Write a test that reproduces the bug (RED — test fails).
2. Run the test to confirm it fails for the right reason.
3. Fix the minimal production code to make the test pass (GREEN).
4. Run the full suite to confirm nothing regressed.

```python
# Step 1 — RED: reproduce the bug
def test_mcp_tool_initializes_bot(self, workspace_root):
    # This test fails before the fix
    bot = MCPTool(workspace_root=workspace_root)
    bot.initialize()
    assert bot.is_ready  # fails here

# Step 2 — fix the production code until test is GREEN
# Step 3 — run full suite
```

## DON'T

- Edit production code without first writing a test that fails because of the bug.
- Deploy a fix and assume it works without a passing test.

```python
# WRONG: edit production code first
# def initialize(self):
#     self._ready = True   ← fix here without a failing test
```
