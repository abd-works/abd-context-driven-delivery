# A folder delete stops half-way on a read-only file and reports "not deleted" after deleting part of it; a folder holding a nested repository's .git is deleted into a corrupt half

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Delete File Or Folder From File Menu - "Delete a folder and every file in it" and "Refuse what may not be deleted" (*board/.git/config* -> VersionControlPathRefused, "nothing is deleted").
- **Module and class:** `space/session/files/file_manager.py`, `FileManager.delete` (`shutil.rmtree(target)` with no handling of read-only entries and no check for a `.git` folder *inside* the folder deleted); `SessionFiles.delete`.
- **Severity:** wrong result (data loss with a message saying nothing was deleted)

## Steps

Project from `...\scratchpad\et\files\sandbox\scripts\seed.py`, session `tidy` works in `board`:

```bash
mkdir board/ro; echo a > board/ro/a.md; echo z > board/ro/z.md; attrib +R board\ro\z.md
mkdir board/vendor; cd board/vendor; git init; echo v > v.md; git add v.md; git commit -m v   # a cloned dependency
```
```python
s = Sessions(project).named("tidy")
s.delete_file("board/ro")
s.delete_file("board/vendor")
```

## Expected

Either the whole folder goes or nothing does, and the answer says which. Deleting a folder that holds a `.git` folder is refused (VersionControlPathRefused), as a path inside `.git` is: the scenario promises "nothing is deleted" for git's own record.

## Actual

- `board/ro` -> `PermissionError [WinError 5] Access is denied: ...\board\ro\z.md`; `a.md` is already gone, `z.md` stays. The Files app shows "board/ro was not deleted: ..." though half of it was.
- `board/vendor` -> `PermissionError ... board\vendor\.git\objects\...`; `v.md` and part of `.git` are gone, `.git/HEAD`, `config`, `hooks` stay: the nested repository is left corrupt. Git's object files are read-only on Windows, so every folder holding a repository fails this way.

## Tier that should catch it

Heavy (real files with the read-only attribute, a real nested `git init`); `session_files_spec.py` only checks paths inside `.git`.

## Triage

- **Status:** confirmed
- **Severity:** wrong result, data loss
- **Triaged by:** Hinge

Reproduced in a unit example: a folder holding a read-only file failed half-way with PermissionError, and a folder holding a .git folder was deleted part way. `FileManager.delete` ran shutil.rmtree with no check of what it removes.

## Fix

Rows "board/vendor, a folder holding a nested repository's .git" and "board/ro, a folder holding a read-only file" in the Refuse outline of `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md`. Tests: `space/session/files/session_files_spec.py` (unit), `session.delete_file` that names a folder holding a nested repository's .git folder (refused naming it, nothing deleted) and one holding a read-only file (refused naming it, nothing deleted); all seen failing. Fix: `FileDeletion` checks every path the delete removes before deleting anything: a .git folder (VersionControlPathRefused "... holds .git ..."), the session's own session.json, a read-only file (new *ReadOnlyDeleteRefused*); a delete the file system still stops part way, such as on a file another program holds open, raises the new *FolderPartlyDeleted*, saying part is gone, never "not deleted". FileManager.delete is gone (SessionFiles was its only caller).

Commit: COMMIT
