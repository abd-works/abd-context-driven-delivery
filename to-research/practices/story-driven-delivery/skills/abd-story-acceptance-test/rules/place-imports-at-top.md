---
scanner: import_placement_scanner.py
---

# Rule: Place Imports at Top

All imports must appear at the **top of the test file**, after the module docstring, before any code. Group imports: (1) standard library, (2) third-party, (3) local project. Never place imports inside functions or test methods.

## DO

```python
"""Agent configuration tests."""
import json
import pytest
from pathlib import Path

from agile_bot.agents.base_bot.src.agent import Agent
from agile_bot.agents.base_bot.src.config_loader import ConfigLoader
```

## DON'T

- Place imports inside functions or after code.

```python
def test_agent_initializes(self, tmp_path):
    from pathlib import Path            # WRONG: import inside function
    from agile_bot.agent import Agent   # WRONG: import inside test method
    ...
```
