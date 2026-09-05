"""Validated load/save for ``story-graph.json`` (same shape as agile_bots graph files).

Use from **drawio-story-sync** or other skills so JSON round-trips go through the same
walk validation as **story_graph_cli** / **story_map.StoryMap** (ops tree).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _validate_graph_dict(data: Dict[str, Any]) -> None:
    """Walk the graph with ops ``StoryMap`` so malformed structure fails early."""
    from story_map import Epic, Story, StoryMap

    sm = StoryMap(data)
    for epic in sm.epics():
        for node in sm.walk(epic):
            if isinstance(node, Story) and not node.name:
                raise ValueError("Story node with empty name under epic walk")


def load_story_graph_dict(path: Path | str) -> Dict[str, Any]:
    """Read JSON from *path*, validate via ops story map walk, return the dict."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("story graph root must be a JSON object")
    _validate_graph_dict(data)
    return data


def save_story_graph_dict(path: Path | str, data: Dict[str, Any]) -> None:
    """Validate *data* then write indented UTF-8 JSON to *path*."""
    if not isinstance(data, dict):
        raise TypeError("story graph root must be a dict")
    _validate_graph_dict(data)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
