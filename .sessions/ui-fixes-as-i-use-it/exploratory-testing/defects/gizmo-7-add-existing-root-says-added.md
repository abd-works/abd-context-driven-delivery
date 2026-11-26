# Adding a folder that is already a practice's root says "added to <practice>" though nothing changed

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** Add File Or Folder To Practice ("the page says *story_tests/checkout added to Stories*"); no scenario covers a path that is already a root.
- **Module and class:** `space/session/practices/practice_session_output.py` `PracticeSessionOutput.add_root` (silently a no-op; `added_roots` stays `[]` because the practice's own root is subtracted); `harness/files_app/app/files/file-menu.ts` `FileMenu.addToPractice` (toasts unconditionally).
- **Severity:** misleading message (cosmetic)

## Steps

Same stack as gizmo-6. All files, Folders, right-click `board/.context` (Stories' own root, `outputs.stories.root = .context`), Add to practice > Stories.

## Expected

"board/.context is already a root of Stories" (or the choice greyed out for a practice it is already a root of), as the charter's risk "add-to-practice on a file already a root" asks.

## Actual

Toast "board/.context added to Stories"; session.json gains `".context"` again only in the fidelities' roots lists, `added_roots` stays empty, the tree does not change. Also true for a file added a second time (no change, same toast).

## Tier that should catch it

Unit (`file-menu.spec.ts`, `practice_session_output_spec.py`).

## Triage

- **Status:** confirmed
- **Severity:** misleading message (cosmetic)
- **Triaged by:** Hinge

Reproduced with roots.py: `add_root('board/.context')` on Stories, whose own root it is, succeeded silently and rewrote each fidelity's roots.

## Fix

Scenario "Refuse a root the practice already has" in `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md`. Test: `space/session/practices/practice_session_output_spec.py` (unit), adds a second time: refused saying it is already a root of Stories (seen failing). Fix: `PracticeSessionOutput.add_root` refuses a path that is already a root of every fidelity of the practice (OutputRootRefused, "... is already a root of Stories"), so the page's existing failure toast says "... was not added to Stories: ... is already a root of Stories"; nothing is written. No page change was needed.

Commit: d64447e5d (scenario) and 4fd201721 (the refusal and its test)
