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

## Triage

- **Status:** confirmed
- **Severity:** blocks work
- **Triaged by:** Hinge

Reproduced with roots.py: `add_root('.git')` was kept, and `all_files()` raised RepoConnectError from git ls-files run in .git.

## Fix

Scenarios "Refuse git's own folder" in `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md` and "Keep listing when git's own folder is a root" in `story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md`. Tests: `space/session/practices/practice_session_output_spec.py` (unit), adds inside git's own .git folder: refused naming the path, no root added (seen failing); `space/session/files/session_files_heavy_spec.py` (heavy), a .git folder kept as a root (written as an older version let it be): All files still lists the other roots (seen failing on HEAD). Fix: `PracticeSessionOutput.root_named` refuses a path inside a .git folder (OutputRootRefused), so choose_root and both add_root refuse it too; `SessionFiles._files_at` lists nothing for a root inside .git. One check, `inside_version_control`, in `file_manager.py`, now serves FileManager, FileDeletion, SessionFiles and the practice.

Commit: d64447e5d (the listing: SessionFiles._files_at, heavy and unit tests, scenarios) and 4fd201721 (the practice root)
