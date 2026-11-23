# Closing a ticket whose worktree folder a running program holds open reports done but leaves the folder, and the ticket can then never be activated: "already exists"

- **Charter:** Round 1 second charter - backlog items, handoffs and closing a ticket when git disagrees, as two chats on two cdd servers sharing one repository
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Delete Ticket Branch - "Delete the branch and the worktree that has it"; Activate Ticket - "Open a ticket in its own worktree".
- **Module and class:** `space/repo/worktree.py` `Worktrees.remove` -> `_unregister_held` (git forgets the checkout, the folder stays); its docstring promises "A folder still there afterwards raises WorktreeNotRemovedError, so a close is never reported done for a checkout that still exists". Then `Worktrees.add` on the next activate.
- **Severity:** blocks work

## Steps
1. `ticket.create title="Held four"`, `ticket.activate ticket="held-four"`; add `src/held.py` in `..\repo-held-four`.
2. Hold the folder open, as a chat's shell or an editor does: `cd ../repo-held-four/src && python -c "import time; time.sleep(45)" &`
3. `ticket.close ticket="held-four" leaving=["commit","push","delete_worktree"]`
4. After the holding program has ended: `ticket.activate ticket="held-four"`

## Expected
Step 3 raises WorktreeNotRemovedError ("close what holds it open and close it again"), or step 4 opens the ticket in the folder left behind.

## Actual
Step 3 answers the closed ticket (4.3 s). The work is committed and pushed ("held-four: leave session"), `git worktree list` no longer lists it, the session folder is in `_complete`, but `..\repo-held-four\src` is still on disk, empty. Step 4:
```
RepoConnectError: Cannot connect git: git worktree add C:\dev\_et\gizmo\work\repo-held-four held-four failed in C:\dev\_et\gizmo\work\repo: Preparing worktree (checking out 'held-four')
fatal: 'C:/dev/_et/gizmo/work/repo-held-four' already exists.
```
Nothing in the product removes the leftover folder, and nothing said it was left. A chat working in the worktree is the usual case of a held folder, so this is the usual close. Same end state as gizmo-07 and the session-log leftover in the known history. No work was lost.

## Tier that should catch it
Heavy on Windows (`space/repo/worktree_heavy_spec.py`): needs a real process holding the folder, then a second open of the same branch.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz2.py`). With a Python process holding `repo-held-four\src` as its working folder, `ticket.close leaving=[commit, push, delete_worktree]` answers the closed ticket; `git worktree list` no longer lists it, the session is in `_complete`, and `repo-held-four\src` is still on disk, empty. After the holder ended, `ticket.activate` fails with the report's `git worktree add ...repo-held-four held-four ... already exists`.
- Cause, if you found it: `space/repo/worktree.py` `Worktrees.remove` -> `_unregister_held`: it removes the folder's `.git` link, logs a warning, and returns, so the folder stays and no `WorktreeNotRemovedError` is raised, though `remove`'s own description promises one. `Worktrees.add` then runs onto the folder.
- Shares its cause with: gizmo-07 (a folder in the way of `Worktrees.add`, which never looks); gizmo-03 and gizmo-08 fail with the same message
