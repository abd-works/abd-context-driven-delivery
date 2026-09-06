# Rule: Self-Documenting Tests

Tests are self-documenting through **code structure** — imports, constructor calls, and assertions show the API design. Do not add verbose comments that explain what will fail or restate what the code already says. Let the code speak for itself.

## DO

- Let imports reveal which classes are needed.
- Let constructors show the required parameters.
- Let assertions show what is expected.

```python
def test_generator_creates_server_for_test_bot(self, workspace_root):
    # Given
    config_file = create_bot_config(workspace_root, 'test_bot', ['shape'])

    # When
    from agile_bot.mcp_server_generator import MCPServerGenerator
    generator = MCPServerGenerator(
        bot_name='test_bot',
        config_path=config_file,
        workspace_root=workspace_root,
    )
    server_file = generator.generate_server()

    # Then
    assert server_file.exists()
    assert server_file.name == 'test_bot_server.py'
```

## DON'T

- Add comments explaining that the test will fail or what API is needed — the code shows this.
- Restate what constructors and assertions already communicate.

```python
# WRONG: verbose noise
    # TEST WILL FAIL: ImportError - MCPServerGenerator doesn't exist yet
    # Shows API needs: MCPServerGenerator(bot_name, config_path, workspace_root)
    # Shows API needs: generator.generate_server() returns Path
    # The code above already communicates all of this!

    assert server_file.exists()
```
