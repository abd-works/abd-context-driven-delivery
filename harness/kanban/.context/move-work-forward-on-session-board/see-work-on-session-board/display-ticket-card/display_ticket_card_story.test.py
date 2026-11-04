from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../story-map.md#s-board-app----display-ticket-card
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Display Ticket Card
# Actor: Board App
#
# Acceptance criteria:
# - Display Sessions As Tickets: each work session shows as one ticket and the main session is not on the board. Observed.
# - Place Ticket In Column: a ticket shows in the stage of its latest move, or before any move in the earliest stage its session shows work in. Observed.
# - Display Active Ticket: the active ticket has a thick orange outline. Observed.
# - Show Active Ticket On Status Line: the chat's status line names the active ticket, its stage, its next guidance, and its violations. Inferred: `statusOf` in `harness/chat-ui/pane/hooks/register.ts`.
with story("Display Ticket Card"):
    with scenario("Show every work session as a ticket"):
        # Evidence: observed: kanban_spec 'should show every work session as a ticket', 'should leave main off the board', 'should leave archived sessions off the board', 'should show closed sessions in Complete'.
        with given("the [repository](../../../kanban-model.md#repo)'s .sessions/ holds the work [sessions](../../../kanban-model.md#session) pet-visits and sign-up, the closed session browse-pets, main, and the archived session old-spike"):
            pass
        with when("the session board reads the [board](../../../kanban-model.md#board)"):
            # Board -> Board.tickets
            # Board -> Session.all_in(repo_root)
            # Session <- pet-visits, sign-up, browse-pets
            pass
        with then("the Discovery [stage](../../../kanban-model.md#stage--column) shows the [tickets](../../../kanban-model.md#ticket--card) Pet visits and Sign up"):
            pass
        with and_("the Complete [column](../../../kanban-model.md#column) shows Browse pets"):
            pass
        with but_("main and old-spike are not on the board"):
            pass
    with scenario("Place a ticket in the stage of its latest move"):
        # Evidence: observed: kanban_tools_spec 'should show the ticket in the next stage'; Ticket.column in ticket.py; fixture-repo.ts second-spec.
        with given("the [session log](../../../kanban-model.md#session) of the [ticket](../../../kanban-model.md#ticket--card) second-spec ends with move Specification"):
            pass
        with when("the session board reads the [board](../../../kanban-model.md#board)"):
            # Board -> Ticket.column
            # Ticket <- the stage of its latest move line: Specification
            pass
        with then("second-spec shows In progress in the Specification [stage](../../../kanban-model.md#stage--column)"):
            pass
    with scenario("Place a ticket with no move in the earliest stage it has work in"):
        # Evidence: observed: kanban_spec 'with its first logged work on a Specification fidelity' — 'should be in Specification'; 'that has just been started' — 'should be in Discovery, in progress'.
        with given("the [session log](../../../kanban-model.md#session) of the [ticket](../../../kanban-model.md#ticket--card) pet-visits has one line, generate /work/ux ux mockup html ux"):
            pass
        with but_("it has no move line"):
            pass
        with when("the session board reads the [board](../../../kanban-model.md#board)"):
            # Board -> Ticket.column
            # Ticket -> Ticket.progress
            # Ticket <- the first stage with work done: Specification
            pass
        with then("pet-visits shows in the Specification [stage](../../../kanban-model.md#stage--column)"):
            pass
    with scenario("Draw the card's title, age, and practice blocks"):
        # Evidence: observed: board-client.spec 'Display Ticket Card' — 'should say how many hours ago its ticket was worked on', 'should say one hour in the singular', 'should say a ticket with no activity has none'; ticket-card-view.tsx SegmentsView draws one block per enabled fidelity of its stage, dim while not started.
        with given("the [ticket](../../../kanban-model.md#ticket--card) checkout-flow, titled Checkout flow, last worked on at 2026-11-01T10:00:00Z"):
            pass
        with and_("its story_map [fidelity](../../../kanban-model.md#fidelityguidance) has violations and its other Discovery fidelities are not started"):
            pass
        with when("the session board draws checkout-flow's [card](../../../kanban-model.md#card) 13 hours later"):
            # Board page -> Ticket.to_json(): title, last_activity, progress, practices
            pass
        with then("the card reads Checkout flow and 13 hours ago"):
            pass
        with and_("it shows one block for each enabled Discovery fidelity, the story_map block in the violations colour and the rest dim"):
            pass
        with and_("a violations link on the card opens the report"):
            pass
    with scenario("Outline the active ticket"):
        # Evidence: observed: kanban_spec 'should name the ticket of the current session as active'; ticket-card-view.tsx draws the active ticket's border 3 pixels wide in the accent colour.
        with given("the [repository](../../../kanban-model.md#repo)'s .sessions/session.json names checkout-flow as the open [session](../../../kanban-model.md#session)"):
            pass
        with when("the session board reads the [board](../../../kanban-model.md#board)"):
            # Board -> Board.active
            # Board <- Ticket checkout-flow
            pass
        with then("the checkout-flow [card](../../../kanban-model.md#card) has a thick orange outline"):
            pass
        with and_("the header names Checkout flow as active"):
            pass
    with scenario("Name the active ticket on the chat's status line"):
        # Evidence: inferred: statusOf and readActive in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), in Discovery, with violations on stories-story_map"):
            pass
        with when("a turn in a chat with the cdd-board mod loaded ends"):
            # chat mod -> Board.show()
            # Board <- the active ticket checkout-flow
            pass
        with then("the chat's status line reads checkout-flow · Discovery · next: stories-story_map · 1 with violations"):
            pass
