"""Round-trip and validation for :mod:`story_graph_file`.

Behaviors covered:
- save then load returns equivalent graph content
- load rejects stories with empty names
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from story_graph_file import load_story_graph_dict, save_story_graph_dict

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

_MINIMAL: Dict[str, Any] = {
    "epics": [
        {
            "name": "Epic A",
            "sub_epics": [
                {
                    "name": "Sub A",
                    "story_groups": [
                        {
                            "name": None,
                            "stories": [{"name": "Story One", "sequential_order": 1.0}],
                        }
                    ],
                }
            ],
        }
    ],
    "increments": [],
}


def given_story_graph_path(workspace: Path) -> Path:
    """Given: a path for story-graph.json under the workspace."""
    return workspace / "story-graph.json"


def when_save_then_load(path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
    """When: graph dict is saved then loaded from disk."""
    save_story_graph_dict(path, data)
    return load_story_graph_dict(path)


def when_load_expecting_validation_error(path: Path) -> None:
    """When: load_story_graph_dict is invoked (expected to raise)."""
    load_story_graph_dict(path)


def then_roundtrip_preserves_epic_and_raw_json(
    path: Path, loaded: Dict[str, Any]
) -> None:
    """Then: epic name matches and file bytes match parsed dict."""
    assert loaded["epics"][0]["name"] == "Epic A"
    assert json.loads(path.read_text(encoding="utf-8")) == loaded


# =============================================================================
# STORY: load / save round-trip
# =============================================================================


class TestStoryGraphLoadSaveRoundTrip:
    """Persisting and reloading a graph yields the same structure."""

    def test_roundtrip_matches_disk_and_model(self, tmp_path: Path) -> None:
        # Given
        path = given_story_graph_path(tmp_path)
        # When
        loaded = when_save_then_load(path, _MINIMAL)
        # Then
        then_roundtrip_preserves_epic_and_raw_json(path, loaded)


# =============================================================================
# STORY: validation on load
# =============================================================================


class TestStoryGraphLoadRejectsInvalidStories:
    """Invalid graph content fails fast with a clear error."""

    def test_rejects_empty_story_name(self, tmp_path: Path) -> None:
        # Given
        bad = {
            "epics": [
                {
                    "name": "E",
                    "sub_epics": [
                        {
                            "name": "S",
                            "story_groups": [
                                {
                                    "name": None,
                                    "stories": [{"name": "", "sequential_order": 1.0}],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        path = given_story_graph_path(tmp_path)
        path.write_text(json.dumps(bad), encoding="utf-8")
        # When / Then
        with pytest.raises(ValueError, match="empty name"):
            when_load_expecting_validation_error(path)
