---
scanner: given_when_then_helpers_scanner.py
---

# Rule: Use Given/When/Then Helpers

Use **reusable helper functions** for any inline code block of 4 or more lines. Place helpers at the right scope: story-level helpers inside the test class, sub-epic helpers at module level, and cross-epic helpers in a shared file. Name helpers with `given_`, `when_`, or `then_` prefixes when the domain language calls for it, but prioritise **domain-verb naming** over mechanical prefixes.

## DO

- Extract 4+ line inline blocks to named helpers.
- Scope helpers to the level that needs them.

```python
def given_bot_config_exists(workspace: Path, name: str = 'story_bot') -> Path:
    return create_config_file(workspace, name)

def when_bot_instantiated(workspace: Path, name: str) -> Bot:
    return Bot(bot_name=name, workspace_root=workspace)

def then_bot_uses_correct_directories(bot: Bot, workspace: Path) -> None:
    assert bot.workspace_root == workspace
    assert bot.config_path.parent.exists()

class TestBotInitialization:
    def test_bot_initializes_with_config(self, workspace_root):
        given_bot_config_exists(workspace_root, 'story_bot')
        bot = when_bot_instantiated(workspace_root, 'story_bot')
        then_bot_uses_correct_directories(bot, workspace_root)
```

## DON'T

- Leave 4+ line inline operations inside test methods.

```python
# WRONG: inline multi-line setup
def test_bot_initializes(self, tmp_path):
    config_dir = tmp_path / 'agents' / 'base'
    config_dir.mkdir(parents=True)
    config_file = config_dir / 'agent.json'
    config_file.write_text('{"name": "story_bot"}')
    # ... more inline code ...
```
