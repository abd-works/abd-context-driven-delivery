"""
## Instructions (for skill maintainers — do NOT paste this block into project test files)

This template defines the required structure for acceptance test files produced by the
abd-story-acceptance-test skill.  When the skill writes test files for a
project, omit this Instructions section and emit only the sections below.

### Inputs
Work from whatever behavioral context is available:
- Spec-by-example scenarios (ideal) — encode Given/When/Then steps directly.
- Acceptance criteria (WHEN/THEN) — convert THEN to assertions, derive Given from preconditions.
- Stories + notes — identify normal, edge, and failure behaviors; make them concrete in tests.
- Unstructured context — extract observable behaviors, name them, then encode as tests.

### Layout
1. Module docstring  — one-line summary + list of behaviors covered in this file.
2. Imports           — stdlib → third-party → local; all at top.
3. HELPER FUNCTIONS  — reusable setup/action/assertion functions (each under 20 lines).
4. FIXTURES          — pytest fixtures defined in this test file (not conftest).
5. TEST CLASSES      — one class per behavior cluster (story, flow, feature area).
   Named TestExactBehaviorName (PascalCase of the behavior name from source).
   Each class contains one test method per scenario or condition.
   Every test method uses Given/When/Then comments and calls helper functions.

### Naming
| source level        | test artifact | example                                   |
|---------------------|---------------|-------------------------------------------|
| Area / flow / group | File name     | test_<area_snake_case>.py                 |
| Behavior / story    | Class name    | Test<ExactBehaviorName>                   |
| Scenario / condition| Method name   | test_<outcome_snake_case>                 |
"""

# =============================================================================
# {Sub-Epic Name} Tests
#
# Tests for all stories in '{Sub-Epic Name}' sub-epic:
# - {Story Name 1}
# - {Story Name 2}
# =============================================================================

import pytest
from pathlib import Path
# from <project>.module import ClassUnderTest

# =============================================================================
# HELPER FUNCTIONS — reusable operations (each under 20 lines)
# =============================================================================

def create_{domain_entity}({param}: {type}, workspace: Path) -> {ReturnType}:
    """Helper: Create {domain entity} with {description}."""
    # ... setup ...
    return {domain_entity}


def verify_{domain_state}({entity}: {Type}, {expected}: {type}) -> None:
    """Helper: Verify {domain entity} is in {expected state}."""
    assert {entity}.{observable_property} == {expected}


# =============================================================================
# FIXTURES — defined here, not in conftest
# =============================================================================

@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


# =============================================================================
# STORY: {Story Name 1}
# =============================================================================

class Test{StoryName1}:
    """{Story Name 1} — {one-line description}."""

    def test_{scenario_name}(self, workspace_root: Path) -> None:
        """
        SCENARIO: {Scenario Name}
        GIVEN: {precondition}
        WHEN: {action}
        THEN: {observable outcome}
        """
        # Given
        {entity} = create_{domain_entity}({arg}, workspace_root)

        # When
        result = {entity}.{domain_operation}()

        # Then
        verify_{domain_state}({entity}, {expected_value})

    def test_{edge_case_scenario}(self, workspace_root: Path) -> None:
        """
        SCENARIO: {Edge Case Scenario Name}
        GIVEN: {edge condition}
        WHEN: {action}
        THEN: {failure or edge outcome}
        """
        # Given
        {entity} = create_{domain_entity}_with_{edge_condition}(workspace_root)

        # When / Then
        with pytest.raises({ExpectedException}):
            {entity}.{domain_operation}()


# =============================================================================
# STORY: {Story Name 2}
# =============================================================================

class Test{StoryName2}:
    """{Story Name 2} — {one-line description}."""

    def test_{scenario_name}(self, workspace_root: Path) -> None:
        """
        SCENARIO: {Scenario Name}
        GIVEN: {precondition}
        WHEN: {action}
        THEN: {observable outcome}
        """
        # Given
        {entity} = create_{domain_entity}({arg}, workspace_root)

        # When
        result = {entity}.{domain_operation}()

        # Then
        assert result == {expected_value}
