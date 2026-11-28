# gizmo-01 Deleting a ticket whose session folder is a junction deletes everything in the folder the junction points to

**Title** - When `.sessions/<name>` is a directory junction (or symbolic link), `ticket.delete` removes every file of the junction's target outside the repository, and leaves a dangling `_removing-<name>` junction behind.

**Charter** - theme 4, deleting a session. **Tester** - Gizmo.

**Story** - Move work forward on session board / Maintain tickets / Delete Ticket; scenario "Delete a ticket and its session folder" (its Then says only `.sessions/pet-visits is gone`). No scenario covers a session folder that is a link.

**Module and class** - `space/session/session_folder.py`, `_removed_whole` via `_extended_length`: `Path(f"\\\\?\\{folder.resolve()}")`. `resolve()` follows the junction that `_set_aside` just renamed, so `shutil.rmtree` is handed the target folder itself, and rmtree's own link refusal ("Cannot call rmtree on a symbolic link") never sees a link. The same call removes `session.work_folder`, so a work folder that is a junction is followed the same way.

**Severity** - wrong result (data loss outside the session's folder).

**Steps** (Python 3.12, Windows; driver in `C:\dev\_et\after-1-2-1\gizmo\drive.py`, script `t1_junctions.py`, case C)
1. Make a repository with a bare origin; `Sessions(repo).switch("is-junction", repo, create=True)`.
2. Move the files of `.sessions/is-junction` into `C:\dev\_et\after-1-2-1\gizmo\canary\t1c`, add `precious.txt` there, remove the emptied folder, and `mklink /J .sessions\is-junction C:\dev\_et\after-1-2-1\gizmo\canary\t1c`.
3. `Board(Sessions.of_project(repo), ...).placement.ticket("is-junction").delete()`.

**Expected** - The session leaves the board and `.sessions/is-junction` (the link) is gone; nothing outside `.sessions` is removed. `remove()` promises to delete "this session's record folder and its work folder", and the charter's rule is that a delete never removes files outside the session's folder.

**Actual** - delete answers success; `canary\t1c` no longer exists (`precious.txt`, `session.json`, `session.log` all gone); `.sessions` now holds `<JUNCTION> _removing-is-junction [C:\dev\_et\after-1-2-1\gizmo\canary\t1c]`, pointing at nothing.

A junction *inside* the session folder (case B, `.sessions/with-junction/linked -> canary`) is handled correctly: the canary survives.

**Tier that should catch it** - unit (`session_folder_spec.py` with a real junction made in a temp folder; fast). The spec covers held files, a held folder, a left-behind set-aside folder and long paths, but no folder that is a link, so `resolve()` was never exercised on one.
