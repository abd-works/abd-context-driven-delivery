from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----close-active-session
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Close Active Session
# Actor: Person
with story("Close Active Session"):
    with scenario("Close the active session from its card"):
        # Evidence: observed: ticket-client.spec 'Close Active Session' — 'should send the close session command to the chat', 'should leave the ticket in its column'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), In progress in Discovery, with a chat connected"):
            pass
        with when("the Person closes checkout-flow's session from its card"):
            # Person -> Chat.command('/space:session:close-session')
            # Chat -> Session.close()
            pass
        with then("the chat is sent /space:session:close-session"):
            pass
        with and_("checkout-flow stays In progress in Discovery"):
            pass
    with scenario("Complete the active ticket with its work committed"):
        # Evidence: observed: activation-client.spec 'Close Active Session' — 'should ask what to do with its work', 'should send what to do with its work', 'should select the ticket in Complete'; ticket-client.tsx dropOn opens the Close dialog for the active ticket; kanban_tools_spec 'should leave no ticket active'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), on its own branch"):
            pass
        with when("the Person moves checkout-flow into Complete"):
            # Person -> Ticket.workspace()
            # Ticket <- leaving_has_branch: true
            pass
        with then("a dialog headed Close session Checkout flow offers commit and push, chosen"):
            pass
        with when("the Person confirms"):
            # Person -> Ticket.close(['commit', 'push'])
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_closed()
            # Board page -> Board.show()
            pass
        with then("checkout-flow shows in Complete and is selected"):
            pass
        with and_("a toast says Checkout flow: committed, pushed · Session Checkout flow closed"):
            pass
        with and_("no ticket is active"):
            pass
    with scenario("Complete a ticket that has no branch of its own"):
        # Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'should commit nothing on a ticket that has no branch'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with but_("it has no branch of its own"):
            pass
        with when("the Person moves checkout-flow into Complete and confirms"):
            # Person -> Ticket.close([])
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_closed()
            pass
        with then("checkout-flow shows in Complete"):
            pass
        with and_("its folder is in .sessions/_complete/checkout-flow"):
            pass
        with but_("nothing is committed"):
            pass
