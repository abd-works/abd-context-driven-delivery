"""
Compare two story-map-shaped trees and fill an UpdateReport.

Uses the same public shape as domain and diagram maps: ``comparison_epics()``,
``get_sub_epics()`` / ``get_stories()``, ``comparison_role()``, ``name``,
``sequential_order``. No DrawIO imports.
"""
from __future__ import annotations

from typing import Any, List, Optional, Set, TYPE_CHECKING

from story_graph_ops.update_report import UpdateReport

if TYPE_CHECKING:
    from story_graph_ops.nodes import Epic, Story, StoryMap, SubEpic


def _add_new_by_type(report: UpdateReport, node: Any, parent_name: str = "") -> None:
    from story_graph_ops.nodes import Epic, SubEpic

    if isinstance(node, Epic):
        report.add_new_epic(node.name, parent=parent_name)
    elif isinstance(node, SubEpic):
        report.add_new_sub_epic(node.name, parent=parent_name)
    else:
        report.add_new_story(node.name, parent=parent_name)


def _add_removed_by_type(report: UpdateReport, node: Any, parent_name: str = "") -> None:
    from story_graph_ops.nodes import Epic, SubEpic

    if isinstance(node, Epic):
        report.add_removed_epic(node.name, parent=parent_name)
    elif isinstance(node, SubEpic):
        report.add_removed_sub_epic(node.name, parent=parent_name)
    else:
        report.add_removed_story(node.name, parent=parent_name)


def _report_all_descendants_as_new(node: Any, report: UpdateReport, parent_name: str = "") -> None:
    sub_epics = list(node.get_sub_epics()) if hasattr(node, "get_sub_epics") else []
    if sub_epics:
        for se in sub_epics:
            report.add_new_sub_epic(se.name, parent=node.name)
            _report_all_descendants_as_new(se, report, parent_name=se.name)
    elif hasattr(node, "get_stories"):
        for story in node.get_stories():
            report.add_new_story(story.name, parent=node.name)


def _report_all_descendants_as_removed(node: Any, report: UpdateReport, parent_name: str = "") -> None:
    sub_epics = []
    if hasattr(node, "get_sub_epics"):
        sub_epics = list(node.get_sub_epics())
    elif hasattr(node, "sub_epics"):
        sub_epics = list(node.sub_epics)

    if sub_epics:
        for se in sub_epics:
            report.add_removed_sub_epic(se.name, parent=node.name)
            _report_all_descendants_as_removed(se, report, parent_name=se.name)

    stories = []
    if hasattr(node, "get_stories"):
        stories = list(node.get_stories())
    elif hasattr(node, "all_stories"):
        stories = list(node.all_stories)

    for story in stories:
        report.add_removed_story(story.name, parent=node.name)


def _collect_all_names(nodes: List[Any]) -> Set[str]:
    names: Set[str] = set()
    for node in nodes:
        names.add(node.name)
        if hasattr(node, "get_sub_epics"):
            names |= _collect_all_names(node.get_sub_epics())
        if hasattr(node, "get_stories"):
            for story in node.get_stories():
                names.add(story.name)
        if hasattr(node, "sub_epics") and not hasattr(node, "get_sub_epics"):
            names |= _collect_all_names(list(node.sub_epics))
        if hasattr(node, "children"):
            for child in getattr(node, "children", []):
                names.add(child.name)
    return names


def _rename_exempt_simple_canvas_id(ext_node: Any) -> bool:
    """Epic/sub-epic cells with a simple mxGraph id (no path) are treated as new, not renames."""
    from story_graph_ops.nodes import Story as DomainStory

    if isinstance(ext_node, DomainStory):
        return False
    cell_id = getattr(ext_node, "cell_id", "") or ""
    if not cell_id or "/" in str(cell_id):
        return False
    if hasattr(ext_node, "get_sub_epics"):
        return True
    return False


def compare_pair_children(
    left: Any,
    right: Any,
    report: UpdateReport,
    *,
    parent_name: str,
    recurse: bool,
    all_extracted_names: Optional[Set[str]] = None,
    all_original_names: Optional[Set[str]] = None,
    extracted_story_to_inc: Optional[dict] = None,
    original_story_to_inc: Optional[dict] = None,
) -> None:
    """Recurse for a matched pair (extracted left vs canonical right)."""
    role = getattr(left, "comparison_role", lambda: "node")()
    if role == "story":
        return
    if role == "epic":
        _compare_node_lists(
            left.get_sub_epics(),
            list(right.get_sub_epics()),
            report,
            parent_name=left.name,
            recurse=True,
            all_extracted_names=all_extracted_names,
            all_original_names=all_original_names,
            extracted_story_to_inc=extracted_story_to_inc,
            original_story_to_inc=original_story_to_inc,
        )
        return
    if role == "sub_epic":
        orig_nested = list(right.get_sub_epics())
        _compare_node_lists(
            left.get_sub_epics(),
            orig_nested,
            report,
            parent_name=left.name,
            recurse=True,
            all_extracted_names=all_extracted_names,
            all_original_names=all_original_names,
            extracted_story_to_inc=extracted_story_to_inc,
            original_story_to_inc=original_story_to_inc,
        )
        seen_names: set = set()
        unique_stories: list = []
        for s in left.get_stories():
            if s.name not in seen_names:
                seen_names.add(s.name)
                unique_stories.append(s)
        orig_stories = list(right.get_stories())
        _compare_node_lists(
            unique_stories,
            orig_stories,
            report,
            parent_name=left.name,
            recurse=False,
            all_extracted_names=all_extracted_names,
            all_original_names=all_original_names,
            extracted_story_to_inc=extracted_story_to_inc,
            original_story_to_inc=original_story_to_inc,
        )


def _compare_node_lists(
    extracted: List[Any],
    original: List[Any],
    report: UpdateReport,
    parent_name: str = "",
    recurse: bool = False,
    all_extracted_names: Optional[Set[str]] = None,
    all_original_names: Optional[Set[str]] = None,
    extracted_story_to_inc: Optional[dict] = None,
    original_story_to_inc: Optional[dict] = None,
) -> None:
    orig_by_name = {}
    for n in original:
        orig_by_name[n.name] = n

    matched_ext: List[tuple] = []
    unmatched_ext: List[Any] = []
    used_orig: set = set()

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
        if recurse:
            compare_pair_children(
                ext_node,
                orig_node,
                report,
                parent_name=parent_name,
                recurse=True,
                all_extracted_names=all_extracted_names,
                all_original_names=all_original_names,
                extracted_story_to_inc=extracted_story_to_inc,
                original_story_to_inc=original_story_to_inc,
            )

    unmatched_ext_sorted = sorted(unmatched_ext, key=lambda n: n.sequential_order or 0)
    unmatched_orig_sorted = sorted(unmatched_orig, key=lambda n: getattr(n, "sequential_order", 0) or 0)

    ext_names_global = all_extracted_names or set()
    orig_names_global = all_original_names or set()

    still_unmatched_ext: List[Any] = []
    still_unmatched_orig: List[Any] = []

    rename_pairs: List[tuple] = []
    used_ext_idx: set = set()
    used_orig_idx: set = set()

    for i, ext_node in enumerate(unmatched_ext_sorted):
        if ext_node.name in orig_names_global:
            still_unmatched_ext.append(ext_node)
            continue
        if _rename_exempt_simple_canvas_id(ext_node):
            still_unmatched_ext.append(ext_node)
            continue
        for j, orig_node in enumerate(unmatched_orig_sorted):
            if j in used_orig_idx:
                continue
            if orig_node.name in ext_names_global:
                continue
            if hasattr(ext_node, "story_type") and extracted_story_to_inc and original_story_to_inc:
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
        report.add_rename(ext_node.name, orig_node.name, confidence=1.0, parent=parent_name)
        if recurse:
            compare_pair_children(
                ext_node,
                orig_node,
                report,
                parent_name=parent_name,
                recurse=True,
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


def diff_hierarchy_epics(
    extracted_map: "StoryMap",
    original_map: "StoryMap",
    report: UpdateReport,
    *,
    extracted_story_to_inc: Optional[dict] = None,
    original_story_to_inc: Optional[dict] = None,
) -> None:
    """Pass 1: compare epic roots and recurse (extracted vs canonical)."""
    extracted_epics = sorted(
        extracted_map.comparison_epics(), key=lambda e: e.sequential_order or 0
    )
    original_epics = sorted(
        original_map.comparison_epics(),
        key=lambda e: getattr(e, "sequential_order", 0) or 0,
    )
    all_extracted = _collect_all_names(extracted_epics)
    all_original = _collect_all_names(original_epics)
    _compare_node_lists(
        extracted_epics,
        original_epics,
        report,
        parent_name="",
        recurse=True,
        all_extracted_names=all_extracted,
        all_original_names=all_original,
        extracted_story_to_inc=extracted_story_to_inc,
        original_story_to_inc=original_story_to_inc,
    )
