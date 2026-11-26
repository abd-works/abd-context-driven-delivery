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
