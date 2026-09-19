"""StoryMap - root container that holds Epics and Increments.

Both collections are reconciled as tree children in a single `child_collections`
pass, so `translate_from` produces UpdateReport entries for epic-level AND
increment-level changes in one call.
"""

from __future__ import annotations

from typing import List

from .nodes import Epic
from .story_node import StoryNode
from .thin_slice import Increment
from .update_report import ChildCollectionPair, UpdateReport


class StoryMap(StoryNode):
    _semantic_type_name = "StoryMap"

    def __init__(self) -> None:
        super().__init__(name="StoryMap", sequential_order=0)
        self.epics: List[Epic] = []
        self.increments: List[Increment] = []

    # -- Epic mutations -------------------------------------------------------

    def append_epic(self, epic: Epic) -> None:
        self.epics.append(epic)
        self._renumber(self.epics)

    def remove_epic(self, epic_name: str) -> Epic:
        for i, epic in enumerate(self.epics):
            if epic.name == epic_name:
                removed = self.epics.pop(i)
                self._renumber(self.epics)
                return removed
        raise KeyError(f"Epic {epic_name!r} not found")

    def reorder_epics(self, new_name_order: List[str]) -> None:
        by_name = {epic.name: epic for epic in self.epics}
        if set(by_name) != set(new_name_order):
            raise ValueError("new_name_order must be a permutation of existing Epic names")
        self.epics = [by_name[name] for name in new_name_order]
        self._renumber(self.epics)

    def find_epic(self, name: str) -> Epic:
        for epic in self.epics:
            if epic.name == name:
                return epic
        raise KeyError(f"Epic {name!r} not found")

    # -- Increment mutations --------------------------------------------------

    def append_increment(self, increment: Increment) -> None:
        self.increments.append(increment)
        self._renumber(self.increments)

    def remove_increment(self, increment_name: str) -> Increment:
        for i, inc in enumerate(self.increments):
            if inc.name == increment_name:
                removed = self.increments.pop(i)
                self._renumber(self.increments)
                return removed
        raise KeyError(f"Increment {increment_name!r} not found")

    def reorder_increments(self, new_name_order: List[str]) -> None:
        by_name = {inc.name: inc for inc in self.increments}
        if set(by_name) != set(new_name_order):
            raise ValueError(
                "new_name_order must be a permutation of existing Increment names"
            )
        self.increments = [by_name[name] for name in new_name_order]
        self._renumber(self.increments)

    # -- StoryNode protocol ---------------------------------------------------

    def update_self(self, source: "StoryMap") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order

    def child_collections(self, source: "StoryMap") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.epics,
                source_children=source.epics,
                create_child=self.create_child_epic,
            ),
            ChildCollectionPair(
                self_children=self.increments,
                source_children=source.increments,
                create_child=self.create_child_increment,
            ),
        ]

    def create_child_epic(self, source: Epic) -> Epic:
        return Epic(source.name, source.sequential_order)

    def create_child_increment(self, source: Increment) -> Increment:
        return Increment(source.name, source.sequential_order)

    def snapshot_fields(self) -> dict:
        return {}

    # -- attachment -----------------------------------------------------------

    def attach_scenarios(self, scenarios) -> None:
        """Link each Scenario to its parent Story by name."""
        stories_by_name: dict = {}
        for story in self.all_stories():
            stories_by_name.setdefault(story.name.strip(), []).append(story)
        for scenario in scenarios:
            target = (getattr(scenario, "story_name", None) or "").strip()
            if not target:
                continue
            for story in stories_by_name.get(target, []):
                story.scenarios.append(scenario)

    def attach_test_suites(self, suites) -> None:
        """Attach each TestSuite to the SubEpic whose name slug appears in the suite's file path."""
        import re
        subs_by_slug: dict = {}
        for sub in self.all_sub_epics():
            slug = re.sub(r"[^a-z0-9]+", "-", sub.name.strip().lower()).strip("-")
            subs_by_slug.setdefault(slug, []).append(sub)
        for suite in suites:
            if not (suite.source and suite.source.file):
                continue
            parts = re.split(r"[\\/]+", suite.source.file)
            for part in parts:
                slug = re.sub(r"[^a-z0-9]+", "-", part.strip().lower()).strip("-")
                matches = subs_by_slug.get(slug)
                if matches:
                    for sub in matches:
                        sub.test_suites.append(suite)
                    break
        self.attach_test_cases(suites)

    def attach_test_cases(self, suites) -> None:
        """Copy TestCases onto Stories when names/paths match (language-agnostic)."""
        import re

        def _norm(text: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

        stories = list(self.all_stories())
        by_name = {_norm(s.name): s for s in stories}
        for suite in suites:
            path = (suite.source.file if suite.source else "") or ""
            path_norm = _norm(path.replace("\\", "/"))
            for case in suite.cases:
                target = None
                for story in stories:
                    if _norm(story.name) and _norm(story.name) in path_norm:
                        target = story
                        break
                if target is None:
                    # Fall back: suite describe / class name contains story name
                    suite_norm = _norm(suite.name)
                    for story in stories:
                        sn = _norm(story.name)
                        if sn and sn in suite_norm:
                            target = story
                            break
                if target is None and stories:
                    # Last resort: only story under a matching sub-epic already holding this suite
                    for sub in self.all_sub_epics():
                        if suite in sub.test_suites and len(sub.stories) == 1:
                            target = sub.stories[0]
                            break
                if target is not None:
                    target.test_cases.append(case)

    # -- tree traversal -------------------------------------------------------

    def all_stories(self) -> List:
        """All Story nodes in the tree, depth-first left-to-right."""
        result = []
        for epic in self.epics:
            for sub in epic.sub_epics:
                result.extend(sub.all_stories_recursive())
        return result

    def all_sub_epics(self) -> List:
        """All SubEpic nodes in the tree, depth-first left-to-right."""
        result = []
        for epic in self.epics:
            self._collect_sub_epics(epic, result)
        return result

    def _collect_sub_epics(self, node, out: List) -> None:
        for sub in getattr(node, "sub_epics", []):
            out.append(sub)
            self._collect_sub_epics(sub, out)

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _renumber(nodes: List[StoryNode]) -> None:
        for i, node in enumerate(nodes, start=1):
            node.sequential_order = i
