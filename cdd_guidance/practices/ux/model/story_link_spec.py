"""BDD spec for a screen's story links - the stories, scenarios, and steps a screen shows."""

import sys
from pathlib import Path

from expects import be, contain, equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph

from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, Story, StoryModel
from cdd_guidance.practices.ux.model.nodes import Screen


def edge_pairs(graph, practice, kind):
    return [(edge.parent.name, edge.child.name) for edge in graph.practice(practice).in_graph.edges(kind)]


def story_map_on(graph):
    story_map = StoryModel(graph=graph)
    epic = Epic("Place New Order", 0)
    story = Story("Browse Product Catalog", 0)
    scenario = Scenario("Products are listed", 0)
    scenario.steps.append(Step("the Customer opens the catalog"))
    story.scenarios.append(scenario)
    epic.append_story(story)
    story_map.append_epic(epic)
    return story_map, story, scenario


with description("a screen that shows stories"):
    with context("with the story map on the screen's graph"):
        with before.each:
            self.graph = Graph()
            self.story_map, self.story, self.scenario = story_map_on(self.graph)
            self.screen = Screen("Catalog", 0, graph=self.graph)
            self.screen.show_story(self.story)
            self.screen.show_scenario("Browse Product Catalog › Products are listed")
            self.screen.show_step("Browse Product Catalog › Products are listed › the Customer opens the catalog")

        with it("should record the story shown on the screen"):
            expect(edge_pairs(self.graph, "stories", "shownOn")).to(contain(("Browse Product Catalog", "Catalog")))

        with it("should record the screen showing the story"):
            expect(edge_pairs(self.graph, "ux", "shows")).to(equal([("Catalog", "Browse Product Catalog")]))

        with it("should record the scenario it names by key shown on the screen"):
            expect(edge_pairs(self.graph, "stories", "shownOn")).to(contain(("Products are listed", "Catalog")))

        with it("should record the step it names by key shown on the screen"):
            expect(edge_pairs(self.graph, "stories", "shownOn")).to(contain(("the Customer opens the catalog", "Catalog")))

        with it("should hold the scenario it named by key"):
            expect(self.screen.shows_scenarios).to(equal([self.scenario]))

        with context("that renames its story"):
            with before.each:
                self.story.name = "Browse The Catalog"

            with it("should still show the renamed story"):
                expect(self.screen.shows).to(equal([self.story]))

            with it("should write the story under its new name"):
                expect(self.screen.story_keys).to(equal(["Browse The Catalog"]))

            with it("should write the scenario under the story's new name"):
                expect(self.screen.scenario_keys).to(equal(["Browse The Catalog › Products are listed"]))

    with context("with no story map on its graph"):
        with before.each:
            self.screen = Screen("Catalog", 0)
            self.screen.show_story("Browse Product Catalog")

        with it("should keep the story's key for the formats"):
            expect(self.screen.story_keys).to(equal(["Browse Product Catalog"]))

        with it("should show no story node"):
            expect(self.screen.shows).to(equal([]))

        with it("should list a story key once"):
            self.screen.show_story("Browse Product Catalog")
            expect(self.screen.story_keys).to(equal(["Browse Product Catalog"]))

        with context("that is joined by the story map"):
            with before.each:
                self.story_map, self.story, _scenario = story_map_on(self.screen.graph)

            with it("should show the story once it is on the graph"):
                expect(self.screen.shows).to(equal([self.story]))

            with it("should record the story shown on the screen"):
                expect(edge_pairs(self.screen.graph, "stories", "shownOn")).to(contain(("Browse Product Catalog", "Catalog")))

    with context("with a copy of the story map drawn on another graph"):
        with before.each:
            self.screen = Screen("Catalog", 0)
            self.screen.show_story("Browse Product Catalog")
            _map, self.copy, _scenario = story_map_on(Graph())

        with it("should list the copy by its key"):
            expect(self.screen.lists(self.copy)).to(be(True))
