"""
Thin Slice Parser Tests

Tests for md_thin_slice_to_story_graph.py: merging thin-slicing.md increments
into story-graph.json.

Behaviors: parse increment headers with names; extract ordered story names from
bullet lists; write increments array to graph; handle missing graph (create
scaffold); exit 2 on unrecognised format.
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
_SCRIPT = _SCRIPTS_DIR / "md_thin_slice_to_story_graph.py"

STANDARD_THIN_SLICING = """\
# Thin slicing -- PawPlace

## Increments

### Increment 1: `Walk-in driver`

**Outcome:** Customer finds nearest store and browses stock.

**Slicing notes:** No checkout, no accounts.

**Stories in this increment** *(order reflects flow):*

- *View Store Map*
- *View Store List*
- *Display Real-Time Stock Availability*

---

### Increment 2: `Click-and-collect`

**Outcome:** Customer pays online, picks up at store.

**Slicing notes:** Guest checkout only.

**Stories in this increment:**

- *Add Product to Cart*
- *Check Out as Guest*
- *Process Card Payment via StripeWave*

---
"""


def create_thin_slicing_md(workspace: Path, content: str = STANDARD_THIN_SLICING) -> Path:
    md_path = workspace / "thin-slicing.md"
    md_path.write_text(content, encoding="utf-8")
    return md_path


def create_existing_graph(workspace: Path) -> Path:
    graph = {"epics": [{"name": "Find a Store", "sub_epics": []}]}
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return graph_path


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


def find_increment(graph: dict, priority: int) -> dict:
    matches = [i for i in graph.get("increments", []) if i["priority"] == priority]
    assert matches, f"Increment {priority} not found in graph"
    return matches[0]


def verify_story_order(increment: dict, expected_names: list[str]) -> None:
    actual = [s["name"] for s in increment["stories"]]
    assert actual == expected_names, f"Expected {expected_names}, got {actual}"


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


@pytest.fixture
def thin_slicing_md(workspace: Path) -> Path:
    return create_thin_slicing_md(workspace)


@pytest.fixture
def graph_file(workspace: Path) -> Path:
    return create_existing_graph(workspace)


# ---------------------------------------------------------------------------
# STORY: Parse increments from thin-slicing markdown
# ---------------------------------------------------------------------------

class TestParseIncrementsIntoGraph:
    """Parse thin slicing -- given valid thin-slicing.md, write increments to graph."""

    def test_parses_two_increments(self, workspace, thin_slicing_md, graph_file):
        # Given
        # When
        result = run_parser(thin_slicing_md, graph_file)
        # Then
        assert result.returncode == 0
        graph = load_graph(graph_file)
        assert len(graph["increments"]) == 2

    def test_increment_has_correct_name(self, workspace, thin_slicing_md, graph_file):
        # Given
        # When
        run_parser(thin_slicing_md, graph_file)
        # Then
        graph = load_graph(graph_file)
        inc1 = find_increment(graph, priority=1)
        assert inc1["name"] == "Walk-in driver"

    def test_increment_has_correct_priority(self, workspace, thin_slicing_md, graph_file):
        # Given
        # When
        run_parser(thin_slicing_md, graph_file)
        # Then
        graph = load_graph(graph_file)
        inc2 = find_increment(graph, priority=2)
        assert inc2["priority"] == 2

    def test_stories_appear_in_declared_order(self, workspace, thin_slicing_md, graph_file):
        # Given
        # When
        run_parser(thin_slicing_md, graph_file)
        # Then
        graph = load_graph(graph_file)
        inc1 = find_increment(graph, priority=1)
        verify_story_order(
            inc1,
            ["View Store Map", "View Store List", "Display Real-Time Stock Availability"],
        )

    def test_stories_have_sequential_order_starting_at_one(self, workspace, thin_slicing_md, graph_file):
        # Given
        # When
        run_parser(thin_slicing_md, graph_file)
        # Then
        graph = load_graph(graph_file)
        inc1 = find_increment(graph, priority=1)
        orders = [s["sequential_order"] for s in inc1["stories"]]
        assert orders == [1.0, 2.0, 3.0]

    def test_preserves_existing_epics_in_graph(self, workspace, thin_slicing_md, graph_file):
        # Given: graph has existing epics
        # When
        run_parser(thin_slicing_md, graph_file)
        # Then: epics are still there
        graph = load_graph(graph_file)
        assert len(graph["epics"]) >= 1
        assert graph["epics"][0]["name"] == "Find a Store"

    def test_creates_graph_file_when_not_present(self, workspace, thin_slicing_md):
        # Given: no graph file yet
        new_graph = workspace / "new-graph.json"
        # When
        result = run_parser(thin_slicing_md, new_graph)
        # Then
        assert result.returncode == 0
        assert new_graph.exists()
        graph = load_graph(new_graph)
        assert "increments" in graph

    def test_replaces_existing_increments(self, workspace, thin_slicing_md, graph_file):
        # Given: graph already has stale increments
        graph = load_graph(graph_file)
        graph["increments"] = [{"name": "Old Increment", "priority": 99, "stories": []}]
        graph_file.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
        # When
        run_parser(thin_slicing_md, graph_file)
        # Then: stale increment is replaced
        graph = load_graph(graph_file)
        priorities = [i["priority"] for i in graph["increments"]]
        assert 99 not in priorities
        assert 1 in priorities


# ---------------------------------------------------------------------------
# STORY: Handle bad and mismatched input
# ---------------------------------------------------------------------------

class TestHandleBadInput:
    """Bad input -- parser exits with meaningful codes."""

    def test_missing_markdown_file_exits_nonzero(self, workspace, graph_file):
        # Given
        missing = workspace / "nonexistent.md"
        # When
        result = run_parser(missing, graph_file)
        # Then
        assert result.returncode != 0

    def test_unrecognised_format_exits_with_code_2(self, workspace, graph_file):
        # Given: markdown with no "### Increment N:" blocks
        md = workspace / "not-thin-slicing.md"
        md.write_text("# Title\n\nJust some notes. No increments.\n", encoding="utf-8")
        # When
        result = run_parser(md, graph_file)
        # Then: exit code 2 signals format mismatch for caller fallback
        assert result.returncode == 2

    def test_wrong_argument_count_exits_nonzero(self, workspace):
        # Given
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
