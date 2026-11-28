# gizmo-02 A dangling link left at `_removing-<name>` makes the session impossible to delete, with a raw FileExistsError

**Title** - When `.sessions/_removing-<name>` is a junction whose target is gone, every `ticket.delete` of `<name>` fails with `FileExistsError: [WinError 183]`, and keeps failing however often it is retried.

**Charter** - theme 4, deleting a session. **Tester** - Gizmo.

**Story** - Maintain tickets / Delete Ticket; scenario "Delete a ticket and its session folder". The spec context "that an earlier removal left a folder set aside under its name" covers a real folder only.

**Module and class** - `space/session/session_folder.py`, `_free_name_beside`: `if not aside.exists() or _removed_whole(aside)` — `Path.exists()` is False for a dangling junction, so the name is taken as free and `record_folder.rename(aside)` in `_set_aside` hits the link; `_set_aside` translates only `PermissionError`, so `FileExistsError` reaches the caller untranslated.

**Severity** - blocks work (the session can neither be deleted nor cleaned up from the board; the message names no fix).

**How the dangling link arises** - gizmo-01 leaves exactly this link behind every time a junctioned session folder is deleted; it also arises from any `_removing-` junction whose target a person later removed.

**Steps** (`C:\dev\_et\after-1-2-1\gizmo\t3_dangling.py`)
1. Repository with a bare origin; `Sessions(repo).switch("old-notes", repo, create=True)`.
2. `mklink /J .sessions\_removing-old-notes <sandbox>\canary\t3-gone`, then remove `t3-gone`.
3. `board.placement.ticket("old-notes").delete()`; then call it again.

**Expected** - The session is deleted (the leftover name cleared, or a numbered name taken, as `_free_name_beside` promises: "the folder an earlier removal left under that name is removed first, and where some of it cannot be, the name takes a number").

**Actual** - both calls: `FileExistsError: [WinError 183] Cannot create a file when that file already exists: '...\.sessions\old-notes' -> '...\.sessions\_removing-old-notes'`. `old-notes` stays on the board, whole.

**Tier that should catch it** - unit (`session_folder_spec.py`, a dangling junction made in a temp folder). The spec's left-behind case makes a real folder, which `exists()` sees.
