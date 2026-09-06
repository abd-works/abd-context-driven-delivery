"""Per-story exploration AC sync: diagram text multiset vs graph; add/remove only.

Moves/renames between stories need no special case: each story is updated in
isolation from ``extract_ac_assignments()`` (delete extras, add missing, keep
matching nodes).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from drawio_story_sync.drawio_story_map import DrawIOStoryMap
    from story_graph_ops.nodes import Story, StoryMap


def _ac_node_text(node: Any) -> str:
    nm = (getattr(node, "name", None) or "").strip()
    tx = (getattr(node, "text", None) or "").strip()
    return nm or tx


def _sync_one_story_ac(story: "Story", desired_texts: List[str]) -> None:
    from drawio_story_sync.ac_text_format import canonical_ac_key, diagram_desired_buckets
    from story_graph_ops.nodes import AcceptanceCriteria

    want_by_canon, exemplars_by_canon = diagram_desired_buckets([t for t in desired_texts if t])

    by_canon: defaultdict[str, List] = defaultdict(list)
    for ch in list(story._children):
        if isinstance(ch, AcceptanceCriteria):
            t = _ac_node_text(ch)
            if not t:
                continue
            ck = canonical_ac_key(t)
            by_canon[ck].append(ch)

    for ck, nodes in list(by_canon.items()):
        limit = int(want_by_canon.get(ck, 0))
        while len(nodes) > limit:
            node = nodes.pop()
            if node in story._children:
                story._children.remove(node)
            node._parent = None

    have = Counter()
    for ch in story._children:
        if isinstance(ch, AcceptanceCriteria):
            tt = _ac_node_text(ch)
            if tt:
                have[canonical_ac_key(tt)] += 1

    exemplars_remaining = {k: list(v) for k, v in exemplars_by_canon.items()}
    for ck, cnt in want_by_canon.items():
        need = int(cnt) - int(have.get(ck, 0))
        for _ in range(max(0, need)):
            bench = exemplars_remaining.get(ck) or []
            if not bench:
                break
            name = bench.pop(0)
            exemplars_remaining[ck] = bench
            story.create_acceptance_criteria(name=name)
    story._resequence_children()


def _find_story_by_diagram_slug(target: "StoryMap", slug: str) -> Optional["Story"]:
    """Match graph ``Story`` to the last segment of a DrawIO story ``cell_id``."""
    from story_graph_ops.nodes import Story
    from drawio_story_sync.drawio_story_node import _slug

    if not slug:
        return None
    for epic in target._epics_list:
        for node in target.walk(epic):
            if isinstance(node, Story) and _slug(node.name) == slug:
                return node
    return None


def apply_per_story_diagram_ac(diagram: "DrawIOStoryMap", target: "StoryMap") -> None:
    """Align graph acceptance criteria to the diagram, one story at a time.

    ``extract_ac_assignments()`` keys AC by the diagram story **above** each
    box (layout). Resolve each key to a graph ``Story`` by slug
    (``cell_id`` last segment vs ``_slug(story.name)``), then by exact diagram
    story name. Adjust AC counts to the diagram multiset (strip whitespace).
    Existing nodes whose text still appears on the diagram are kept; extras
    are removed; missing strings get new nodes.
    """
    from story_graph_ops.nodes import Story

    want_by_cid = diagram.extract_ac_assignments()
    story_cell_to_drawio = {s.cell_id: s for s in diagram.get_stories()}
    for cid, texts in want_by_cid.items():
        dstory = story_cell_to_drawio.get(cid)
        slug = cid.rsplit("/", 1)[-1] if cid else ""
        story: Optional[Story] = _find_story_by_diagram_slug(target, slug)
        if not isinstance(story, Story) and dstory is not None:
            story = target.find_story_by_name(dstory.name)
        if not isinstance(story, Story):
            continue
        _sync_one_story_ac(story, texts)
