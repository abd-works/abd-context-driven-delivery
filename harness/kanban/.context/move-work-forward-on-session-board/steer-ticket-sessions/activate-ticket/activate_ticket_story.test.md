# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Activate Ticket

#### Scenario: Switch to another ticket, committing, pushing, and merging the one left

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card), on its own branch pushed to origin
*And* billing-report has no branch in the [repository](../../../kanban-model.md#repo)
*When* the Person activates billing-report
*Then* a dialog headed Switch from Checkout flow to Billing report offers commit and push, chosen, and merge, not chosen
*And* it offers a branch for billing-report, chosen
*When* the Person chooses merge and confirms
*Then* billing-report is the active ticket with a thick orange outline
*And* a toast says Checkout flow: committed, pushed, merged to main · Billing report: branch created · Billing report is now active

#### Scenario: Activate a ticket when the active one has no branch

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*But* checkout-flow has no branch of its own
*When* the Person activates billing-report with nothing chosen
*Then* billing-report is the active ticket
*And* the branch checked out is as it was
*But* nothing is committed

#### Scenario: Commit nothing when the ticket left is not checked out

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card) and has a branch
*But* that branch is not checked out
*When* the Person activates billing-report with commit chosen
*Then* billing-report is the active ticket
*But* nothing is committed on checkout-flow's branch

#### Scenario: Cancel the switch

*Given* the dialog to switch from Checkout flow to Billing report is open
*When* the Person cancels
*Then* the dialog is closed
*And* checkout-flow is still the active ticket

#### Scenario: Create the ticket's branch on activation

*Given* the git [repository](../../../kanban-model.md#repo) has no branch billing-report
*When* the Person activates billing-report with a new branch
*Then* the repository has the branch billing-report
*And* billing-report is the active ticket
