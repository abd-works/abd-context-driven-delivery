# All files lists files reached through a junction: the same file twice, and a file outside every root that delete then refuses

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Filter Files In Files App / List Every File In Session Folders - "List each file once when roots overlap" and "List every file in the session's folders" (every file *under* the session's roots).
- **Module and class:** `space/session/files/session_files.py`, `SessionFiles._tracked_under` / `in_roots` (`git ls-files --cached --others --exclude-standard` walks into an untracked junction; entries are keyed by their spelled path, so the same file under two names is kept twice).
- **Severity:** wrong result

## Steps

Project as in gizmo-1: `board/link-in` a junction to `board/drafts`, `board/link-out` a junction to `<project>/outside` (outside every root). `Sessions(project).named("tidy").all_files()` (driver `scripts/list.py <project>`).

## Expected

Each file once (`board/drafts/a.md`, `b.md`), and nothing from `outside/` (scenario "List every file in the session's folders": every file under *board* and its roots).

## Actual

```
board/drafts/a.md
board/drafts/b.md
board/link-in/a.md        <- same file again
board/link-in/b.md        <- same file again
board/link-out/keep.md    <- really <project>/outside/keep.md, outside every root
```
And the file menu cannot act on what it lists: `delete_file("board/link-out/keep.md")` answers `PathOutsideRootsError: board/link-out/keep.md is outside the session's roots` for a path the page itself showed under `board`.

## Tier that should catch it

Heavy (`session_files_heavy_spec.py` runs real git; no example holds a link under the root).

## Triage

- **Status:** confirmed
- **Severity:** wrong result
- **Triaged by:** Hinge

Reproduced with roots.py: All files listed `board/link-in/a.md`, `b.md` and `board/link-out/keep.md`. git ls-files --others walks into an untracked junction.

## Fix

Scenario "List no file through a link" in `story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md`. Test: `space/session/files/session_files_heavy_spec.py` (heavy), `session.all_files` with a link to a folder in it and one outside every root: each file once under its own path, nothing through the link outside; seen failing on HEAD. Fix: `SessionFiles._files_at` leaves out every file whose folder below the root is a link (`is_link`, a symbolic link or a junction, checked once per folder).

Commit: COMMIT
