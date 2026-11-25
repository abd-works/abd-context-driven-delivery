"""Spec support: UX screen rules on a screen of a UX map, on a graph that also holds the stories it shows; the story
canvas rules on a canvas read from files (canvas_rule_examples.py)."""

from __future__ import annotations

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import SchemaRuleRun

from cdd_guidance.practices.stories.model.story_map import Epic, Story, StoryMap
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.rules import BY_SLUG
from cdd_guidance.practices.ux.rules import canvas_rule_examples as canvas

_STORIES = ("Browse Catalog", "Search Catalog", "Filter Catalog", "Compare Products", "Save Product")


class ScreenExample:
    """A story map and a UX map on one graph; the screen lists the first ``shown`` stories."""

    def __init__(self, screen_name: str, shown: int) -> None:
        self.graph = Graph()
        story_map = StoryMap(self.graph)
        epic = Epic("Shop Online", 1)
        for order, name in enumerate(_STORIES, start=1):
            epic.stories.append(Story(name, order))
        story_map.epics.append(epic)
        ux_map = UxMap.create(self.graph)
        self.screen = Screen(screen_name, 0)
        ux_map.append_screen(self.screen)
        for name in _STORIES[:shown]:
            self.screen.show_story(name)

    def violations(self, rule) -> list[str]:
        """What the rule reports on the screen where validate runs it."""
        return SchemaRuleRun(rule, RuleCheckContext(self.screen.practice)).node_hits(self.screen)


class ScreenPair:
    """One rule with the screen it flags and the screen it passes."""

    def __init__(self, slug: str, failing: tuple[str, int], repaired: tuple[str, int]) -> None:
        self._slug = slug
        self._failing = failing
        self._repaired = repaired

    def check(self) -> None:
        """The rule flags the failing screen and passes the repaired one."""
        rule = BY_SLUG[self._slug]
        if not ScreenExample(*self._failing).violations(rule):
            raise AssertionError(f"{self._slug}: expected a finding on the screen {self._failing}, got none")
        found = ScreenExample(*self._repaired).violations(rule)
        if found:
            raise AssertionError(f"{self._slug}: expected the screen {self._repaired} to pass, got {found!r}")


_SCREEN = canvas.SCREEN_ARTBOARD

# What proves each rule flags its failing example and passes its repaired one, for the spec every practice shares: the
# screen rules by the screen's name and how many stories it shows, the story canvas rules by the canvas's files.
EXAMPLE_PAIRS = {
    "screen-story-budget": ScreenPair("screen-story-budget", ("Catalog", 5), ("Catalog", 4)).check,
    "screen-names-use-domain-terms": ScreenPair("screen-names-use-domain-terms", ("Home", 0), ("Catalog", 0)).check,
    "screen-is-a-prototype": canvas.CanvasPair(BY_SLUG["screen-is-a-prototype"], {_SCREEN: canvas.SCREENSHOT_SCREEN}, {}).check,
    "screen-follows-scenario": canvas.CanvasPair(BY_SLUG["screen-follows-scenario"], {_SCREEN: canvas.FROZEN_SCREEN}, {}).check,
    "every-scenario-has-a-state": canvas.CanvasPair(BY_SLUG["every-scenario-has-a-state"], {_SCREEN: canvas.ONE_STATE_SCREEN}, {}).check,
    "scenario-listed-once": canvas.CanvasPair(
        BY_SLUG["scenario-listed-once"], {canvas.EXPLORER_PAGE: canvas.explorer_page(*canvas.SCENARIOS, canvas.SCENARIOS[0])}, {}).check,
}
