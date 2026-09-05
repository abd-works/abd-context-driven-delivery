"""Exploration: diagram with no AC cells clears graph AC via per-story sync."""
from __future__ import annotations

import copy
from pathlib import Path


from .drawio_story_sync_helper import MINIMAL_STORY_GRAPH, requires_story_graph_ops

pytestmark = requires_story_graph_ops


def test_apply_per_story_diagram_ac_clears_when_no_ac_boxes_on_diagram(
    tmp_path: Path,
) -> None:
    from drawio_story_sync.diagram_ac_sync import apply_per_story_diagram_ac
    from drawio_story_sync.drawio_story_map import DrawIOExplorationMap, DrawIOStoryMap
    from story_graph_ops.nodes import StoryMap

    graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
    graph["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0][
        "acceptance_criteria"
    ] = [{"name": "WHEN smoke THEN pass", "text": "WHEN smoke THEN pass"}]
    sm = StoryMap(copy.deepcopy(graph))
    dm = DrawIOExplorationMap()
    dm.render_exploration_from_story_map(sm, layout_data=None)
    path = tmp_path / "exploration.drawio"
    dm.save(path)

    loaded = DrawIOStoryMap.load(path, diagram_type="acceptance_criteria")
    for story in loaded.get_stories():
        if hasattr(story, "_ac_elements"):
            story._ac_elements.clear()
    loaded._loaded_nodes = []
    loaded._has_rendered_ac = False

    apply_per_story_diagram_ac(loaded, sm)
    story = sm.find_story_by_name("Story One")
    assert story is not None
    assert story.acceptance_criteria == []
