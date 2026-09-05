"""Shared Given/When/Then helpers for drawio_story_sync acceptance tests.

Epic: Drawio Story Sync. Reused by CLI, outline sync, and increment-scope stories.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Tuple

import pytest

_SKILL_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _SKILL_ROOT / "scripts"
_OPS_SCRIPTS = _SKILL_ROOT.parent / "story-graph-ops" / "scripts"

requires_story_graph_ops = pytest.mark.skipif(
    not _OPS_SCRIPTS.is_dir(),
    reason="story-graph-ops skill not present as sibling (skills/supporting/story-graph-ops/scripts)",
)

MINIMAL_STORY_GRAPH: Dict[str, Any] = {
    "epics": [
        {
            "name": "Epic A",
            "sequential_order": 1.0,
            "sub_epics": [
                {
                    "name": "Sub A",
                    "sequential_order": 1.0,
                    "sub_epics": [],
                    "story_groups": [
                        {
                            "name": None,
                            "type": "and",
                            "connector": None,
                            "stories": [
                                {
                                    "name": "Story One",
                                    "sequential_order": 1.0,
                                    "story_type": "user",
                                    "users": [],
                                    "acceptance_criteria": [],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ],
    "increments": [],
}

STORY_GRAPH_WITH_ONE_INCREMENT: Dict[str, Any] = {
    "epics": MINIMAL_STORY_GRAPH["epics"],
    "increments": [
        {
            "name": "Slice A",
            "priority": 1,
            "stories": [{"name": "Story One", "sequential_order": 1.0}],
            "description": "Smoke increment",
            "goal": "Cover Story One",
        }
    ],
}


# =============================================================================
# Given
# =============================================================================


def given_cli_pythonpath_env() -> Dict[str, str]:
    """Given: PYTHONPATH includes this skill's scripts and story-graph-ops scripts."""
    env = os.environ.copy()
    parts = [str(_SCRIPTS.resolve()), str(_OPS_SCRIPTS.resolve())]
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(parts + ([prev] if prev else []))
    return env


def given_minimal_story_graph_file(workspace: Path) -> Path:
    """Given: story-graph.json with one epic / sub-epic / story."""
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps(MINIMAL_STORY_GRAPH), encoding="utf-8")
    return graph_path


def given_story_graph_file_with_one_increment(workspace: Path) -> Path:
    """Given: story-graph.json with one increment referencing Story One."""
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps(STORY_GRAPH_WITH_ONE_INCREMENT), encoding="utf-8")
    return graph_path


def given_empty_story_graph_file(workspace: Path) -> Path:
    """Given: story-graph.json with no epics and no increments."""
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps({"epics": [], "increments": []}), encoding="utf-8")
    return graph_path


def given_minimal_epic_graph_with_story_users(
    workspace: Path, story_users: list
) -> Tuple[Path, Path, Dict[str, Any]]:
    """Given: story-graph.json with one story and specified users; paths for graph and drawio."""
    graph: Dict[str, Any] = {
        "epics": [
            {
                "name": "Epic A",
                "sequential_order": 1.0,
                "sub_epics": [
                    {
                        "name": "Sub A",
                        "sequential_order": 1.0,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "name": "",
                                "sequential_order": 0.0,
                                "type": "and",
                                "connector": None,
                                "stories": [
                                    {
                                        "name": "Story One",
                                        "sequential_order": 1.0,
                                        "story_type": "user",
                                        "users": list(story_users),
                                        "acceptance_criteria": [],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
        "increments": [],
    }
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps(graph), encoding="utf-8")
    drawio_path = workspace / "story-map.drawio"
    return graph_path, drawio_path, graph


def given_two_story_columns_and_actor_chip_over_story_b_column() -> tuple:
    """Given: two story columns; actor chip (tool fill) sits over column B."""
    from drawio_story_sync.drawio_element import DrawIOElement

    st_a = SimpleNamespace(
        cell_id="e/se/story-a",
        position=SimpleNamespace(x=0.0, y=50.0),
        boundary=SimpleNamespace(width=50.0, height=50.0),
        users=[],
    )
    st_b = SimpleNamespace(
        cell_id="e/se/story-b",
        position=SimpleNamespace(x=100.0, y=50.0),
        boundary=SimpleNamespace(width=50.0, height=50.0),
        users=[],
    )
    actor = DrawIOElement("e/se/story-a/actor-game-master", "Game Master")
    actor.apply_style_for_type("actor")
    actor.set_position(110.0, 10.0)
    actor.set_size(50.0, 20.0)
    return [st_a, st_b], [actor], st_a, st_b


# =============================================================================
# When
# =============================================================================


def when_cli_runs_render_outline(
    graph: Path, out_drawio: Path, env: Dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """When: drawio_story_sync_cli render --mode outline."""
    cli = _SCRIPTS / "drawio_story_sync_cli.py"
    return subprocess.run(
        [
            sys.executable,
            str(cli),
            "render",
            "--mode",
            "outline",
            "--graph",
            str(graph),
            "--out",
            str(out_drawio),
        ],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS),
    )


def when_cli_runs_render_increments(
    graph: Path, out_drawio: Path, env: Dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """When: drawio_story_sync_cli render --mode increments."""
    cli = _SCRIPTS / "drawio_story_sync_cli.py"
    return subprocess.run(
        [
            sys.executable,
            str(cli),
            "render",
            "--mode",
            "increments",
            "--graph",
            str(graph),
            "--out",
            str(out_drawio),
        ],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS),
    )


def when_cli_runs_sync_outline(
    outline: Path, graph: Path, env: Dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """When: drawio_story_sync_cli sync from outline (default diagram type)."""
    cli = _SCRIPTS / "drawio_story_sync_cli.py"
    return subprocess.run(
        [
            sys.executable,
            str(cli),
            "sync",
            "--drawio",
            str(outline),
            "--graph",
            str(graph),
        ],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS),
    )


def when_cli_runs_sync_with_diagram_type(
    drawio: Path,
    graph: Path,
    diagram_type: str,
    env: Dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """When: drawio_story_sync_cli sync with explicit --diagram-type."""
    cli = _SCRIPTS / "drawio_story_sync_cli.py"
    return subprocess.run(
        [
            sys.executable,
            str(cli),
            "sync",
            "--diagram-type",
            diagram_type,
            "--drawio",
            str(drawio),
            "--graph",
            str(graph),
        ],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS),
    )


def given_three_story_row_with_actor_chip_above_first_column():
    """Given: three story columns in a row; one actor chip above the first column."""
    from drawio_story_sync.drawio_element import DrawIOElement

    s1 = SimpleNamespace(
        cell_id="r/s1",
        position=SimpleNamespace(x=0.0, y=100.0),
        boundary=SimpleNamespace(width=50.0, height=50.0),
        users=[],
    )
    s2 = SimpleNamespace(
        cell_id="r/s2",
        position=SimpleNamespace(x=70.0, y=100.0),
        boundary=SimpleNamespace(width=50.0, height=50.0),
        users=[],
    )
    s3 = SimpleNamespace(
        cell_id="r/s3",
        position=SimpleNamespace(x=140.0, y=100.0),
        boundary=SimpleNamespace(width=50.0, height=50.0),
        users=[],
    )
    chip = DrawIOElement("1", "Game Master")
    chip.apply_style_for_type("actor")
    chip.set_position(0.0, 40.0)
    chip.set_size(50.0, 20.0)
    return [s1, s2, s3], [chip]


def when_outline_is_rendered_loaded_and_diffed_against_canonical(
    graph: Dict[str, Any], drawio_path: Path
):
    """When: render outline from StoryMap, save, load, generate_update_report vs same graph."""
    from drawio_story_sync.drawio_story_map import DrawIOStoryMap
    from story_graph_ops.nodes import StoryMap

    sm0 = StoryMap(graph)
    dm = DrawIOStoryMap()
    dm.render_from_story_map(sm0, layout_data=None)
    dm.save(drawio_path)
    loaded = DrawIOStoryMap.load(drawio_path)
    sm1 = StoryMap(graph)
    return loaded.generate_update_report(sm1)


def when_synchronizer_renders_with_increment_scope(
    graph_path: Path,
    out_drawio: Path,
    increment_label: str,
) -> Dict[str, Any]:
    """When: DrawIOSynchronizer.render uses increment scope."""
    from drawio_story_sync.story_io_synchronizer import DrawIOSynchronizer

    sync = DrawIOSynchronizer()
    return sync.render(
        graph_path,
        out_drawio,
        renderer_command="render-exploration",
        scope=f"increment:{increment_label}",
    )


def when_cli_module_is_loaded():
    """When: drawio_story_sync_cli.py is loaded as a module (pure helpers)."""
    cli_path = _SCRIPTS / "drawio_story_sync_cli.py"
    spec = importlib.util.spec_from_file_location("drawio_story_sync_cli", cli_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def when_outline_row_personas_are_applied(ordered_stories, persona_nodes):
    """When: outline row persona assignment runs on ordered stories."""
    from drawio_story_sync.drawio_story_map import _apply_outline_row_personas

    _apply_outline_row_personas(ordered_stories, persona_nodes)


def then_story_row_users_match_forward_fill_from_chip(stories, expected_user: str) -> None:
    """Then: each story.users is a single-element list with expected_user."""
    for s in stories:
        assert s.users == [expected_user]
        assert getattr(s, "_had_actor_cells", False) is True


def then_chip_over_second_column_assigns_persona_to_b_only(st_a, st_b) -> None:
    """Then: first story empty users; second gets Game Master; row had actor cells."""
    assert st_a.users == []
    assert st_b.users == ["Game Master"]
    assert getattr(st_a, "_had_actor_cells", False) is True
    assert getattr(st_b, "_had_actor_cells", False) is True


# =============================================================================
# Then
# =============================================================================


def then_subprocess_succeeded(proc: subprocess.CompletedProcess[str]) -> None:
    """Then: process exit code is zero."""
    assert proc.returncode == 0, proc.stderr + proc.stdout


def then_last_stdout_line_is_ok_json(proc: subprocess.CompletedProcess[str]) -> None:
    """Then: last stdout line parses as JSON with status ok."""
    line = proc.stdout.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload.get("status") == "ok"


def then_drawio_file_exists_and_has_min_size(path: Path, min_bytes: int = 100) -> None:
    """Then: path exists and file size exceeds min_bytes."""
    assert path.is_file() and path.stat().st_size > min_bytes


def then_payload_refreshed_diagrams_include(
    proc: subprocess.CompletedProcess[str], paths: Tuple[Path, ...]
) -> None:
    """Then: JSON payload refreshed_diagrams includes each path string."""
    line = proc.stdout.strip().splitlines()[-1]
    payload = json.loads(line)
    refreshed = payload.get("refreshed_diagrams", [])
    for p in paths:
        assert str(p) in refreshed


def then_story_users_changes_list_is_empty(report) -> None:
    """Then: no persona deltas on the update report."""
    assert report.story_users_changes == []


def then_render_was_skipped_for_missing_increment(
    result: Dict[str, Any], increment_snippet: str, out_drawio: Path
) -> None:
    """Then: result is skipped, reason mentions increment, no file written."""
    assert result.get("skipped") is True
    assert increment_snippet in result.get("skip_reason", "")
    assert not out_drawio.exists()


def then_story_graph_cli_read_succeeds(graph: Path) -> None:
    """Then: story_graph_cli read succeeds (story-graph-ops obligation after graph writes)."""
    cli = _OPS_SCRIPTS / "story_graph_cli.py"
    if not cli.is_file():
        return
    proc = subprocess.run(
        [sys.executable, str(cli), "read", "--file", str(graph)],
        capture_output=True,
        text=True,
        cwd=str(_OPS_SCRIPTS),
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout


# =============================================================================
# Increment lane layout helpers
# =============================================================================


def when_increments_diagram_is_rendered(story_graph_data: Dict[str, Any]):
    """When: DrawIOIncrementsMap.render() is called from story graph data."""
    from drawio_story_sync.drawio_story_map import DrawIOIncrementsMap
    from story_graph_ops.nodes import StoryMap

    sm = StoryMap(story_graph_data)
    dm = DrawIOIncrementsMap()
    dm.render(sm, sm.story_graph.get("increments", []))
    return dm


def then_increment_lane_height_is_compact(dm, max_height_px: int) -> None:
    """Then: every rendered lane background element height <= max_height_px."""
    assert dm._increment_lanes, "No increment lanes were rendered"
    for lane in dm._increment_lanes:
        assert lane._lane_element is not None
        h = lane._lane_element.boundary.height
        assert h <= max_height_px, (
            f"Lane '{lane.name}' height {h}px exceeds compact max {max_height_px}px"
        )


def then_story_copies_are_within_lane_bounds(dm) -> None:
    """Then: every story copy fits vertically inside its lane's bounds."""
    from diagram_story_sync.layout_constants import CELL_SIZE

    assert dm._increment_lanes, "No increment lanes were rendered"
    for lane in dm._increment_lanes:
        lane_y = lane._lane_element.position.y
        lane_bottom = lane_y + lane._lane_element.boundary.height
        for copy in lane._story_copies:
            story_top = copy.position.y
            story_bottom = story_top + CELL_SIZE
            assert story_top >= lane_y, (
                f"Story copy y={story_top} is above lane top y={lane_y}"
            )
            assert story_bottom <= lane_bottom, (
                f"Story copy bottom {story_bottom} exceeds lane bottom {lane_bottom} "
                f"in lane '{lane.name}'"
            )
