from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../story-map.md#s-person----split-ticket-into-child-tickets
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Split Ticket Into Child Tickets
# Actor: Person
with story("Split Ticket Into Child Tickets"):
    with scenario("Ask the chat to split a ticket into child tickets"):
        # Evidence: observed: ticket-client.tsx fillSplit and ticket-card-view.tsx SplitActionView; kanban_tools_spec 'that opens a ticket split from another' — 'should name the ticket it was split from'; ticket-client.spec 'should name a split ticket by its parent'. No spec presses Split.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) and a chat is connected"):
            pass
        with when("the Person splits checkout-flow into child tickets"):
            # Board page -> Chat.send('fill', 'Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.new with parent checkout-flow for each story.')
            pass
        with then("the chat's prompt holds Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.new with parent checkout-flow for each story."):
            pass
        with when("the chat opens a child ticket Enter card details with parent checkout-flow"):
            # Agent -> Ticket.new('Enter card details', 'story', 'checkout-flow')
            # Ticket -> Session.new('enter-card-details', <repo>, <repo>, {parent: checkout-flow}, is_current=False)
            pass
        with then("enter-card-details is In progress in Discovery"):
            pass
        with and_("its details read enter-card-details · story of checkout-flow"):
            pass
    with scenario("Keep Split off where nothing can take the prompt"):
        # Evidence: observed: ticket-card-view.tsx useCannotFill; tests/board-surface.spec.ts 'with no chat connected'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the Person looks at checkout-flow's card"):
            pass
        with then("Split is off"):
            pass
        with and_("Split is also off on a closed ticket and on a locked one"):
            pass
