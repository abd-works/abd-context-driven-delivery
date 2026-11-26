from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Activate And Move Ticket Sessions
# Map: ../../../../.context/story-map.md#s-person----activate-ticket
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Activate Ticket
# Actor: Person
#
# Acceptance criteria:
# - Sessions open only from main: activating a ticket opens it in its own worktree, on its own branch, made when
#   missing, and the chat that asked stays on main. Requested 2026-11-10.
with story("Activate Ticket"):
    with scenario("Open a ticket in its own worktree"):
        # Evidence: requested 2026-11-10: main is the only place sessions open; another ticket is another chat and worktree.
        with given("the git [repository](../../../../.context/kanban-model.md#repo) has no branch billing-report"):
            pass
        with when("the Person activates billing-report"):
            # Person -> Ticket.activate()
            # TicketCheckout -> Branch.open_in_worktree()
            pass
        with then("billing-report has its own worktree, on the branch billing-report"):
            pass
        with and_("the repository's own folder stays on main"):
            pass
        with and_("main is still the session of the chat that activated it"):
            pass
    with scenario("Save the session folders on main before opening"):
        with given("billing-report's session folder is not yet committed"):
            pass
        with when("the Person activates billing-report"):
            # TicketCheckout -> WorkingTree.commit(.sessions), Origin.push_upstream()
            pass
        with then("main on origin holds billing-report's session folder"):
            pass
    with scenario("Open a ticket again in the worktree it has"):
        with given("billing-report is open in its own worktree"):
            pass
        with when("the Person activates billing-report again"):
            pass
        with then("billing-report keeps that worktree"):
            pass
    with scenario("Open a ticket again after its worktree folder was deleted"):
        # Evidence: tested by heavy: space/repo/worktree_heavy_spec.py 'whose folder was deleted outside CDD'; unit: space/repo/worktree_spec.py.
        with given("billing-report is open in its own worktree"):
            pass
        with but_("that worktree's folder is no longer on disk"):
            pass
        with when("the Person activates billing-report"):
            # Person -> Ticket.activate()
            # TicketCheckout -> Branch.open_in_worktree()
            # Worktrees -> Worktrees.add(folder, branch)
            pass
        with then("billing-report has its own worktree again, on the branch billing-report"):
            pass
    with scenario("Give tickets whose names start alike their own worktrees"):
        # Evidence: tested by heavy: space/repo/worktree_heavy_spec.py 'with another branch whose name starts with the same 24 characters open in its worktree'; unit: space/repo/worktree_spec.py.
        with given("customer-order-history-export-monthly is open in its own worktree"):
            pass
        with when("the Person activates customer-order-history-export-weekly"):
            # Person -> Ticket.activate()
            # Worktrees -> Worktrees.sibling_folder(branch)
            pass
        with then("customer-order-history-export-weekly has a worktree of its own, in another folder"):
            pass
    with scenario("Answer every chat that activates a ticket at the same moment"):
        # Evidence: tested by heavy: space/repo/worktree_heavy_spec.py 'that two callers open for one branch at the same moment'.
        with given("billing-report has no worktree yet"):
            pass
        with when("three chats activate billing-report at the same moment"):
            # Chat -> Ticket.activate()
            # Worktrees -> Worktrees.open(branch), one caller at a time
            pass
        with then("each is answered billing-report, in the one worktree"):
            pass
