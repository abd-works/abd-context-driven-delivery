---
scanner: orchestrator_pattern_scanner.py
scanner_note: Python / pytest — use the equivalent scanner for the target language
---

# Rule: pytest Orchestrator Pattern

Use the **orchestrator pattern** for story-based tests — no step-definition files. Every test method (under 20 lines) shows the Given-When-Then flow by calling named helper functions. Helper functions handle details (also under 20 lines). Test classes (or equivalent groupings) stay under 300 lines. Examples below are Python / pytest — apply the same structure in the idioms of the target language and framework.

## DO

- Test methods show the flow; helpers execute the details.
- Use `# Given`, `# When`, `# Then` comment labels inside every test method.
- Keep test methods under 20 lines; extract anything longer to a helper.
- Keep helper functions under 20 lines each.

```python
# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_config_file(workspace: Path, name: str = 'bot') -> Path:
    """Helper: Create bot configuration file."""
    config_dir = workspace / 'agents' / 'base'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'agent.json'
    config_file.write_text(f'{{"name": "{name}"}}')
    return config_file

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

# ============================================================================
# ORCHESTRATOR TESTS
# ============================================================================

class TestAgentInitialization:
    def test_agent_initializes_with_config(self, workspace_root):
        # Given
        config = create_config_file(workspace_root, 'story_bot')

        # When
        agent = Agent(agent_name='story_bot', workspace_root=workspace_root)
        agent.initialize()

        # Then
        assert agent.is_initialized
        assert agent.config_path == config
```

## DON'T

- Use feature files or `@given`/`@when`/`@then` step decorators.
- Inline 10+ lines of setup directly inside test methods.
- Write test methods longer than 20 lines.

```python
# WRONG: step definitions
@given('config file exists')
def step_config_exists(context): ...

# WRONG: all setup inline — extract to helpers
def test_agent(self, tmp_path):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    config_dir = workspace / 'agents' / 'base'
    config_dir.mkdir(parents=True)
    config_file = config_dir / 'agent.json'
    config_file.write_text('{"name": "bot"}')
    agent = Agent('bot', workspace)
    # ... 15 more lines ...
```
