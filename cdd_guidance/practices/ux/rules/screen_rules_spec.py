"""UX screen graph rules - a failing and a passing example of each, on a graph that also holds the stories."""

import sys
from pathlib import Path

from expects import contain, equal, expect, have_len
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext

from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.rules.screen_rules import ScreenNamesUseDomainTerms, ScreenStoryBudget

_STORIES = ("Browse Catalog", "Search Catalog", "Filter Catalog", "Compare Products", "Save Product")


class ScreenExample:
    """A story map and a UX map on one graph; the screen lists the first ``shown`` stories."""

    def __init__(self, screen_name: str, shown: int) -> None:
        self.graph = Graph()
        story_map = StoryModel(self.graph)
        epic = Epic("Shop Online", 1)
        for order, name in enumerate(_STORIES, start=1):
            epic.stories.append(Story(name, order))
        story_map.append_epic(epic)
        ux_map = UxMap.create(self.graph)
        self.screen = Screen(screen_name, 0)
        ux_map.append_screen(self.screen)
        for name in _STORIES[:shown]:
            self.screen.show_story(name)

    def violations(self, rule) -> list[str]:
        return rule.check(self.screen, RuleCheckContext(self.graph.practice("ux"), None))


with description("a screen checked against the screen-story-budget rule"):
    with context("that shows five stories"):
        with before.each:
            self.example = ScreenExample("Catalog", 5)

        with it("should record that it shows each story"):
            practice = self.example.graph.practice("ux")
            expect([edge.child.name for edge in practice.in_graph.edges("shows")]).to(have_len(5))

        with it("should be over the budget"):
            expect(self.example.violations(ScreenStoryBudget())).to(
                equal(["Screen 'Catalog' has 5 stories (budget ~4)."])
            )

    with context("that shows four stories"):
        with it("should be within the budget"):
            expect(ScreenExample("Catalog", 4).violations(ScreenStoryBudget())).to(equal([]))


with description("a screen checked against the screen-names-use-domain-terms rule"):
    with context("that is named with a generic label"):
        with it("should ask for a domain term"):
            expect(ScreenExample("Home", 0).violations(ScreenNamesUseDomainTerms())).to(
                contain("Screen 'Home' should use a domain term, not a generic label.")
            )

    with context("that is named with a domain term"):
        with it("should pass"):
            expect(ScreenExample("Catalog", 0).violations(ScreenNamesUseDomainTerms())).to(equal([]))
