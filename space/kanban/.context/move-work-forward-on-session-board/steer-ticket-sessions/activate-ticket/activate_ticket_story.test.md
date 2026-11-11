# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Activate Ticket

#### Scenario: Open a ticket in its own worktree

*Given* the git [repository](../../../kanban-model.md#repo) has no branch billing-report
*When* the Person activates billing-report
*Then* billing-report has its own worktree, on the branch billing-report
*And* the repository's own folder stays on main
*And* main is still the session of the chat that activated it

#### Scenario: Save the session folders on main before opening

*Given* billing-report's session folder is not yet committed
*When* the Person activates billing-report
*Then* main on origin holds billing-report's session folder

#### Scenario: Open a ticket again in the worktree it has

*Given* billing-report is open in its own worktree
*When* the Person activates billing-report again
*Then* billing-report keeps that worktree

#### Scenario: Work on the ticket from a chat in its worktree

*Given* billing-report is open in its own worktree
*When* a chat in that worktree asks which session it works on
*Then* the answer is billing-report

#### Scenario: Find a branch and worktree made outside CDD

*Given* checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree
*But* checkout-flow's session records no branch or worktree
*When* the Person activates checkout-flow
*Then* checkout-flow opens in that worktree, creating nothing
*And* checkout-flow's session records claude/checkout-flow-cef4bc and its worktree

#### Scenario: Correct a branch the session records wrongly

*Given* checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree
*But* checkout-flow's session records a branch the repository no longer has
*When* the Person activates checkout-flow
*Then* checkout-flow's session records claude/checkout-flow-cef4bc and its worktree

#### Scenario: Say which branches could be the session's rather than guess

*Given* the repository has the branches claude/checkout-flow-cef4bc and claude/checkout-flow-9a1b2c
*When* the Person activates checkout-flow
*Then* the Person is told both branches could be checkout-flow's
*And* checkout-flow's session records no branch
