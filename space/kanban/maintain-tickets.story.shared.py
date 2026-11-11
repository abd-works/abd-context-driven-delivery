"""Maintain Tickets: the shared scenarios the Python tiers will replay, at scenarios fidelity: the steps only, no bodies yet.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md.
Map: harness/.context/stories/story-map.md. Model: .context/kanban-model.md.

Only the stories of ticket maintain-tickets-on-board are here; the sub-epic's built stories stay in
steer-ticket-sessions.story.shared.py. No tier spec loads this file yet: its steps have no bodies, so replaying them
would pass without checking anything. Acceptance tests give each step its body and add the domain and server specs.
"""

from __future__ import annotations

from space.kanban.story_test import SharedStories

shared_stories = SharedStories("Maintain Tickets")


@shared_stories.scenario("Edit Ticket Text", "Show a ticket's text from its session file")
def _(s):
    @s.given("the ticket checkout-flow's session folder holds checkout-flow.md with the text Pay for the basket.")
    def _(world):
        pass

    @s.when('the Person opens the board')
    def _(world):
        pass

    @s.then("checkout-flow's card shows Pay for the basket.")
    def _(world):
        pass


@shared_stories.scenario("Edit Ticket Text", "Edit a ticket's text")
def _(s):
    @s.given("the ticket checkout-flow's card shows Pay for the basket.")
    def _(world):
        pass

    @s.when("the Person edits checkout-flow's text to Pay for the basket by card.")
    def _(world):
        pass

    @s.then("checkout-flow.md in checkout-flow's session folder holds Pay for the basket by card.")
    def _(world):
        pass

    @s.and_("checkout-flow's card shows Pay for the basket by card.")
    def _(world):
        pass


@shared_stories.scenario("Edit Ticket Text", "Write the text file for a ticket that has none")
def _(s):
    @s.given('the ticket pet-visits is In progress in Discovery')
    def _(world):
        pass

    @s.but_("pet-visits' session folder holds no pet-visits.md")
    def _(world):
        pass

    @s.when("the Person edits pet-visits' text to Book a visit for a pet.")
    def _(world):
        pass

    @s.then("pet-visits.md in pet-visits' session folder holds Book a visit for a pet.")
    def _(world):
        pass

    @s.and_("pet-visits' card shows Book a visit for a pet.")
    def _(world):
        pass


@shared_stories.scenario("Edit Ticket Text", "Edit a backlog item's text")
def _(s):
    @s.given('the backlog item Gift cards has the text Sell gift cards.')
    def _(world):
        pass

    @s.when("the Person edits Gift cards' text to Sell gift cards at the till.")
    def _(world):
        pass

    @s.then('.sessions/_backlog/gift-cards.md holds Sell gift cards at the till.')
    def _(world):
        pass

    @s.and_('the Backlog shows Gift cards with the text Sell gift cards at the till.')
    def _(world):
        pass


@shared_stories.scenario("Edit Ticket Text", "Tell the agent which file holds the ticket's text")
def _(s):
    @s.given("the ticket checkout-flow's session folder holds checkout-flow.md")
    def _(world):
        pass

    @s.when('checkout-flow becomes the active ticket')
    def _(world):
        pass

    @s.then("the agent's context for checkout-flow names .sessions/checkout-flow/checkout-flow.md as the ticket's text")
    def _(world):
        pass


@shared_stories.scenario("Reorder Tickets In Column", "Keep a ticket where it was moved in its column")
def _(s):
    @s.given('the Discovery column shows the ticket pet-visits above sign-up')
    def _(world):
        pass

    @s.when('the Person moves sign-up above pet-visits in Discovery')
    def _(world):
        pass

    @s.then('Discovery shows sign-up above pet-visits')
    def _(world):
        pass

    @s.and_('Discovery still shows sign-up above pet-visits when the board is read again')
    def _(world):
        pass


@shared_stories.scenario("Reorder Tickets In Column", "Keep a backlog item where it was moved")
def _(s):
    @s.given('the Backlog shows the backlog item Gift cards above Returns and refunds')
    def _(world):
        pass

    @s.when('the Person moves Returns and refunds above Gift cards')
    def _(world):
        pass

    @s.then('the Backlog shows Returns and refunds above Gift cards')
    def _(world):
        pass

    @s.and_('the Backlog still shows Returns and refunds above Gift cards when the board is read again')
    def _(world):
        pass


@shared_stories.scenario("Delete Ticket", "Delete a ticket and its session folder")
def _(s):
    @s.given('the ticket pet-visits is In progress in Discovery')
    def _(world):
        pass

    @s.when('the Person deletes pet-visits')
    def _(world):
        pass

    @s.then('no column shows pet-visits')
    def _(world):
        pass

    @s.and_('.sessions/pet-visits is gone')
    def _(world):
        pass


@shared_stories.scenario("Delete Ticket", "Refuse to delete a ticket the board does not have")
def _(s):
    @s.given('the board shows no ticket named no-such-ticket')
    def _(world):
        pass

    @s.when('the Person deletes no-such-ticket')
    def _(world):
        pass

    @s.then("the board says no ticket named 'no-such-ticket' on the board")
    def _(world):
        pass

    @s.but_('no session folder is removed')
    def _(world):
        pass


@shared_stories.scenario("Tag Ticket Session", "Tag a ticket's session")
def _(s):
    @s.given('the ticket pet-visits has no tags')
    def _(world):
        pass

    @s.when("the Person tags pet-visits' session with billing")
    def _(world):
        pass

    @s.then("pet-visits' card shows the tag billing")
    def _(world):
        pass

    @s.and_("pet-visits' session.json holds the tag billing")
    def _(world):
        pass


@shared_stories.scenario("Tag Ticket Session", "Add a second tag")
def _(s):
    @s.given('the ticket pet-visits is tagged billing')
    def _(world):
        pass

    @s.when("the Person tags pet-visits' session with urgent")
    def _(world):
        pass

    @s.then("pet-visits' card shows the tags billing and urgent")
    def _(world):
        pass
