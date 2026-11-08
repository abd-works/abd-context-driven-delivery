"""BDD spec for model objects that are their graph nodes: moving onto an owner's graph, and pausing schema edges."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be, be_none, equal, expect
from mamba import before, context, description, it

from harness.graph import model_node
from harness.graph.model_node import ModelReferences, schema_sync_paused
from harness.graph.graph import Graph

from cdd_guidance.practices.stories.model.story_model import Epic, Increment, Story, StoryModel
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ux.model.nodes import Region, Screen
from cdd_guidance.practices.ux.ux import Ux


with description("a model object built on its own graph"):
    with before.each:
        self.graph = Graph()
        self.screen = Screen("Catalog", 0, graph=self.graph)
        self.region = Region("product list", 0, "body")
        self.own_practice = self.region.practice
        self.screen.append_region(self.region)

    with context("that is appended to an owner on another graph"):
        with it("should be a node of the owner's practice"):
            expect(self.graph.node(self.region.node_id)).to(be(self.region))

        with it("should leave the practice it was built in"):
            expect(self.own_practice.graph.holds(self.own_practice, self.region.node_id)).to(equal(False))

        with it("should keep the source it already had"):
            expect(self.region.has_source_file).to(equal(False))

    with context("that has the same name as a node already on the owner's graph"):
        with before.each:
            self.second = Region("product list", 1, "aside")
            self.screen.append_region(self.second)

        with it("should take a node id of its own"):
            expect(self.second.node_id).to(equal("ux:Region:product list:2"))


with description("a model object's practice"):
    with before.each:
        self.graph = Graph()
        self.screen = Screen("Catalog", 0, graph=self.graph)

    with it("should be the graph's practice of the class its model names"):
        expect(self.screen.practice).to(be(self.graph.practice_of(Ux)))


with description("an owner that refers to objects it does not own"):
    with before.each:
        self.story_map = StoryModel()
        self.epic = Epic("Shop")
        self.story = Story("Place order")
        self.epic.append_story(self.story)
        self.story_map.append_epic(self.epic)
        self.increment = Increment("First release")
        self.increment.stories.append(self.story)
        self.story_map.append_increment(self.increment)
        self.graph = self.story_map.graph

    with it("should keep a references list"):
        expect(isinstance(self.increment.stories, ModelReferences)).to(equal(True))

    with it("should leave each object under its own parent"):
        expect(self.story.parent).to(be(self.epic))

    with it("should record a relationship edge to each object on the owner's graph"):
        edges = self.graph.edges_from("stories", self.increment)
        expect([(edge.child, edge.display) for edge in edges]).to(equal([(self.story, "relationship")]))

    with context("that drops an object"):
        with before.each:
            self.increment.stories = []

        with it("should drop the edge to it"):
            expect(self.graph.edges_from("stories", self.increment)).to(equal([]))


with description("schema edges paused while models are parsed"):
    with context("with one pause inside another"):
        with before.each:
            with schema_sync_paused():
                with schema_sync_paused():
                    pass
                self.after_inner = model_node._SCHEMA_SYNC_PAUSED[0] > 0
            self.after_outer = model_node._SCHEMA_SYNC_PAUSED[0] > 0

        with it("should stay paused when the inner pause ends"):
            expect(self.after_inner).to(equal(True))

        with it("should resume when the outer pause ends"):
            expect(self.after_outer).to(equal(False))
