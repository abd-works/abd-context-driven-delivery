---
scanner: object_oriented_helpers_scanner.py
---

# Rule: Object-Oriented Test Helpers

Consolidate test setup around **shared helper objects** (test hoppers / factories) that build **complete domain fixtures** with standard data. Avoid scattering many primitive parameters across `parametrize` blocks or inline setups. A helper object centralizes construction of the full domain context in one place.

## DO

- Use a test helper class (e.g. `BotTestHelper`) that builds a complete domain object in one call.
- Assert against complete objects, not fragments.

```python
class BotTestHelper:
    def __init__(self, workspace: Path) -> None:
        self._workspace = workspace
        self._bot = create_bot(workspace)

    def set_state(self, behavior: str, action: str) -> None:
        self._bot.navigate_to(behavior, action)

    def assert_at_behavior_action(self, behavior: str, action: str) -> None:
        assert self._bot.current_behavior == behavior
        assert self._bot.current_action == action

def test_bot_navigates_to_shape_clarify(self, workspace_root):
    helper = BotTestHelper(workspace_root)
    helper.set_state('shape', 'clarify')
    helper.assert_at_behavior_action('shape', 'clarify')
```

## DON'T

- Spread test setup across many primitive parameters in `parametrize` blocks.
- Cherry-pick single values from a partial object.

```python
# WRONG: many primitives scattered across parametrize
@pytest.mark.parametrize('behavior, action, workspace, config, expected_status', [
    ('shape', 'clarify', '/tmp/ws1', {'k': 'v'}, 'active'),
    ...
])
def test_bot_state(self, behavior, action, workspace, config, expected_status):
    assert bot.status == expected_status  # single field
```
