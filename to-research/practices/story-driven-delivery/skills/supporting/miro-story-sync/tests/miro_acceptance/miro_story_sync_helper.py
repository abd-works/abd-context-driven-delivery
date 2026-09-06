"""Shared Given/When/Then helpers for miro_story_sync acceptance tests.

Mirrors ``drawio_story_sync_helper`` so contributors moving between the two
backends find the same shape: graph fixtures, CLI runners with PYTHONPATH
plumbing, and assertion helpers.

Tests in this skill **do not stub the production transport**. They stand up a
``LocalMiroServer`` (a real localhost HTTP server speaking the Miro v2
boards REST protocol) and point the production ``RestMiroTransport`` at it.
That covers real urllib calls, real JSON serialisation, real ``Authorization``
header construction, and real response parsing — without a Miro account and
without any real secret value (the local server accepts any non-empty Bearer
token, so ``MIRO_TEST_BEARER_TOKEN`` is a literal test-only string).

Epic: Miro Story Sync. Reused by CLI and outline-render stories.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

_SKILL_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _SKILL_ROOT / "scripts"
_SKILLS_DIR = _SKILL_ROOT.parent
_PACKAGE_ROOT = _SKILLS_DIR.parent
_LIB = _PACKAGE_ROOT / "lib"
_LEGACY_COMMON = _SKILLS_DIR / "common"
_OPS_SCRIPTS = _SKILLS_DIR / "story-graph-ops" / "scripts"

requires_story_graph_ops = pytest.mark.skipif(
    not _OPS_SCRIPTS.is_dir(),
    reason="story-graph-ops skill not present as sibling (skills/supporting/story-graph-ops/scripts)",
)


# Test-only literals. Not secrets — the LocalMiroServer accepts any non-empty
# Bearer token so we keep something obvious here.
MIRO_TEST_BEARER_TOKEN = "test-bearer-token-not-a-real-secret"
MIRO_TEST_BOARD_ID = "test-board"


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


# =============================================================================
# Given
# =============================================================================


def given_running_local_miro_server():
    """Given: a real localhost HTTP server speaking Miro v2 routes."""
    from .local_miro_server import LocalMiroServer

    server = LocalMiroServer()
    server.start()
    return server


def given_rest_transport_pointing_at_local_server(server):
    """Given: a production ``RestMiroTransport`` configured for the local server."""
    from miro_story_sync.miro_transport import RestMiroTransport

    return RestMiroTransport(
        board_id=MIRO_TEST_BOARD_ID,
        access_token=MIRO_TEST_BEARER_TOKEN,
        base_url=server.base_url,
    )


def given_minimal_story_graph_file(workspace: Path) -> Path:
    """Given: story-graph.json with one epic / sub-epic / story."""
    graph_path = workspace / "story-graph.json"
    graph_path.write_text(json.dumps(MINIMAL_STORY_GRAPH), encoding="utf-8")
    return graph_path


def given_cli_pythonpath_env(extra: Dict[str, str] = None) -> Dict[str, str]:
    """Given: PYTHONPATH includes lib/, this skill's scripts, and story-graph-ops scripts."""
    env = os.environ.copy()
    parts = [
        str(_LIB.resolve()),
        str(_SCRIPTS.resolve()),
        str(_OPS_SCRIPTS.resolve()),
    ]
    if _LEGACY_COMMON.is_dir():
        parts.insert(0, str(_LEGACY_COMMON.resolve()))
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(parts + ([prev] if prev else []))
    env.pop("MIRO_ACCESS_TOKEN", None)
    if extra:
        env.update(extra)
    return env


# =============================================================================
# When
# =============================================================================


def when_outline_is_rendered_and_flushed(graph: Dict[str, Any], transport):
    """When: render outline from StoryMap, flush to the supplied transport."""
    from miro_story_sync.miro_story_map import MiroStoryMap
    from story_graph_ops.nodes import StoryMap

    story_map = StoryMap(graph)
    miro_map = MiroStoryMap(transport, diagram_type="outline")
    summary = miro_map.render_from_story_map(story_map, layout_data=None)
    items = miro_map.flush()
    return miro_map, summary, items


def when_synchronizer_renders_outline(graph_path: Path, transport):
    """When: ``MiroSynchronizer.render`` renders outline mode against the transport."""
    from miro_story_sync.miro_story_synchronizer import MiroSynchronizer

    sync = MiroSynchronizer(transport=transport)
    return sync.render(graph_path, renderer_command="render-outline")


def when_cli_renders_outline_against_local_server(graph: Path,
                                                    server,
                                                    env: Dict[str, str]) -> subprocess.CompletedProcess[str]:
    """When: ``miro_story_sync_cli render`` posts to the local Miro server.

    Production CLI gets ``MIRO_ACCESS_TOKEN`` and ``MIRO_API_BASE_URL`` from
    the environment; we set the env so the CLI runs the **real**
    ``RestMiroTransport`` path against the localhost server.
    """
    cli = _SCRIPTS / "miro_story_sync_cli.py"
    real_env = dict(env)
    real_env["MIRO_ACCESS_TOKEN"] = MIRO_TEST_BEARER_TOKEN
    real_env["MIRO_API_BASE_URL"] = server.base_url
    return subprocess.run(
        [
            sys.executable,
            str(cli),
            "render",
            "--mode", "outline",
            "--graph", str(graph),
            "--board", MIRO_TEST_BOARD_ID,
        ],
        env=real_env,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS),
    )


def when_cli_module_is_loaded():
    """When: ``miro_story_sync_cli.py`` is loaded as a module (pure helpers)."""
    cli_path = _SCRIPTS / "miro_story_sync_cli.py"
    spec = importlib.util.spec_from_file_location("miro_story_sync_cli", cli_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


# =============================================================================
# Then
# =============================================================================


def then_summary_reports_one_epic_one_sub_epic_one_story(summary) -> None:
    assert summary.epics == 1
    assert summary.sub_epic_count == 1
    assert summary.story_count == 1
    assert summary.diagram_generated is True


def then_local_server_received_three_items_with_expected_roles(server) -> None:
    """Then: the localhost server received exactly the three story-map items."""
    items = server.items
    assert len(items) == 3
    types = [item.type for item in items]
    assert types == ['shape', 'shape', 'sticky_note']
    roles = [item.metadata.get('story_sync_role', '') for item in items]
    assert roles == ['epic', 'sub_epic', 'story_user']


def then_each_received_item_carries_a_stable_cell_id(server) -> None:
    """Then: every item the server received has a non-empty ``story_sync_cell_id``."""
    for item in server.items:
        cell_id = item.metadata.get('story_sync_cell_id', '')
        assert cell_id, f"item {item.id} missing cell_id metadata"


def then_every_request_carried_a_bearer_authorization_header(server) -> None:
    """Then: production transport sent the configured Bearer token on every call."""
    headers = server.authorization_headers
    assert headers, 'expected at least one authorization header recorded'
    expected = f'Bearer {MIRO_TEST_BEARER_TOKEN}'
    assert all(value == expected for value in headers), headers


CANONICAL_EPIC_PAYLOAD = {
    'type': 'shape',
    'data': {'content': 'Epic A', 'shape': 'round_rectangle'},
    'geometry': {'width': 100, 'height': 60},
    'position': {'x': 70.0, 'y': 150.0,
                 'origin': 'center', 'relativeTo': 'canvas_center'},
    'metadata_role': 'epic',
    'metadata_cell_id': 'epic-a',
}

CANONICAL_SUB_EPIC_PAYLOAD = {
    'type': 'shape',
    'data': {'content': 'Sub A', 'shape': 'round_rectangle'},
    'geometry': {'width': 60, 'height': 60},
    'position': {'x': 55.0, 'y': 225.0,
                 'origin': 'center', 'relativeTo': 'canvas_center'},
    'metadata_role': 'sub_epic',
    'metadata_cell_id': 'epic-a/sub-a',
}

CANONICAL_STORY_PAYLOAD = {
    'type': 'sticky_note',
    'data': {'content': 'Story One'},
    'geometry': {'width': 50, 'height': 50},
    'position': {'x': 55.0, 'y': 370.0,
                 'origin': 'center', 'relativeTo': 'canvas_center'},
    'metadata_role': 'story_user',
    'metadata_cell_id': 'epic-a/sub-a/story-one',
}


def _compact_received_payload(item) -> Dict[str, Any]:
    """Project a server-received item to the fields under canonical comparison."""
    return {
        'type': item.type,
        'data': item.data,
        'geometry': item.geometry,
        'position': item.position,
        'metadata_role': item.metadata.get('story_sync_role', ''),
        'metadata_cell_id': item.metadata.get('story_sync_cell_id', ''),
    }


def then_rendered_items_match_canonical_outline_payload(server) -> None:
    """Then: each item's full payload matches the canonical outline.

    Compares full received payloads (type, data, geometry, position,
    metadata role, metadata cell id) against the canonical fixtures derived
    from ``common/diagram_story_sync.layout_constants``. Asserting full
    objects catches any regression in geometry, role tags, slug paths, or
    wire format — see the **Assert Full Results** rule in
    ``abd-story-acceptance-test``.
    """
    received: List[Dict[str, Any]] = [_compact_received_payload(item) for item in server.items]
    expected = [CANONICAL_EPIC_PAYLOAD, CANONICAL_SUB_EPIC_PAYLOAD, CANONICAL_STORY_PAYLOAD]
    assert received == expected


def then_subprocess_succeeded(proc: subprocess.CompletedProcess[str]) -> None:
    assert proc.returncode == 0, proc.stderr + proc.stdout


def then_last_stdout_line_is_ok_json(proc: subprocess.CompletedProcess[str]) -> Dict[str, Any]:
    line = proc.stdout.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload.get("status") == "ok"
    return payload
