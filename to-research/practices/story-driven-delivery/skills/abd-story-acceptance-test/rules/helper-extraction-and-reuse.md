---
scanner: helper_extraction_scanner.py
---

# Rule: Helper Extraction and Reuse

Extract **duplicate test setup** into reusable helper functions. Keep test method bodies focused on the scenario behavior, not on building infrastructure. Group helpers by purpose: `create_*` for factories, `verify_*` for assertions, `load_*` for data loading.

## DO

- Extract any setup or verification that appears in two or more tests.
- Name helpers after their domain purpose (see **consistent-vocabulary**).

```python
def create_agent_with_config(name: str, workspace: Path) -> Agent:
    """Helper: Create fully initialized agent."""
    config = create_config_file(workspace, name)
    agent = Agent(agent_name=name, workspace_root=workspace)
    agent.initialize()
    return agent

# Tests reuse the helper — no duplication
def test_agent_reports_correct_name(self, workspace_root):
    agent = create_agent_with_config('story_bot', workspace_root)
    assert agent.name == 'story_bot'

def test_agent_is_initialized(self, workspace_root):
    agent = create_agent_with_config('story_bot', workspace_root)
    assert agent.is_initialized
```

## DON'T

- Copy the same 10 lines of setup into every test method.

```python
# WRONG: duplicated setup in every test
def test_agent_reports_name(self):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    config_dir = workspace / 'agents' / 'base'
    config_dir.mkdir(parents=True)
    config_file = config_dir / 'agent.json'
    config_file.write_text('{"name": "story_bot"}')
    agent = Agent('story_bot', workspace)
    agent.initialize()
    assert agent.name == 'story_bot'

def test_agent_is_initialized(self):
    # ... same 10 lines again ...
```
