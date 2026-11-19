# The Files app's another-project browser test fails: it expects story-map.drawio as the one file on disk, and the story map's whiteboard is listed beside it

- **Charter:** Closing the gaps - the e2e tier run on the finished code (HEAD 8762cff7a)
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > List This Session Or All Session Files, Scenario "List all session files, then this session's", Example: another project.
- **Module and class:** the test, `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review-files-in-files-app.story.ui_e2e_spec.py` (its `button.file-entry:not(.is-missing)` count), against `harness/files_app/app/files/files-page-view.tsx` `WhiteboardEntryView` and the seed in `files_app_browser.py` `_seed_project`.
- **Severity:** test out of date (the page does what Open Whiteboard In Files App asks; the older test was not brought in line)

## Steps

1. Run `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review-files-in-files-app.story.ui_e2e_spec.py` (mamba, as the e2e tier runs it).

## Expected

"Then the file bar lists that project's story-map.drawio as the one story map file on disk, not a file of the CDD checkout" passes.

## Actual

It fails: expected `['design/.context/story-map.drawio']`, got that and `'design/.context/story-map.whiteboard: opens the whiteboard as a canvas'`. Seen in the coordinator's e2e run on 8762cff7a; I read the cause from the code and history and did not run the spec again.

## Cause

Not caused by this session's fixes: none of `files-page-view.tsx`, `file-bar.ts`, `files_app_browser.py` or this spec changed between 302efe378 (the commit before the session's fixes) and HEAD.

- The test dates from d82a0b437 (2026-11-17), when a whiteboard was listed as a link and the seeded project held no whiteboard file.
- c377a83ed (2026-11-18 15:28) made a whiteboard entry a `button.file-entry` titled `<path>: opens the whiteboard as a canvas`, and a6d35f084 (2026-11-18 15:30) seeded `design/.context/story-map.whiteboard` with a real board in `_seed_project` for the story Open Whiteboard In Files App. From then on the project holds two story map files on disk, and both are `button.file-entry:not(.is-missing)`.

The scenario's own words ("the one story map file on disk") are out of date too: the seeded project now holds the drawing and the whiteboard.

## Tier that should catch it

e2e, which did. It was not seen on 2026-11-18 because the e2e tier was not run after a6d35f084.

## Needs the person's decision

Which is right for the example: the list names both files (then the test and the scenario's Then say so), or the another-project seed should hold no whiteboard.
