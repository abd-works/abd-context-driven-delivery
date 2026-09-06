"""
Acceptance Criteria Parser Tests

Tests for md_acceptance_criteria_to_story_graph.py: merging acceptance-criteria.md
content into an existing story-graph.json.

Behaviors: parse story blocks with numbered AC items; inject into matching stories;
report unmatched names; reject missing files; exit 2 on unrecognised format.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import subprocess
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
_SCRIPT = _SCRIPTS_DIR / "md_acceptance_criteria_to_story_graph.py"

STANDARD_GRAPH = {
    "epics": [
        {
            "name": "Find a Store",
            "sub_epics": [
                {
                    "name": "Browse Stores",
                    "story_groups": [
                        {
                            "stories": [
                                {
                                    "name": "View Store Map",
                                    "story_type": "user",
                                    "acceptance_criteria": [],
                                    "scenarios": [],
                                },
                                {
                                    "name": "View Store List",
                                    "story_type": "user",
                                    "acceptance_criteria": [],
                                    "scenarios": [],
                                },
                            ]
                        }
                    ],
                }
            ],
        }
    ]
}

STANDARD_AC_CONTENT = """\
# Acceptance Criteria -- Increment 1: Walk-in driver

---

## Story: View Store Map

**Story type:** user

### Domain terms

- *Store* -- physical retail location

### Acceptance criteria

1. **WHEN** the customer opens the Store Locator
   **THEN** the system displays all stores on a Map View
   **Evidence:** requirements.md -- line 11

2. **WHEN** the customer selects a store point
   **THEN** the system displays the store's address and hours
   **Evidence:** requirements.md -- line 9

---

## Story: View Store List

**Story type:** user

### Domain terms

- *Store* -- physical retail location

### Acceptance criteria

1. **WHEN** the customer opens the Store Locator
   **THEN** the system offers a List View of all stores
   **Evidence:** requirements.md -- line 11

---
"""


def create_graph_file(workspace: Path, graph: dict) -> Path:
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return graph_path


def create_ac_md(workspace: Path, content: str = STANDARD_AC_CONTENT) -> Path:
    md_path = workspace / "acceptance-criteria.md"
    md_path.write_text(content, encoding="utf-8")
    return md_path


def run_parser(md_path: Path, graph_path: Path) -> subprocess.CompletedProcess:
    env = _env_with_scripts_on_path()
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(md_path), str(graph_path)],
        capture_output=True,
        text=True,
        env=env,
    )


def _env_with_scripts_on_path() -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_SCRIPTS_DIR)
    return env


def load_graph(graph_path: Path) -> dict:
    return json.loads(graph_path.read_text(encoding="utf-8"))


def find_story(graph: dict, story_name: str) -> dict:
    for story in _all_stories(graph):
        if story["name"] == story_name:
            return story
    raise AssertionError(f"Story '{story_name}' not found in graph")


def _all_stories(graph: dict) -> list[dict]:
    stories: list[dict] = []
    for epic in graph.get("epics", []):
        stories.extend(_stories_from_node(epic))
    return stories


def _stories_from_node(node: dict) -> list[dict]:
    stories: list[dict] = []
    for sg in node.get("story_groups", []):
        stories.extend(sg.get("stories", []))
    for sub in node.get("sub_epics", []):
        stories.extend(_stories_from_node(sub))
    return stories


def verify_ac_injected(story: dict, expected_count: int) -> None:
    assert len(story["acceptance_criteria"]) == expected_count, (
        f"Expected {expected_count} AC items, got {len(story['acceptance_criteria'])}"
    )


def create_graph_with_scenario_on_first_story(workspace: Path) -> Path:
    graph = copy.deepcopy(STANDARD_GRAPH)
    graph["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0]["scenarios"] = [
        {"name": "Map shows all stores", "steps": ["Given a store exists"]}
    ]
    return create_graph_file(workspace, graph)


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


@pytest.fixture
def graph_file(workspace: Path) -> Path:
    return create_graph_file(workspace, copy.deepcopy(STANDARD_GRAPH))


@pytest.fixture
def ac_md(workspace: Path) -> Path:
    return create_ac_md(workspace)


# ---------------------------------------------------------------------------
# STORY: Inject acceptance criteria into graph
# ---------------------------------------------------------------------------

class TestInjectAcceptanceCriteria:
    """Inject AC -- matched story names receive their AC items from the markdown."""

    def test_injects_ac_into_matched_story(self, workspace, graph_file, ac_md):
        # Given: graph with View Store Map, AC markdown with 2 items for it
        # When
        result = run_parser(ac_md, graph_file)
        # Then
        assert result.returncode == 0
        graph = load_graph(graph_file)
        story = find_story(graph, "View Store Map")
        verify_ac_injected(story, expected_count=2)

    def test_injects_ac_into_all_matched_stories(self, workspace, graph_file, ac_md):
        # Given: markdown has AC for both View Store Map and View Store List
        # When
        result = run_parser(ac_md, graph_file)
        # Then
        assert result.returncode == 0
        graph = load_graph(graph_file)
        map_story = find_story(graph, "View Store Map")
        list_story = find_story(graph, "View Store List")
        verify_ac_injected(map_story, expected_count=2)
        verify_ac_injected(list_story, expected_count=1)

    def test_ac_items_preserve_when_then_format(self, workspace, graph_file, ac_md):
        # Given
        # When
        run_parser(ac_md, graph_file)
        # Then
        graph = load_graph(graph_file)
        story = find_story(graph, "View Store Map")
        first_ac = story["acceptance_criteria"][0]
        assert "**WHEN**" in first_ac
        assert "**THEN**" in first_ac

    def test_unmatched_story_exits_nonzero(self, workspace, graph_file):
        # Given: AC for a story not in the graph
        content = STANDARD_AC_CONTENT + (
            "\n## Story: Nonexistent Story\n\n"
            "### Acceptance criteria\n\n"
            "1. **WHEN** anything happens\n   **THEN** something occurs\n"
        )
        md = create_ac_md(workspace, content)
        # When
        result = run_parser(md, graph_file)
        # Then: exit nonzero, graph still updated for matched stories
        assert result.returncode != 0
        graph = load_graph(graph_file)
        matched = find_story(graph, "View Store Map")
        verify_ac_injected(matched, expected_count=2)

    def test_preserves_existing_scenarios_on_story(self, workspace):
        # Given: a story that already has a scenario alongside empty AC
        graph_path = create_graph_with_scenario_on_first_story(workspace)
        md = create_ac_md(workspace)
        # When
        run_parser(md, graph_path)
        # Then: scenario is still present after AC injection
        loaded = load_graph(graph_path)
        story = find_story(loaded, "View Store Map")
        assert len(story["scenarios"]) == 1


# ---------------------------------------------------------------------------
# STORY: Handle bad and mismatched input
# ---------------------------------------------------------------------------

class TestHandleBadInput:
    """Bad input -- parser exits cleanly with informative codes."""

    def test_missing_markdown_file_exits_nonzero(self, workspace, graph_file):
        # Given
        missing_md = workspace / "missing.md"
        # When
        result = run_parser(missing_md, graph_file)
        # Then
        assert result.returncode != 0

    def test_missing_graph_file_exits_nonzero(self, workspace, ac_md):
        # Given
        missing_graph = workspace / "missing-graph.json"
        # When
        result = run_parser(ac_md, missing_graph)
        # Then
        assert result.returncode != 0

    def test_unrecognised_format_exits_with_code_2(self, workspace, graph_file):
        # Given: plain text with no "## Story:" blocks
        md = workspace / "plain.md"
        md.write_text("This is not an acceptance criteria file.\n\nNo story blocks here.", encoding="utf-8")
        # When
        result = run_parser(md, graph_file)
        # Then: exit code 2 signals format mismatch for caller fallback
        assert result.returncode == 2

    def test_wrong_argument_count_exits_nonzero(self, workspace):
        # Given
        env = _env_with_scripts_on_path()
        # When
        result = subprocess.run(
            [sys.executable, str(_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
        )
        # Then
        assert result.returncode != 0
