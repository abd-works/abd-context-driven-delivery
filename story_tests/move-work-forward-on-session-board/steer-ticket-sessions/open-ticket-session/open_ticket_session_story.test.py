from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----open-ticket-session
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Open Ticket Session
# Actor: Person
with story("Open Ticket Session"):
    with scenario("Open a new ticket"):
        # Evidence: observed: kanban_tools_spec 'that opens a new ticket' — 'should return the new ticket in Discovery', 'should leave the current session as it is'; kanban_spec 'should name Generate on story_map as next'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the Person opens a new ticket titled Pet visits"):
            # Person -> Ticket.create('Pet visits', 'feature')
            # Ticket -> Sessions.create('pet-visits', <repo>, title, scope, parent)
            # Ticket <- Ticket pet-visits
            pass
        with then("pet-visits is In progress in Discovery, titled Pet visits"):
            pass
        with and_("its next step is Generate on stories-story-map"):
            pass
        with and_("checkout-flow is still the active ticket"):
            pass
    with scenario("Ask a chat to open a ticket"):
        # Evidence: observed: board-page.ts openNewTicket; tests/board-surface.spec.ts 'with no chat connected' shows + Ticket off.
        with given("a chat is connected to the session board"):
            pass
        with when("the Person asks for a new ticket from the board's header"):
            # Board page -> Chat.send('fill', 'Open a new ticket with ticket.create, titled: ')
            pass
        with then("the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish"):
            pass
    with scenario("Keep + Ticket off with no chat"):
        # Evidence: observed: tests/board-surface.spec.ts 'with no chat connected' shows + Ticket off.
        with given("no chat is connected to the session board"):
            pass
        with when("the session board draws its header"):
            # Board page -> ChatClient.canSend <- false
            pass
        with then("+ Ticket is off"):
            pass
    with scenario("Open a ticket on a folder of the repository"):
        # Evidence: observed: kanban_tools_spec 'that opens a ticket on a folder in the repository' — 'should save that folder as the session's workpath'; 'that opens a ticket with no folder' — 'should leave the session working on the repository'.
        with given("the [repository](../../../.context/kanban-model.md#repo) has the folder src/billing"):
            pass
        with when("the Person opens a ticket titled Billing report on src/billing"):
            # Person -> Ticket.create('Billing report', 'feature', '', 'src/billing')
            # Ticket -> Sessions.create('billing-report', <repo>/src/billing, title, scope, parent)
            pass
        with then("billing-report's [session](../../../.context/kanban-model.md#session) works in src/billing"):
            pass
        with and_("the details show its workpath as src/billing"):
            pass
