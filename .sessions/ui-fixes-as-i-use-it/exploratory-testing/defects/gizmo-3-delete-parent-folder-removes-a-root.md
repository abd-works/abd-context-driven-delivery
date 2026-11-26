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
