# gizmo-05 Deleting a ticket in its own worktree commits and pushes the contents of a folder outside the repository that a junction in the worktree points to

**Title** - Before removing a ticket's worktree, `ticket.delete` commits everything in it and pushes the branch; a directory junction in the worktree is followed by Git for Windows, so the files of the outside folder it points to are committed and pushed to origin.

**Charter** - theme 4, deleting a session. **Tester** - Gizmo.

**Story** - Maintain tickets / Delete Ticket; scenario "Delete a ticket that is open in its own worktree" (Then: that work is committed on the branch on origin). No scenario covers links in the worktree. The same commit runs on archive (`free_worktree`), and likely on close with `commit`.

**Module and class** - `space/kanban/ticket_checkout.py` `TicketCheckout.free_worktree` -> `worktree.close(...)` (space/repo worktree close: add everything, commit, push). It adds the worktree as a whole, without leaving out reparse points. Files owned by space/kanban and space/repo, so not one fixer's alone: the person decides who takes it.

**Severity** - wrong result (files from outside the project are published to origin without the person seeing them; the canary itself survives the delete).

**Steps** (`C:\dev\_et\after-1-2-1\gizmo\t5_worktree.py`)
1. Repository with a bare origin; `Ticket.create("Spike work", project=repo)`; `board.placement.ticket("spike-work").activate()`.
2. In the worktree `repo-spike-work`: `mklink /J linked-assets <sandbox>\canary\t5` (holds `precious.txt`), and `mklink /J .sessions\spike-work\linked-in-work <sandbox>\canary\t5`.
3. `board.placement.ticket("spike-work").delete()`.
4. `git ls-tree -r --name-only origin/spike-work`.

**Expected** - The work the ticket did is committed; a link to a folder outside the repository is not followed (committed as a link, or left out and named in the answer). The canary's files stay private.

**Actual** - origin/spike-work holds `linked-assets/precious.txt` and `.sessions/spike-work/linked-in-work/precious.txt`. The canary folder itself survives, and the worktree is removed.

**Tier that should catch it** - heavy (`ticket_work_heavy_spec.py`, Windows-only context with a junction in the worktree). The heavy spec's delete case writes only an ordinary file.
