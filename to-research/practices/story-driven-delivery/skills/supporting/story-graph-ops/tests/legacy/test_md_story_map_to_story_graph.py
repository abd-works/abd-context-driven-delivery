"""
Story Map Parser Tests

Tests for md_story_map_to_story_graph.py: converting story-map.md tree syntax
into story-graph.json.

Behaviors: parse epics, sub-epics, and stories with actors; skip preamble;
stop at notes sections; produce valid graph JSON; reject wrong arg count.
"""
from __future__ import annotations

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
_SCRIPT = _SCRIPTS_DIR / "md_story_map_to_story_graph.py"


def create_story_map_md(workspace: Path, content: str, name: str = "story-map.md") -> Path:
    md_file = workspace / name
    md_file.write_text(content, encoding="utf-8")
    return md_file


def create_minimal_story_map(workspace: Path) -> Path:
    content = """\
# Story Map

(E) Find a Store
    (E) Browse Stores
        (S) user --> View Store Map
        (S) user --> View Store List
    (S) admin --> Manage Store Data
(E) Manage Orders
    (S) user --> Place Order
"""
    return create_story_map_md(workspace, content)


def parse_story_map(md_path: Path, out_path: Path) -> dict:
    """Run the parser script and return the loaded graph."""
    env = _env_with_scripts_on_path()
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(md_path), str(out_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"Parser failed:\n{result.stderr}"
    return json.loads(out_path.read_text(encoding="utf-8"))


def _env_with_scripts_on_path() -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_SCRIPTS_DIR)
    return env


def verify_epic_exists(graph: dict, epic_name: str) -> dict:
    matches = [e for e in graph["epics"] if e["name"] == epic_name]
    assert matches, f"Epic '{epic_name}' not found in graph"
    return matches[0]


def verify_story_in_epic(epic: dict, story_name: str) -> dict:
    stories = _collect_stories(epic)
    matches = [s for s in stories if s["name"] == story_name]
    assert matches, f"Story '{story_name}' not found under epic '{epic['name']}'"
    return matches[0]


def _collect_stories(node: dict) -> list[dict]:
    stories: list[dict] = []
    for sg in node.get("story_groups", []):
        stories.extend(sg.get("stories", []))
    for sub in node.get("sub_epics", []):
        stories.extend(_collect_stories(sub))
    return stories


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


@pytest.fixture
def out_graph(workspace: Path) -> Path:
    return workspace / "story-graph.json"


# ---------------------------------------------------------------------------
# STORY: Parse story map into graph
# ---------------------------------------------------------------------------

class TestParseStoryMapIntoGraph:
    """Parse story map -- given a valid story-map.md, produce a graph with epics."""

    def test_parses_top_level_epics(self, workspace, out_graph):
        # Given
        md = create_minimal_story_map(workspace)
        # When
        graph = parse_story_map(md, out_graph)
        # Then
        assert len(graph["epics"]) == 2
        verify_epic_exists(graph, "Find a Store")
        verify_epic_exists(graph, "Manage Orders")

    def test_parses_sub_epics(self, workspace, out_graph):
        # Given
        md = create_minimal_story_map(workspace)
        # When
        graph = parse_story_map(md, out_graph)
        # Then
        epic = verify_epic_exists(graph, "Find a Store")
        sub_names = [s["name"] for s in epic.get("sub_epics", [])]
        assert "Browse Stores" in sub_names

    def test_parses_stories_with_actor(self, workspace, out_graph):
        # Given
        md = create_minimal_story_map(workspace)
        # When
        graph = parse_story_map(md, out_graph)
        # Then
        epic = verify_epic_exists(graph, "Find a Store")
        story = verify_story_in_epic(epic, "View Store Map")
        assert story["story_type"] == "user"

    def test_parses_optional_stories_same_as_required(self, workspace, out_graph):
        # Given
        content = "(E) Catalog\n    opt (S) user --> Browse by Category\n"
        md = create_story_map_md(workspace, content)
        # When
        graph = parse_story_map(md, out_graph)
        # Then
        epic = verify_epic_exists(graph, "Catalog")
        verify_story_in_epic(epic, "Browse by Category")

    def test_skips_preamble_before_first_epic(self, workspace, out_graph):
        # Given
        content = (
            "# Title\n\nSome intro text.\n\n---\n\n"
            "(E) Real Epic\n    (S) user --> Real Story\n"
        )
        md = create_story_map_md(workspace, content)
        # When
        graph = parse_story_map(md, out_graph)
        # Then
        assert len(graph["epics"]) == 1
        verify_epic_exists(graph, "Real Epic")

    def test_stops_at_notes_section(self, workspace, out_graph):
        # Given
        content = (
            "(E) Epic One\n    (S) user --> Story A\n\n"
            "## Consolidation Notes\n\n"
            "(E) Epic Two\n    (S) user --> Story B\n"
        )
        md = create_story_map_md(workspace, content)
        # When
        graph = parse_story_map(md, out_graph)
        # Then: Epic Two is after the notes section and must not appear
        assert len(graph["epics"]) == 1
        verify_epic_exists(graph, "Epic One")

    def test_stories_have_empty_ac_and_scenarios_by_default(self, workspace, out_graph):
        # Given
        md = create_minimal_story_map(workspace)
        # When
        graph = parse_story_map(md, out_graph)
        # Then
        epic = verify_epic_exists(graph, "Find a Store")
        story = verify_story_in_epic(epic, "View Store Map")
        assert story["acceptance_criteria"] == []
        assert story["scenarios"] == []


# ---------------------------------------------------------------------------
# STORY: Handle bad input gracefully
# ---------------------------------------------------------------------------

class TestHandleBadInput:
    """Bad input -- script exits with error and does not write partial output."""

    def test_wrong_argument_count_exits_nonzero(self, workspace):
        # Given: only one argument instead of two
        env = _env_with_scripts_on_path()
        # When
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "only-one-arg"],
            capture_output=True,
            text=True,
            env=env,
        )
        # Then
        assert result.returncode != 0

    def test_missing_input_file_exits_nonzero(self, workspace, out_graph):
        # Given
        missing = workspace / "nonexistent.md"
        env = _env_with_scripts_on_path()
        # When
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(missing), str(out_graph)],
            capture_output=True,
            text=True,
            env=env,
        )
        # Then
        assert result.returncode != 0
