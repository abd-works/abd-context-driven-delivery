---
scanner: exact_variable_names_scanner.py
---

# Rule: Use Exact Variable Names

Use the **exact variable names** from the specification scenario in both the test code and the production code. When a scenario says `agent_name`, `workspace_root`, or `config_path`, use those exact identifiers — not abbreviations or synonyms. This keeps the traceability chain from spec → test → production intact.

## DO

- Copy variable names verbatim from the scenario's Given/When/Then terminology.

```python
# Specification uses: agent_name, workspace_root, config_path
agent = Agent(agent_name='story_bot', workspace_root=workspace_root)
assert agent.config_path == workspace_root / 'agents' / 'base' / 'agent.json'
```

## DON'T

- Shorten, abbreviate, or rename variables from the specification.

```python
# WRONG: different names from specification
agent = Agent(name='story_bot')          # spec says agent_name
agent = Agent(workspace=workspace_root)  # spec says workspace_root
assert agent.path == ...                 # spec says config_path
```
