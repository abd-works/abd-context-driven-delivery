from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../story-map.md#s-person----write-ticket-handoff
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Write Ticket Handoff
# Actor: Person
with story("Write Ticket Handoff"):
    with scenario("Ask the chat to write a handoff"):
        # Evidence: observed: ticket-client.spec 'Write Ticket Handoff' — 'should fill the prompt with the handoff command'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) and a chat is connected"):
            pass
        with when("the Person asks for a handoff on checkout-flow"):
            # Board page -> Chat.send('fill', 'Write a handoff for ticket checkout-flow with /space-handoff-handoff-session.')
            # chat mod -> Chat.check_in(is_busy=False) <- the fill
            # chat mod -> Claude Code prompt.fill(text, append)  [External: Claude Code]
            pass
        with then("the chat's prompt holds Write a handoff for ticket checkout-flow with /space-handoff-handoff-session."):
            pass
        with and_("a toast says Queued for the prompt, for you to review"):
            pass
    with scenario("Hold the handoff until the chat's turn ends"):
        # Evidence: observed: chat-client.spec 'should say a fill waits for the turn to end while the chat is busy'; story-actions.spec 'should hold a fill at the server until the turn ends'; Chat.check_in keeps a fill waiting while busy.
        with given("the connected chat is running a turn"):
            pass
        with when("the Person asks for a handoff on checkout-flow"):
            # Board page -> Chat.send('fill', ...)
            # chat mod -> Chat.check_in(is_busy=True) <- nothing
            pass
        with then("a toast says the fill goes in when this turn ends"):
            pass
        with and_("the prompt receives the text once the turn has ended"):
            pass
    with scenario("Keep Handoff off with no chat"):
        # Evidence: observed: tests/board-surface.spec.ts 'with no chat connected' — 'should say to load the mod and turn off what sends to a chat'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the Person looks at checkout-flow's card"):
            pass
        with then("Handoff is off"):
            pass
        with and_("the header says No chat connected: load the cdd-board mod in a chat to send commands"):
            pass
