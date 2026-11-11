"""Organize Ticket Hierarchy: the shared scenarios the Python tiers replay.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md.
Map: harness/.context/stories/story-map.md. Model: .context/kanban-model.md.

Only the stories of ticket maintain-tickets-on-board are here; the sub-epic's built stories stay in
steer-ticket-sessions.story.shared.py. Steps reach the board only through the World a tier hands them, so the domain
spec and the cdd tools spec replay the same steps. Each When carries its scenario's realization as comments.

Left to the board app's TypeScript specs, because only the page shows them: Display Child Tickets In Parent, Expand
Parent Ticket. Nest Child Branch And Session is set aside.
"""

from __future__ import annotations

import json

from expects import be_none, equal, expect

from space.kanban.session_board_examples import (
    BILLING_REPORT,
    CHECKOUT_FLOW,
    CONFIRM_ORDER_CHILD,
    CONFIRM_ORDER_DONE_IN_DISCOVERY,
    ENTER_CARD_DETAILS,
    ENTER_CARD_DETAILS_CHILD,
    ENTER_CARD_DETAILS_IN_SPECIFICATION,
    ENTER_CARD_DETAILS_PULLED_OUT_DONE,
    PET_VISITS,
    PULLED_OUT_TITLE,
)
from space.kanban.story_test import SharedStories, children_in, expect_placed, expect_refused, refusal_of, ticket_in
from space.kanban.ticket import ParentMovesWithChildrenError

shared_stories = SharedStories("Organize Ticket Hierarchy")


def board_of(world) -> dict:
    return world.data_of(world.Board.load().show())


def card_of(world, name: str) -> dict | None:
    """The ticket named name as a card of its own on the board; none when it shows in no column."""
    return ticket_in(board_of(world), name)


def saved_parent(world, seed) -> str:
    """The parent seed's session.json names; empty when it names none."""
    return json.loads((world.project.sessions / seed.name / "session.json").read_text(encoding="utf-8")).get("parent", "")


@shared_stories.scenario("Add Child Ticket", "Add a child ticket by hand")
def _(s):
    @s.given('the ticket checkout-flow is In progress in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.but_('checkout-flow has no child tickets')
    def _(world):
        # No other session is seeded.
        pass

    @s.when('the Person adds the child ticket Enter card details to checkout-flow')
    def _(world):
        # Board.ticket("checkout-flow")
        #   <- checkout-flow
        # checkout-flow.add_child("Enter card details")
        #   -> self.session.open_child("Enter card details", scope="story")
        #   <- enter-card-details In progress in Discovery, its parent checkout-flow
        world.child = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).add_child(title=ENTER_CARD_DETAILS.title))

    @s.then('the ticket enter-card-details is In progress in Discovery with the parent checkout-flow')
    def _(world):
        expect_placed(world.child, "Discovery", is_done=False)
        expect((world.child["name"], world.child["session"]["parent"])).to(equal((ENTER_CARD_DETAILS_CHILD.name, CHECKOUT_FLOW.name)))

    @s.and_("checkout-flow's card holds enter-card-details (Display Child Tickets In Parent)")
    def _(world):
        expect(children_in(card_of(world, CHECKOUT_FLOW.name))).to(equal([ENTER_CARD_DETAILS_CHILD.name]))


@shared_stories.scenario("Add Child Ticket", "Drag a ticket onto a parent")
def _(s):
    @s.given('the ticket pet-visits is In progress in Discovery with no parent')
    def _(world):
        world.project.seed_session(PET_VISITS)

    @s.and_('the ticket checkout-flow is In progress in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when('the Person drags pet-visits onto checkout-flow')
    def _(world):
        # Board.ticket("pet-visits")
        #   <- pet-visits
        # Board.ticket("checkout-flow")
        #   <- checkout-flow
        # pet-visits.reassign_parent(checkout-flow)
        #   -> self.session.set_parent(checkout-flow.session)
        #   <- pet-visits inside checkout-flow
        world.Ticket.load(PET_VISITS.name).reassign_parent(world.Ticket.load(CHECKOUT_FLOW.name))

    @s.then("checkout-flow's card holds pet-visits")
    def _(world):
        expect(children_in(card_of(world, CHECKOUT_FLOW.name))).to(equal([PET_VISITS.name]))

    @s.and_('no column shows pet-visits as a card of its own')
    def _(world):
        expect(card_of(world, PET_VISITS.name)).to(be_none)


@shared_stories.scenario("Detach Child Ticket", "Pull a child out of its parent")
def _(s):
    @s.given('the ticket checkout-flow holds its child ticket enter-card-details in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(ENTER_CARD_DETAILS_CHILD)

    @s.when('the Person drags enter-card-details out of checkout-flow')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # enter-card-details.pull_out()
        #   -> self.session.mark_pulled_out()
        #   <- enter-card-details pulled out, its parent still checkout-flow
        world.Ticket.load(ENTER_CARD_DETAILS_CHILD.name).pull_out()

    @s.then('enter-card-details shows as a card of its own beside checkout-flow, titled Checkout flow.Enter card details')
    def _(world):
        child, parent = card_of(world, ENTER_CARD_DETAILS_CHILD.name), card_of(world, CHECKOUT_FLOW.name)
        expect((child["title"], child["column"]["name"])).to(equal((PULLED_OUT_TITLE, parent["column"]["name"])))

    @s.and_('enter-card-details still has the parent checkout-flow')
    def _(world):
        expect(card_of(world, ENTER_CARD_DETAILS_CHILD.name)["session"]["parent"]).to(equal(CHECKOUT_FLOW.name))

    @s.and_("checkout-flow's card holds a dashed row for enter-card-details")
    def _(world):
        rows = [(child["name"], child["is_pulled_out"]) for child in card_of(world, CHECKOUT_FLOW.name)["children"]]
        expect(rows).to(equal([(ENTER_CARD_DETAILS_CHILD.name, True)]))


@shared_stories.scenario("Detach Child Ticket", "Move a pulled-out child like any ticket")
def _(s):
    @s.given('the ticket enter-card-details was pulled out of checkout-flow and is Done in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(ENTER_CARD_DETAILS_PULLED_OUT_DONE)

    @s.when('the Person moves enter-card-details to Specification')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # enter-card-details.move_next()
        #   <- enter-card-details in Specification, its parent still checkout-flow
        world.Ticket.load(ENTER_CARD_DETAILS_CHILD.name).move_next()

    @s.then('the Specification column shows enter-card-details')
    def _(world):
        expect_placed(card_of(world, ENTER_CARD_DETAILS_CHILD.name), "Specification", is_done=False)

    @s.and_('enter-card-details still has the parent checkout-flow (Place Parent At Leftmost Child Stage)')
    def _(world):
        expect(card_of(world, ENTER_CARD_DETAILS_CHILD.name)["session"]["parent"]).to(equal(CHECKOUT_FLOW.name))


@shared_stories.scenario("Reassign Ticket Parent", "Move a child to another parent")
def _(s):
    @s.given('the ticket enter-card-details is a child of checkout-flow')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(ENTER_CARD_DETAILS_CHILD)

    @s.and_('the ticket billing-report is In progress in Discovery')
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when('the Person drags enter-card-details onto billing-report')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # Board.ticket("billing-report")
        #   <- billing-report
        # enter-card-details.reassign_parent(billing-report)
        #   -> self.session.set_parent(billing-report.session)
        #   <- enter-card-details, its parent billing-report
        world.Ticket.load(ENTER_CARD_DETAILS_CHILD.name).reassign_parent(world.Ticket.load(BILLING_REPORT.name))

    @s.then("billing-report's card holds enter-card-details")
    def _(world):
        expect(children_in(card_of(world, BILLING_REPORT.name))).to(equal([ENTER_CARD_DETAILS_CHILD.name]))

    @s.and_("checkout-flow's card no longer holds enter-card-details")
    def _(world):
        expect(children_in(card_of(world, CHECKOUT_FLOW.name))).to(equal([]))

    @s.and_("enter-card-details' session.json names billing-report as its parent")
    def _(world):
        expect(saved_parent(world, ENTER_CARD_DETAILS_CHILD)).to(equal(BILLING_REPORT.name))


@shared_stories.scenario("Reassign Ticket Parent", "Take a child off its parent")
def _(s):
    @s.given('the ticket enter-card-details is a child of checkout-flow')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(ENTER_CARD_DETAILS_CHILD)

    @s.when('the Person Alt-drags enter-card-details out of checkout-flow')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # enter-card-details.reassign_parent(None)
        #   -> self.session.set_parent(None)
        #   <- enter-card-details with no parent
        world.Ticket.load(ENTER_CARD_DETAILS_CHILD.name).reassign_parent(None)

    @s.then('enter-card-details shows as a card of its own with no parent')
    def _(world):
        child = card_of(world, ENTER_CARD_DETAILS_CHILD.name)
        expect((child["title"], child["session"]["parent"])).to(equal((ENTER_CARD_DETAILS_CHILD.title, "")))

    @s.and_("checkout-flow's card holds no row for enter-card-details, dashed or not")
    def _(world):
        expect(children_in(card_of(world, CHECKOUT_FLOW.name))).to(equal([]))

    @s.and_("enter-card-details' session.json names no parent")
    def _(world):
        expect(saved_parent(world, ENTER_CARD_DETAILS_CHILD)).to(equal(""))


@shared_stories.scenario("Place Parent At Leftmost Child Stage", "Show a parent in its earliest child's stage")
def _(s):
    @s.given('the ticket checkout-flow has the child tickets enter-card-details in Specification and confirm-order in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(ENTER_CARD_DETAILS_IN_SPECIFICATION)
        world.project.seed_session(CONFIRM_ORDER_CHILD)

    @s.when('the board shows checkout-flow')
    def _(world):
        # Board.show()
        #   -> checkout-flow.column
        #      -> self.children
        #   <- checkout-flow in Discovery, the stage of its leftmost child
        world.parent = card_of(world, CHECKOUT_FLOW.name)

    @s.then('checkout-flow shows in the Discovery column')
    def _(world):
        expect(world.parent["column"]["name"]).to(equal("Discovery"))


@shared_stories.scenario("Place Parent At Leftmost Child Stage", "Move a parent on when its last child moves on")
def _(s):
    @s.given('the ticket checkout-flow has the child tickets enter-card-details in Specification and confirm-order Done in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(ENTER_CARD_DETAILS_IN_SPECIFICATION)
        world.project.seed_session(CONFIRM_ORDER_DONE_IN_DISCOVERY)

    @s.when('the Person moves confirm-order to Specification')
    def _(world):
        # Board.ticket("confirm-order")
        #   <- confirm-order
        # confirm-order.move_next()
        #   <- confirm-order in Specification
        # Board.show()
        #   -> checkout-flow.column
        #      -> self.children
        #   <- checkout-flow in Specification, the stage of its leftmost child
        world.Ticket.load(CONFIRM_ORDER_CHILD.name).move_next()

    @s.then('checkout-flow shows in the Specification column')
    def _(world):
        expect(card_of(world, CHECKOUT_FLOW.name)["column"]["name"]).to(equal("Specification"))


@shared_stories.scenario("Place Parent At Leftmost Child Stage", "Refuse to move a parent by hand")
def _(s):
    @s.given('the ticket checkout-flow has the child ticket confirm-order in Discovery')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(CONFIRM_ORDER_CHILD)

    @s.when('the Person tries to move checkout-flow to Specification')
    def _(world):
        # Board.ticket("checkout-flow")
        #   <- checkout-flow
        # checkout-flow.move_next()
        #   -> self.children
        #   <- checkout-flow, still in Discovery: a parent moves only with its children
        world.refusal = refusal_of(lambda: world.Ticket.load(CHECKOUT_FLOW.name).move_next())

    @s.then('checkout-flow stays in the Discovery column')
    def _(world):
        expect_refused(world.refusal, ParentMovesWithChildrenError, "checkout-flow has child tickets; a parent moves only with its children")
        expect_placed(card_of(world, CHECKOUT_FLOW.name), "Discovery", is_done=False)
