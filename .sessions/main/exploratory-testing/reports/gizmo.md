# Gizmo - theme 4, deleting a session

Tested `ticket.delete` -> `SessionFolder.remove` in process against real git repositories with bare origins under `C:\dev\_et\after-1-2-1\gizmo\work`, on Windows 11, Python 3.12.10. Notes per case: `C:\dev\_et\after-1-2-1\gizmo\notes.md`; scripts `t1`-`t6` beside it.

## Worst defects
1. **gizmo-01** - a session folder that is a junction: delete removes everything in the junction's target outside the repository (`_extended_length` calls `resolve()`). Data loss.
2. **gizmo-04** - whatever a delete leaves in `_removing-<name>` is committed onto main and pushed; a nested repository goes in as a gitlink.
3. **gizmo-03** - a session holding a git repository with a commit: nothing removed (read-only objects), session gone from the board, files hidden in the set-aside folder, never cleared by later deletes. Includes the question whether a nested repository should be deleted at all.
4. **gizmo-05** - delete of a ticket in its own worktree commits and pushes the files an in-worktree junction points to (space/kanban + space/repo; no single fixer owns it).
5. **gizmo-02** - a dangling link at `_removing-<name>` (which gizmo-01 always leaves) blocks every delete of that name with a raw `FileExistsError`.

## Held up well
Junction inside the session folder (not followed), file held open and a program working in the folder (refused, session whole, deletable afterwards), paths of 376 characters, an open and a closed session of one name.

## Confusing
- `remove()` promises "the next removal of a session of that name clears it"; with any read-only file it never does.
- A session named `_removing-x` is silently not created: `switch(create=True)` returns, `named()` answers None (not reported, outside this charter).

## Not reached
- Symbolic links (`mklink /D`, needs developer mode or admin); expected to behave as gizmo-01.
- Delete through the cdd server and the board page (charter gave no ports); two deletes of one ticket at the same moment; a process killed between the set-aside rename and the save.
- Deleting a Backlog item folder (`BacklogItem.delete`) with the same data.

## Where the risk still is
Every path that hands `rmtree` a `resolve()`d path, and every save that commits `.sessions` as a whole: both turn a bad folder into lost or published data. The unit spec stands in for Windows with fake `rmtree`s, so real links and read-only files never reach it.
