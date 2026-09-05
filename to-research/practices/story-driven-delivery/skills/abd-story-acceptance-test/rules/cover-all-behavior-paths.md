---
scanner: cover_all_paths_scanner.py
---

# Rule: Cover All Behavior Paths

Every story needs tests for the **normal (happy) path**, **edge cases**, and **failure paths**. Each distinct behavior gets its own focused, independent test. Tests must be deterministic (same result every run) and independent of execution order.

## DO

- Write separate tests for normal, edge, and failure scenarios.
- Make every test independent — no shared mutable state across test methods.

```python
def test_loads_valid_configuration(self, workspace_root):     # normal path
    ...

def test_loads_empty_configuration(self, workspace_root):     # edge case
    ...

def test_raises_error_when_config_missing(self, workspace_root):  # failure path
    with pytest.raises(FileNotFoundError):
        Agent(config_path=workspace_root / 'missing.json')
```

## DON'T

- Test only the happy path and leave edge and failure behavior unspecified.
- Combine multiple behaviors in one test method.

```python
# WRONG: single test for both success and failure
def test_loads_config(self, workspace_root):
    # Tests valid case AND missing file in same method
    ...
```
