"""Structural diff helpers shared by every diagram backend.

The functions here compare an *extracted* (loaded-from-diagram) node tree
against the canonical *original* story map and populate an
``UpdateReport``: matches, renames, new, removed, and sibling reorders.
They never touch backend-specific element details — only ``name``,
``sequential_order``, ``cell_id``, and child collections.

The single backend hook is ``is_manual_subtree_root(node)``: nodes whose
identity hints they were drawn manually (e.g. DrawIO ``cell_id`` without a
``/`` for path-based hierarchy) should not be paired as renames. Backends
pass an appropriate predicate; the default treats everything as
hierarchically-generated (no manual nodes).
"""
from __future__ import annotations

from typing import Any, Callable, List, Optional, Set

from . import bootstrap  # noqa: F401

from story_graph_ops.nodes import Epic, SubEpic, Story  # noqa: E402

from .layout_constants import (
    EPIC_Y,
    EPIC_HEIGHT,
    SUB_EPIC_HEIGHT,
    ROW_GAP,
    ACTOR_GAP,
    CELL_SIZE,
)
from .update_report import UpdateReport


def slug(name: str) -> str:
    """Lowercase and hyphenate a name for use in stable IDs."""
    return name.lower().replace(' ', '-')


# ---------------------------------------------------------------------------
# Reporting helpers (type-aware new/removed)
# ---------------------------------------------------------------------------


def _add_new_by_type(report: UpdateReport, node, parent_name: str = '') -> None:
    if isinstance(node, Epic):
        report.add_new_epic(node.name, parent=parent_name)
    elif isinstance(node, SubEpic):
        report.add_new_sub_epic(node.name, parent=parent_name)
    else:
        report.add_new_story(node.name, parent=parent_name)


def _add_removed_by_type(report: UpdateReport, node, parent_name: str = '') -> None:
    if isinstance(node, Epic):
        report.add_removed_epic(node.name, parent=parent_name)
    elif isinstance(node, SubEpic):
        report.add_removed_sub_epic(node.name, parent=parent_name)
    else:
        report.add_removed_story(node.name, parent=parent_name)


def _report_all_descendants_as_new(node, report: UpdateReport,
                                    parent_name: str = '') -> None:
    sub_epics = list(node.get_sub_epics()) if hasattr(node, 'get_sub_epics') else []
    if sub_epics:
        for se in sub_epics:
            report.add_new_sub_epic(se.name, parent=node.name)
            _report_all_descendants_as_new(se, report, parent_name=se.name)
    elif hasattr(node, 'get_stories'):
        for story in node.get_stories():
            report.add_new_story(story.name, parent=node.name)


def _report_all_descendants_as_removed(node, report: UpdateReport,
                                        parent_name: str = '') -> None:
    sub_epics: List[Any] = []
    if hasattr(node, 'get_sub_epics'):
        sub_epics = list(node.get_sub_epics())
    elif hasattr(node, 'sub_epics'):
        sub_epics = list(node.sub_epics)

    if sub_epics:
        for se in sub_epics:
            report.add_removed_sub_epic(se.name, parent=node.name)
            _report_all_descendants_as_removed(se, report, parent_name=se.name)

    stories: List[Any] = []
    if hasattr(node, 'get_stories'):
        stories = list(node.get_stories())
    elif hasattr(node, 'all_stories'):
        stories = list(node.all_stories)

    for story in stories:
        report.add_removed_story(story.name, parent=node.name)


def collect_all_names(nodes) -> Set[str]:
    """Recursively collect every node ``name`` (epic, sub-epic, story)."""
    names: Set[str] = set()
    for node in nodes:
        names.add(node.name)
        if hasattr(node, 'get_sub_epics'):
            names |= collect_all_names(node.get_sub_epics())
        if hasattr(node, 'get_stories'):
            for story in node.get_stories():
                names.add(story.name)
        if hasattr(node, 'sub_epics') and not hasattr(node, 'get_sub_epics'):
            names |= collect_all_names(node.sub_epics)
        if hasattr(node, 'children'):
            for child in getattr(node, 'children', []):
                names.add(child.name)
    return names


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def _default_is_manual_subtree_root(_node: Any) -> bool:
    """Default backend hook: treat every node as part of a generated hierarchy.

    DrawIO overrides this to flag epics / sub-epics whose ``cell_id`` lacks a
    ``/`` separator (manually drawn cells).
    """
    return False


def compare_node_lists(extracted, original, report: UpdateReport, *,
                       parent_name: str = '',
                       recurse: bool = False,
                       all_extracted_names: Optional[Set[str]] = None,
                       all_original_names: Optional[Set[str]] = None,
                       extracted_story_to_inc: Optional[dict] = None,
                       original_story_to_inc: Optional[dict] = None,
                       is_manual_subtree_root: Callable[[Any], bool] = _default_is_manual_subtree_root) -> None:
    """Diff one level of children, populate ``report``, and (optionally) recurse.

    Backends pass ``is_manual_subtree_root`` to skip rename pairing for
    nodes the user drew themselves; without it every unmatched node is fair
    game for rename detection.
    """
    orig_by_name = {n.name: n for n in original}

    matched_ext = []
    unmatched_ext = []
    used_orig: Set[str] = set()

    for ext_node in extracted:
        orig_node = orig_by_name.get(ext_node.name)
        if orig_node and ext_node.name not in used_orig:
            matched_ext.append((ext_node, orig_node))
            used_orig.add(ext_node.name)
        else:
            unmatched_ext.append(ext_node)

    unmatched_orig = [n for n in original if n.name not in used_orig]

    for ext_node, orig_node in matched_ext:
        report.add_exact_match(ext_node.name, orig_node.name, parent=parent_name)
        if recurse and hasattr(ext_node, '_compare_children'):
            ext_node._compare_children(
                orig_node, report,
                all_extracted_names=all_extracted_names,
                all_original_names=all_original_names,
                extracted_story_to_inc=extracted_story_to_inc,
                original_story_to_inc=original_story_to_inc,
            )

    unmatched_ext_sorted = sorted(unmatched_ext, key=lambda n: n.sequential_order or 0)
    unmatched_orig_sorted = sorted(
        unmatched_orig, key=lambda n: getattr(n, 'sequential_order', 0) or 0
    )

    ext_names_global = all_extracted_names or set()
    orig_names_global = all_original_names or set()

    still_unmatched_ext: List[Any] = []
    still_unmatched_orig: List[Any] = []

    rename_pairs: List = []
    used_ext_idx: Set[int] = set()
    used_orig_idx: Set[int] = set()

    for i, ext_node in enumerate(unmatched_ext_sorted):
        if ext_node.name in orig_names_global:
            still_unmatched_ext.append(ext_node)
            continue
        if is_manual_subtree_root(ext_node):
            still_unmatched_ext.append(ext_node)
            continue
        for j, orig_node in enumerate(unmatched_orig_sorted):
            if j in used_orig_idx:
                continue
            if orig_node.name in ext_names_global:
                continue
            if hasattr(ext_node, 'story_type') and extracted_story_to_inc and original_story_to_inc:
                ext_inc = extracted_story_to_inc.get(ext_node.name)
                orig_inc = original_story_to_inc.get(orig_node.name)
                if (ext_inc or orig_inc) and ext_inc != orig_inc:
                    continue
            rename_pairs.append((ext_node, orig_node))
            used_ext_idx.add(i)
            used_orig_idx.add(j)
            break
        else:
            still_unmatched_ext.append(ext_node)

    for j, orig_node in enumerate(unmatched_orig_sorted):
        if j not in used_orig_idx:
            still_unmatched_orig.append(orig_node)

    for ext_node, orig_node in rename_pairs:
        report.add_rename(ext_node.name, orig_node.name,
                          confidence=1.0, parent=parent_name)
        if recurse and hasattr(ext_node, '_compare_children'):
            ext_node._compare_children(
                orig_node, report,
                all_extracted_names=all_extracted_names,
                all_original_names=all_original_names,
                extracted_story_to_inc=extracted_story_to_inc,
                original_story_to_inc=original_story_to_inc,
            )

    for ext_node in still_unmatched_ext:
        _add_new_by_type(report, ext_node, parent_name=parent_name)
        _report_all_descendants_as_new(ext_node, report)

    for orig_node in still_unmatched_orig:
        _add_removed_by_type(report, orig_node, parent_name=parent_name)
        _report_all_descendants_as_removed(orig_node, report)


def report_sub_epic_sibling_reorder_if_needed(parent_name: str,
                                              extracted_sub_epics: List[Any],
                                              original_sub_epics: List[SubEpic],
                                              report: UpdateReport) -> None:
    """Record sub-epic column order when names match the graph but sequence differs."""
    if not extracted_sub_epics or not original_sub_epics:
        return
    diagram_names = [
        s.name for s in sorted(extracted_sub_epics,
                                key=lambda n: n.sequential_order or 0)
    ]
    graph_names = [
        s.name for s in sorted(original_sub_epics,
                                key=lambda n: getattr(n, 'sequential_order', 0) or 0)
    ]
    if diagram_names == graph_names:
        return
    if set(diagram_names) != set(graph_names):
        return
    if len(diagram_names) != len(set(diagram_names)):
        return
    report.add_sub_epic_sibling_reorder(parent_name, diagram_names)


def report_leaf_story_group_reorder_if_needed(diagram_sub_epic: Any,
                                              original_sub_epic: SubEpic,
                                              unique_stories_in_diagram_order: List[Any],
                                              report: UpdateReport) -> None:
    """Record left-to-right diagram order when names match but sequence differs."""
    if original_sub_epic.has_subepics or diagram_sub_epic.get_sub_epics():
        return
    orig_stories = [c for c in original_sub_epic.children if isinstance(c, Story)]
    if not orig_stories or not unique_stories_in_diagram_order:
        return
    ordered_orig = sorted(
        orig_stories, key=lambda s: getattr(s, 'sequential_order', 0) or 0
    )
    diagram_names = [s.name for s in unique_stories_in_diagram_order]
    graph_names = [s.name for s in ordered_orig]
    if diagram_names == graph_names:
        return
    if set(diagram_names) != set(graph_names):
        return
    if len(diagram_names) != len(set(diagram_names)):
        return
    report.add_story_group_reorder(diagram_sub_epic.name, diagram_names)


def max_sub_epic_depth(node) -> int:
    """Maximum nesting depth of sub-epics under ``node``.

    ``0`` if the node has no sub-epics, ``1`` for flat sub-epics, ``2`` for
    one level of nesting, etc.
    """
    sub_epics: List[Any] = []
    if hasattr(node, 'sub_epics'):
        sub_epics = list(node.sub_epics)
    elif hasattr(node, 'children'):
        sub_epics = [c for c in node.children if isinstance(c, SubEpic)]
    if not sub_epics:
        return 0
    return 1 + max(max_sub_epic_depth(se) for se in sub_epics)


class RowPositions:
    """Compute absolute Y for every row in a story map.

    All epics share row layout so stories across different epics line up
    horizontally. Backend renderers consult ``RowPositions`` for the Y of
    each sub-epic depth, the actor row, and the story row.
    """

    def __init__(self, max_depth: int):
        self.max_depth = max(max_depth, 1)

    def sub_epic_y(self, depth: int) -> float:
        return EPIC_Y + EPIC_HEIGHT + ROW_GAP + depth * (SUB_EPIC_HEIGHT + ROW_GAP)

    @property
    def actor_y(self) -> float:
        deepest = self.sub_epic_y(self.max_depth - 1)
        return deepest + SUB_EPIC_HEIGHT + ACTOR_GAP

    @property
    def story_y(self) -> float:
        from .layout_constants import ROW_GAP as _ROW_GAP

        return self.actor_y + CELL_SIZE + _ROW_GAP
