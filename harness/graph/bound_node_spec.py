"""BDD spec for model objects that are their graph nodes: moving onto an owner's graph, and pausing schema edges."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be, be_none, equal, expect
from mamba import before, context, description, it

from harness.graph import bound_node
from harness.graph.bound_node import schema_sync_paused
from harness.graph.graph import Graph

from cdd_guidance.practices.ux.model.nodes import Region, Screen


with description("a model object built on its own graph"):
    with before.each:
        self.graph = Graph()
        self.screen = Screen("Catalog", 0, graph=self.graph)
        self.region = Region("product list", 0, "body")
        self.own_practice = self.region.practice
        self.screen.append_region(self.region)

    with context("that is appended to an owner on another graph"):
        with it("should be a node of the owner's practice"):
            expect(self.graph.practice("ux").by_id[self.region.node_id]).to(be(self.region))

        with it("should leave the practice it was built in"):
            expect(self.own_practice.by_id.get(self.region.node_id)).to(be_none)

        with it("should keep the source it already had"):
            expect(self.region.has_source_file).to(equal(False))

    with context("that has the same name as a node already on the owner's graph"):
        with before.each:
            self.second = Region("product list", 1, "aside")
            self.screen.append_region(self.second)

        with it("should take a node id of its own"):
            expect(self.second.node_id).to(equal("ux:Region:product list:2"))


with description("schema edges paused while models are parsed"):
    with context("with one pause inside another"):
        with before.each:
            with schema_sync_paused():
                with schema_sync_paused():
                    pass
                self.after_inner = bound_node._SCHEMA_SYNC_PAUSED[0] > 0
            self.after_outer = bound_node._SCHEMA_SYNC_PAUSED[0] > 0

        with it("should stay paused when the inner pause ends"):
            expect(self.after_inner).to(equal(True))

        with it("should resume when the outer pause ends"):
            expect(self.after_outer).to(equal(False))
