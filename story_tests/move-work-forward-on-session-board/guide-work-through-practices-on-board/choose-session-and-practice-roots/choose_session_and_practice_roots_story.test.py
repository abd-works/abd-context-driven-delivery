from __future__ import annotations

from expects import contain, equal, expect

from harness.agent_tools.agent_tools import AgentToolSet
from space.session.session import Session
from space.session.session_roots_examples import (
    PAYMENT_CODE,
    PAYMENT_DOMAIN,
    PLACE_ORDER_STORIES,
    REFUND_AGGREGATE,
    REFUND_CODE,
    REFUND_DOMAIN,
    REFUND_ORDER_CHANGES,
    REFUND_SHARED_STORY,
    REFUND_STORIES,
    RETURN_PARCEL_STORIES,
    ROOTED_FIDELITIES,
    RefundOrderSession,
)
from story_test import and_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../../.context/story-map.md
# Scenarios: ../guide_work_through_practices_on_board_story.test.md#story-choose-session-and-practice-roots
# Requested 2026-11-16: a session's roots cover exactly the pieces its ticket works on, in every practice it has on,
# and nothing beside them. The agent follows session.set_up_roots; these steps make the calls it makes.

# Story: Choose Session And Practice Roots
# Actor: Agent
with story("Choose Session And Practice Roots"):
    with scenario("Root a session on one aggregate's pieces in every practice"):
        with given("the ticket refund-order names the Refund aggregate, which the repository keeps in domain/orders/refund, implements in src/orders/refund, and covers in story_tests/manage-orders/refund-order"):
            self.refund = RefundOrderSession(REFUND_ORDER_CHANGES)
        with and_("domain/orders/payment, src/orders/payment and story_tests/manage-orders/place-order sit beside them"):
            pass
        with when("the agent sets up refund-order's session roots"):
            # Agent -> FidelitySessionOutput.propose_roots(['Refund'])
            # Agent -> FidelitySessionOutput.choose_root(first) -> FidelitySessionOutput.add_root(each further one)
            for practice, fidelity in ROOTED_FIDELITIES:
                output = self.refund.output(practice, fidelity)
                first, *further = output.propose_roots(["Refund"])
                output.choose_root(first)
                for folder in further:
                    output.add_root(folder)
        with then("DDD's model and tactics are rooted at domain/orders/refund"):
            expect((self.refund.roots("ddd", "model"), self.refund.roots("ddd", "tactics"))).to(equal(([REFUND_DOMAIN], [REFUND_DOMAIN])))
        with and_("Clean Engineering's code is rooted at src/orders/refund"):
            expect(self.refund.roots("clean_engineering", "code")).to(equal([REFUND_CODE]))
        with and_("Stories' scenarios and acceptance tests are rooted at story_tests/manage-orders/refund-order"):
            expect((self.refund.roots("stories", "scenarios"), self.refund.roots("stories", "acceptance_tests"))).to(equal(([REFUND_STORIES], [REFUND_STORIES])))
        with and_("no root names domain/orders/payment, src/orders/payment or story_tests/manage-orders/place-order"):
            every = [root for practice, fidelity in ROOTED_FIDELITIES for root in self.refund.roots(practice, fidelity)]
            expect([root for root in every if root in (PAYMENT_DOMAIN, PAYMENT_CODE, PLACE_ORDER_STORIES)]).to(equal([]))
            self.refund.close()

    with scenario("Add a folder found later beside the roots a fidelity has"):
        with given("refund-order's acceptance tests are rooted at story_tests/manage-orders/refund-order"):
            self.refund = RefundOrderSession()
            self.refund.output("stories", "acceptance_tests").choose_root(REFUND_STORIES)
        with when("the agent finds a story test of the Refund aggregate in story_tests/ship-orders/return-parcel"):
            # Agent -> FidelitySessionOutput.add_root('story_tests/ship-orders/return-parcel')
            self.refund.output("stories", "acceptance_tests").add_root(RETURN_PARCEL_STORIES)
        with then("it adds story_tests/ship-orders/return-parcel to the acceptance tests' roots with fidelity-session-output.add_root"):
            expect(self.refund.roots("stories", "acceptance_tests")).to(contain(RETURN_PARCEL_STORIES))
        with and_("the acceptance tests keep story_tests/manage-orders/refund-order"):
            expect(self.refund.roots("stories", "acceptance_tests")).to(equal([REFUND_STORIES, RETURN_PARCEL_STORIES]))
            self.refund.close()

    with scenario("Propose roots from the ticket and its branch, then confirm them with the person"):
        with given("refund-order's ticket text names Refund"):
            self.names = ["Refund"]
        with and_("its branch changed domain/orders/refund/refund.py and story_tests/manage-orders/refund-order/refund-order.story.shared.py"):
            self.refund = RefundOrderSession((REFUND_AGGREGATE, REFUND_SHARED_STORY))
        with when("the agent asks each fidelity for the roots it proposes"):
            # Agent -> FidelitySessionOutput.propose_roots(['Refund'])
            self.proposed = {(practice, fidelity): self.refund.output(practice, fidelity).propose_roots(self.names) for practice, fidelity in ROOTED_FIDELITIES}
            self.instructions = "\n".join(AgentToolSet.instantiate(Session).tools["set_up_roots"].prompt)
        with then("DDD's tactics propose domain/orders/refund and Stories' acceptance tests propose story_tests/manage-orders/refund-order"):
            expect((self.proposed[("ddd", "tactics")], self.proposed[("stories", "acceptance_tests")])).to(equal(([REFUND_DOMAIN], [REFUND_STORIES])))
        with and_("the agent shows the proposed roots for each practice and fidelity to the person"):
            expect(self.instructions).to(contain("fidelity-session-output.propose_roots"))
        with and_("it sets them only once the person confirms them"):
            expect(self.instructions).to(contain("set nothing before they answer"))
            self.refund.close()
