# The same ticket activated by several chats at once fails one of them with git's "already exists"

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Activate Ticket - "Open a ticket again in the worktree it has"; no scenario covers two activations at once.
- **Module and class:** `space/kanban/ticket_checkout.py` `TicketCheckout.open` (the check `if not self.worktree` and `branch.open_in_worktree()` are not held under one lock); `space/repo/worktree.py` `Worktrees.add`.
- **Severity:** misleading message

## Steps
With ticket kid-two never activated, start three client processes at the same moment (three chats, one cdd server), each calling `ticket.activate ticket="kid-two"`. On the board this is a double click on Activate, or the board and the chat bar acting together.

## Expected
All three answer the ticket, in the one worktree (the second and third meet "the worktree it has").

## Actual
Two answer the ticket; one answers
```
RepoConnectError: Cannot connect git: git worktree add C:\dev\_et\gizmo\work\repo-kid-two kid-two failed in C:\dev\_et\gizmo\work\repo: Preparing worktree (checking out 'kid-two')
fatal: 'C:/dev/_et/gizmo/work/repo-kid-two' already exists.
```
The end state is sound (one worktree, session.json records it, main clean), so only the losing caller is misled: it is told git cannot be reached when the ticket is in fact open.

## Tier that should catch it
Heavy (`ticket_work_heavy_spec.py`, real server and git, calls sent together). No spec sends two calls for one ticket at once.

## Also seen by
- Gizmo, second charter: two cdd servers (two CDD_HOME, ports 48731 and 48732) on one repository each sent `ticket.close` for twin-six with commit, push, merge, delete_branch, delete_worktree at the same moment. One closed it; the other answered `RepoConnectError: Cannot connect git: git add -A -- . failed ... Unable to create '.../.git/worktrees/repo-twin-six/index.lock': File exists.` End state sound: work merged to main and pushed once, one handoff, both servers' boards show it in Complete.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). Three processes calling `ticket.activate ticket="kid-two"` at one moment: in 2 runs of 6 one caller got a `RepoConnectError`, in 4 all three answered the ticket. The git line differs from the report's: `git worktree add -b kid-two ... origin/main ... fatal: a branch named 'kid-two' already exists`. The end state was sound each time: one worktree, main clean.
- Cause, if you found it: `space/kanban/ticket_checkout.py` `TicketCheckout.open`: the test `if not self.worktree` and `self.branch.open_in_worktree()` are not held together, so two callers both go on to `Worktrees.add`.
- Shares its cause with: gizmo-03, gizmo-07 (same failing call and message; the cause, two callers at once, is this report's alone)
