"""StoryMap - root container that holds Epics and Increments.

Both collections are reconciled as tree children in a single `child_collections`
pass, so `translate_from` produces UpdateReport entries for epic-level AND
increment-level changes in one call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from .nodes import Epic
from .story_node import StoryNode
from .thin_slice import Increment
from .update_report import ChildCollectionPair, UpdateReport

if TYPE_CHECKING:
    from .example import Example


class StoryMap(StoryNode):
    _semantic_type_name = "StoryMap"

    def __init__(self) -> None:
        super().__init__(name="StoryMap", sequential_order=0)
        self.epics: List[Epic] = []
        self.increments: List[Increment] = []
        self.examples: List["Example"] = []

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
                load=self.load_epic,
            ),
            ChildCollectionPair(
                self_children=self.increments,
                source_children=source.increments,
                load=self.load_increment,
            ),
            ChildCollectionPair(
                self_children=self.examples,
                source_children=getattr(source, "examples", []),
                load=self.load_example,
            ),
        ]

    def load_epic(self, source: Epic) -> Epic:
        return Epic(source.name, source.sequential_order)

    def load_increment(self, source: Increment) -> Increment:
        return Increment(source.name, source.sequential_order)

    def load_example(self, source: "Example") -> "Example":
        from .example import Example

        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    def snapshot_fields(self) -> dict:
        return {}

    # -- attachment -----------------------------------------------------------

    def attach_scenarios(self, scenarios) -> None:
        """Link each Scenario to its parent Story by name."""
        stories_by_name: dict = {}
        for story in self.all_stories():
            stories_by_name.setdefault(story.name.strip(), []).append(story)
        attached_story_examples: set = set()
        for scenario in scenarios:
            target = (getattr(scenario, "story_name", None) or "").strip()
            if not target:
                continue
            extras = list(getattr(scenario, "story_examples", None) or [])
            for story in stories_by_name.get(target, []):
                story.scenarios.append(scenario)
                if extras and id(story) not in attached_story_examples:
                    story.examples.extend(extras)
                    attached_story_examples.add(id(story))

    def attach_test_suites(self, suites) -> None:
        """Attach each TestSuite to the SubEpic whose name slug appears in the suite's file path."""
        import re
        self._subs_by_slug: dict = {}
        for sub in self.all_sub_epics():
            slug = re.sub(r"[^a-z0-9]+", "-", sub.name.strip().lower()).strip("-")
            self._subs_by_slug.setdefault(slug, []).append(sub)
        for suite in suites:
            self._attach_suite(suite)
        self.attach_test_cases(suites)

    def _attach_suite(self, suite) -> None:
        import re
        if not (suite.source and suite.source.file):
            return
        for part in re.split(r"[\\/]+", suite.source.file):
            slug = re.sub(r"[^a-z0-9]+", "-", part.strip().lower()).strip("-")
            matches = self._subs_by_slug.get(slug)
            if not matches:
                continue
            for sub in matches:
                sub.test_suites.append(suite)
            return

    def attach_test_cases(self, suites) -> None:
        """Copy TestCases onto Stories when names/paths match (language-agnostic)."""
        self._stories = list(self.all_stories())
        for suite in suites:
            self._attach_suite_cases(suite)

    def _normalized(self, text: str) -> str:
        import re
        return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

    def _attach_suite_cases(self, suite) -> None:
        path = (suite.source.file if suite.source else "") or ""
        path_norm = self._normalized(path.replace("\\", "/"))
        for case in suite.cases:
            target = self._story_for_case(suite, path_norm)
            if target is not None:
                target.test_cases.append(case)

    def _story_for_case(self, suite, path_norm: str):
        target = self._story_matching_text(path_norm)
        if target is not None:
            return target
        target = self._story_matching_text(self._normalized(suite.name))
        if target is not None:
            return target
        return self._sole_story_for_suite(suite)

    def _story_matching_text(self, haystack: str):
        for story in self._stories:
            name = self._normalized(story.name)
            if name and name in haystack:
                return story
        return None

    def _sole_story_for_suite(self, suite):
        if not self._stories:
            return None
        for sub in self.all_sub_epics():
            if suite in sub.test_suites and len(sub.stories) == 1:
                return sub.stories[0]
        return None

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

    def _renumber(self, nodes: List[StoryNode]) -> None:
        for i, node in enumerate(nodes, start=1):
            node.sequential_order = i
