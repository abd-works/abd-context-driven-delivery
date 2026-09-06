---
scanner: failing_test_api_scanner.py
---

# Rule: Design API Through Failing Tests

Write tests against the **real expected API before** implementing the code. The test **must fail initially** (RED phase). The failure message — `ImportError`, `AttributeError`, `TypeError` — reveals the complete API design: class names, constructor parameters, methods, return types. This is how tests drive implementation rather than simply verify it.

## DO

- Call the real expected class and method even when they do not exist yet.
- Set up real test data (real files, real paths via `tmp_path`) rather than mock objects.
- Assert real expected behavior so the test verifies something meaningful once implemented.

```python
def test_project_initializes_with_agent_config(self, tmp_path):
    # Given: real config file (tmp_path)
    agent_config_path = tmp_path / 'agents' / 'base' / 'agent.json'
    agent_config_path.parent.mkdir(parents=True)
    agent_config_path.write_text('{"name": "story_bot", "behaviors": ["shape"]}')

    # When: call REAL expected API (doesn't exist yet — will fail)
    from agile_bot.project import Project
    project = Project(
        project_path=tmp_path / 'projects' / 'test-project',
        agent_config_path=agent_config_path,
    )
    project.initialize()

    # Then: verify real behavior
    assert project.agent.name == 'story_bot'
    assert project.is_initialized is True
    # Test fails with ImportError/AttributeError until implemented — that's correct (RED)
```

## DON'T

- Use placeholder values (`None`, `'TODO'`, `{}`) that hide the real API.
- Skip the RED phase by implementing first, then writing a test that passes.
- Write vacuous tests that assert nothing meaningful.

```python
# WRONG: placeholders hide the API
project = None        # placeholder — reveals nothing
agent = 'TODO'        # placeholder — reveals nothing
assert project is None  # useless assertion

# WRONG: test passes immediately (GREEN before RED)
def test_something():
    assert True       # proves nothing
```
