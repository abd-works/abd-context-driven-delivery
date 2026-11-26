# A file added to a practice can no longer be deleted from the file menu, and the refusal tells the person to "delete the files and folders in it"

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Act On Files From File Menu: "Add a file to a practice" (the file itself becomes a root) meets "Refuse what may not be deleted" (*a root itself* -> RootDeleteRefused). No scenario says how a person then tidies that file away; the menu has no "remove from practice".
- **Module and class:** `space/session/files/session_files.py`, `SessionFiles.delete` / `RootDeleteRefused` (message written for a folder); `harness/files_app/app/files/file-menu.ts` `FileMenu` (no way to take a root back).
- **Severity:** misleading message (and blocks tidying a file once added)

## Steps

Real stack: cdd server on 18750 (own CDD_HOME), Files server (`spec-files-server.ts`) on 18751, project from `...\scratchpad\et\files\sandbox\scripts\seed.py`, Playwright driver `scripts/ui2.py`:

1. Open `http://127.0.0.1:18751/?files=tidy&fidelity=stories-story-map&project=<project>`, press All files.
2. Right-click `board/notes.md`, Add to practice > CE. Toast: "board/notes.md added to CE"; the file moves to the top of the tree.
3. Right-click `board/notes.md`, Delete..., confirm Delete.

## Expected

Either the file is deleted (and dropped from the practice's roots), or the refusal says what to do that the person can do: e.g. "board/notes.md was added to Clean Engineering as a root; take it out of the practice first", with a menu choice to do so.

## Actual

`board/notes.md was not deleted: cdd session.delete_file failed: RootDeleteRefused: board/notes.md is one of the session's roots, which is not deleted: delete the files and folders in it` - a file has no files in it, and there is no menu choice (and no Files app control) to take the root back; only an agent editing session.json can. Same for a folder added (`board/drafts`), where the folder can never go.

## Tier that should catch it

Unit (`file-menu.spec.ts` / `session_files_spec.py`): the refusal is tested with a folder root only.
