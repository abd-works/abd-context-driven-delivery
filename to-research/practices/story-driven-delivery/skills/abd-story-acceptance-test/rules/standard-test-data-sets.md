---
scanner: standard_data_reuse_scanner.py
---

# Rule: Standard Test Data Sets

Define **canonical, named test data sets** as module-level constants or factory functions and **reuse them** across tests. Do not recreate ad-hoc values in every test method. Standard data sets ensure every test exercises the full domain object and prevent tests from diverging on what "valid" data looks like.

## DO

- Define standard data once at the module level (or in a shared helpers module).
- Reuse the same constants across tests in the file.

```python
STANDARD_AGENT_CONFIG = {
    'name': 'story_bot',
    'behaviors': ['shape', 'discovery', 'tests'],
    'workspace': 'agile_bots',
}

STANDARD_BOT_STATE = {
    'behavior': 'shape',
    'action': 'clarify',
    'phase': 'exploration',
}

def test_agent_loads_standard_config(self, workspace_root):
    config_file = create_config_file(workspace_root, STANDARD_AGENT_CONFIG)
    agent = Agent(config_path=config_file)
    agent.initialize()
    assert agent.config == STANDARD_AGENT_CONFIG
```

## DON'T

- Create new ad-hoc config values per test.
- Assert only one field from a complex object that has a matching standard.

```python
# WRONG: ad-hoc values differ per test — hard to maintain
def test_agent_loads_config_a(self):
    config = {'name': 'bot', 'behaviors': ['shape']}
    ...

def test_agent_loads_config_b(self):
    config = {'name': 'mybot', 'behaviors': ['shape', 'tests']}  # inconsistent
    ...
```
