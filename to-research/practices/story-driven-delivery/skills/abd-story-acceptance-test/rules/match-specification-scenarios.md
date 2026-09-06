---
scanner: specification_match_scanner.py
---

# Rule: Match Specification Scenarios

Tests must match the corresponding **specification scenarios exactly**. Use the same terminology, variable names, and steps that the scenario states. Assertions verify exactly what the scenario's THEN conditions specify — nothing more, nothing less.

## DO

- Use exact variable names from the specification (`agent_name`, `workspace_root`, `config_path`).
- Assert only the outcomes the scenario explicitly states.

```python
# Specification scenario:
# GIVEN: configuration file exists at agents/base/agent.json
# WHEN: Agent is initialized with agent_name='story_bot'
# THEN: agent.config_path == agents/base/agent.json

def test_agent_loads_configuration_when_file_exists(self, workspace_root):
    # Given
    config_path = create_config_file(workspace_root, agent_name='story_bot')

    # When
    agent = Agent(agent_name='story_bot', workspace_root=workspace_root)
    agent.initialize()

    # Then — matches the THEN from the scenario exactly
    assert agent.config_path == workspace_root / 'agents' / 'base' / 'agent.json'
```

## DON'T

- Use different terminology from the specification (`name` when spec says `agent_name`).
- Assert internal state not mentioned in the scenario.

```python
# WRONG: different variable name from spec
agent = Agent(name='story_bot')       # spec says agent_name, not name

# WRONG: asserting internal detail not in scenario
assert agent._initialized == True     # not in the scenario THEN conditions
```
