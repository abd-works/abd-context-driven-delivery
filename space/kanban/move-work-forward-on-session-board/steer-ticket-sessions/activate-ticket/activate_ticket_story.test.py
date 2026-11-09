from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----activate-ticket
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Activate Ticket
# Actor: Person
#
# Acceptance criteria:
# - Commit, push, and merge into main are chosen when the session is left, and merge starts off. Observed: `Ticket.activate`, `Ticket.close`.
# - Create Ticket Branch And Worktree: they are created when a ticket that has none is activated, and a ticket that has one is offered neither again. Observed.
with story("Activate Ticket"):
    with scenario("Find a branch and worktree made outside CDD"):
        # Evidence: observed 2026-11-09: the chat bar offered to create a branch and worktree for chat-ui-defects, whose work was already on claude/chat-ui-defects-cef4bc in its own worktree, made by the Claude desktop app.
        with given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree"):
            pass
        with but_("checkout-flow's session records no branch or worktree"):
            pass
        with when("the Person picks checkout-flow to open"):
            # Person -> Ticket.open_choices()
            # TicketCheckout -> Repo.branches, Worktrees.of(branch) -> Session.save_fields(branch, worktree)
            pass
        with then("the open dialog offers nothing to create"):
            pass
        with and_("checkout-flow's session records claude/checkout-flow-cef4bc and its worktree"):
            pass
    with scenario("Correct a branch the session records wrongly"):
        with given("checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree"):
            pass
        with but_("checkout-flow's session records a branch the repository no longer has"):
            pass
        with when("the Person picks checkout-flow to open"):
            pass
        with then("checkout-flow's session records claude/checkout-flow-cef4bc and its worktree"):
            pass
    with scenario("Say which branches could be the session's rather than guess"):
        with given("the repository has the branches claude/checkout-flow-cef4bc and claude/checkout-flow-9a1b2c"):
            pass
        with when("the Person picks checkout-flow to open"):
            pass
        with then("the open dialog names both branches"):
            pass
        with and_("checkout-flow's session records no branch"):
            pass
    with scenario("Merge the branch left into main and keep it"):
        # Evidence: requested 2026-11-09: LEAVE offers, after push, merge to main, delete the branch, and delete the worktree, each with its existing repo operation.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), on its own branch pushed to origin"):
            pass
        with when("the Person activates billing-report, committing, pushing, and merging checkout-flow"):
            # Person -> Ticket.activate(leaving=['commit', 'push', 'merge'])
            # TicketCheckout -> Branch.land_on_default()
            pass
        with then("main on origin holds checkout-flow's work"):
            pass
        with and_("the checkout-flow branch is still there"):
            pass
    with scenario("Merge the branch left while its worktree stays"):
        # Evidence: requested 2026-11-09: a merge no longer refuses while the worktree stays, since main's checkout merges it.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its branch open in its own worktree"):
            pass
        with when("the Person activates billing-report, committing, pushing, and merging checkout-flow"):
            # Person -> Ticket.activate(leaving=['commit', 'push', 'merge'])
            # TicketCheckout -> Branch.land_on_default()
            pass
        with then("main on origin holds checkout-flow's work"):
            pass
        with and_("the worktree folder is still there"):
            pass
    with scenario("Delete the worktree left"):
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), its branch open in its own worktree"):
            pass
        with when("the Person activates billing-report, committing, pushing, and deleting checkout-flow's worktree"):
            # Person -> Ticket.activate(leaving=['commit', 'push', 'delete_worktree'])
            # TicketCheckout -> Worktree.close()
            pass
        with then("the worktree folder is gone"):
            pass
        with and_("checkout-flow's work is on its branch on origin"):
            pass
    with scenario("Switch to another ticket, committing, pushing, and merging the one left"):
        # Evidence: observed: activation-client.spec 'Activate Ticket' — 'should offer commit and push on leaving and open with merge off', 'should offer a branch to a ticket that has none', 'should say what it switches from and to', 'that a person has confirmed with merge chosen'; story-actions.spec 'should switch the session from the dialog, with merge off'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card), on its own branch pushed to origin"):
            pass
        with and_("billing-report has no branch in the [repository](../../../.context/kanban-model.md#repo)"):
            pass
        with when("the Person activates billing-report"):
            # Person -> Ticket.open_choices(), Ticket.leave_choices()
            # Ticket <- Branch exists: false (billing-report); the leaving ticket's Branch is_checked_out: true
            pass
        with then("a dialog headed Switch from Checkout flow to Billing report offers commit and push, chosen, and merge, not chosen"):
            pass
        with and_("it offers a branch for billing-report, chosen"):
            pass
        with when("the Person chooses merge and confirms"):
            # Person -> Ticket.activate(['commit', 'push', 'merge'], ['branch'])
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # TicketCheckout -> Branch.land_on_default()
            # Ticket -> Repo.switch_branch('billing-report')
            # Ticket -> Sessions.switch('billing-report')
            pass
        with then("billing-report is the active ticket with a thick orange outline"):
            pass
        with and_("a toast says Checkout flow: committed, pushed, merged to main · Billing report: branch created · Billing report is now active"):
            pass
    with scenario("Write a handoff for the session being left"):
        # Evidence: observed: chat-ui-defects backlog item — switching with Create handoff on writes a handoff for the session being left.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the Person activates billing-report with Create handoff chosen"):
            # Person -> Ticket.activate(leaving=['handoff'], opening=[])
            # Ticket -> active TicketCheckout.leave(['handoff'])
            # Ticket -> Handoffs.write(LeavingHandoff(checkout-flow).document)
            pass
        with then("checkout-flow's session folder holds a handoff"):
            pass
        with but_("billing-report's session folder holds none"):
            pass
    with scenario("Activate a ticket when the active one has no branch"):
        # Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'with the active ticket on no branch of its own' — 'should commit nothing on a ticket that has no branch', 'should leave the branch checked out as it was'; 'that activates a ticket' — 'should make the chosen ticket the current session'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with but_("checkout-flow has no branch of its own"):
            pass
        with when("the Person activates billing-report with nothing chosen"):
            # Person -> Ticket.activate([], [])
            # Ticket -> Sessions.switch('billing-report')
            pass
        with then("billing-report is the active ticket"):
            pass
        with and_("the branch checked out is as it was"):
            pass
        with but_("nothing is committed"):
            pass
    with scenario("Commit nothing when the ticket left is not checked out"):
        # Evidence: observed: kanban_tools_spec 'with the active ticket's branch not checked out' — 'should commit nothing on a branch that is not checked out'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card) and has a branch"):
            pass
        with but_("that branch is not checked out"):
            pass
        with when("the Person activates billing-report with commit chosen"):
            # Person -> Ticket.activate(['commit'], [])
            # Ticket -> Sessions.switch('billing-report')
            pass
        with then("billing-report is the active ticket"):
            pass
        with but_("nothing is committed on checkout-flow's branch"):
            pass
    with scenario("Cancel the switch"):
        # Evidence: observed: activation-client.spec 'that a person has cancelled' — 'should close the dialog', 'should send nothing'.
        with given("the dialog to switch from Checkout flow to Billing report is open"):
            pass
        with when("the Person cancels"):
            # Person -> ActivationClient.cancel()
            pass
        with then("the dialog is closed"):
            pass
        with and_("checkout-flow is still the active ticket"):
            pass
    with scenario("Create the ticket's branch on activation"):
        # Evidence: observed: kanban_tools_spec 'that activates a ticket with a new branch' — 'should create the ticket's branch when a ticket that has none is activated'; 'should say a ticket has no branch yet'.
        with given("the git [repository](../../../.context/kanban-model.md#repo) has no branch billing-report"):
            pass
        with when("the Person activates billing-report with a new branch"):
            # Person -> Ticket.activate(opening=['branch'])
            # Ticket -> Repo.switch_branch('billing-report')
            # Ticket -> Sessions.switch('billing-report')
            pass
        with then("the repository has the branch billing-report"):
            pass
        with and_("billing-report is the active ticket"):
            pass
