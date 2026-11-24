from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-board-app----find-ticket-branch-and-worktree
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Find Ticket Branch And Worktree
# Actor: Board App
with story("Find Ticket Branch And Worktree"):
    with scenario("Find a branch and worktree made outside CDD"):
        # Evidence: observed 2026-11-09: the chat bar offered to create a branch and worktree for chat-ui-defects, whose work was already on claude/chat-ui-defects-cef4bc in its own worktree, made by the Claude desktop app.
        with given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree"):
            pass
        with but_("checkout-flow's session records no branch or worktree"):
            pass
        with when("the Person activates checkout-flow"):
            # TicketCheckout -> Repo.branches, Worktrees.of(branch) -> SessionCheckout.record_opened(branch, worktree)
            pass
        with then("checkout-flow opens in that worktree, creating nothing"):
            pass
        with and_("checkout-flow's session records claude/checkout-flow-cef4bc and its worktree"):
            pass
    with scenario("Correct a branch the session records wrongly"):
        with given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree"):
            pass
        with but_("checkout-flow's session records a branch the repository no longer has"):
            pass
        with when("the Person activates checkout-flow"):
            pass
        with then("checkout-flow's session records claude/checkout-flow-cef4bc and its worktree"):
            pass
    with scenario("Say which branches could be the session's rather than guess"):
        with given("the repository has the branches claude/checkout-flow-cef4bc and claude/checkout-flow-9a1b2c"):
            pass
        with when("the Person activates checkout-flow"):
            pass
        with then("the Person is told both branches could be checkout-flow's"):
            pass
        with and_("checkout-flow's session records no branch"):
            pass
    with scenario("Leave a branch named as another ticket to that ticket"):
        with given("checkout-flow-retry is a ticket whose work is on the branch checkout-flow-retry"):
            pass
        with when("the Person activates checkout-flow"):
            # Person -> Ticket.activate()
            # SessionCheckout -> SessionCheckout.candidate_branches
            # SessionListing -> SessionListing.open_names()
            pass
        with then("checkout-flow's session records its own branch checkout-flow"):
            pass
    with scenario("Refuse to open a ticket onto a folder that is not its checkout"):
        # Evidence: tested by heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is activated while a folder left on no branch is where its worktree goes'.
        with given("billing-report's worktree folder is still there, left on no branch"):
            pass
        with and_("the git [repository](../../../.context/kanban-model.md#repo) no longer has the branch billing-report"):
            pass
        with when("the Person activates billing-report"):
            # Person -> Ticket.activate()
            # TicketCheckout -> Branch.open_in_worktree()
            # Worktrees -> Worktrees.add(folder, branch)
            pass
        with then("the board says billing-report cannot open in a worktree, naming that folder"):
            pass
        with and_("the folder's files are as they were"):
            pass
