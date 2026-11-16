from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----delete-ticket-branch
# Model: ../../../.context/kanban-model.md

# Story: Delete Ticket Branch
# Actor: Person
with story("Delete Ticket Branch"):
    with scenario("Delete the branch on closing without merging it"):
        # Evidence: requested 2026-11-09: delete branch only deletes the branch; merge is its own choice.
        with given("checkout-flow is open in its own worktree, with work in it"):
            pass
        with when("the Person closes checkout-flow, committing, pushing, and deleting its branch"):
            # Person -> Ticket.close(leaving=['commit', 'push', 'delete_branch'])
            # TicketCheckout -> Branch(main).check_out()
            # TicketCheckout -> Branch.delete(unmerged=True)
            pass
        with then("the checkout-flow branch is gone, here and on origin"):
            pass
        with but_("main on origin does not hold checkout-flow's work"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
    with scenario("Delete the branch and the worktree that has it"):
        with given("checkout-flow is open in its own worktree"):
            pass
        with when("the Person closes checkout-flow, deleting its branch"):
            # Person -> Ticket.close(leaving=['delete_branch'])
            # TicketCheckout -> Worktree.close(), Branch.delete(unmerged=True)
            pass
        with then("the worktree folder is gone"):
            pass
        with and_("the checkout-flow branch is gone"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
    with scenario("Delete a branch checked out nowhere"):
        with given("checkout-flow has a branch"):
            pass
        with but_("that branch is not checked out"):
            pass
        with when("the Person asks what closing checkout-flow can do"):
            # Person -> Ticket.close_choices()
            pass
        with then("closing offers to delete checkout-flow's branch"):
            pass
        with when("the Person closes checkout-flow, deleting its branch"):
            pass
        with then("the checkout-flow branch is gone"):
            pass
        with and_("checkout-flow shows in Complete"):
            pass
