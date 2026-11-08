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
            # Person -> Ticket.open_choices(), Ticket.leave_choices()
            # Ticket <- Branch is_checked_out: true
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
    with scenario("Close a session whose work is on main"):
        # Evidence: observed: chat-ui-defects backlog item — closing a session on main should commit and push main, as switching a branch does, and not try to delete a worktree; main has no worktree to delete.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its work on main"):
            pass
        with when("the Person closes checkout-flow"):
            # Person -> Ticket.leave_choices()
            # Ticket <- Branch main, is_checked_out: true
            pass
        with then("the close dialog offers to commit and push main"):
            pass
        with when("the Person confirms"):
            # Person -> Ticket.close(['commit', 'push'])
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_closed()
            pass
        with then("main on origin holds the commit checkout-flow: leave session"):
            pass
        with and_("the checkout is still on main"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
    with scenario("Write a handoff for the session being closed"):
        # Evidence: observed: chat-ui-defects backlog item — the close and switch dialogs need a Create handoff checkbox, on by default; when it is on, closing or switching writes a handoff for the session being left.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its story map held on violations"):
            pass
        with when("the Person closes checkout-flow with Create handoff chosen"):
            # Person -> Ticket.close(['handoff'])
            # Ticket -> Handoffs.write(LeavingHandoff(ticket).document)
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_closed()
            pass
        with then("checkout-flow's folder in .sessions/_complete holds a handoff"):
            pass
        with and_("the handoff names stories-story-map as what comes next"):
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
