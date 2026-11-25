# A close whose merge conflicts fails after it has removed the worktree, written the handoff and ended the session; the ticket stays open with no worktree

- **Charter:** Round 1 second charter - backlog items, handoffs and closing a ticket when git disagrees, as two chats on two cdd servers sharing one repository
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Close Active Session - "Complete the active ticket with its work committed", "Return to main whatever is chosen". No scenario covers a merge that conflicts on close.
- **Module and class:** `space/kanban/ticket.py` `Ticket.close`: `checkout.free_worktree(leaving)` and `self.session.close()` run before `checkout.save_work(leaving)`, which merges. Its docstring says "its branch merged before anything moves", and the comment on free_worktree says a failure there "stops the close with nothing changed".
- **Severity:** wrong result (no work is lost)

## Steps
1. `ticket.create title="Conflict one"`, `ticket.activate ticket="conflict-one"`; `session.write_handoff` for it.
2. In `..\repo-conflict-one`: change line 1 of `src/order.py`, add `src/ticket_only.py` and an untracked `scratch.txt`.
3. In `repo` on main: change line 1 of `src/order.py` differently, commit, push.
4. `ticket.close ticket="conflict-one" leaving=["handoff","commit","push","merge","delete_branch","delete_worktree"]`

## Expected
The close refuses before changing anything, saying the branch conflicts with main in `src/order.py`, and leaves the worktree so the person can resolve it there.

## Actual
```
RepoConnectError: Cannot connect git: git merge conflict-one -m merge conflict-one into main failed in C:\dev\_et\gizmo\work\repo: Auto-merging src/order.py
CONFLICT (content): Merge conflict in src/order.py
Automatic merge failed; fix conflicts and then commit the result..
```
After it: the merge was aborted and main is clean (good); the work, both handoffs and `scratch.txt` are in commit "conflict-one: leave session" on `conflict-one`, pushed to origin (good). But `..\repo-conflict-one` is gone, `session.json` still names it as the ticket's worktree, the card is still In progress in Discovery, and the handoff the close wrote is only on the unmerged branch, not in main's `.sessions/conflict-one`. The message says git cannot be reached and tells the person to "fix conflicts and then commit the result" in a merge that no longer exists. `ticket.activate` afterwards does open the worktree again from the branch.

## Tier that should catch it
Heavy (`space/kanban/ticket_work_heavy_spec.py` has "walk-conflict" closed with delete_branch only; no example closes with merge into a conflicting main).

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz2.py`). Without the handoff step (`session.write_handoff`'s arguments are not in the report). The close fails with the report's `RepoConnectError: Cannot connect git: git merge conflict-one ... CONFLICT (content): Merge conflict in src/order.py`. Afterwards `..\repo-conflict-one` is gone, `session.json` still names it as the worktree, the ticket's folder is still among the open sessions, main has no merge under way, and `origin/conflict-one` holds `conflict-one: leave session`.
- Cause, if you found it: `space/kanban/ticket.py` `Ticket.close`: `checkout.free_worktree(leaving)` (line 240) and `self.session.close()` (line 242) run before `checkout.save_work(leaving)` (line 246), which is where the merge is tried.
- Shares its cause with: gizmo-17 (the same order in `Ticket.close`: the worktree is freed before the work is saved and merged)
