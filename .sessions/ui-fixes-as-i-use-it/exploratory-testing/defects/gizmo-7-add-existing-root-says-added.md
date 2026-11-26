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
