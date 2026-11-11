"""Organize Ticket Hierarchy: the shared scenarios the Python tiers will replay, at scenarios fidelity: the steps only, no bodies yet.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md.
Map: harness/.context/stories/story-map.md. Model: .context/kanban-model.md.

Only the stories of ticket maintain-tickets-on-board are here; the sub-epic's built stories stay in
steer-ticket-sessions.story.shared.py. No tier spec loads this file yet: its steps have no bodies, so replaying them
would pass without checking anything. Acceptance tests give each step its body and add the domain and server specs.
Each When carries its scenario's realization as comments: the operations it needs, none of which exists yet.

Left to the board app's TypeScript specs, because only the page shows them: Display Child Tickets In Parent, Expand Parent Ticket.
"""

from __future__ import annotations

from space.kanban.story_test import SharedStories

shared_stories = SharedStories("Organize Ticket Hierarchy")


@shared_stories.scenario("Add Child Ticket", "Add a child ticket by hand")
def _(s):
    @s.given('the ticket checkout-flow is In progress in Discovery')
    def _(world):
        pass

    @s.but_('checkout-flow has no child tickets')
    def _(world):
        pass

    @s.when('the Person adds the child ticket Enter card details to checkout-flow')
    def _(world):
        # Board.ticket("checkout-flow")
        #   <- checkout-flow
        # checkout-flow.add_child("Enter card details")
        #   -> self.session.open_child("Enter card details", scope="story")
        #   <- enter-card-details In progress in Discovery, its parent checkout-flow
        pass

    @s.then('the ticket enter-card-details is In progress in Discovery with the parent checkout-flow')
    def _(world):
        pass

    @s.and_("checkout-flow's card holds enter-card-details (Display Child Tickets In Parent)")
    def _(world):
        pass


@shared_stories.scenario("Detach Child Ticket", "Pull a child out of its parent")
def _(s):
    @s.given('the ticket checkout-flow holds its child ticket enter-card-details in Discovery')
    def _(world):
        pass

    @s.when('the Person pulls enter-card-details out of checkout-flow')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # enter-card-details.pull_out()
        #   -> self.session.mark_pulled_out()
        #   <- enter-card-details pulled out, its parent still checkout-flow
        pass

    @s.then('enter-card-details shows as a card of its own beside checkout-flow, titled Checkout flow.Enter card details')
    def _(world):
        pass

    @s.and_('enter-card-details still has the parent checkout-flow')
    def _(world):
        pass

    @s.and_("checkout-flow's card holds a dashed row for enter-card-details")
    def _(world):
        pass


@shared_stories.scenario("Detach Child Ticket", "Move a pulled-out child like any ticket")
def _(s):
    @s.given('the ticket enter-card-details was pulled out of checkout-flow and is Done in Discovery')
    def _(world):
        pass

    @s.when('the Person moves enter-card-details to Specification')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # enter-card-details.move_next()
        #   <- enter-card-details in Specification, its parent still checkout-flow
        pass

    @s.then('the Specification column shows enter-card-details')
    def _(world):
        pass

    @s.and_('enter-card-details still has the parent checkout-flow (Place Parent At Leftmost Child Stage)')
    def _(world):
        pass


@shared_stories.scenario("Reassign Ticket Parent", "Move a child to another parent")
def _(s):
    @s.given('the ticket enter-card-details is a child of checkout-flow')
    def _(world):
        pass

    @s.and_('the ticket billing-report is In progress in Discovery')
    def _(world):
        pass

    @s.when('the Person makes enter-card-details a child of billing-report')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # Board.ticket("billing-report")
        #   <- billing-report
        # enter-card-details.reassign_parent(billing-report)
        #   -> self.session.set_parent(billing-report.session)
        #   <- enter-card-details, its parent billing-report
        pass

    @s.then("billing-report's card holds enter-card-details")
    def _(world):
        pass

    @s.and_("checkout-flow's card no longer holds enter-card-details")
    def _(world):
        pass

    @s.and_("enter-card-details' session.json names billing-report as its parent")
    def _(world):
        pass


@shared_stories.scenario("Reassign Ticket Parent", "Take a child off its parent")
def _(s):
    @s.given('the ticket enter-card-details is a child of checkout-flow')
    def _(world):
        pass

    @s.when('the Person takes enter-card-details off checkout-flow')
    def _(world):
        # Board.ticket("enter-card-details")
        #   <- enter-card-details
        # enter-card-details.reassign_parent(None)
        #   -> self.session.set_parent(None)
        #   <- enter-card-details with no parent
        pass

    @s.then('enter-card-details shows as a card of its own with no parent')
    def _(world):
        pass

    @s.and_("checkout-flow's card holds no row for enter-card-details, dashed or not")
    def _(world):
        pass

    @s.and_("enter-card-details' session.json names no parent")
    def _(world):
        pass


@shared_stories.scenario("Place Parent At Leftmost Child Stage", "Show a parent in its earliest child's stage")
def _(s):
    @s.given('the ticket checkout-flow has the child tickets enter-card-details in Specification and confirm-order in Discovery')
    def _(world):
        pass

    @s.when('the board shows checkout-flow')
    def _(world):
        # Board.show()
        #   -> checkout-flow.column
        #      -> self.children
        #   <- checkout-flow in Discovery, the stage of its leftmost child
        pass

    @s.then('checkout-flow shows in the Discovery column')
    def _(world):
        pass


@shared_stories.scenario("Place Parent At Leftmost Child Stage", "Move a parent on when its last child moves on")
def _(s):
    @s.given('the ticket checkout-flow has the child tickets enter-card-details in Specification and confirm-order Done in Discovery')
    def _(world):
        pass

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
        pass

    @s.then('checkout-flow shows in the Specification column')
    def _(world):
        pass


@shared_stories.scenario("Place Parent At Leftmost Child Stage", "Refuse to move a parent by hand")
def _(s):
    @s.given('the ticket checkout-flow has the child ticket confirm-order in Discovery')
    def _(world):
        pass

    @s.when('the Person tries to move checkout-flow to Specification')
    def _(world):
        # Board.ticket("checkout-flow")
        #   <- checkout-flow
        # checkout-flow.move_next()
        #   -> self.children
        #   <- checkout-flow, still in Discovery: a parent moves only with its children
        pass

    @s.then('checkout-flow stays in the Discovery column')
    def _(world):
        pass


@shared_stories.scenario("Nest Child Branch And Session", "Nest a child's session and branch under its parent's")
def _(s):
    @s.given("the ticket checkout-flow's session is .sessions/checkout-flow on the branch checkout-flow")
    def _(world):
        pass

    @s.when('Claude Code opens the child ticket Enter card details of checkout-flow')
    def _(world):
        # ticket.create("Enter card details", scope="story", parent="checkout-flow")
        #   -> Board.ticket("checkout-flow")
        #   <- checkout-flow
        #   -> checkout-flow.add_child("Enter card details")
        #      -> self.session.open_child("Enter card details", scope="story")
        #      <- the session .sessions/checkout-flow/enter-card-details
        #      -> enter-card-details.branch
        #         -> self.parent.branch
        #      <- checkout-flow.enter-card-details
        pass

    @s.then("enter-card-details' session folder is .sessions/checkout-flow/enter-card-details")
    def _(world):
        pass

    @s.and_("enter-card-details' branch is checkout-flow.enter-card-details")
    def _(world):
        pass
