"""Epic / sub-epic apply scenarios: manual UpdateReport vs hierarchy diff (exploration/outline Pass 1).

``diff_hierarchy_epics`` is what DrawIOStoryMap uses for Pass 1 hierarchy comparison; it does
not emit ``sub_epic_sibling_reorder`` / ``story_group_reorder`` (those come from layout order in
drawio_story_node). Reorder tests therefore use the manual report path only.
"""
from __future__ import annotations

import copy
from typing import Any, Callable, Dict, Literal

import pytest

from story_graph_ops.nodes import Epic, StoryMap, SubEpic
from story_graph_ops.story_graph_diff import diff_hierarchy_epics
from story_graph_ops.story_map_updater import StoryMapUpdater
from story_graph_ops.update_report import UpdateReport

ReportSource = Literal["manual", "hierarchy_diff"]

_MINIMAL: Dict[str, Any] = {
    "epics": [
        {
            "name": "Epic A",
            "sequential_order": 1.0,
            "sub_epics": [
                {
                    "name": "Sub A",
                    "sequential_order": 1.0,
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


def _given_story_map(graph: Dict[str, Any]) -> StoryMap:
    return StoryMap(copy.deepcopy(graph))


def _when_apply(target: StoryMap, report: UpdateReport) -> None:
    StoryMapUpdater(target_map=target).update_from_report(
        report=report, apply_ac_patches=False
    )


def _report_from_hierarchy_diff(
    extracted_graph: Dict[str, Any], original_graph: Dict[str, Any]
) -> UpdateReport:
    report = UpdateReport()
    diff_hierarchy_epics(
        _given_story_map(extracted_graph),
        _given_story_map(original_graph),
        report,
    )
    return report


def _build_report(
    source: ReportSource,
    manual_fn: Callable[[], UpdateReport],
    extracted_graph: Dict[str, Any],
    original_graph: Dict[str, Any],
) -> UpdateReport:
    if source == "manual":
        return manual_fn()
    return _report_from_hierarchy_diff(extracted_graph, original_graph)


# --- graphs for hierarchy_diff (extracted = diagram-shaped, original = JSON before edit) ---


def _graph_add_sub_gamma() -> Dict[str, Any]:
    g = copy.deepcopy(_MINIMAL)
    g["epics"][0]["sub_epics"].append(
        {
            "name": "Sub Gamma",
            "sequential_order": 2.0,
            "sub_epics": [],
            "story_groups": [
                {"type": "and", "connector": None, "stories": []},
            ],
        }
    )
    return g


def _graph_two_subs() -> Dict[str, Any]:
    return {
        "epics": [
            {
                "name": "Epic A",
                "sequential_order": 1.0,
                "sub_epics": [
                    {
                        "name": "Sub Alpha",
                        "sequential_order": 0.0,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "type": "and",
                                "connector": None,
                                "stories": [
                                    {"name": "Only A", "sequential_order": 0.0},
                                ],
                            }
                        ],
                    },
                    {
                        "name": "Sub Beta",
                        "sequential_order": 1.0,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "type": "and",
                                "connector": None,
                                "stories": [
                                    {"name": "Only B", "sequential_order": 0.0},
                                ],
                            }
                        ],
                    },
                ],
            }
        ],
        "increments": [],
    }


def _graph_two_epics() -> Dict[str, Any]:
    g = copy.deepcopy(_MINIMAL)
    g["epics"].append(
        {
            "name": "Epic B",
            "sequential_order": 2.0,
            "sub_epics": [
                {
                    "name": "Sub B1",
                    "sequential_order": 0.0,
                    "sub_epics": [],
                    "story_groups": [
                        {
                            "type": "and",
                            "connector": None,
                            "stories": [{"name": "SB Story", "sequential_order": 0.0}],
                        }
                    ],
                }
            ],
        }
    )
    return g


def _graph_epic_renamed_same_children() -> Dict[str, Any]:
    g = copy.deepcopy(_MINIMAL)
    g["epics"][0]["name"] = "Epic Renamed"
    return g


@pytest.mark.parametrize("report_source", ["manual", "hierarchy_diff"])
def test_add_sub_epic_under_existing_epic(report_source: ReportSource) -> None:
    original = copy.deepcopy(_MINIMAL)
    extracted = _graph_add_sub_gamma()

    def manual() -> UpdateReport:
        r = UpdateReport()
        r.add_new_sub_epic("Sub Gamma", parent="Epic A")
        return r

    report = _build_report(report_source, manual, extracted, original)
    target = _given_story_map(original)
    epic = target.find_epic_by_name("Epic A")
    assert epic is not None
    assert epic.find_sub_epic_by_name("Sub Gamma") is None

    _when_apply(target, report)

    assert epic.find_sub_epic_by_name("Sub Gamma") is not None


@pytest.mark.parametrize("report_source", ["manual", "hierarchy_diff"])
def test_remove_leaf_sub_epic_and_descendants(report_source: ReportSource) -> None:
    original = _graph_two_subs()
    extracted = copy.deepcopy(original)
    extracted["epics"][0]["sub_epics"] = [extracted["epics"][0]["sub_epics"][0]]

    def manual() -> UpdateReport:
        r = UpdateReport()
        r.add_removed_sub_epic("Sub Beta", parent="Epic A")
        r.add_removed_story("Only B", parent="Sub Beta")
        return r

    report = _build_report(report_source, manual, extracted, original)
    target = _given_story_map(original)
    assert target.find_node("Sub Beta") is not None

    _when_apply(target, report)

    assert target.find_node("Sub Beta") is None
    assert target.find_story_by_name("Only B") is None
    assert target.find_node("Sub Alpha") is not None


@pytest.mark.parametrize("report_source", ["manual", "hierarchy_diff"])
def test_add_root_epic_with_sub_and_story(report_source: ReportSource) -> None:
    original = copy.deepcopy(_MINIMAL)
    extracted = _graph_two_epics()

    def manual() -> UpdateReport:
        r = UpdateReport()
        r.add_new_epic("Epic B", parent="")
        r.add_new_sub_epic("Sub B1", parent="Epic B")
        r.add_new_story("SB Story", parent="Sub B1")
        return r

    report = _build_report(report_source, manual, extracted, original)
    target = _given_story_map(original)

    _when_apply(target, report)

    assert target.find_epic_by_name("Epic B") is not None
    assert target.find_node("Sub B1") is not None
    assert target.find_story_by_name("SB Story") is not None


@pytest.mark.parametrize("report_source", ["manual", "hierarchy_diff"])
def test_rename_root_epic_preserves_children(report_source: ReportSource) -> None:
    original = copy.deepcopy(_MINIMAL)
    extracted = _graph_epic_renamed_same_children()

    def manual() -> UpdateReport:
        r = UpdateReport()
        r.add_rename("Epic Renamed", "Epic A", confidence=1.0, parent="")
        return r

    report = _build_report(report_source, manual, extracted, original)
    target = _given_story_map(original)
    assert target.find_epic_by_name("Epic A") is not None

    _when_apply(target, report)

    assert target.find_epic_by_name("Epic A") is None
    assert target.find_epic_by_name("Epic Renamed") is not None
    se = target.find_node("Sub A")
    assert isinstance(se, SubEpic)
    assert target.find_story_by_name("Story One") is not None


@pytest.mark.parametrize("report_source", ["manual", "hierarchy_diff"])
def test_remove_root_epic(report_source: ReportSource) -> None:
    original = _graph_two_epics()
    extracted = copy.deepcopy(_MINIMAL)

    def manual() -> UpdateReport:
        r = UpdateReport()
        r.add_removed_epic("Epic B", parent="")
        r.add_removed_sub_epic("Sub B1", parent="Epic B")
        r.add_removed_story("SB Story", parent="Sub B1")
        return r

    report = _build_report(report_source, manual, extracted, original)
    target = _given_story_map(original)

    _when_apply(target, report)

    assert target.find_epic_by_name("Epic B") is None
    assert target.find_epic_by_name("Epic A") is not None


def test_sub_epic_sibling_reorder_is_manual_report_not_hierarchy_diff() -> None:
    """DrawIO layout emits sibling order; diff_hierarchy_epics matches by name only."""
    graph = {
        "epics": [
            {
                "name": "Epic A",
                "sequential_order": 1.0,
                "sub_epics": [
                    {
                        "name": "Sub Alpha",
                        "sequential_order": 0.0,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "type": "and",
                                "connector": None,
                                "stories": [{"name": "Only A", "sequential_order": 0.0}],
                            }
                        ],
                    },
                    {
                        "name": "Sub Beta",
                        "sequential_order": 1.0,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "type": "and",
                                "connector": None,
                                "stories": [{"name": "Only B", "sequential_order": 0.0}],
                            }
                        ],
                    },
                ],
            }
        ],
        "increments": [],
    }
    swapped = copy.deepcopy(graph)
    swapped["epics"][0]["sub_epics"] = [
        swapped["epics"][0]["sub_epics"][1],
        swapped["epics"][0]["sub_epics"][0],
    ]
    diff_r = _report_from_hierarchy_diff(swapped, graph)
    assert not diff_r.sub_epic_sibling_reorders

    target = _given_story_map(graph)
    epic = target.find_node("Epic A")
    assert isinstance(epic, Epic)
    manual_r = UpdateReport()
    manual_r.add_sub_epic_sibling_reorder("Epic A", ["Sub Beta", "Sub Alpha"])
    _when_apply(target, manual_r)
    assert [c.name for c in epic._children if isinstance(c, SubEpic)] == [
        "Sub Beta",
        "Sub Alpha",
    ]


@pytest.mark.parametrize(
    "report_source,exploration_label",
    [
        ("manual", "outline"),
        ("manual", "exploration"),
        ("hierarchy_diff", "outline"),
        ("hierarchy_diff", "exploration"),
    ],
)
def test_param_labels_document_dual_diagram_apply(
    report_source: ReportSource, exploration_label: str
) -> None:
    """Hierarchy-only apply (no legacy AC patches); label distinguishes test IDs only."""
    del exploration_label
    original = copy.deepcopy(_MINIMAL)
    extracted = _graph_add_sub_gamma()

    def manual() -> UpdateReport:
        r = UpdateReport()
        r.add_new_sub_epic("Sub Gamma", parent="Epic A")
        return r

    report = _build_report(report_source, manual, extracted, original)
    target = _given_story_map(original)
    _when_apply(target, report)
    epic = target.find_epic_by_name("Epic A")
    assert epic is not None
    assert epic.find_sub_epic_by_name("Sub Gamma") is not None
