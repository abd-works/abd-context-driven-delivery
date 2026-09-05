---
scanner: observable_behavior_scanner.py
---

# Rule: Test Observable Behavior

Test behavior through the **public API** — observable properties, return values, and state changes visible to callers. Do not assert on private attributes, internal flags, or implementation details. Tests that verify private state break on refactoring even when behavior is correct.

## DO

- Assert on public properties and return values.
- Verify the outcome a caller would see.

```python
# Test public API
assert agent.is_initialized
assert agent.config_path.exists()
assert agent.get_config_value('name') == 'story_bot'
assert result.status == 'ready'
```

## DON'T

- Assert on private attributes (`_`, `__`-prefixed).
- Test internal data structures or intermediate state that is not part of the contract.

```python
# WRONG: private implementation details
assert agent._initialized == True
assert agent._setup_called == True
assert len(agent._internal_steps) == 5
assert agent._config_cache is not None
```
