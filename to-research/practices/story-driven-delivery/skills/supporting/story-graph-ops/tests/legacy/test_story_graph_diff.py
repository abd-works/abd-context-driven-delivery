"""Hierarchy diff and StoryMapUpdater.generate_report_from (no DrawIO).

Behaviors covered:
- StoryMap.comparison_epics aligns with the internal epic list
- Identical maps yield matched hierarchy counts and an empty report delta
- generate_report_from surfaces new stories present only on the source map
- generate_report_from surfaces removed stories present only on the target map
- update_from_report rename entries propagate into increment story references
- update_from_report can add only a new sub-epic under an existing epic (no new epic)
- update_from_report removes stories (and increments references) when the report says removed
- update_from_report with ``apply_ac_patches=True`` applies legacy AC adds/removes/moves (used by ``apply-report`` and these tests)
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Set

from story_graph_ops.nodes import Epic, Story, StoryGroup, StoryMap, SubEpic
from story_graph_ops.story_graph_diff import diff_hierarchy_epics
from story_graph_ops.story_map_updater import StoryMapUpdater
from story_graph_ops.update_report import (
    ACChange,
    ACMove,
    StoryMove,
    UpdateReport,
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

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


def given_minimal_story_graph() -> StoryMap:
    """Given: canonical single-story map loaded from the minimal graph dict."""
    return StoryMap(copy.deepcopy(_MINIMAL))


def given_story_map_from(graph: Dict[str, Any]) -> StoryMap:
    """Given: a StoryMap built from a graph dictionary (deep-copied)."""
    return StoryMap(copy.deepcopy(graph))


def when_diff_hierarchy_epics(source: StoryMap, target: StoryMap) -> UpdateReport:
    """When: hierarchy diff runs with source as extracted and target as canonical."""
    report = UpdateReport()
    diff_hierarchy_epics(source, target, report)
    return report


def when_updater_generates_report_from(
    target: StoryMap, source: StoryMap
) -> UpdateReport:
    """When: StoryMapUpdater compares source against target."""
    return StoryMapUpdater(target_map=target).generate_report_from(source)


def when_updater_applies_report(target: StoryMap, report: UpdateReport) -> None:
    """When: StoryMapUpdater applies an update report to the target map."""
    StoryMapUpdater(target_map=target).update_from_report(
        report=report, apply_ac_patches=True
    )


def then_comparison_epic_names_match_internal_list(story_map: StoryMap) -> None:
    """Then: comparison_epics() names match _epics_list names."""
    assert [e.name for e in story_map.comparison_epics()] == [
        e.name for e in story_map._epics_list
    ]


def then_report_has_expected_match_count_and_no_changes(
    report: UpdateReport, matched: int
) -> None:
    """Then: diff report shows the expected match count and no pending changes."""
    assert report.matched_count == matched
    assert not report.has_changes


def then_new_story_names_include(report: UpdateReport, names: Set[str]) -> None:
    """Then: report.new_stories includes every name in ``names``."""
    found = {s.name for s in report.new_stories}
    assert names <= found


def then_removed_story_names_include(report: UpdateReport, names: Set[str]) -> None:
    """Then: report.removed_stories includes every name in ``names``."""
    found = {s.name for s in report.removed_stories}
    assert names <= found


def then_story_renamed_and_increment_reference_updated(
    target: StoryMap, old_name: str, new_name: str
) -> None:
    """Then: story exists under new name, old name is gone, increment lists match."""
    assert target.find_story_by_name(new_name) is not None
    assert target.find_story_by_name(old_name) is None
    assert target._increments.to_list()[0]["stories"][0]["name"] == new_name


def given_two_story_graph_dict() -> Dict[str, Any]:
    """Minimal graph with two stories under Sub A (order One, Two in JSON)."""
    g = copy.deepcopy(_MINIMAL)
    g["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"].append(
        {"name": "Story Two", "sequential_order": 2.0}
    )
    return g


def then_leaf_story_names_match(
    target: StoryMap, sub_epic_name: str, expected: List[str]
) -> None:
    """Then: first story group's children match ``expected`` name order."""
    sub = target.find_node(sub_epic_name)
    assert sub is not None
    groups = [c for c in sub._children if isinstance(c, StoryGroup)]
    assert groups
    stories = [c for c in groups[0]._children if isinstance(c, Story)]
    assert [s.name for s in stories] == expected


# =============================================================================
# STORY: StoryMap comparison epics list
# =============================================================================


class TestStoryMapComparisonEpicsList:
    """comparison_epics exposes the same epic ordering as the internal list."""

    def test_comparison_epics_matches_epics_list(self) -> None:
        # Given
        story_map = given_minimal_story_graph()
        # When / Then
        then_comparison_epic_names_match_internal_list(story_map)


# =============================================================================
# STORY: Hierarchy diff on identical maps
# =============================================================================


class TestHierarchyDiffIdenticalMaps:
    """Diffing two identical maps records matches only."""

    def test_diff_counts_matches_and_reports_no_changes(self) -> None:
        # Given
        left = given_minimal_story_graph()
        right = given_minimal_story_graph()
        # When
        report = when_diff_hierarchy_epics(left, right)
        # Then — epic, sub-epic, story
        then_report_has_expected_match_count_and_no_changes(report, matched=3)


# =============================================================================
# STORY: generate_report_from — new stories
# =============================================================================


class TestGenerateReportFromDetectsNewStories:
    """Source-only stories appear on the report as new_stories."""

    def test_detects_story_added_on_source(self) -> None:
        # Given
        target = given_minimal_story_graph()
        source_graph = copy.deepcopy(_MINIMAL)
        source_graph["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"].append(
            {"name": "Story Two", "sequential_order": 2.0}
        )
        source = given_story_map_from(source_graph)
        # When
        report = when_updater_generates_report_from(target, source)
        # Then
        then_new_story_names_include(report, {"Story Two"})


# =============================================================================
# STORY: generate_report_from — removed stories
# =============================================================================


class TestGenerateReportFromDetectsRemovedStories:
    """Target-only stories appear on the report as removed_stories."""

    def test_detects_story_removed_from_source(self) -> None:
        # Given
        target_graph = copy.deepcopy(_MINIMAL)
        target_graph["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"].append(
            {"name": "Story Two", "sequential_order": 2.0}
        )
        target = given_story_map_from(target_graph)
        source = given_minimal_story_graph()
        # When
        report = when_updater_generates_report_from(target, source)
        # Then
        then_removed_story_names_include(report, {"Story Two"})


# =============================================================================
# STORY: apply rename — increments
# =============================================================================


class TestApplyRenameUpdatesIncrementStoryReferences:
    """Renaming a story through the report rewrites increment lane references."""

    def test_increment_lane_points_at_renamed_story(self) -> None:
        # Given
        graph = copy.deepcopy(_MINIMAL)
        graph["increments"] = [
            {
                "name": "Slice 1",
                "priority": 1,
                "stories": [{"name": "Story One", "sequential_order": 1.0}],
            }
        ]
        target = given_story_map_from(graph)
        report = UpdateReport()
        report.add_rename("Renamed Story", "Story One", confidence=1.0, parent="Sub A")
        # When
        when_updater_applies_report(target, report)
        # Then
        then_story_renamed_and_increment_reference_updated(
            target, old_name="Story One", new_name="Renamed Story"
        )


# =============================================================================
# STORY: apply story-group reorder (DrawIO left-to-right)
# =============================================================================


class TestApplyNewEpicSubEpicAndStories:
    """update_from_report creates root epics before sub-epics and stories."""

    def test_applies_new_epic_then_sub_epic_then_stories(self) -> None:
        # Given
        target = given_minimal_story_graph()
        report = UpdateReport()
        report.add_new_epic("Epic B", parent="")
        report.add_new_sub_epic("Sub B1", parent="Epic B")
        report.add_new_story("Story B1", parent="Sub B1")
        # When
        when_updater_applies_report(target, report)
        # Then
        assert target.find_epic_by_name("Epic B") is not None
        assert target.find_node("Sub B1") is not None
        assert target.find_story_by_name("Story B1") is not None


class TestApplyRemovedStory:
    """update_from_report deletes stories missing from the diagram."""

    def test_removes_story_and_drops_increment_reference(self) -> None:
        # Given
        graph = copy.deepcopy(_MINIMAL)
        graph["increments"] = [
            {"name": "Lane 1", "priority": 1, "stories": [{"name": "Story One"}]}
        ]
        target = given_story_map_from(graph)
        assert target.find_story_by_name("Story One") is not None
        report = UpdateReport()
        report.add_removed_story("Story One", parent="Sub A")
        # When
        when_updater_applies_report(target, report)
        # Then
        assert target.find_story_by_name("Story One") is None
        inc_names = [
            s.get("name")
            for inc in target._increments.to_list()
            for s in inc.get("stories", [])
            if isinstance(s, dict)
        ]
        assert "Story One" not in inc_names


class TestApplyNewSubEpicOnly:
    """update_from_report adds a sub-epic when the report has no new epic or stories."""

    def test_adds_sub_epic_under_existing_epic(self) -> None:
        # Given
        target = given_minimal_story_graph()
        epic = target.find_epic_by_name("Epic A")
        assert epic is not None
        assert epic.find_sub_epic_by_name("Sub Gamma") is None
        report = UpdateReport()
        report.add_new_sub_epic("Sub Gamma", parent="Epic A")
        # When
        when_updater_applies_report(target, report)
        # Then
        assert epic.find_sub_epic_by_name("Sub Gamma") is not None


class TestApplySubEpicSiblingReorder:
    """update_from_report reorders sub-epic columns under an epic."""

    def test_reorders_sub_epics_under_epic(self) -> None:
        # Given — two sub-epics under one epic (Alpha then Beta in JSON)
        graph: Dict[str, Any] = {
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
                                    "name": None,
                                    "stories": [
                                        {"name": "Only A", "sequential_order": 0.0}
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
                                    "name": None,
                                    "stories": [
                                        {"name": "Only B", "sequential_order": 0.0}
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
            "increments": [],
        }
        target = given_story_map_from(graph)
        epic = target.find_node("Epic A")
        assert isinstance(epic, Epic)
        assert [c.name for c in epic._children if isinstance(c, SubEpic)] == [
            "Sub Alpha",
            "Sub Beta",
        ]
        report = UpdateReport()
        report.add_sub_epic_sibling_reorder("Epic A", ["Sub Beta", "Sub Alpha"])
        # When
        when_updater_applies_report(target, report)
        # Then
        assert [c.name for c in epic._children if isinstance(c, SubEpic)] == [
            "Sub Beta",
            "Sub Alpha",
        ]


class TestApplyAcChanges:
    """update_from_report applies exploration/diagram AC deltas (DrawIO sync)."""

    def _graph_one_story_with_ac(self, ac_texts: List[str]) -> Dict[str, Any]:
        g = copy.deepcopy(_MINIMAL)
        story = g["epics"][0]["sub_epics"][0]["story_groups"][0]["stories"][0]
        story["acceptance_criteria"] = [{"name": t, "text": t} for t in ac_texts]
        return g

    def test_adds_new_acceptance_criterion(self) -> None:
        target = given_story_map_from(self._graph_one_story_with_ac(["AC one"]))
        story = target.find_story_by_name("Story One")
        assert story is not None
        assert len(story.acceptance_criteria) == 1
        report = UpdateReport()
        report.set_ac_changes(
            [
                ACChange(
                    story_name="Story One",
                    parent="Sub A",
                    added=["WHEN a token is eligible for grouping THEN it glows"],
                    removed=[],
                )
            ]
        )
        when_updater_applies_report(target, report)
        texts = [(ac.name or "").strip() for ac in story.acceptance_criteria]
        assert "AC one" in texts
        assert "WHEN a token is eligible for grouping THEN it glows" in texts

    def test_removes_acceptance_criterion(self) -> None:
        target = given_story_map_from(
            self._graph_one_story_with_ac(["Keep me", "Drop me"])
        )
        story = target.find_story_by_name("Story One")
        assert story is not None
        report = UpdateReport()
        report.set_ac_changes(
            [
                ACChange(
                    story_name="Story One",
                    parent="Sub A",
                    added=[],
                    removed=["Drop me"],
                )
            ]
        )
        when_updater_applies_report(target, report)
        texts = [(ac.name or "").strip() for ac in story.acceptance_criteria]
        assert texts == ["Keep me"]

    def test_removes_all_acceptance_criteria(self) -> None:
        """Diagram with no AC boxes for a story yields removed=[...] for every prior AC."""
        target = given_story_map_from(
            self._graph_one_story_with_ac(["First AC", "Second AC"])
        )
        story = target.find_story_by_name("Story One")
        assert story is not None
        report = UpdateReport()
        report.set_ac_changes(
            [
                ACChange(
                    story_name="Story One",
                    parent="Sub A",
                    added=[],
                    removed=["First AC", "Second AC"],
                )
            ]
        )
        when_updater_applies_report(target, report)
        assert story.acceptance_criteria == []

    def test_add_and_remove_in_one_change(self) -> None:
        """Same report entry can add new AC and remove an old one (typical diagram edit)."""
        target = given_story_map_from(self._graph_one_story_with_ac(["Old AC"]))
        story = target.find_story_by_name("Story One")
        assert story is not None
        report = UpdateReport()
        report.set_ac_changes(
            [
                ACChange(
                    story_name="Story One",
                    parent="Sub A",
                    added=["New AC"],
                    removed=["Old AC"],
                )
            ]
        )
        when_updater_applies_report(target, report)
        texts = [(ac.name or "").strip() for ac in story.acceptance_criteria]
        assert texts == ["New AC"]

    def test_moves_ac_between_stories(self) -> None:
        g = copy.deepcopy(_MINIMAL)
        sg = g["epics"][0]["sub_epics"][0]["story_groups"][0]
        sg["stories"] = [
            {"name": "Story One", "sequential_order": 1.0, "acceptance_criteria": [{"name": "Shared AC", "text": "Shared AC"}]},
            {"name": "Story Two", "sequential_order": 2.0, "acceptance_criteria": []},
        ]
        target = given_story_map_from(g)
        report = UpdateReport()
        report._ac_moves.append(
            ACMove(ac_text="Shared AC", from_story="Story One", to_story="Story Two")
        )
        when_updater_applies_report(target, report)
        s1 = target.find_story_by_name("Story One")
        s2 = target.find_story_by_name("Story Two")
        assert s1 is not None and s2 is not None
        assert [ac.name for ac in s1.acceptance_criteria] == []
        assert [ac.name for ac in s2.acceptance_criteria] == ["Shared AC"]


def given_two_sub_epics_traveler_ac_graph() -> Dict[str, Any]:
    """Epic with two leaf sub-epics; Traveler under Alpha has two AC (move target: Beta)."""
    return {
        "epics": [
            {
                "name": "Epic E",
                "sequential_order": 0.0,
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
                                    {
                                        "name": "Traveler",
                                        "sequential_order": 0.0,
                                        "acceptance_criteria": [
                                            {"name": "T AC 1", "text": "T AC 1"},
                                            {"name": "T AC 2", "text": "T AC 2"},
                                        ],
                                    }
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
                                    {
                                        "name": "Local",
                                        "sequential_order": 0.0,
                                        "acceptance_criteria": [],
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        ],
        "increments": [],
    }


def given_merge_donor_keeper_graph() -> Dict[str, Any]:
    """One sub-epic with Donor (two AC) and Keeper (one AC) for merge-via-move tests."""
    return {
        "epics": [
            {
                "name": "Epic E",
                "sequential_order": 0.0,
                "sub_epics": [
                    {
                        "name": "Sub Merge",
                        "sequential_order": 0.0,
                        "sub_epics": [],
                        "story_groups": [
                            {
                                "type": "and",
                                "connector": None,
                                "stories": [
                                    {
                                        "name": "Donor",
                                        "sequential_order": 0.0,
                                        "acceptance_criteria": [
                                            {"name": "D1", "text": "D1"},
                                            {"name": "D2", "text": "D2"},
                                        ],
                                    },
                                    {
                                        "name": "Keeper",
                                        "sequential_order": 1.0,
                                        "acceptance_criteria": [
                                            {"name": "K1", "text": "K1"}
                                        ],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
        "increments": [],
    }


class TestApplyStoryMovesAndAcIntegration:
    """Story moves, reorders, merges, and new stories combined with acceptance criteria."""

    def test_move_story_between_sub_epics_retains_all_acceptance_criteria(self) -> None:
        target = given_story_map_from(given_two_sub_epics_traveler_ac_graph())
        traveler = target.find_story_by_name("Traveler")
        assert traveler is not None
        assert [ac.name for ac in traveler.acceptance_criteria] == ["T AC 1", "T AC 2"]
        report = UpdateReport()
        report._moved_stories.append(
            StoryMove(
                name="Traveler",
                from_parent="Sub Alpha",
                to_parent="Sub Beta",
            )
        )
        when_updater_applies_report(target, report)
        t2 = target.find_story_by_name("Traveler")
        assert t2 is not None
        assert [ac.name for ac in t2.acceptance_criteria] == ["T AC 1", "T AC 2"]
        sub_beta = target.find_node("Sub Beta")
        assert sub_beta is not None
        names = [s.name for s in sub_beta.stories]
        assert "Traveler" in names
        sub_alpha = target.find_node("Sub Alpha")
        assert sub_alpha is not None
        assert "Traveler" not in [s.name for s in sub_alpha.stories]

    def test_story_group_reorder_preserves_acceptance_criteria(self) -> None:
        g: Dict[str, Any] = {
            "epics": [
                {
                    "name": "Epic E",
                    "sequential_order": 0.0,
                    "sub_epics": [
                        {
                            "name": "Sub Row",
                            "sequential_order": 0.0,
                            "sub_epics": [],
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "stories": [
                                        {
                                            "name": "First",
                                            "sequential_order": 0.0,
                                            "acceptance_criteria": [
                                                {"name": "AC-A", "text": "AC-A"}
                                            ],
                                        },
                                        {
                                            "name": "Second",
                                            "sequential_order": 1.0,
                                            "acceptance_criteria": [
                                                {"name": "AC-B", "text": "AC-B"}
                                            ],
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
            "increments": [],
        }
        target = given_story_map_from(g)
        report = UpdateReport()
        report.add_story_group_reorder("Sub Row", ["Second", "First"])
        when_updater_applies_report(target, report)
        first = target.find_story_by_name("First")
        second = target.find_story_by_name("Second")
        assert first is not None and second is not None
        assert [ac.name for ac in first.acceptance_criteria] == ["AC-A"]
        assert [ac.name for ac in second.acceptance_criteria] == ["AC-B"]

    def test_merge_moves_two_ac_then_removes_donor_story(self) -> None:
        """Diagram merge: reparent AC onto keeper, then drop empty donor (apply order)."""
        target = given_story_map_from(given_merge_donor_keeper_graph())
        keeper = target.find_story_by_name("Keeper")
        donor = target.find_story_by_name("Donor")
        assert keeper is not None and donor is not None
        report = UpdateReport()
        report._ac_moves.append(ACMove(ac_text="D1", from_story="Donor", to_story="Keeper"))
        report._ac_moves.append(ACMove(ac_text="D2", from_story="Donor", to_story="Keeper"))
        report.add_removed_story("Donor", parent="Sub Merge")
        when_updater_applies_report(target, report)
        assert target.find_story_by_name("Donor") is None
        keeper2 = target.find_story_by_name("Keeper")
        assert keeper2 is not None
        texts = {(ac.name or "").strip() for ac in keeper2.acceptance_criteria}
        assert texts == {"K1", "D1", "D2"}

    def test_new_story_then_add_two_acceptance_criteria(self) -> None:
        target = given_minimal_story_graph()
        report = UpdateReport()
        report.add_new_story("Fresh Story", parent="Sub A")
        report.set_ac_changes(
            [
                ACChange(
                    story_name="Fresh Story",
                    parent="Sub A",
                    added=["WHEN new THEN appear", "AND second line"],
                    removed=[],
                )
            ]
        )
        when_updater_applies_report(target, report)
        st = target.find_story_by_name("Fresh Story")
        assert st is not None
        texts = [(ac.name or "").strip() for ac in st.acceptance_criteria]
        assert "WHEN new THEN appear" in texts
        assert "AND second line" in texts
        assert len(texts) == 2


class TestApplyStoryGroupReorder:
    """update_from_report reorders stories in a leaf sub-epic to match the diagram."""

    def test_swaps_two_stories_when_report_lists_diagram_order(self) -> None:
        # Given — graph order Story One, Story Two
        target = given_story_map_from(given_two_story_graph_dict())
        then_leaf_story_names_match(target, "Sub A", ["Story One", "Story Two"])
        report = UpdateReport()
        report.add_story_group_reorder("Sub A", ["Story Two", "Story One"])
        # When
        when_updater_applies_report(target, report)
        # Then
        then_leaf_story_names_match(target, "Sub A", ["Story Two", "Story One"])
