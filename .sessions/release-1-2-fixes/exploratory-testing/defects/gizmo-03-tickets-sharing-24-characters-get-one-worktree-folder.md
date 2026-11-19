# Two tickets whose names share their first 24 characters get the same worktree folder, so the second can never be activated

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Activate Ticket - "Open a ticket in its own worktree".
- **Module and class:** `space/repo/worktree.py` `Worktrees.sibling_folder` (`slug[:_FOLDER_BRANCH_LENGTH]`, 24 characters, with nothing to tell two branches apart); the failure shows in `Worktrees.add`.
- **Severity:** blocks work

## Steps
1. `ticket.create title="Customer order history export monthly"`
2. `ticket.create title="Customer order history export weekly"`
3. `ticket.activate ticket="customer-order-history-export-monthly"` - worktree `..\repo-customer-order-history-e`.
4. `ticket.activate ticket="customer-order-history-export-weekly"`

## Expected
Each ticket opens in its own worktree (space/kanban module-context: "opening the ticket's own worktree, with its branch").

## Actual
```
RepoConnectError: Cannot connect git: git worktree add -b customer-order-history-export-weekly C:\dev\_et\gizmo\work\repo-customer-order-history-e origin/main failed in C:\dev\_et\gizmo\work\repo: Preparing worktree (new branch 'customer-order-history-export-weekly')
fatal: 'C:/dev/_et/gizmo/work/repo-customer-order-history-e' already exists.
```
The second ticket cannot be opened until the first is closed with its worktree deleted. The message says "Cannot connect git" and names neither ticket. Titles that start alike are common ("Release 1.2 fixes ...", "Exploratory testing of ...").

## Tier that should catch it
Unit (`sibling_folder` is pure naming, MockRepo can show it) and heavy for the real `git worktree add`. The specs use short, distinct titles.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). The second activate fails with the report's `RepoConnectError: Cannot connect git: git worktree add -b customer-order-history-export-weekly ...repo-customer-order-history-e ... already exists`.
- Cause, if you found it: `space/repo/worktree.py` `Worktrees.sibling_folder` cuts the branch name to 24 characters; `Worktrees.add` then runs `git worktree add` onto a folder that is already there.
- Shares its cause with: gizmo-07 and gizmo-08 fail at the same place, `Worktrees.add`, with the same raw `RepoConnectError: Cannot connect git`; the naming cause is this report's alone
