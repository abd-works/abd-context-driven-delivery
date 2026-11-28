# widget-01 A ticket started from the Backlog takes over a branch of its name that already exists, with someone else's commits

**Title** - Starting a Backlog item (here a child started with its parent) whose name matches a branch that already exists gives no warning, and `ticket.activate` then opens the new ticket's worktree on that old branch, holding commits that are not the ticket's.

**Charter** - theme 3, starting work from the Backlog and the board at once. **Tester** - Widget.

**Story** - Move work forward from chat bar / Steer Sessions / Start Backlog Item From Session List, "Start a parent with its child items"; Steer Ticket Sessions / Open Ticket Sessions, "Refuse a title whose name a ticket already has". No scenario covers a name whose *branch* (rather than session) already exists.

**Module and class** - `space/kanban/board.py` `CardPlacement.free_name_for` (checks sessions and session folders only, never `refs/heads/<name>`); `ticket.activate` (`TicketCheckout`) then reuses the branch it finds.

**Severity** - question (could be wrong result: a later close with "merge into the default branch" merges the foreign commits).

**Steps** (sandbox `C:\dev\_et\after-1-2-1\widget`, cdd server on 8931 with `CDD_HOME` set, calls over MCP with `X-CDD-Project` = `work\repo`)
1. Repository with bare origin; `git branch gift-wrap`, then add a commit "unrelated work on gift-wrap" to that branch.
2. `backlog-item.create` Checkout flow, Address form, Card form, Gift wrap; `backlog-item.nest_under` each of the last three under Checkout flow.
3. `backlog-item.start {"backlog_item":"Checkout flow"}` - succeeds, gift-wrap is a child ticket.
4. `ticket.branch {"ticket":"gift-wrap"}` answers `{"exists": true, "is_checked_out": false}` for a ticket made a second ago.
5. `ticket.activate {"ticket":"gift-wrap"}`.

**Expected** - Either the start is refused before anything moves (as `TicketNameTakenError` refuses a session name: "a name already taken is refused ... before any folder, file, or branch is made", `space/kanban/.context/module-context.md`, Constraint), or the new ticket gets a fresh branch from main. The module context says activate makes "a new one on its own branch, made when missing", which reads as a branch belonging to the ticket.

**Actual** - `work\repo-gift-wrap` is a worktree on `gift-wrap` at `a60e8d1 unrelated work on gift-wrap`, based on the old commit, not on main; the ticket now carries another person's work and none of main's.

**Tier that should catch it** - unit (a `MockGit` with a branch already present, through `free_name_for`/`open_ticket`); no spec gives the git fake a pre-existing branch of a new card's name.
