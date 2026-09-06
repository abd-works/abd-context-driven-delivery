---
scanner: fixture_placement_scanner.py
---

# Rule: Define Fixtures in Test File

Define **pytest fixtures in the same test file** that uses them, not in a separate `conftest.py`. Only truly cross-cutting fixtures (generic filesystem helpers, shared infrastructure) belong in a base `conftest.py`. Story-specific fixtures stay local.

## DO

- Declare fixtures at the top of the test file, after helpers.
- Keep them focused on what the tests in that file need.

```python
# In test_edit_story_graph.py

@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

@pytest.fixture
def story_graph(workspace_root: Path) -> StoryGraph:
    return create_story_graph(workspace_root)
```

## DON'T

- Create a new `conftest.py` for agent- or sub-epic-specific fixtures.
- Create shared files before there is an explicit, demonstrated need.

```python
# WRONG: story-specific fixture in conftest.py
# conftest.py
@pytest.fixture
def story_graph(tmp_path):  # belongs in test_edit_story_graph.py, not here
    ...
```
