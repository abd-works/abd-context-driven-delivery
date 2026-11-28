# gizmo-04 What a delete leaves in `_removing-<name>` is committed onto main and pushed to origin, a nested repository as a gitlink

**Title** - The save that records a session's removal commits `.sessions/_removing-<name>/` as ordinary session files and pushes them, so the deleted session's files (and any nested git repository, as a mode 160000 gitlink with no `.gitmodules`) land on main on origin.

**Charter** - theme 4, deleting a session. **Tester** - Gizmo.

**Story** - Maintain tickets / Delete Ticket; the Delete ticket docstring says "its folder, log, and files are removed, that removal committed on main and pushed". No scenario covers what a partial removal commits.

**Module and class** - `space/session/session_saves.py` (*SessionSaves*: commits the session folders on main) together with `space/session/session_folder.py` `remove()`, which queues `record.saved("removed")` whatever `_removed_whole` answered. The sessions' own `.gitignore` written by SessionSaves lists `**/*.tmp`, `**/*.lock`, `**/progress-cache.json`, but not `_removing-*/`.

**Severity** - wrong result (the deleted work, and a stray embedded repository, are published on main for every clone).

**Steps** (`C:\dev\_et\after-1-2-1\gizmo\t4_git_held_long.py`, case F; any leftover in the set-aside folder does the same)
1. As gizmo-03 steps 1-3: a session `has-git` holding a committed git repository in `spike/`, deleted through `ticket.delete`.
2. Wait for the save; `git --git-dir origin.git ls-tree main .sessions/_removing-has-git/`.

**Expected** - The removal's commit removes the session's files from main; nothing under `_removing-` is ever committed, since the module describes it as a folder "which no board lists" that "is no session".

**Actual** - commit `sessions: has-git name has-git / sessions: has-git removed` adds:
```
100644 blob ...	.sessions/_removing-has-git/session.json
100644 blob ...	.sessions/_removing-has-git/session.log
160000 commit 5ed6fdd9...	.sessions/_removing-has-git/spike
```
and origin's main holds them.

**Tier that should catch it** - heavy (`session_saves_heavy_spec.py` or `ticket_work_heavy_spec.py`: a real git repository, a delete that leaves a file aside, and a look at what main committed). No test leaves a file aside with real git underneath.
