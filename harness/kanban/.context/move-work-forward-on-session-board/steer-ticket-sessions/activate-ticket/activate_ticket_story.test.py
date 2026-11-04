from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../story-map.md#s-person----activate-ticket
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Activate Ticket
# Actor: Person
#
# Acceptance criteria:
# - Commit, push, and merge into main are chosen when the session is left, and merge starts off. Observed: `Ticket.activate`, `Ticket.close`.
# - Create Ticket Branch And Worktree: they are created when a ticket that has none is activated, and a ticket that has one is offered neither again. Observed.
with story("Activate Ticket"):
    with scenario("Switch to another ticket, committing, pushing, and merging the one left"):
        # Evidence: observed: activation-client.spec 'Activate Ticket' — 'should offer commit and push on leaving and open with merge off', 'should offer a branch to a ticket that has none', 'should say what it switches from and to', 'that a person has confirmed with merge chosen'; story-actions.spec 'should switch the session from the dialog, with merge off'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), on its own branch pushed to origin"):
            pass
        with and_("billing-report has no branch in the [repository](../../../kanban-model.md#repo)"):
            pass
        with when("the Person activates billing-report"):
            # Person -> Ticket.workspace()
            # Ticket <- has_branch: false, has_worktree: false, leaving_has_branch: true
            pass
        with then("a dialog headed Switch from Checkout flow to Billing report offers commit and push, chosen, and merge, not chosen"):
            pass
        with and_("it offers a branch for billing-report, chosen"):
            pass
        with when("the Person chooses merge and confirms"):
            # Person -> Ticket.activate(['commit', 'push', 'merge'], ['branch'])
            # Ticket -> Repo.push_commit('checkout-flow: leave session', sync_remote=True)
            # Ticket -> Repo.close_branch('checkout-flow')
            # Ticket -> Repo.switch_branch('billing-report')
            # Ticket -> Session.switch('billing-report', repo_path)
            pass
        with then("billing-report is the active ticket with a thick orange outline"):
            pass
        with and_("a toast says Checkout flow: committed, pushed, merged to main · Billing report: branch created · Billing report is now active"):
            pass
    with scenario("Activate a ticket when the active one has no branch"):
        # Evidence: observed: activation-client.spec 'should choose nothing to leave when the session has no branch'; kanban_tools_spec 'with the active ticket on no branch of its own' — 'should commit nothing on a ticket that has no branch', 'should leave the branch checked out as it was'; 'that activates a ticket' — 'should make the chosen ticket the current session'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)"):
            pass
        with but_("checkout-flow has no branch of its own"):
            pass
        with when("the Person activates billing-report with nothing chosen"):
            # Person -> Ticket.activate([], [])
            # Ticket -> Session.switch('billing-report', repo_path)
            pass
        with then("billing-report is the active ticket"):
            pass
        with and_("the branch checked out is as it was"):
            pass
        with but_("nothing is committed"):
            pass
    with scenario("Commit nothing when the ticket left is not checked out"):
        # Evidence: observed: kanban_tools_spec 'with the active ticket's branch not checked out' — 'should commit nothing on a branch that is not checked out'.
        with given("checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) and has a branch"):
            pass
        with but_("that branch is not checked out"):
            pass
        with when("the Person activates billing-report with commit chosen"):
            # Person -> Ticket.activate(['commit'], [])
            # Ticket -> Session.switch('billing-report', repo_path)
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
            pass
        with then("the dialog is closed"):
            pass
        with and_("checkout-flow is still the active ticket"):
            pass
    with scenario("Create the ticket's branch on activation"):
        # Evidence: observed: kanban_tools_spec 'that activates a ticket with a new branch' — 'should create the ticket's branch when a ticket that has none is activated'; 'should say a ticket has no branch yet'.
        with given("the git [repository](../../../kanban-model.md#repo) has no branch billing-report"):
            pass
        with when("the Person activates billing-report with a new branch"):
            # Person -> Ticket.activate(opening=['branch'])
            # Ticket -> Repo.switch_branch('billing-report')
            # Ticket -> Session.switch('billing-report', repo_path)
            pass
        with then("the repository has the branch billing-report"):
            pass
        with and_("billing-report is the active ticket"):
            pass
