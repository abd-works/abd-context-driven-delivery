---
scanner: consistent_vocabulary_scanner.py
---

# Rule: Consistent Vocabulary

Use **one word per concept** across the entire codebase. Pick a verb and stick to it: `create` (not `build`/`make`/`construct`), `verify` (not `check`/`assert`/`validate`), `load` (not `fetch`/`get`/`retrieve`). Document the vocabulary at the top of the test file when it helps reviewers.

## DO

- Use the same verb for the same operation everywhere.

```python
# Consistent vocabulary: create / verify / load
def create_agent(name: str, workspace: Path) -> Agent: ...
def create_config(workspace: Path, name: str) -> Path: ...
def create_workspace(tmp_path: Path) -> Path: ...

def verify_agent_initialized(agent: Agent) -> None: ...
def verify_config_valid(config: dict) -> None: ...

def load_config(path: Path) -> dict: ...
```

## DON'T

- Mix synonyms for the same concept.

```python
# WRONG: three verbs for creation
def create_agent(...): ...
def build_config(...):   # should be create_config
def make_workspace(...): # should be create_workspace
```
