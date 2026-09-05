# Rule: Create Parameterized Tests for Scenarios

When specification scenarios include an **Examples table**, create **parameterized tests** using `@pytest.mark.parametrize`. Each row in the Examples table becomes a separate test case. Do not write a single test that only exercises one example, and do not duplicate test methods per row.

## DO

- Map each Examples column to a `parametrize` parameter.
- Name the combined test so the parameter values appear in the test ID.

```python
@pytest.mark.parametrize('input_paths,expected_count', [
    (['path/a', 'path/b'], 2),
    (['path/c'],            1),
    ([],                    0),
])
def test_loader_counts_paths(self, workspace_root, input_paths, expected_count):
    # Given
    loader = create_loader(workspace_root, input_paths)

    # When
    result = loader.count()

    # Then
    assert result == expected_count
```

## DON'T

- Hardcode a single example when the specification has a table.
- Create one test method per row.

```python
# WRONG: separate method per row
def test_with_two_paths(self): ...
def test_with_one_path(self):  ...

# WRONG: single hardcoded example from a multi-row table
def test_loader_counts_paths(self):
    loader = create_loader(workspace_root, ['path/a', 'path/b'])
    assert loader.count() == 2  # only one of several rows tested
```
