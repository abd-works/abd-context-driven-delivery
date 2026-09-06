---
scanner: full_result_assertions_scanner.py
---

# Rule: Assert Full Results

Assert **complete domain objects** (state dictionaries, dataclasses, graph objects, log records) rather than cherry-picking a single field. Single-field assertions miss structural regressions and leave most of the domain object unverified.

## DO

- Compare the full result against a named standard fixture.
- Define standard data sets as module-level constants or helper factories.

```python
STANDARD_STATE = {
    'behavior': 'shape',
    'action': 'clarify',
    'phase': 'exploration',
    'context': {},
}

def test_bot_starts_in_standard_state(self, workspace_root):
    # Given
    helper = BotTestHelper(workspace_root)

    # When
    helper.set_state('shape', 'clarify')

    # Then — assert full state object
    assert helper.get_state() == STANDARD_STATE
```

## DON'T

- Assert only one field from a complex domain result.
- Assert a count instead of the underlying records.

```python
# WRONG: cherry-picking a single field
assert helper.get_state()['behavior'] == 'shape'

# WRONG: asserting count when the records matter
assert len(result.stories) == 3
```
