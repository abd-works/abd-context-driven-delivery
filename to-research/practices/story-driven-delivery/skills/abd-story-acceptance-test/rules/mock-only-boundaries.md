---
scanner: mock_boundaries_scanner.py
---

# Rule: Mock Only Boundaries

Mock **only** at architectural boundaries — external APIs, network calls, third-party services, and genuinely uncontrollable dependencies. Do **not** mock internal business logic, the class under test, or file operations. Use real temp files (`tmp_path`) for file I/O. Tests that mock internal logic verify the mock, not the code.

## DO

- Mock external HTTP calls, remote APIs, or third-party services.
- Use `pytest`'s `tmp_path` for real file operations instead of mocking the file system.

```python
# Mock an external HTTP boundary
with patch('requests.get') as mock_get:
    mock_get.return_value.json.return_value = {'status': 'ok'}
    result = agent.fetch_remote_config('http://api.example.com')

# Real file I/O — no mock needed
config_file = tmp_path / 'config.json'
config_file.write_text('{"name": "story_bot"}')
agent = Agent(config_path=config_file)
```

## DON'T

- Mock the class under test.
- Mock internal business logic or validation methods.
- Mock file I/O when `tmp_path` works.

```python
# WRONG: mocking the class under test
agent = Mock(spec=Agent)          # tests nothing real

# WRONG: mocking internal logic
with patch.object(Agent, 'validate_config'):   # defeats the test

# WRONG: mocking file ops that could use tmp_path
with patch('builtins.open', mock_open(read_data='{}')): ...
```
