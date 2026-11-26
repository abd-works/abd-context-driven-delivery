# Deleting a folder that holds a root deletes the root, which a delete of the root itself refuses

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Act On Files From File Menu / Delete File Or Folder From File Menu / "Refuse what may not be deleted" (row: *board, a root itself* -> RootDeleteRefused). No row covers a folder *holding* a root.
- **Module and class:** `space/session/files/session_files.py`, `SessionFiles.delete` (`if path in self._roots` checks equality only, not whether a root lies under the folder deleted).
- **Severity:** wrong result (the root and its files go; session.json keeps naming a root that is not there)

## Steps

Project and session `tidy` (works in `board`) from `...\scratchpad\et\files\sandbox\scripts\seed.py`; driver `scripts/roots.py`:

```python
s = Sessions(project).named("tidy")
s.own_practices["clean_engineering"].add_root("board/deep/nested/root")  # Add to practice
s.delete_file("board/deep/nested/root")   # RootDeleteRefused - as promised
s.delete_file("board/deep")               # answers 'board/deep'
```

## Expected

The delete of `board/deep` is refused (RootDeleteRefused, naming the root it holds), as the delete of the root itself is: the module doc says a root is "not deleted: delete the files and folders in it", and the charter's risk list names "a delete that removes a root". (If the intent is that a parent may go, the scenario table should say so and session.json should drop the root.)

## Actual

`board/deep`, `board/deep/nested/root` and `x.md` are gone; session.json still holds `"roots": [".", "deep/nested/root"]` for every Clean Engineering fidelity, now naming nothing. Refusing the root while allowing its parent makes the refusal only cosmetic.

## Tier that should catch it

Unit (`session_files_spec.py`, refusal examples on a stubbed folder): only the root itself is tried.

## Triage

- **Status:** confirmed
- **Severity:** wrong result, data loss
- **Triaged by:** Hinge

Reproduced with roots.py: after adding `board/deep/nested/root` to Clean Engineering, `delete_file('board/deep')` deleted the root; `SessionFiles.delete` compared the path with each root for equality only.

## Fix

Row "board/deep, a folder holding the root ..." in the Refuse outline of `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md`. Test: `space/session/files/session_files_spec.py` (unit), `session.delete_file` that names a folder holding a root a person added: refused naming the root it holds, and the folder kept; seen failing. Fix: `SessionFiles._deletable` refuses a path that is a root or holds one that is there (*RootDeleteRefused*, "src/drafts holds src/drafts/deep, one of the session's roots ..."). The intent (a parent of a root may not go) follows the module's rule that a root is not deleted; if the person wants a parent to go with its root dropped, that is a new scenario.

Commit: d64447e5d (test, fix, scenario); listing halves of gizmo-4 and gizmo-5 in the same commit
