"""Per-story multiset AC sync (add / remove only; keeps matching nodes)."""
from __future__ import annotations

import copy
from pathlib import Path

from .drawio_story_sync_helper import MINIMAL_STORY_GRAPH, requires_story_graph_ops

pytestmark = requires_story_graph_ops


def test_multiset_remove_extra_duplicate() -> None:
    from drawio_story_sync.diagram_ac_sync import _sync_one_story_ac
    from story_graph_ops.nodes import StoryMap

    g = copy.deepcopy(MINIMAL_STORY_GRAPH)
    g["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0][
        "acceptance_criteria"
    ] = [
        {"name": "A", "text": "A"},
        {"name": "A", "text": "A"},
        {"name": "B", "text": "B"},
    ]
    sm = StoryMap(copy.deepcopy(g))
    story = sm.find_story_by_name("Story One")
    assert story is not None
    _sync_one_story_ac(story, ["A", "B"])
    texts = [(ac.name or "").strip() for ac in story.acceptance_criteria]
    assert sorted(texts) == ["A", "B"]


def test_multiset_add_missing() -> None:
    from drawio_story_sync.diagram_ac_sync import _sync_one_story_ac
    from story_graph_ops.nodes import StoryMap

    sm = StoryMap(copy.deepcopy(MINIMAL_STORY_GRAPH))
    story = sm.find_story_by_name("Story One")
    assert story is not None
    _sync_one_story_ac(story, ["X", "Y"])
    texts = {(ac.name or "").strip() for ac in story.acceptance_criteria}
    assert texts == {"X", "Y"}


def test_unchanged_when_counts_match() -> None:
    from drawio_story_sync.diagram_ac_sync import _sync_one_story_ac
    from story_graph_ops.nodes import StoryMap

    g = copy.deepcopy(MINIMAL_STORY_GRAPH)
    g["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0][
        "acceptance_criteria"
    ] = [{"name": "Only", "text": "Only"}]
    sm = StoryMap(copy.deepcopy(g))
    story = sm.find_story_by_name("Story One")
    assert story is not None
    before = id(story.acceptance_criteria[0])
    _sync_one_story_ac(story, ["Only"])
    assert id(story.acceptance_criteria[0]) == before


def test_apply_per_story_diagram_ac_matches_rendered_canvas(tmp_path: Path) -> None:
    """Rendered exploration and graph both carry the same AC text → sync is a no-op."""
    from drawio_story_sync.diagram_ac_sync import apply_per_story_diagram_ac
    from drawio_story_sync.drawio_story_map import DrawIOExplorationMap, DrawIOStoryMap
    from story_graph_ops.nodes import StoryMap

    graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
    graph["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0][
        "acceptance_criteria"
    ] = [{"name": "KEEP", "text": "KEEP"}]
    sm = StoryMap(copy.deepcopy(graph))
    dm = DrawIOExplorationMap()
    dm.render_exploration_from_story_map(sm, layout_data=None)
    path = tmp_path / "exploration.drawio"
    dm.save(path)
    loaded = DrawIOStoryMap.load(path, diagram_type="acceptance_criteria")

    story = sm.find_story_by_name("Story One")
    assert story is not None
    before = id(story.acceptance_criteria[0])
    apply_per_story_diagram_ac(loaded, sm)
    texts = [(ac.name or "").strip() for ac in story.acceptance_criteria]
    assert texts == ["KEEP"]
    assert id(story.acceptance_criteria[0]) == before


def test_extract_ac_assignments_matches_ac_far_below_story(tmp_path: Path) -> None:
    """AC stacked arbitrarily far under a story must still map to that story (no y cap)."""
    from drawio_story_sync.drawio_story_map import DrawIOExplorationMap, DrawIOStoryMap
    from story_graph_ops.nodes import StoryMap

    graph = copy.deepcopy(MINIMAL_STORY_GRAPH)
    graph["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0][
        "acceptance_criteria"
    ] = [{"name": "N", "text": "VERY_FAR_BELOW"}]
    sm = StoryMap(copy.deepcopy(graph))
    dm = DrawIOExplorationMap()
    dm.render_exploration_from_story_map(sm, layout_data=None)
    path = tmp_path / "exploration.drawio"
    dm.save(path)
    loaded = DrawIOStoryMap.load(path, diagram_type="acceptance_criteria")

    story = next(s for s in loaded.get_stories() if s.name == "Story One")
    ac_elems = getattr(story, "_ac_elements", [])
    assert len(ac_elems) == 1
    ac = ac_elems[0]
    ac.set_position(
        ac.position.x,
        story.position.y + getattr(story.boundary, "height", 0) + 50_000,
    )

    got = loaded.extract_ac_assignments()
    assert got.get(story.cell_id, []) == ["VERY_FAR_BELOW"]
