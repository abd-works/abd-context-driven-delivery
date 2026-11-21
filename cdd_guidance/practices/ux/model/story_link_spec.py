"""BDD spec for a screen's story links - the stories, scenarios, and steps a screen shows."""

import sys
from pathlib import Path

from expects import be, contain, equal, expect
from mamba import after, before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph

from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, Story, StoryModel
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen
from cdd_guidance.practices.ux.model.story_link import key_of
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.ux import Ux

_STORY_TESTS = _REPO / "cdd_guidance/practices/stories/model/_examples/actual/from-typescript/to-typescript/tests/onboard-a-customer/create-customer"


def edge_pairs(graph, practice, kind):
    return [(edge.parent.name, edge.child.name) for edge in graph.practices.named(practice).reading.in_graph.edge_index.of(kind)]


def story_map_on(graph):
    story_map = StoryModel(graph=graph)
    epic = Epic("Place New Order", 0)
    story = Story("Browse Product Catalog", 0)
    scenario = Scenario("Products are listed", 0)
    scenario.steps.append(Step("the Customer opens the catalog"))
    story.scenarios.append(scenario)
    epic.stories.append(story)
    story_map.epics.append(epic)
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

        with context("that joins a graph the story map is on"):
            with before.each:
                self.graph = Graph()
                self.screen.join(self.graph.practices.of(Ux))
                self.story_map, self.story, _scenario = story_map_on(self.graph)

            with it("should show the story once it is on the graph"):
                expect(self.screen.shows).to(equal([self.story]))

            with it("should record the story shown on the screen"):
                expect(edge_pairs(self.graph, "stories", "shownOn")).to(contain(("Browse Product Catalog", "Catalog")))

    # A graph opened from its save holds Stories' nodes as plain nodes, with only their saved facts and edges.
    with context("with a story map read from story tests, on a graph opened again from its save"):
        with before.all:
            import shutil
            import tempfile

            self.working_copy = Path(tempfile.mkdtemp())
            shutil.copytree(_STORY_TESTS, self.working_copy / "tests" / "onboard-a-customer" / "create-customer")
            fresh = Graph()
            fresh.load_working_copy(str(self.working_copy), {"stories": "."})
            fresh.save_json()
            stories = fresh.practices.named("stories")
            self.scenario = stories.reading.in_graph.nodes("Scenario")[0]
            self.step = stories.reading.story_tree.steps(self.scenario)[0]
            self.keys = (key_of(self.scenario), key_of(self.step))
            self.reopened = Graph()
            self.reopened.reads.open_saved(self.working_copy)
            self.screen = Screen("Catalog", 0, graph=self.reopened)
            self.screen.show_scenario(self.keys[0])
            self.screen.show_step(self.keys[1])

        with after.all:
            import shutil

            shutil.rmtree(self.working_copy, ignore_errors=True)

        with it("should hold the scenario it names by the key a fresh build gives it"):
            expect([node.node_id for node in self.screen.shows_scenarios]).to(equal([self.scenario.node_id]))

        with it("should hold the step it names by the key a fresh build gives it"):
            expect([node.node_id for node in self.screen.shows_steps]).to(equal([self.step.node_id]))

        with it("should write the keys a fresh build writes"):
            expect((self.screen.scenario_keys, self.screen.step_keys)).to(equal(([self.keys[0]], [self.keys[1]])))

    with context("with a copy of the story map drawn on another graph"):
        with before.each:
            self.screen = Screen("Catalog", 0)
            self.screen.show_story("Browse Product Catalog")
            _map, self.copy, _scenario = story_map_on(Graph())

        with it("should list the copy by its key"):
            expect(self.screen.lists(self.copy)).to(be(True))


_SCENARIO_LINK = "[Browse Product Catalog › Products are listed](story_tests/browse/browse_story.test.md#scenario-products-are-listed)"

with description("a control that serves stories"):
    with context("that is given a story by name, a scenario as a markdown link, and a step by its key"):
        with before.each:
            self.control = Control("Products", 0)
            self.control.show_story("Browse Product Catalog")
            self.control.show_scenario(_SCENARIO_LINK)
            self.control.show_step("Browse Product Catalog › Products are listed › the Customer opens the catalog")

        with it("should write the story by its name"):
            expect(self.control.story_keys).to(equal(["Browse Product Catalog"]))

        with it("should write the scenario as the link it was given, with its target"):
            expect(self.control.scenario_keys).to(equal([_SCENARIO_LINK]))

        with it("should write the step by its key"):
            expect(self.control.step_keys).to(equal(["Browse Product Catalog › Products are listed › the Customer opens the catalog"]))

        with it("should serve an association it is given twice only once"):
            self.control.show_scenario(_SCENARIO_LINK)
            expect(len(self.control.scenario_keys)).to(equal(1))

    with context("that is copied into a map of another format"):
        with before.each:
            source = UxMap.create()
            screen = Screen("Catalog", 0)
            region = Region("product list", 0)
            control = Control("Products", 0)
            control.show_scenario(_SCENARIO_LINK)
            region.append_control(control)
            screen.append_region(region)
            screen.show_scenario(_SCENARIO_LINK)
            source.append_screen(screen)
            self.copy = JsonUxMap.create().parse(JsonUxMap.create().render(source))

        with it("should keep the scenario the control serves, with its target"):
            expect(self.copy.screens[0].regions[0].controls[0].scenario_keys).to(equal([_SCENARIO_LINK]))

        with it("should keep the scenario the screen serves, with its target"):
            expect(self.copy.screens[0].scenario_keys).to(equal([_SCENARIO_LINK]))
