"""LERN behavior rules flag the faulty shape and pass the repaired one — reading the facts the recorder sets."""

from expects import contain, equal, expect, have_len
from mamba import context, description, it

from cdd_guidance.patterns.lern_domain_driven.practices.bdd.rules.shared_behavior_rules import (
    E2eRunsTheWholeStack,
    ServerTierCallsTheRealThing,
    SharedBehaviorStaysTierFree,
    TierRunsSharedBehavior,
)
from cdd_guidance.patterns.lern_domain_driven.tier_facts import behavior_file_facts
from cdd_guidance.practices.bdd.model.code_spec_model import TypeScriptBddModel
from harness.graph.graph import Graph, Node, Source
from harness.graph.pattern_overlays import PatternOverlays

_SHARED = """
export const ticketBehavior = shareBehavior<TicketDriver>(({ describe, it, before, driver, expect }) => {
  describe('a ticket', () => {
    describe('that is done in its stage', () => {
      before(() => driver().markDone('session-board'))
      it('should show the ticket in the next stage', async () => {
        expect(await driver().columnOf('session-board')).toEqual('Specification')
      })
    })
  })
})
"""


def checks(practice, *patterns):
    """The graph rules practice checks in a graph that applies patterns."""
    graph = Graph()
    graph.overlays = PatternOverlays(list(patterns)).paths
    return graph.practice(practice).checks()


def behavior_file(text, node_type):
    node = Node(Graph().practice("bdd"), node_type, f"bdd:{node_type}:tests/x", "x.behavior.ts", Source("tests/x/x.behavior.ts", 1, 1))
    for key, value in behavior_file_facts(text).items():
        node.set_fact(key, value)
    return node


with description("the lern_domain_driven behavior rules"):
    with it("should load into the bdd practice only when the overlay is active"):
        expect(list(checks("bdd", "lern_domain_driven"))).to(contain("tier-runs-shared-behavior"))
        expect("tier-runs-shared-behavior" in checks("bdd")).to(equal(False))

    with description("a shared behavior"):
        with it("should read as the same describe tree the bdd practice reads from any spec"):
            subject = TypeScriptBddModel().parse_code(_SHARED).descriptions[0]
            expect([subject.name, subject.contexts[0].name, subject.contexts[0].observations[0].name]).to(
                equal(["a ticket", "that is done in its stage", "should show the ticket in the next stage"])
            )

        with context("that reaches its driver alone"):
            with it("should pass"):
                expect(SharedBehaviorStaysTierFree().check(behavior_file(_SHARED, "BehaviorShared"), None)).to(have_len(0))

        with context("that imports a node"):
            with it("should be flagged"):
                faulty = "import { TicketNode } from '@src/kanban/ticket/ticket-node'\n" + _SHARED
                expect(SharedBehaviorStaysTierFree().check(behavior_file(faulty, "BehaviorShared"), None)).to(have_len(1))

        with context("that drives the page itself"):
            with it("should be flagged"):
                faulty = _SHARED.replace("await driver().columnOf('session-board')", "await page.getByText('x').count()")
                expect(SharedBehaviorStaysTierFree().check(behavior_file(faulty, "BehaviorShared"), None)).to(have_len(1))

    with description("a tier file"):
        with context("that runs the shared behavior"):
            with it("should pass"):
                repaired = "itBehavesLike(ticketBehavior, { describe, it, before: beforeEach, expect, driver: () => tier })"
                expect(TierRunsSharedBehavior().check(behavior_file(repaired, "BehaviorServer"), None)).to(have_len(0))

        with context("that states its own behavior alone"):
            with it("should be flagged"):
                faulty = "describe('a ticket', () => { it('should move', () => {}) })"
                expect(TierRunsSharedBehavior().check(behavior_file(faulty, "BehaviorServer"), None)).to(have_len(1))

    with description("the server tier"):
        with context("that mocks what the node calls"):
            with it("should be flagged"):
                faulty = "vi.mock('@src/cdd/gateway')\nconst call = vi.fn()"
                expect(ServerTierCallsTheRealThing().check(behavior_file(faulty, "BehaviorServer"), None)).to(have_len(2))

    with description("the e2e tier"):
        with context("that intercepts a request"):
            with it("should be flagged"):
                faulty = "await page.route('**/api/board', route => route.fulfill({ json: {} }))"
                expect(E2eRunsTheWholeStack().check(behavior_file(faulty, "BehaviorE2e"), None)).to(have_len(1))

        with context("that leaves every request to the real server"):
            with it("should pass"):
                expect(E2eRunsTheWholeStack().check(behavior_file("await page.goto('/')", "BehaviorE2e"), None)).to(have_len(0))
