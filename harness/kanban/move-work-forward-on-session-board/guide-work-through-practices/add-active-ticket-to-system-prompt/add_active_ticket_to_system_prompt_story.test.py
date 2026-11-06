from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-board-app----add-active-ticket-to-system-prompt
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Add Active Ticket To System Prompt
# Actor: Board App
with story("Add Active Ticket To System Prompt"):
    with scenario("Name the active ticket and its next guidance in the system prompt"):
        # Evidence: inferred: the prompt.compose handler in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod. The map records it Live with a local stand-in for the model.
        with given("checkout-flow, titled Checkout flow, is the active [ticket](../../../.context/kanban-model.md#ticket--card), in Discovery, with stories-story-map next"):
            pass
        with when("a chat with the cdd-board mod loaded composes its system prompt"):
            # chat mod -> Board.show()
            # Board <- active ticket checkout-flow
            pass
        with then("the system prompt holds CDD session board: you are working on ticket checkout-flow (Checkout flow), in Discovery. Its next guidance is stories-story-map."):
            pass
        with and_("it says each fidelity goes through generate, validate, then review by a person"):
            pass
    with scenario("Say a done ticket waits for a person to move it"):
        # Evidence: inferred: register.ts prompt.compose.
        with given("the active [ticket](../../../.context/kanban-model.md#ticket--card) ready-to-move is in Discovery's Done with no next guidance"):
            pass
        with when("the chat composes its system prompt"):
            # chat mod -> Board.show()
            pass
        with then("the system prompt says Its stage is done and waits for a person to move it."):
            pass
    with scenario("Add nothing with no active ticket"):
        # Evidence: inferred: register.ts prompt.compose returns the prompt unchanged with no active ticket.
        with given("no [ticket](../../../.context/kanban-model.md#ticket--card) is active"):
            pass
        with when("the chat composes its system prompt"):
            # chat mod -> Board.show()
            # Board <- active: none
            pass
        with then("the system prompt holds no session board section"):
            pass
