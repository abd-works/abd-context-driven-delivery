# Question: session.write_file replaces a file that changed on disk since it was read, with no word

- **Charter:** Round 1 - explore the Files app and the board's pages in a real browser as a person whose files change under the page
- **Tester:** Pixel
- **Story:** no scenario covers this.
- **Module and class:** `space/session/session.py` `Session.write_file` ("Save text as the whole of path"), `SessionFiles.write` in `space/session/session_files.py`. The Files page itself has no save: nothing under `harness/files_app/app/files/` calls `write-file`, so only a caller of the route or the tool meets this.
- **Severity:** answered question

## Steps

Sandbox: `C:\dev\_et\pixel\work\repo`, session `pixel-files`; Files server on 8902; headers `x-cdd-files: 1`, `content-type: application/json`, `x-cdd-project: C:\dev\_et\pixel\work\repo`.

1. `POST /api/session/.sessions%2Fpixel-files%2Fsession.json/read-file` with `{"path":"src/cart.py"}`: answers the three lines of `Cart`.
2. On disk, replace `src/cart.py` with `class Cart:\n    CHANGED_ON_DISK = True\n`.
3. `POST .../write-file` with `{"path":"src/cart.py","text":"class Cart:\n    pass\n"}`.

## Expected

Unknown, hence the question: `read_file` answers no version, time or hash of the file, so a caller cannot say what it read and `write_file` cannot tell that the file changed.

## Actual

The write answers the new text and the file holds `class Cart:\n    pass`; the line `CHANGED_ON_DISK = True`, written by someone else between the read and the write, is gone with no refusal and no warning.

Related, same cause as pixel-01: `read-file` of a folder (`{"path":"src"}`) answers `{"path":"src","text":"","language":"plaintext"}`, an empty file, and a file in Latin-1 (`# café`) is answered with `�` in place of each such letter, so writing back what was read damages the file.

## Tier that should catch it

unit (a spec of `SessionFiles.write` on a file changed since `read`), once the answer is that it is refused or warned.

## Also seen by

## Answer (2026-11-23)

Refuse it and say so: read_file answers the file's version, a hash of its bytes, and write_file takes it back; a file changed, made or deleted on disk since that read is refused with *FileChangedSinceReadError* naming the path, and left as it is; a file not there yet is written with no version. Built in `space/session/files/file_manager.py` (`FileText.version`, `FileManager.read`/`write(path, text, version)`), `space/session/files/session_files.py` (`SessionFiles.write`) and `space/session/session.py` (`read_file`, `write_file(path, text, version)`, and the debug skill's step 3, which passes the version its step 2 write answered); the TypeScript adapters and the Files server's `write-file` route are generated from these signatures and take `version` at the next install; tested by `space/session/files/session_files_spec.py`, "session.write_file, on a file that read_file read"; scenario "Refuse to save over a file changed on disk since it was read" in `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md`, and "Save the edited text to the file on disk" now reads the file and saves with its version. The folder read answered as an empty file and the Latin-1 file read with replacement letters (same cause as pixel-01) are left as they were.
