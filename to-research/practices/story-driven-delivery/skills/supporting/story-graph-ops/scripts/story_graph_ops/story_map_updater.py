"""
story_map_updater.py

Domain area: story map merge
Responsibilities: compare a source map to a target, produce an UpdateReport, apply
that report to the target (renames, new nodes, moves, reorders, removals, increments,
acceptance criteria from diagram sync).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from story_graph_ops.nodes import AcceptanceCriteria, Epic, Story, StoryGroup, StoryMap, SubEpic
    from story_graph_ops.update_report import IncrementMove, UpdateReport

_logger = logging.getLogger(__name__)


def _increment_lane_story_name(story_entry: Any) -> str:
    """Name of a story as stored inside an increment lane entry."""
    if isinstance(story_entry, dict):
        return story_entry.get("name", "")
    return str(story_entry)


def _reorder_increments_from_report(
    increments: List[Dict[str, Any]],
    increment_order: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build increment list in report order, updating priorities; add new lanes."""
    existing_by_name = {inc.get("name", ""): inc for inc in increments}
    new_increments: List[Dict[str, Any]] = []
    for inc_order in increment_order:
        inc_name = inc_order["name"]
        if inc_name in existing_by_name:
            existing_by_name[inc_name]["priority"] = inc_order["priority"]
            new_increments.append(existing_by_name[inc_name])
        else:
            new_increments.append(
                {"name": inc_name, "priority": inc_order["priority"], "stories": []}
            )
    return new_increments


def _lane_has_story(stories: List[Any], story_name: str) -> bool:
    return any(_increment_lane_story_name(s) == story_name for s in stories)


def _remove_story_from_increment(increment: Dict[str, Any], story_name: str) -> None:
    stories = increment.get("stories", [])
    increment["stories"] = [
        s for s in stories if _increment_lane_story_name(s) != story_name
    ]


def _add_story_to_increment_if_absent(increment: Dict[str, Any], story_name: str) -> None:
    stories = increment.get("stories", [])
    if not _lane_has_story(stories, story_name):
        stories = list(stories)
        stories.append({"name": story_name})
        increment["stories"] = stories


def _apply_increment_lane_moves(
    increments: List[Dict[str, Any]], moves: List["IncrementMove"]
) -> None:
    for move in moves:
        if move.from_increment:
            for inc in increments:
                if inc.get("name") == move.from_increment:
                    _remove_story_from_increment(inc, move.story)
        if move.to_increment:
            for inc in increments:
                if inc.get("name") == move.to_increment:
                    _add_story_to_increment_if_absent(inc, move.story)


def _increments_without_removed_names(
    increments: List[Dict[str, Any]], removed_names: List[str]
) -> List[Dict[str, Any]]:
    dead = set(removed_names)
    return [inc for inc in increments if inc.get("name", "") not in dead]


class StoryMapUpdater:
    """Merges diagram-derived updates into a canonical story map."""

    def __init__(self, target_map: "StoryMap") -> None:
        self._target_map = target_map
        self._last_source: Optional["StoryMap"] = None
        self._last_report: Optional["UpdateReport"] = None

    def generate_report_from(self, source_map: "StoryMap") -> "UpdateReport":
        """Compare ``source_map`` (extracted) to the target map (canonical); store report."""
        from story_graph_ops.story_graph_diff import diff_hierarchy_epics
        from story_graph_ops.update_report import UpdateReport

        report = UpdateReport()
        diff_hierarchy_epics(source_map, self._target_map, report)
        self._last_source = source_map
        self._last_report = report
        return report

    def update_from_report(
        self,
        source: Optional["StoryMap"] = None,
        report: Optional["UpdateReport"] = None,
        *,
        apply_ac_patches: bool = False,
    ) -> None:
        """Apply ``report`` to the target map; if omitted, use the last generated report.

        Exploration acceptance criteria are synced separately
        (``drawio_story_sync.diagram_ac_sync``); by default this does **not**
        apply ``ac_moves`` / ``ac_changes`` from the report. Set
        ``apply_ac_patches=True`` only for tests or legacy tooling that still
        feeds AC deltas through ``UpdateReport``.
        """
        if report is None:
            if self._last_report is None:
                raise ValueError(
                    "No report provided and no stored report from generate_report_from()"
                )
            report = self._last_report

        self._apply_renames(report)
        self._apply_new_nodes(report)
        self._apply_moves(report)
        self._apply_sub_epic_sibling_reorders(report)
        self._apply_story_group_reorders(report)
        self._apply_sub_epic_moves(report)
        self._apply_story_users_changes(report)
        if apply_ac_patches:
            self._apply_ac_moves(report)
            self._apply_ac_changes(report)
        self._apply_removals(report)
        self._apply_increment_changes(report)

    def _apply_renames(self, report: "UpdateReport") -> None:
        from story_graph_ops.nodes import Story

        for rename in report.renames:
            node = self._target_map.find_node(rename.original_name)
            if not node:
                continue
            if isinstance(node, Story):
                self._target_map._increments.rename_story_references(
                    rename.original_name,
                    rename.extracted_name,
                )
            node.name = rename.extracted_name

    def _apply_new_nodes(self, report: "UpdateReport") -> None:
        for new_epic in report.new_epics:
            if new_epic.parent:
                _logger.warning(
                    "Skipping new epic %r: parent %r not supported for root epics",
                    new_epic.name,
                    new_epic.parent,
                )
                continue
            try:
                self._target_map.create_epic(name=new_epic.name)
            except ValueError as e:
                _logger.warning("Skipping new epic %r: %s", new_epic.name, e)

        for new_se in report.new_sub_epics:
            parent = (
                self._target_map.find_node(new_se.parent) if new_se.parent else None
            )
            if parent and hasattr(parent, "create_sub_epic"):
                try:
                    parent.create_sub_epic(name=new_se.name)
                except ValueError as e:
                    _logger.warning(
                        "Skipping new sub-epic %r under %r: %s",
                        new_se.name,
                        new_se.parent,
                        e,
                    )

        for new_story in report.new_stories:
            parent = (
                self._target_map.find_node(new_story.parent)
                if new_story.parent
                else None
            )
            if parent and hasattr(parent, "create_story"):
                try:
                    parent.create_story(name=new_story.name)
                except ValueError as e:
                    _logger.warning(
                        "Skipping new story %r under %r: %s",
                        new_story.name,
                        new_story.parent,
                        e,
                    )

    def _apply_moves(self, report: "UpdateReport") -> None:
        for moved in report.moved_stories:
            story = self._target_map.find_story_by_name(moved.name)
            target = (
                self._target_map.find_node(moved.to_parent)
                if moved.to_parent
                else None
            )
            if not story or not target or not hasattr(story, "move_to"):
                continue
            try:
                story.move_to(target)
            except ValueError as e:
                _logger.warning(
                    "Skipping move of %r to %r: %s",
                    moved.name,
                    moved.to_parent,
                    e,
                )

    def _apply_sub_epic_sibling_reorders(self, report: "UpdateReport") -> None:
        from story_graph_ops.nodes import Epic, SubEpic

        for entry in report.sub_epic_sibling_reorders:
            parent = self._target_map.find_node(entry.parent)
            if not isinstance(parent, (Epic, SubEpic)):
                continue
            subs = [c for c in parent._children if isinstance(c, SubEpic)]
            rest = [c for c in parent._children if not isinstance(c, SubEpic)]
            by_name = {s.name: s for s in subs}
            if set(by_name.keys()) != set(entry.sub_epic_names):
                continue
            if len(entry.sub_epic_names) != len(set(entry.sub_epic_names)):
                continue
            parent._children = [by_name[n] for n in entry.sub_epic_names] + rest
            for child in parent._children:
                if hasattr(child, "_parent"):
                    child._parent = parent
            parent._resequence_children()

    def _apply_story_group_reorders(self, report: "UpdateReport") -> None:
        from story_graph_ops.nodes import Story, StoryGroup, SubEpic

        for entry in report.story_group_reorders:
            node = self._target_map.find_node(entry.parent_sub_epic)
            if not isinstance(node, SubEpic):
                continue
            group = self._story_group_matching_exact_names(node, entry.story_names)
            if not group:
                continue
            by_name = {s.name: s for s in group._children if isinstance(s, Story)}
            if set(by_name.keys()) != set(entry.story_names):
                continue
            group._children = [by_name[n] for n in entry.story_names]
            for child in group._children:
                child._parent = group
            group._resequence_children()

    def _story_group_matching_exact_names(
        self, sub_epic: "SubEpic", story_names: List[str]
    ) -> Optional["StoryGroup"]:
        from story_graph_ops.nodes import Story, StoryGroup

        need = set(story_names)
        if len(need) != len(story_names):
            return None
        for ch in sub_epic._children:
            if not isinstance(ch, StoryGroup):
                continue
            have = {s.name for s in ch._children if isinstance(s, Story)}
            if have == need:
                return ch
        return None

    def _apply_story_users_changes(self, report: "UpdateReport") -> None:
        """Sync ``Story.users`` from outline actor cells (after renames/moves)."""
        from story_graph_ops.domain import StoryUser
        from story_graph_ops.nodes import Story, SubEpic

        for entry in report.story_users_changes:
            story: Optional["Story"] = None
            parent_name = (entry.parent_sub_epic or "").strip()
            if parent_name:
                parent_node = self._target_map.find_node(parent_name)
                if isinstance(parent_node, SubEpic):
                    try:
                        cand = parent_node[entry.story_name]
                        if isinstance(cand, Story):
                            story = cand
                    except KeyError:
                        story = None
            if story is None:
                found = self._target_map.find_story_by_name(entry.story_name)
                if isinstance(found, Story):
                    story = found
            if story is None:
                _logger.warning(
                    "Skipping story_users_change: no story %r (parent %r)",
                    entry.story_name,
                    parent_name or "(any)",
                )
                continue
            story.users = StoryUser.from_list(list(entry.users))

    @staticmethod
    def _ac_node_matches_text(node: "AcceptanceCriteria", text: str) -> bool:
        from story_graph_ops.nodes import AcceptanceCriteria

        if not isinstance(node, AcceptanceCriteria):
            return False
        t = (text or "").strip()
        if not t:
            return False
        nm = (node.name or "").strip()
        tx = (getattr(node, "text", "") or "").strip()
        return t == nm or t == tx

    def _find_story_for_ac(self, story_name: str, parent_sub_epic: str) -> Optional["Story"]:
        from story_graph_ops.nodes import Story, SubEpic

        p = (parent_sub_epic or "").strip()
        if p:
            parent = self._target_map.find_node(p)
            if isinstance(parent, SubEpic):
                try:
                    cand = parent[story_name]
                    if isinstance(cand, Story):
                        return cand
                except KeyError:
                    pass
        found = self._target_map.find_story_by_name(story_name)
        return found if isinstance(found, Story) else None

    def _insert_ac_before_scenarios(self, story: "Story", node: "AcceptanceCriteria") -> None:
        from story_graph_ops.nodes import AcceptanceCriteria, Scenario

        if not isinstance(node, AcceptanceCriteria):
            return
        if node in story._children:
            story._children.remove(node)
        insert_at = next(
            (i for i, ch in enumerate(story._children) if isinstance(ch, Scenario)),
            len(story._children),
        )
        story._children.insert(insert_at, node)
        node._parent = story

    def _pop_first_ac_by_text(self, story: "Story", text: str) -> Optional["AcceptanceCriteria"]:
        from story_graph_ops.nodes import AcceptanceCriteria

        for i, ch in enumerate(story._children):
            if isinstance(ch, AcceptanceCriteria) and self._ac_node_matches_text(ch, text):
                return story._children.pop(i)  # type: ignore[return-value]
        return None

    def _apply_ac_moves(self, report: "UpdateReport") -> None:
        from story_graph_ops.nodes import AcceptanceCriteria, Story

        for move in report.ac_moves:
            src = self._target_map.find_story_by_name(move.from_story)
            dst = self._target_map.find_story_by_name(move.to_story)
            if not isinstance(src, Story) or not isinstance(dst, Story):
                _logger.warning(
                    "Skipping ac_move: stories not found (%r -> %r)",
                    move.from_story,
                    move.to_story,
                )
                continue
            node = self._pop_first_ac_by_text(src, move.ac_text)
            if node is None:
                _logger.warning(
                    "Skipping ac_move: AC not found on story %r",
                    move.from_story,
                )
                continue
            if not isinstance(node, AcceptanceCriteria):
                continue
            self._insert_ac_before_scenarios(dst, node)
            src._resequence_children()
            dst._resequence_children()

    def _apply_ac_changes(self, report: "UpdateReport") -> None:
        from collections import defaultdict

        from story_graph_ops.nodes import AcceptanceCriteria, Scenario, Story

        for change in report.ac_changes:
            story = self._find_story_for_ac(change.story_name, change.parent)
            if story is None:
                _logger.warning(
                    "Skipping ac_changes: unknown story %r (parent %r)",
                    change.story_name,
                    change.parent or "",
                )
                continue

            for mod in change.modified or []:
                if not isinstance(mod, dict):
                    continue
                old_t = (mod.get("old") or "").strip()
                new_t = (mod.get("new") or "").strip()
                if not old_t or not new_t:
                    continue
                for ch in story._children:
                    if isinstance(ch, AcceptanceCriteria) and self._ac_node_matches_text(
                        ch, old_t
                    ):
                        ch.name = new_t
                        ch.text = new_t
                        break

            for text in change.removed:
                while self._pop_first_ac_by_text(story, text):
                    pass

            for text in change.added:
                t = (text or "").strip()
                if not t:
                    continue
                try:
                    ac = story.create_acceptance_criteria(name=t)
                except ValueError as e:
                    _logger.warning(
                        "Skipping new AC on story %r: %s",
                        story.name,
                        e,
                    )
                    continue
                if isinstance(ac, AcceptanceCriteria) and ac in story._children:
                    story._children.remove(ac)
                    self._insert_ac_before_scenarios(story, ac)
                story._resequence_children()

            if change.reordered:
                texts = [str(t).strip() for t in change.reordered if str(t).strip()]
                ac_blocks = [
                    c for c in story._children if isinstance(c, AcceptanceCriteria)
                ]
                scen = [c for c in story._children if isinstance(c, Scenario)]
                pool: defaultdict[str, list] = defaultdict(list)
                for c in ac_blocks:
                    key = (c.name or "").strip() or (
                        getattr(c, "text", "") or ""
                    ).strip()
                    pool[key].append(c)
                ordered: List[Any] = []
                for t in texts:
                    if pool.get(t):
                        ordered.append(pool[t].pop(0))
                for lst in pool.values():
                    ordered.extend(lst)
                story._children = ordered + scen
                story._resequence_children()

    def _apply_sub_epic_moves(self, report: "UpdateReport") -> None:
        from story_graph_ops.nodes import SubEpic

        for moved in report.moved_sub_epics:
            node = self._target_map.find_node(moved.name)
            to_parent = (
                self._target_map.find_node(moved.to_parent)
                if moved.to_parent
                else None
            )
            if not isinstance(node, SubEpic) or not to_parent:
                continue
            if not hasattr(to_parent, "_children") or not hasattr(
                to_parent, "create_sub_epic"
            ):
                continue
            old_parent = getattr(node, "_parent", None)
            if not old_parent or old_parent is to_parent:
                continue
            try:
                self._reparent_sub_epic(node, old_parent, to_parent)
            except (ValueError, AttributeError) as e:
                _logger.warning(
                    "Skipping sub-epic move of %r to %r: %s",
                    moved.name,
                    moved.to_parent,
                    e,
                )

    def _reparent_sub_epic(
        self, node: "SubEpic", old_parent: Any, to_parent: Any
    ) -> None:
        if hasattr(old_parent, "_children") and node in old_parent._children:
            old_parent._children.remove(node)
        to_parent._children.append(node)
        node._parent = to_parent
        if hasattr(node, "save"):
            node.save()

    def _apply_removals(self, report: "UpdateReport") -> None:
        """Drop nodes listed as removed (diagram no longer shows them)."""
        from story_graph_ops.nodes import Story, SubEpic

        for entry in report.removed_epics:
            epic = self._target_map.find_epic_by_name(entry.name)
            if epic is not None:
                self._remove_epic_from_map(epic)

        for entry in report.removed_sub_epics:
            node = self._target_map.find_node(entry.name)
            if isinstance(node, SubEpic):
                self._remove_sub_epic_branch(node)

        for entry in report.removed_stories:
            story = self._target_map.find_story_by_name(entry.name)
            if isinstance(story, Story):
                self._detach_story_from_map(story)

    def _detach_story_from_map(self, story: "Story") -> None:
        from story_graph_ops.nodes import StoryGroup

        self._target_map.remove_story_from_all_increments(story.name)
        parent = getattr(story, "_parent", None)
        if parent is None:
            return
        if isinstance(parent, StoryGroup):
            if story in parent._children:
                parent._children.remove(story)
            parent._resequence_children()
            if not parent._children:
                sub_epic = parent._parent
                if sub_epic is not None and parent in sub_epic._children:
                    sub_epic._children.remove(parent)
                    sub_epic._resequence_children()
        story._parent = None

    def _remove_sub_epic_branch(self, sub: "SubEpic") -> None:
        from story_graph_ops.nodes import StoryGroup, SubEpic

        for nested in list(sub.get_sub_epics()):
            self._remove_sub_epic_branch(nested)
        for story in list(sub.stories):
            self._detach_story_from_map(story)
        for child in list(sub._children):
            if isinstance(child, StoryGroup) and not child._children:
                if child in sub._children:
                    sub._children.remove(child)
        parent = sub._parent
        if parent is not None and sub in parent._children:
            parent._children.remove(sub)
            parent._resequence_children()
        sub._parent = None

    def _remove_epic_from_map(self, epic: "Epic") -> None:
        from story_graph_ops.nodes import EpicsCollection, Story, StoryGroup

        for sub in list(epic.get_sub_epics()):
            self._remove_sub_epic_branch(sub)
        for child in list(epic._children):
            if isinstance(child, StoryGroup):
                for story in list(child._children):
                    if isinstance(story, Story):
                        self._detach_story_from_map(story)
                if child in epic._children:
                    epic._children.remove(child)
        if epic in self._target_map._epics_list:
            self._target_map._epics_list.remove(epic)
        self._target_map._epics = EpicsCollection(self._target_map._epics_list)
        for idx, e in enumerate(self._target_map._epics_list):
            e.sequential_order = float(idx)
        epic._parent = None

    def _apply_increment_changes(self, report: "UpdateReport") -> None:
        from story_graph_ops.nodes import IncrementCollection

        increments = self._target_map._increments.to_list()
        if report.increment_order:
            increments = _reorder_increments_from_report(
                increments, report.increment_order
            )
        if report.increment_moves:
            _apply_increment_lane_moves(increments, report.increment_moves)
        if report.removed_increments:
            increments = _increments_without_removed_names(
                increments, report.removed_increments
            )
        self._target_map._increments = IncrementCollection.from_list(
            increments, story_map=self._target_map
        )
        self._target_map.story_graph["increments"] = increments

    def reconcile_moves(self, original_map: "StoryMap") -> None:
        raise NotImplementedError("Move reconciliation not yet implemented")

    def reconcile_ac_moves(self) -> None:
        raise NotImplementedError("AC move reconciliation not yet implemented")
