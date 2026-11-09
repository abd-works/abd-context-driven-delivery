from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----delete-ticket-branch
# Model: ../../../.context/kanban-model.md

# Story: Delete Ticket Branch
# Actor: Person
with story("Delete Ticket Branch"):
    with scenario("Delete the branch left without merging it"):
        # Evidence: requested 2026-11-09: delete branch only deletes the branch; merge is its own choice; deleting a session's branch closes the session.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), on its own branch pushed to origin"):
            pass
        with when("the Person activates billing-report, committing, pushing, and deleting checkout-flow's branch"):
            # Person -> Ticket.activate(leaving=['commit', 'push', 'delete_branch'])
            # Ticket -> Ticket.close(['commit', 'push', 'delete_branch'])
            # TicketCheckout -> Branch(main).check_out()
            # TicketCheckout -> Branch.delete(unmerged=True)
            pass
        with then("the checkout-flow branch is gone, here and on origin"):
            pass
        with but_("main on origin does not hold checkout-flow's work"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
        with and_("billing-report is the active ticket"):
            pass
    with scenario("Delete the branch and the worktree that has it"):
        # Evidence: observed 2026-11-09: "cdd-chat-ui did not open: LeaveRefused: integrated-harness-flow: its worktree still has it checked out"; git deletes no branch a worktree has checked out.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its branch open in its own worktree"):
            pass
        with when("the Person activates billing-report, deleting checkout-flow's branch"):
            # Person -> Ticket.activate(leaving=['delete_branch'])
            # Ticket -> Ticket.close(['delete_branch'])
            # TicketCheckout -> Worktree.close()
            # TicketCheckout -> Branch.delete(unmerged=True)
            pass
        with then("the worktree folder is gone"):
            pass
        with and_("the checkout-flow branch is gone"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
    with scenario("Delete a branch checked out nowhere"):
        # Evidence: observed 2026-11-09: leaving us-taxes after its worktree was deleted offered no delete branch, though the branch was still in git.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card) and has a branch"):
            pass
        with but_("that branch is not checked out"):
            pass
        with when("the Person picks billing-report to open"):
            # Person -> Ticket.leave_choices() <- own_branch: checkout-flow, choices: handoff, commit, push, merge, delete_branch
            pass
        with then("the dialog offers to delete checkout-flow's branch"):
            pass
        with when("the Person activates billing-report, deleting checkout-flow's branch"):
            # Person -> Ticket.activate(leaving=['delete_branch'])
            # TicketCheckout -> Branch.delete(unmerged=True)
            pass
        with then("the checkout-flow branch is gone"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
