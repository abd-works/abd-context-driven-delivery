# Deleting a junction (Windows directory link) inside a root deletes the folder it points to, with every file in it

- **Charter:** C3 (Files app file menu and All files)
- **Tester:** Gizmo
- **Story:** Review Generated Work In File Viewer / Act On Files From File Menu / Delete File Or Folder From File Menu. No scenario covers a link; nearest is "Delete a folder and every file in it" (the folder named, not another one).
- **Module and class:** `space/session/files/session_files.py`, `SessionFiles.delete` (`path = self.existing(named).resolve()` follows the link, then `FileManager.delete` runs `shutil.rmtree` on the target).
- **Severity:** wrong result (data loss: the files deleted are not the ones the person chose, and nothing is kept to undo it)

## Steps

Throwaway git project, session `tidy` working in `board` (Stories and Clean Engineering on). This machine gives no symlink privilege, so the link is a junction, which is what a Windows user or tool makes:

```python
import _winapi
_winapi.CreateJunction(r"<project>\board\drafts", r"<project>\board\link-in")   # board/drafts holds a.md, b.md
from space.session import Sessions; import cdd_guidance.practices
Sessions(project).named("tidy").delete_file("board/link-in")
```

Seed and driver: `...\scratchpad\et\files\sandbox\scripts\seed.py` and `delete.py <project> board/link-in`.

## Expected

The link `board/link-in` is removed and `board/drafts` with `a.md` and `b.md` stays: the person chose `link-in` in the menu and was asked "Delete board/link-in? This cannot be undone." (scenario "Delete a file after confirming": the session deletes the path named).

## Actual

`delete_file("board/link-in")` answers `'board/drafts'` - the answer names a different folder from the one asked - and `board/drafts`, `a.md` and `b.md` are gone; `board/link-in` is left as a dangling junction. Same for a file: `delete_file("board/link-in/a.md")` deletes `board/drafts/a.md`.

## Tier that should catch it

Heavy (a real junction or symlink on disk): `session_files_spec.py` stubs the folder and lists symlink only among the refusals (outside the roots); no example deletes a link whose target is inside the roots.

## Also seen in the Files app (real stack, ports 18750/18751, `scripts/ui4.py`)

All files, Folders, open `board/drafts/a.md`, right-click folder `board/link-in`, Delete..., confirm. The page asks "Delete board/link-in? This cannot be undone." and toasts "Deleted board/link-in", but `board/drafts` is what went. The open file `board/drafts/a.md` stays open showing its old text (`x`), since the page closes only an open file under the path it asked to delete (`FilesPage.forget('board/link-in')`), not under the path the session answers (`board/drafts`): a stale view of a deleted file.
