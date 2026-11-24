from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Show Tickets On Board
# Map: ../../../../.context/story-map.md#s-board-app----display-ticket-card
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Display Ticket Card
# Actor: Board App
#
# Acceptance criteria:
# - Display Sessions As Tickets: each session shows as one ticket, main first. Observed.
# - Display Active Ticket: the active ticket has a thick orange outline. Observed.
# - Show Active Ticket On Status Line: the chat's status line names the active ticket, its stage, its next guidance, and its violations. Inferred: `statusOf` in `harness/chat-ui/pane/hooks/register.ts`.
with story("Display Ticket Card"):
    with scenario("Show every work session as a ticket"):
        # Evidence: observed: kanban_spec 'should show every work session as a ticket', 'should leave main off the board', 'should leave archived sessions off the board', 'should show closed sessions in Complete'.
        with given("the [repository](../../../../.context/kanban-model.md#repo)'s .sessions/ holds the work [sessions](../../../../.context/kanban-model.md#session) pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike"):
            pass
        with when("the session board reads the [board](../../../../.context/kanban-model.md#board)"):
            # Board -> Board.tickets
            # Board -> Sessions.all()
            # Session <- pet-visits, sign-up, browse-pets
            pass
        with then("the Discovery [stage](../../../../.context/kanban-model.md#stage--column) shows the [tickets](../../../../.context/kanban-model.md#ticket--card) main, Pet visits, and Sign up"):
            pass
        with and_("the Complete [column](../../../../.context/kanban-model.md#column) shows Browse pets"):
            pass
        with but_("old-spike is not on the board"):
            pass
    with scenario("Draw the card's title, age, and fidelity segments"):
        # Evidence: observed: board-client.spec 'Display Ticket Card' — 'should say how many hours ago its ticket was worked on', 'should say one hour in the singular', 'should say a ticket with no activity has none'; ticket-card-view.tsx SegmentsView draws one segment per enabled fidelity of its stage, dim while not started.
        with given("the [ticket](../../../../.context/kanban-model.md#ticket--card) checkout-flow, titled Checkout flow, last worked on at 2026-11-01T10:00:00Z"):
            pass
        with and_("its story_map [fidelity](../../../../.context/kanban-model.md#fidelityguidance) has violations and its other Discovery fidelities are not started"):
            pass
        with when("the session board draws checkout-flow's [card](../../../../.context/kanban-model.md#card) 13 hours later"):
            # Board page -> data_of(Ticket): title, last_activity, progress, practices
            pass
        with then("the card reads Checkout flow and 13 hours ago"):
            pass
        with and_("it shows one segment for each enabled Discovery fidelity, the story_map segment in the violations colour and the rest dim"):
            pass
        with and_("a violations link on the card opens the report"):
            pass
    with scenario("Outline the active ticket"):
        # Evidence: observed: kanban_spec 'should name the ticket of the current session as active'; ticket-card-view.tsx draws the active ticket's border 3 pixels wide in the accent colour.
        with given("the [repository](../../../../.context/kanban-model.md#repo)'s .sessions/session.json names checkout-flow as the open [session](../../../../.context/kanban-model.md#session)"):
            pass
        with when("the session board reads the [board](../../../../.context/kanban-model.md#board)"):
            # Board -> Board.active
            # Board <- Ticket checkout-flow
            pass
        with then("the checkout-flow [card](../../../../.context/kanban-model.md#card) has a thick orange outline"):
            pass
        with and_("the header names Checkout flow as active"):
            pass
    with scenario("Name the active ticket on the chat's status line"):
        # Evidence: inferred: statusOf and readActive in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod.
        with given("checkout-flow is the active [ticket](../../../../.context/kanban-model.md#ticket--card), in Discovery, with violations on stories-story-map"):
            pass
        with when("a turn in a chat with the cdd-board mod loaded ends"):
            # chat mod -> Board.show()
            # Board <- the active ticket checkout-flow
            pass
        with then("the chat's status line reads checkout-flow · Discovery · next: stories-story-map · 1 with violations"):
            pass
