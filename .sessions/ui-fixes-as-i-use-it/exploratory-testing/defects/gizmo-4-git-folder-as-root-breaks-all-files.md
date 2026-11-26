# Add to practice takes the .git folder as a root, and from then on All files fails for the whole session

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Act On Files From File Menu / Add File Or Folder To Practice ("Refuse a path outside the project" is the only refusal) and Filter Files In Files App / List Every File In Session Folders.
- **Module and class:** `space/session/practices/practice_session_output.py`, `PracticeSessionOutput.root_named` / `add_root` (accepts any path inside the project, `.git` included); `space/session/files/session_files.py`, `SessionFiles._tracked_under` (runs `git ls-files` with `.git` as its folder).
- **Severity:** blocks work (All files answers an error until session.json is edited by hand)

## Steps

Project and session `tidy` from `...\scratchpad\et\files\sandbox\scripts\seed.py`, driver `scripts/roots.py`:

```python
s = Sessions(project).named("tidy")
s.own_practices["stories"].add_root(".git")   # accepted: added_roots ['.git']
s.all_files()
```

In the Files app: right-click `.git` (only reachable when the project root is listed, or by an agent calling `practice-session-output.add_root`), Add to practice > Stories, then press All files.

## Expected

`.git` is refused as a root, as every read, write and delete of a path inside `.git` is (VersionControlPathRefused: ".git holds git's own record ... neither read nor written as a file"). At the least All files keeps listing the other roots.

## Actual

`add_root(".git")` succeeds and is kept in session.json. Then `all_files()` raises
`RepoConnectError: Cannot connect git: git ls-files --cached --others --exclude-standard -z failed in <project>\.git: fatal: this operation must be run in a work tree.` - one bad root takes the whole listing down. (Also: Validate and other readers of the session's roots now carry a root inside `.git`.)

## Tier that should catch it

Unit for the refusal (`practice_session_output_spec.py` add_root examples); heavy for the listing (`session_files_heavy_spec.py`).
