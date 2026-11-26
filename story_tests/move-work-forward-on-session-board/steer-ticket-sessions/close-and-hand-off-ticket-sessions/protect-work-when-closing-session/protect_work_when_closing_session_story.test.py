from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Close And Hand Off Ticket Sessions
# Map: ../../../../.context/story-map.md#s-board-app----protect-work-when-closing-session
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Protect Work When Closing Session
# Actor: Board App
with story("Protect Work When Closing Session"):
    with scenario("Offer to commit a branch open in its worktree"):
        # Evidence: observed: e2e-report B3 — the close dialog said "branch none yet" for a ticket whose branch exists in a worktree, and labelled the choices with the ticket title.
        with given("checkout-flow is the active [ticket](../../../../.context/kanban-model.md#ticket--card), its branch open in its own worktree"):
            pass
        with when("the Person closes checkout-flow"):
            # Person -> Ticket.close_choices() <- branch: checkout-flow, choices: handoff, commit, push
            pass
        with then("the close dialog offers a handoff, and to commit and push checkout-flow"):
            pass
    with scenario("Leave what the repository's own folder holds uncommitted out of the close"):
        # Evidence: tested by heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with its branch merged while the clone's own folder holds an edit nobody committed'.
        with given("checkout-flow is open in its own worktree, with work in it"):
            pass
        with and_("the repository's own folder holds an edit to README.md that nobody committed"):
            pass
        with when("the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree"):
            # Person -> Ticket.close(['commit', 'push', 'merge', 'delete_branch', 'delete_worktree'])
            # Ticket -> TicketCheckout.save_work(leaving)
            # Ticket -> TicketCheckout.leave_branch(leaving)
            pass
        with then("main on origin holds checkout-flow's work"):
            pass
        with but_("main on origin does not hold the edit to README.md"):
            pass
        with and_("that edit is still uncommitted in the repository's own folder"):
            pass
    with scenario("Keep the ticket open when its branch does not merge into main"):
        # Evidence: tested by heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with its branch merged into a main it conflicts with'.
        with given("checkout-flow is open in its own worktree"):
            pass
        with and_("its branch and main on origin each changed the same line"):
            pass
        with when("the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree"):
            # Person -> Ticket.close(['commit', 'push', 'merge', 'delete_branch', 'delete_worktree'])
            # Ticket -> TicketCheckout.save_work(leaving)
            # Ticket -> TicketCheckout.leave_branch(leaving)
            pass
        with then("the board says checkout-flow does not merge into main"):
            pass
        with and_("main has no merge half done"):
            pass
        with and_("checkout-flow still has its worktree"):
            pass
        with and_("checkout-flow stays In progress in Discovery"):
            pass
    with scenario("Refuse to call a ticket closed while a program holds its worktree open"):
        # Evidence: tested by heavy, Windows: space/repo/worktree_heavy_spec.py 'whose folder a running program holds open'.
        with given("checkout-flow is open in its own worktree"):
            pass
        with and_("a running program works in that worktree's folder"):
            pass
        with when("the Person closes checkout-flow, deleting its worktree"):
            # Person -> Ticket.close(['delete_worktree'])
            # TicketCheckout -> Worktrees.remove(worktree) <- WorktreeNotRemovedError
            pass
        with then("the board says the worktree could not be removed, naming its folder"):
            pass
        with and_("checkout-flow's work is committed on its branch on origin"):
            pass
        with when("that program has ended and the Person activates checkout-flow"):
            # Person -> Ticket.activate()
            # Worktrees -> Worktrees.add(folder, branch)
            pass
        with then("checkout-flow has its own worktree again"):
            pass
