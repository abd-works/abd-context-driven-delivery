# Report - Gizmo, charter C3 (Files app file menu and All files)

Build: branch `ui-fixes-as-i-use-it` worktree at 222d97cb5. Sandbox `...\scratchpad\et\files\sandbox` (seed, drivers and screenshots in `scripts/` and `shots/`, notes in `notes.md`), CDD_HOME `...\et\files\cdd-home`, ports 18750 (cdd server) and 18751 (Files server); 18752 named as the draw.io port but never started. Both servers stopped at the end; nothing listens on 18750-18754.

## What I tested

Throwaway git project: session `tidy` working in `board`, Stories and Clean Engineering on, `.gitignore`d `ignored/`, `board/node_modules/`, a nested folder added as a root, a file outside every root, junctions (this machine has no symlink privilege, so junctions stand in for symlinks; git and Python both follow them), files named with a space, accents and kanji, another session's record.

- Through the session's own operations (`session.delete_file`, `session.all_files`, `practice-session-output.add_root`): about 40 delete paths (odd names, case spellings, empty, `..`, outside, roots, records, `.sessions`, ignored folders, junctions, folders holding a root, a read-only file, a nested repository), about 15 add_root paths (nested, outside the workpath, ignored file and folder, `.git`, `.`, `..`, empty, not there yet, already a root), and All files after each.
- Through the real Files app (page built from this checkout, `spec-files-server.ts`, a real cdd server, Chromium via Playwright): All files list and folders, Add to practice (folder, file, already a root), Delete (odd names, a file root, a folder root, a junction with a file open, double-click on confirm), Validate and Display violations on a declared and an undeclared file, two pages on one session.

## Defects (defect area, each queued as a `[defect]` card)

| File | Severity | In short |
|---|---|---|
| gizmo-1-delete-through-junction-deletes-target-folder.md | wrong result, data loss | Deleting a junction deletes the folder it points to; the page toasts the link's name and keeps the deleted file open |
| gizmo-8-folder-delete-half-done-and-reaches-nested-git.md | wrong result, data loss | Folder delete stops half-way on a read-only file and says "not deleted"; a folder holding a nested repository's `.git` is left corrupt |
| gizmo-3-delete-parent-folder-removes-a-root.md | wrong result | Deleting a folder that holds a root removes the root that a direct delete refuses; session.json keeps naming it |
| gizmo-4-git-folder-as-root-breaks-all-files.md | blocks work | `.git` is accepted as a practice root, then All files fails for the whole session |
| gizmo-2-all-files-lists-through-junctions.md | wrong result | All files lists the same file twice through a junction, and a file outside every root that delete then refuses |
| gizmo-5-project-root-added-shows-empty-name-and-lock-file.md | wrong result | Adding `.` gives an added root named `""`; All files then lists `session.json.lock` and other sessions' records, which can be deleted |
| gizmo-6-file-added-to-practice-can-never-be-deleted.md | misleading message | A file added to a practice can't be deleted ("delete the files and folders in it"), and there's no way to take the root back |
| gizmo-7-add-existing-root-says-added.md | misleading message | Adding a practice's own root again toasts "added" |
| gizmo-9-question-ignored-root-listed-or-not.md | question | An ignored file added as a root is listed, but an ignored folder added as a root lists nothing |

## Confusing places

- Disabled practices (UX, DDD, BDD) still count their default folders as session roots (`board/ux`, `board/src`, `board/story_tests`), so what "the session's roots" means for delete is wider than the practices the person turned on.
- In the selected scope the code format is chosen by default, so the session's markdown files are hidden until the M↓ chip is pressed (Pip's question pip-3 covers this).
- A file deleted in another page gives `NamedPathNotFoundError: ... name paths from the project's root, or absolute`, which tells the person they spelled the path wrong when it is simply gone. I did not file this.

## Not reached

- Real symlinks: this machine has no privilege to make them. Junctions show the same follow-the-link fault; a file symlink or a symlink to outside the project is untested.
- A session in a ticket's worktree, where the record folder sits in the main checkout and roots are in two checkouts.
- Two people or chats adding roots at once (add_root claims to keep a concurrent add); a delete racing a write from the agent.
- Add to practice on a root outside the workpath from the UI: All files lists nothing outside the workpath until a root is added there, so the page has nothing to right-click.
- The menu's Add to chat context and Open in file browser (they need a chat and the desktop).
- Very long paths (over 260 characters), and Validate on a folder.

## Remaining risk

The worst risk is in `SessionFiles.delete` / `FileManager.delete`. The checks look at the path as named or as resolved, never at what the delete will actually remove: links are followed, roots and `.git` folders lower down are not checked, and `rmtree` is not all-or-nothing. Any fix should check every path the delete will remove. The add_root side accepts any path inside the project, and All files trusts every root, so one bad root takes the whole listing down.
