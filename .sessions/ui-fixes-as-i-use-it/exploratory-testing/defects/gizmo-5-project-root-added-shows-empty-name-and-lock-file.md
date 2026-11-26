# Adding the project's top folder to a practice answers an added root named "" and makes All files list session.json.lock and other sessions' records

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Add File Or Folder To Practice ("the file bar shows <root> at its top, under its own name"); List Every File In Session Folders.
- **Module and class:** `space/session/practices/practice_session_output.py`, `PracticeSessionOutput.added_roots` (`paths.from_project(project root)` gives `''`); `space/session/files/session_files.py`, `SessionFiles.in_roots` (does not leave out what `record.is_left_beside` leaves out, unlike `in_folder`).
- **Severity:** wrong result (the empty name) / misleading listing

## Steps

```python
s = Sessions(project).named("tidy")        # works in board
s.own_practices["stories"].add_root(".")   # the project's top folder
s.own_practices["stories"].added_roots     # ['']
[e.path for e in s.all_files()]
```

## Expected

The added root is answered under a name (`.` or the project's folder name), so the file bar can show it at its top "under its own name". All files leaves out what is no file of anyone's work: `in_folder` already leaves out session.json's lock file and staged text.

## Actual

`added_roots` is `['']` (and `['', 'nothere/yet']` after another add): the page gets a root with an empty name. All files lists `.sessions/tidy/session.json.lock`, `.sessions/tidy/session.json`, and another session's `.sessions/other/session.json`; and the file menu can then delete `.sessions/other` (another session's whole record), `.sessions/tidy/session.log` and `.sessions/tidy/session.json.lock` - only the own session.json and its folder are refused. Whether deleting another session's record or the own log is intended is a question for the supervisor.

## Tier that should catch it

Unit (`practice_session_output_spec.py`: no example adds the project's top folder).

## Triage

- **Status:** confirmed (the empty name and the lock file); question for the person (deleting another session's record or the own log)
- **Severity:** wrong result / misleading listing
- **Triaged by:** Hinge

Reproduced with roots.py: `added_roots` answered `['']`, and All files listed `.sessions/tidy/session.json.lock`. Whether the file menu may delete another session's `.sessions/other` or the own `session.log` no scenario says: the Refuse outline protects only the own session.json and its folder. I changed no behaviour there; I would recommend refusing any session's record folder (`.sessions/<name>`) and its session.json, since only session tools change a record, while letting a log or report file go.

## Fix

Scenarios "Name the project's top folder added as a root" in `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md` and "Leave out what a change to session.json leaves beside it" in `story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md`. Tests: `space/session/practices/practice_session_output_spec.py` (unit), adds as the project's top folder from a session working below it: listed as `.` (seen failing); `space/session/files/session_files_spec.py` (unit), `session.all_files` with a session.json under its folder that a change held: the lock file left out (seen failing). Fix: `added_roots` names the project's top `.`; `SessionFiles._files_at` leaves out what `record.is_left_beside` names, as `in_folder` already did.

Commit: COMMIT
