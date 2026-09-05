# Rule: Call Production Code Directly

Call production code **directly** in tests. Let tests fail naturally when the code does not exist or has bugs. Do not comment out production code calls, mock the class under test, or fabricate state to make tests pass. A `NameError` or `AttributeError` is the test driving the implementation — not a problem to hide.

## DO

- Call the real class and method.
- Let the test fail with a clear error if the code is not yet implemented.

```python
def test_agent_loads_config(self, workspace_root):
    # Given
    config_file = create_config_file(workspace_root, 'story_bot')

    # When — call real production code directly
    agent = Agent(workspace_root=workspace_root)
    agent.initialize()

    # Then
    assert agent.is_initialized
```

## DON'T

- Mock the class under test.
- Comment out the call because the code does not exist.
- Fake state by writing to private attributes.

```python
# WRONG: mocking the class under test
agent = Mock(spec=Agent)

# WRONG: commenting out the real call
# agent.initialize()  # TODO: implement
result = None  # placeholder

# WRONG: setting private state to make the test pass
agent._initialized = True
```
