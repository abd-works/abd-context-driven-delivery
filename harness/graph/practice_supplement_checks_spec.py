"""The graph rules a practice supplement adds to each practice it supplements, whatever overlays the session chose. The
graph-checked supplement (``harness/graph/fixtures/graph_checked_supplement``) shares one rule, ``sample-one-outcome``, across BDD
observations and Clean Engineering operations."""

from expects import be_none, equal, expect, have_key
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.graph.pattern_overlays import PatternOverlays
from harness.graph.fixtures.graph_checked_supplement.graph_checked_supplement import GraphCheckedSupplement
from harness.graph.fixtures.graph_checked_supplement.rules import SampleOneOutcome
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE


with description("a rule a practice supplement shares across practices") as self:
    with before.all:
        self.registered = PRACTICE_CATALOGUE.supplement_classes
        PRACTICE_CATALOGUE.register_supplements(GraphCheckedSupplement)
        self.practices = {practice.key: practice for practice in PRACTICE_CATALOGUE.create_all(fidelity=None)}

    with after.all:
        PRACTICE_CATALOGUE.register_supplements(*self.registered)

    with context("that is bound to a practice it names"):
        with it("should check that practice's own node types"):
            bound = SampleOneOutcome().for_practice(self.practices["bdd"])
            expect(bound.node_types).to(equal(("Observation",)))

        with it("should check another practice's node types for that practice"):
            bound = SampleOneOutcome().for_practice(self.practices["clean_engineering"])
            expect(bound.node_types).to(equal(("Operation",)))

    with context("that is bound to a practice it does not name"):
        with it("should not be bound"):
            expect(SampleOneOutcome().for_practice(self.practices["stories"])).to(be_none)

    # Every practice answers the overlay it gives the graph through its typed base, so the framework asks for it by a
    # call it can follow rather than by its name.
    with context("given by a practice that gives the graph no overlay of its own"):
        with it("should be none"):
            expect(self.practices["stories"].graph_overlay).to(be_none)

    with context("with no overlay chosen"):
        with before.each:
            self.overlays = PatternOverlays()

        with it("should be among the graph rules each supplemented practice checks"):
            expect(self.overlays.checks_of(self.practices["bdd"])).to(have_key("sample-one-outcome"))

        with it("should check the node types of the practice it is checked on"):
            rule = self.overlays.checks_of(self.practices["clean_engineering"])["sample-one-outcome"]
            expect(rule.node_types).to(equal(("Operation",)))

        with it("should not be among the graph rules of a practice it does not supplement"):
            expect(self.overlays.checks_of(self.practices["stories"])).not_to(have_key("sample-one-outcome"))
