# A ticket whose branch was deleted while its worktree folder stayed can never be activated again: "already exists"

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Activate Ticket - "Open a ticket again in the worktree it has"; Delete Ticket Branch - "Delete the branch and the worktree that has it". No scenario covers a worktree whose branch is gone.
- **Module and class:** `space/repo/worktree.py` `Worktrees.open` / `Worktrees.add`: the worktree is looked up by branch (`Worktrees.of`), so a folder git lists as detached is not found, and `git worktree add -b` is run onto the folder that is already there. `space/kanban/ticket_checkout.py` `TicketCheckout.open`.
- **Severity:** blocks work

## Steps
1. `ticket.create title="Gift wrap"`, `ticket.activate ticket="gift-wrap"` - worktree `..\repo-gift-wrap`.
2. Outside CDD (an interrupted clean-up): `git -C ../repo-gift-wrap checkout --detach`, then `git branch -D gift-wrap` in `repo`.
3. `ticket.branch ticket="gift-wrap"` -> `{"exists": false, "is_checked_out": false}`
4. `ticket.activate ticket="gift-wrap"`

## Expected
The ticket opens: in the folder it recorded in session.json (`"worktree": "...\repo-gift-wrap"`) with its branch made again there, or the call says the folder is in the way and what to remove.

## Actual
```
RepoConnectError: Cannot connect git: git worktree add -b gift-wrap C:\dev\_et\gizmo\work\repo-gift-wrap origin/main failed in C:\dev\_et\gizmo\work\repo: Preparing worktree (new branch 'gift-wrap')
fatal: 'C:/dev/_et/gizmo/work/repo-gift-wrap' already exists.
```
Every later activate fails the same way. `ticket.close_choices` offers no `delete_worktree` for it, so the product has no way out; the person must know to run `git worktree remove`. Same failure class as the session-log leftover in the known history, reached another way. It also happens with a plain folder of that name that is no worktree at all.

## Tier that should catch it
Heavy (`space/repo/worktree_heavy_spec.py`): real git. The specs delete branches only through the product, which removes the worktree first.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). After `checkout --detach` in the worktree and `git branch -D gift-wrap`, `ticket.branch` answers `exists false, is_checked_out false`, and `ticket.activate` fails with the report's `git worktree add -b gift-wrap ...repo-gift-wrap origin/main ... already exists`. `close_choices` offers no `delete_worktree`. Not run: the plain folder of that name.
- Cause, if you found it: `space/repo/worktree.py` `Worktrees.open` and `Worktrees.add` find a worktree only by its branch (`Worktrees.of`), so the folder git lists as detached is not found and `git worktree add` is run onto it.
- Shares its cause with: gizmo-01 (lookup by branch alone); gizmo-03 and gizmo-08 (same failing call and message)
