# Question: session.write_file and session.read_file take a path inside the repository's .git folder

- **Charter:** Round 1 - explore the Files app and the board's pages in a real browser as a person whose files change under the page
- **Tester:** Pixel
- **Story:** no scenario covers this.
- **Module and class:** `space/session/session.py` `Session.write_file` / `read_file`, through `SessionFiles.write` / `read` in `space/session/session_files.py`; reached from a page by the Files server's routes `POST /api/session/<session.json>/write-file` and `/read-file` (`harness/files_app/app/files-server.ts`).
- **Severity:** answered question

## Steps

Sandbox: `C:\dev\_et\pixel\work\repo`, session `pixel-files`; Files server on 8902.

```
curl -X POST -H "x-cdd-files: 1" -H "content-type: application/json" -H "x-cdd-project: C:\dev\_et\pixel\work\repo" -d "{\"path\":\".git/pixel-probe\",\"text\":\"x\"}" "http://127.0.0.1:8902/api/session/.sessions%2Fpixel-files%2Fsession.json/write-file"
curl -X POST (same headers) -d "{\"path\":\".git/config\"}" ".../read-file"
```

## Expected

Unknown, hence the question. A path outside the session's roots is refused (`PathOutsideRootsError: ../outside2.txt is outside the session's roots`), and the list leaves `.git` out. A write under `.git` can place `hooks/pre-commit`, which git then runs on the person's next commit, or rewrite `config`.

## Actual

The write answers `{"path":".git/pixel-probe","text":"x","language":"plaintext"}` and the file is there; the read answers the whole of `.git/config`. The same write also makes folders that are missing (`src/new/deep/made.py`), which reads as intended.

Is `.git` meant to count as "a file in this repository" for `write_file`?

## Tier that should catch it

unit (a spec of `SessionFiles.write` naming a path under `.git`), once the answer is that it is refused.

## Also seen by

## Answer (2026-11-23)

No: a path inside a .git folder is refused for reading and writing, with a named refusal carrying the path. Built in `space/session/files/file_manager.py` (*VersionControlPathRefused*, checked in `FileManager._inside` for every segment of the path under its root, in any case, so `list`, `read` and `write` and through them `session.read_file`, `session.write_file` and `session.file` refuse it; `.gitignore` is still read and saved); tested by `space/session/files/session_files_spec.py`, "session.read_file and session.write_file, on a path inside the repository's .git folder"; scenario "Refuse to read or save a file inside the repository's .git folder" in `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md`, replayed by its domain story spec.
