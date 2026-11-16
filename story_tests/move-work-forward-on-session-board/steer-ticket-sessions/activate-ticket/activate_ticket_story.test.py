from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----activate-ticket
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Activate Ticket
# Actor: Person
#
# Acceptance criteria:
# - Sessions open only from main: activating a ticket opens it in its own worktree, on its own branch, made when
#   missing, and the chat that asked stays on main. Requested 2026-11-10.
# - A chat in a ticket's worktree works on that ticket; no chat moves. Requested 2026-11-10.
with story("Activate Ticket"):
    with scenario("Open a ticket in its own worktree"):
        # Evidence: requested 2026-11-10: main is the only place sessions open; another ticket is another chat and worktree.
        with given("the git [repository](../../../.context/kanban-model.md#repo) has no branch billing-report"):
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
            # TicketCheckout -> Repo.commit(.sessions), Repo.push_upstream()
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
    with scenario("Work on the ticket from a chat in its worktree"):
        with given("billing-report is open in its own worktree"):
            pass
        with when("a chat in that worktree asks which session it works on"):
            # Chat -> Sessions.current()
            pass
        with then("the answer is billing-report"):
            pass
    with scenario("Find a branch and worktree made outside CDD"):
        # Evidence: observed 2026-11-09: the chat bar offered to create a branch and worktree for chat-ui-defects, whose work was already on claude/chat-ui-defects-cef4bc in its own worktree, made by the Claude desktop app.
        with given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree"):
            pass
        with but_("checkout-flow's session records no branch or worktree"):
            pass
        with when("the Person activates checkout-flow"):
            # TicketCheckout -> Repo.branches, Worktrees.of(branch) -> Session.save_fields(branch, worktree)
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
            # TicketCheckout -> Board.ticket_names
            pass
        with then("checkout-flow's session records its own branch checkout-flow"):
            pass
