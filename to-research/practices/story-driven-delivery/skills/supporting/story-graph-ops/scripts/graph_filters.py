"""Filter and subset operations on raw story-graph JSON dicts.

Ported from agile_bots ``story_graph.nodes`` (subset) for use without the full bot.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional, Set


def _filter_story_group_dict(
    sg: Dict[str, Any], story_names: Set[str]
) -> Optional[Dict[str, Any]]:
    stories = [
        s for s in sg.get("stories", [])
        if isinstance(s, dict) and s.get("name") in story_names
    ]
    if not stories:
        return None
    out = dict(sg)
    out["stories"] = stories
    return out


def _filter_sub_epic_dict(
    se: Dict[str, Any], story_names: Set[str]
) -> Optional[Dict[str, Any]]:
    nested = []
    for child in se.get("sub_epics", []):
        if isinstance(child, dict):
            f = _filter_sub_epic_dict(child, story_names)
            if f:
                nested.append(f)
    groups = []
    for sg in se.get("story_groups", []):
        if not isinstance(sg, dict):
            continue
        fg = _filter_story_group_dict(sg, story_names)
        if fg:
            groups.append(fg)
    if nested or groups:
        out = dict(se)
        out["sub_epics"] = nested
        out["story_groups"] = groups
        return out
    return None


def _filter_epic_dict(
    epic: Dict[str, Any], story_names: Set[str]
) -> Optional[Dict[str, Any]]:
    nested = []
    for se in epic.get("sub_epics", []):
        if isinstance(se, dict):
            f = _filter_sub_epic_dict(se, story_names)
            if f:
                nested.append(f)
    groups = []
    for sg in epic.get("story_groups", []):
        if not isinstance(sg, dict):
            continue
        fg = _filter_story_group_dict(sg, story_names)
        if fg:
            groups.append(fg)
    if nested or groups:
        out = dict(epic)
        out["sub_epics"] = nested
        out["story_groups"] = groups
        return out
    return None


def filter_story_graph_to_story_names(
    story_graph: Dict[str, Any], story_names: Set[str]
) -> Dict[str, Any]:
    """Return a deep copy of *story_graph* whose epics tree only includes stories in *story_names*."""
    data = deepcopy(story_graph)
    filtered_epics = []
    for e in data.get("epics", []):
        if isinstance(e, dict):
            fe = _filter_epic_dict(e, story_names)
            if fe:
                filtered_epics.append(fe)
    data["epics"] = filtered_epics
    return data
