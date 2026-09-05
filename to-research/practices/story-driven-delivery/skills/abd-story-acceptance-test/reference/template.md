# Acceptance Tests — Example and Shape

Worked example aligned with **`abd-story-specification/reference/examples.md`** (Manage Customer Orders domain).

Full Python/pytest file (plain scenario, scenario outline, Background fixture): **`../templates/acceptance-tests-example.py`**.

## What to notice

- **One class per story** — `TestCustomerPlacesAndTracksNewOrder`, `TestApplyDiscountCodeReducesOrderTotal`
- **One method per scenario** — outline rows use `@pytest.mark.parametrize` (joined `scenario` column)
- **Background** — shared `given_*` steps in a pytest fixture (`given_warehouse_and_customer`)
- **Orchestrator** — test methods call `given_*` / `when_*` / `then_*` helpers; helpers raise `NotImplementedError` until GREEN
- **Scenario docstrings** — copy Given/When/Then text from the spec scenario verbatim

## The shape of a good test file

```
test_<area_snake_case>.py
  Module docstring: area name + behaviors/stories covered
  Imports (stdlib → third-party → local)
  HELPER FUNCTIONS section
    given_*() / create_*() setup factories — parameterized, not duplicated
    when_*() actions
    then_*() / verify_*() assertions — parameterized, not duplicated
  FIXTURES section
    @pytest.fixture workspace_root (or domain equivalent)
  # STORY / BEHAVIOR: <Name> section comment
  class Test<BehaviorName>:
    def test_<outcome_snake_case>(self, workspace_root):
      # Given: <step text verbatim>
      # When: <step text verbatim>
      # Then: <step text verbatim>
  # STORY / BEHAVIOR: <Next Name> section comment
  class Test<NextBehaviorName>:
    ...

When helpers are shared across sub-epic files, extract them into:
  tests/<epic_name>/<epic_name>_helper.py
    class <EpicName>Helpers:
      given_*() / when_*() / then_*() methods only — no test_*() methods
  tests/<epic_name>/<sub_epic_name>/<sub_epic_name>.py
    class Test<Story>(<EpicName>Helpers): ...
```
