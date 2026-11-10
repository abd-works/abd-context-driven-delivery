from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: See Work On Session Board
# Map: ../../../.context/story-map.md#s-person----open-board
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Open Board
# Actor: Person
with story("Open Board"):
    with scenario("Open the board on a project"):
        # Evidence: observed: board-page.ts start() and board-header-view.tsx; tests/board-surface.spec.ts 'with the board drawn'. The header counts each ticket name once.
        with given("the [board](../../../.context/kanban-model.md#board) of project cdd-board-surface-fixture shows 9 [tickets](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with and_("its [session](../../../.context/kanban-model.md#session) checkout-flow, titled Checkout flow, is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the Person opens the session board at http://127.0.0.1:8778"):
            # Board page -> Board.show()
            # Board <- data_of(Board): project, active, columns
            # Board page -> Chat.list()
            # Chat <- the chats whose cdd-board mod checked in lately
            pass
        with then("the header reads cdd-board-surface-fixture · 10 tickets · active: Checkout flow"):
            pass
        with and_("the session board reads the [board](../../../.context/kanban-model.md#board) again every two seconds"):
            pass
    with scenario("Find the board from a chat"):
        # Evidence: inferred: the 'board' command handler in harness/chat-ui/pane/hooks/register.ts; no spec runs the mod.
        with given("a Claude Code chat has the cdd-board mod loaded"):
            pass
        with when("the Person asks the chat where the session board is"):
            # Person -> Claude Code command.run('board')  [External: Claude Code]
            # chat mod -> board server start when it does not answer
            # chat mod <- the board's address
            pass
        with then("the chat answers The board is at http://127.0.0.1:8778, and starts the board first when nothing answers on that port"):
            pass
