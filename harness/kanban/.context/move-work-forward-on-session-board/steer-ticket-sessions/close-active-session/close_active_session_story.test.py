from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../story-map.md#s-person----close-active-session
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Close Active Session
# Actor: Person
with story("Close Active Session"):
    with scenario("Close the active session with its work committed"):
        # Evidence: observed: activation-client.spec 'Close Active Session' — 'should ask what to do with its work', 'should send what to do with its work', 'should select the ticket in Complete'; story-actions.spec 'should ask what to do with its work, then show the ticket in Complete'; kanban_tools_spec 'should leave no ticket active'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), on its own branch"):
            pass
        with when("the Person closes checkout-flow's session"):
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
    with scenario("Close a ticket that has no branch of its own"):
        # Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'should commit nothing on a ticket that has no branch'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)"):
            pass
        with but_("it has no branch of its own"):
            pass
        with when("the Person closes checkout-flow's session and confirms"):
            # Person -> Ticket.close([])
            # Ticket -> Session.close()
            # Ticket -> Session.move_to_closed()
            pass
        with then("checkout-flow shows in Complete"):
            pass
        with and_("its folder is in .sessions/closed/checkout-flow"):
            pass
        with but_("nothing is committed"):
            pass
    with scenario("Close the active ticket by moving it to Complete"):
        # Evidence: observed: ticket-client.spec 'should let only the active ticket, or one done in Implementation, be dropped on Complete'; ticket-client.tsx dropOn opens the Close dialog for the active ticket.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), In progress in Discovery"):
            pass
        with when("the Person moves checkout-flow into Complete"):
            pass
        with then("the dialog headed Close session Checkout flow asks what to do with its work"):
            pass
