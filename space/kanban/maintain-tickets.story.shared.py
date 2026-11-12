"""Maintain Tickets: the shared scenarios the Python tiers replay.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md.
Map: harness/.context/stories/story-map.md. Model: .context/kanban-model.md.

Only the stories of ticket maintain-tickets-on-board are here; the sub-epic's built stories stay in
steer-ticket-sessions.story.shared.py. Steps reach the board only through the namespace a tier hands them (`world.Ticket`,
`world.BacklogItem`, `world.Board`), so the domain spec and the cdd tools spec replay the same steps. Each When carries
its scenario's realization as comments.
"""

from __future__ import annotations

import json

from expects import be_none, contain, equal, expect

from space.kanban.board import TicketNotFoundError
from space.kanban.session_board_examples import (
    BILLING_TAG,
    CHECKOUT_FLOW,
    CHECKOUT_FLOW_TEXT,
    CONFIRM_ORDER_CHILD,
    CONFIRM_ORDER_TEXT,
    EDITED_CHECKOUT_FLOW_TEXT,
    EDITED_CONFIRM_ORDER_TEXT,
    EDITED_GIFT_CARDS_TEXT,
    GIFT_CARDS_IN_BACKLOG,
    NO_SUCH_TICKET,
    PET_VISITS,
    PET_VISITS_TEXT,
    RETURNS_AND_REFUNDS,
    SIGN_UP,
    URGENT_TAG,
    idea_file_text,
)
from space.kanban.story_test import SharedStories, column_in, expect_backlog, expect_refused, names_in, refusal_of, ticket_in

shared_stories = SharedStories("Maintain Tickets")


def board_of(world) -> dict:
    return world.data_of(world.Board.load().show())


def idea_file(world, seed) -> str:
    """The text of the idea file in seed's session folder, <name>.md."""
    return (world.project.sessions / seed.name / f"{seed.name}.md").read_text(encoding="utf-8")


def shown_in_order(column: dict, *names: str) -> list[str]:
    """names in the order column shows them."""
    return [name for name in names_in(column) if name in names]


@shared_stories.scenario("Edit Ticket Text", "Show a ticket's text from its session file")
def _(s):
    @s.given("the ticket checkout-flow's session folder holds checkout-flow.md with the text Pay for the basket.")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_file(CHECKOUT_FLOW, f"{CHECKOUT_FLOW.name}.md", idea_file_text(CHECKOUT_FLOW.title, CHECKOUT_FLOW_TEXT))

    @s.when('the Person opens the board')
    def _(world):
        # Board.show()
        #   -> checkout-flow.text
        #      -> self.session.text
        #   <- checkout-flow with the text Pay for the basket.
        world.board = board_of(world)

    @s.then("checkout-flow's card shows Pay for the basket.")
    def _(world):
        expect(ticket_in(world.board, CHECKOUT_FLOW.name)["text"]).to(equal(CHECKOUT_FLOW_TEXT))


@shared_stories.scenario("Edit Ticket Text", "Edit a ticket's text")
def _(s):
    @s.given("the ticket checkout-flow's card shows Pay for the basket.")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_file(CHECKOUT_FLOW, f"{CHECKOUT_FLOW.name}.md", idea_file_text(CHECKOUT_FLOW.title, CHECKOUT_FLOW_TEXT))

    @s.when("the Person edits checkout-flow's text to Pay for the basket by card.")
    def _(world):
        # Board.ticket("checkout-flow")
        #   <- checkout-flow
        # checkout-flow.edit_text("Pay for the basket by card.")
        #   -> self.session.keep_text("Pay for the basket by card.")
        #   <- checkout-flow with the text Pay for the basket by card.
        world.edited = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).edit_text(text=EDITED_CHECKOUT_FLOW_TEXT))

    @s.then("checkout-flow.md in checkout-flow's session folder holds Pay for the basket by card.")
    def _(world):
        expect(idea_file(world, CHECKOUT_FLOW)).to(equal(idea_file_text(CHECKOUT_FLOW.title, EDITED_CHECKOUT_FLOW_TEXT)))

    @s.and_("checkout-flow's card shows Pay for the basket by card.")
    def _(world):
        expect(ticket_in(board_of(world), CHECKOUT_FLOW.name)["text"]).to(equal(EDITED_CHECKOUT_FLOW_TEXT))


@shared_stories.scenario("Edit Ticket Text", "Write the text file for a ticket that has none")
def _(s):
    @s.given('the ticket pet-visits is on the board')
    def _(world):
        world.project.seed_session(PET_VISITS)

    @s.but_("pet-visits' session folder holds no pet-visits.md")
    def _(world):
        # The session seeded above holds only its session.json and log.
        pass

    @s.when("the Person edits pet-visits' text to Book a visit for a pet.")
    def _(world):
        # Board.ticket("pet-visits")
        #   <- pet-visits
        # pet-visits.edit_text("Book a visit for a pet.")
        #   -> self.session.keep_text("Book a visit for a pet.")
        #   <- pet-visits with the text Book a visit for a pet.
        world.Ticket.load(PET_VISITS.name).edit_text(text=PET_VISITS_TEXT)

    @s.then("pet-visits.md in pet-visits' session folder holds Book a visit for a pet.")
    def _(world):
        expect(idea_file(world, PET_VISITS)).to(contain(PET_VISITS_TEXT))

    @s.and_("pet-visits' card shows Book a visit for a pet.")
    def _(world):
        expect(ticket_in(board_of(world), PET_VISITS.name)["text"]).to(equal(PET_VISITS_TEXT))


@shared_stories.scenario("Edit Ticket Text", "Edit a backlog item's text")
def _(s):
    @s.given('the backlog item Gift cards has the text Sell gift cards.')
    def _(world):
        world.project.seed_backlog_file(GIFT_CARDS_IN_BACKLOG)

    @s.when("the Person edits Gift cards' text to Sell gift cards at the till.")
    def _(world):
        # Board.backlog_item("Gift cards")
        #   <- Gift cards
        # Gift cards.edit_text("Sell gift cards at the till.")
        #   <- Gift cards with the text Sell gift cards at the till.
        world.BacklogItem.load(GIFT_CARDS_IN_BACKLOG.heading).edit_text(text=EDITED_GIFT_CARDS_TEXT)

    @s.then('.sessions/_backlog/gift-cards.md holds Sell gift cards at the till.')
    def _(world):
        held = (world.project.sessions / "_backlog" / GIFT_CARDS_IN_BACKLOG.file_name).read_text(encoding="utf-8")
        expect(held).to(equal(idea_file_text(GIFT_CARDS_IN_BACKLOG.heading, EDITED_GIFT_CARDS_TEXT)))

    @s.and_('the Backlog shows Gift cards with the text Sell gift cards at the till.')
    def _(world):
        items = column_in(board_of(world), "Backlog")["items"]
        expect([(item["title"], item["text"]) for item in items]).to(equal([(GIFT_CARDS_IN_BACKLOG.heading, EDITED_GIFT_CARDS_TEXT)]))


@shared_stories.scenario("Edit Ticket Text", "Edit a child's text inside its parent")
def _(s):
    @s.given('the ticket checkout-flow holds its child ticket confirm-order')
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session(CONFIRM_ORDER_CHILD)

    @s.and_("confirm-order's text is Show the order and take the payment.")
    def _(world):
        world.project.seed_session_file(CONFIRM_ORDER_CHILD, f"{CONFIRM_ORDER_CHILD.name}.md", idea_file_text(CONFIRM_ORDER_CHILD.title, CONFIRM_ORDER_TEXT))

    @s.when("the Person edits confirm-order's text inside checkout-flow's card to Show the order, then take the payment.")
    def _(world):
        # Board.ticket("confirm-order")
        #   <- confirm-order
        # confirm-order.edit_text("Show the order, then take the payment.")
        #   -> self.session.keep_text("Show the order, then take the payment.")
        #   <- confirm-order with the text Show the order, then take the payment.
        world.Ticket.load(CONFIRM_ORDER_CHILD.name).edit_text(text=EDITED_CONFIRM_ORDER_TEXT)

    @s.then("confirm-order.md in confirm-order's session folder holds Show the order, then take the payment.")
    def _(world):
        expect(idea_file(world, CONFIRM_ORDER_CHILD)).to(equal(idea_file_text(CONFIRM_ORDER_CHILD.title, EDITED_CONFIRM_ORDER_TEXT)))

    @s.and_("confirm-order's tooltip in checkout-flow's card shows Show the order, then take the payment.")
    def _(world):
        children = ticket_in(board_of(world), CHECKOUT_FLOW.name)["children"]
        expect([(child["name"], child["text"]) for child in children]).to(equal([(CONFIRM_ORDER_CHILD.name, EDITED_CONFIRM_ORDER_TEXT)]))


@shared_stories.scenario("Reorder Tickets In Column", "Keep a ticket where it was moved in its column")
def _(s):
    @s.given('the Discovery column shows the ticket pet-visits above sign-up')
    def _(world):
        world.project.seed_session(PET_VISITS)
        world.project.seed_session(SIGN_UP)

    @s.when('the Person moves sign-up above pet-visits in Discovery')
    def _(world):
        # Board.ticket("sign-up")
        #   <- sign-up
        # sign-up.move_before(pet-visits)
        #   <- Discovery with sign-up above pet-visits
        world.Ticket.load(SIGN_UP.name).move_before(world.Ticket.load(PET_VISITS.name))

    @s.then('Discovery shows sign-up above pet-visits')
    def _(world):
        discovery = column_in(board_of(world), "Discovery")
        expect(shown_in_order(discovery, SIGN_UP.name, PET_VISITS.name)).to(equal([SIGN_UP.name, PET_VISITS.name]))

    @s.and_('Discovery still shows sign-up above pet-visits when the board is read again')
    def _(world):
        discovery = column_in(board_of(world), "Discovery")
        expect(shown_in_order(discovery, SIGN_UP.name, PET_VISITS.name)).to(equal([SIGN_UP.name, PET_VISITS.name]))


@shared_stories.scenario("Reorder Tickets In Column", "Keep a backlog item where it was moved")
def _(s):
    @s.given('the Backlog shows the backlog item Gift cards above Returns and refunds')
    def _(world):
        world.project.seed_backlog_file(GIFT_CARDS_IN_BACKLOG)
        world.project.seed_backlog_file(RETURNS_AND_REFUNDS)

    @s.when('the Person moves Returns and refunds above Gift cards')
    def _(world):
        # Board.backlog_item("Returns and refunds")
        #   <- Returns and refunds
        # Returns and refunds.move_before(Gift cards)
        #   <- the Backlog with Returns and refunds above Gift cards
        world.BacklogItem.load(RETURNS_AND_REFUNDS.heading).move_before(world.BacklogItem.load(GIFT_CARDS_IN_BACKLOG.heading))

    @s.then('the Backlog shows Returns and refunds above Gift cards')
    def _(world):
        backlog = column_in(board_of(world), "Backlog")
        expect([item["title"] for item in backlog["items"]]).to(equal([RETURNS_AND_REFUNDS.heading, GIFT_CARDS_IN_BACKLOG.heading]))

    @s.and_('the Backlog still shows Returns and refunds above Gift cards when the board is read again')
    def _(world):
        expect_backlog(board_of(world), [RETURNS_AND_REFUNDS.heading, GIFT_CARDS_IN_BACKLOG.heading])


@shared_stories.scenario("Delete Ticket", "Delete a ticket and its session folder")
def _(s):
    @s.given('the ticket pet-visits is on the board')
    def _(world):
        world.project.seed_session(PET_VISITS)

    @s.when('the Person deletes pet-visits')
    def _(world):
        # Board.ticket("pet-visits")
        #   <- pet-visits
        # pet-visits.delete()
        #   -> self.session.remove()
        #   <- the board without pet-visits
        world.Ticket.load(PET_VISITS.name).delete()

    @s.then('no column shows pet-visits')
    def _(world):
        expect(ticket_in(board_of(world), PET_VISITS.name)).to(be_none)

    @s.and_('.sessions/pet-visits is gone')
    def _(world):
        expect((world.project.sessions / PET_VISITS.name).exists()).to(equal(False))


@shared_stories.scenario("Delete Ticket", "Refuse to delete a ticket the board does not have")
def _(s):
    @s.given('the board shows no ticket named no-such-ticket')
    def _(world):
        world.project.seed_session(PET_VISITS)
        world.folders = sorted(path.name for path in world.project.sessions.iterdir())

    @s.when('the Person deletes no-such-ticket')
    def _(world):
        # Board.ticket("no-such-ticket")
        #   <- TicketNotFoundError: no ticket named 'no-such-ticket' on the board
        world.refusal = refusal_of(lambda: world.Ticket.load(NO_SUCH_TICKET).delete())

    @s.then("the board says no ticket named 'no-such-ticket' on the board")
    def _(world):
        expect_refused(world.refusal, TicketNotFoundError, "no ticket named 'no-such-ticket' on the board")

    @s.and_('no session folder is removed')
    def _(world):
        expect(sorted(path.name for path in world.project.sessions.iterdir())).to(equal(world.folders))


@shared_stories.scenario("Tag Ticket Session", "Tag a ticket's session")
def _(s):
    @s.given('the ticket pet-visits has no tags')
    def _(world):
        world.project.seed_session(PET_VISITS)

    @s.when("the Person tags pet-visits' session with billing")
    def _(world):
        # Board.ticket("pet-visits")
        #   <- pet-visits
        # pet-visits.tag("billing")
        #   -> self.session.add_tag("billing")
        #   <- pet-visits tagged billing
        world.Ticket.load(PET_VISITS.name).tag(word=BILLING_TAG)

    @s.then("pet-visits' card shows the tag billing")
    def _(world):
        expect(ticket_in(board_of(world), PET_VISITS.name)["tags"]).to(equal([BILLING_TAG]))

    @s.and_("pet-visits' session.json holds the tag billing")
    def _(world):
        saved = json.loads((world.project.sessions / PET_VISITS.name / "session.json").read_text(encoding="utf-8"))
        expect(saved["tags"]).to(equal([BILLING_TAG]))


@shared_stories.scenario("Tag Ticket Session", "Add a second tag")
def _(s):
    @s.given('the ticket pet-visits is tagged billing')
    def _(world):
        world.project.seed_session(PET_VISITS)
        world.project.seed_session_fields(PET_VISITS, tags=[BILLING_TAG])

    @s.when("the Person tags pet-visits' session with urgent")
    def _(world):
        # Board.ticket("pet-visits")
        #   <- pet-visits
        # pet-visits.tag("urgent")
        #   -> self.session.add_tag("urgent")
        #   <- pet-visits tagged billing and urgent
        world.Ticket.load(PET_VISITS.name).tag(word=URGENT_TAG)

    @s.then("pet-visits' card shows the tags billing and urgent")
    def _(world):
        expect(ticket_in(board_of(world), PET_VISITS.name)["tags"]).to(equal([BILLING_TAG, URGENT_TAG]))
