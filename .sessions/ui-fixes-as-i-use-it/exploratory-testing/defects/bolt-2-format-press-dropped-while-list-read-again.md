# A format press made while the Files app reads the list again is dropped without a word

- **Charter:** supervisor, found by the regression run (e2e tier), after exploratory testing closed.
- **Tester:** Bolt (regression run resumed in chat d0e9c5f2).
- **Story:** Review Generated Work In File Viewer > Filter Files In Files App > Filter Files By Format In Files App. No scenario covered a press made while the list is read again.
- **Module and class:** `harness/files_app/app/files/guidance-selector.ts`, `GuidanceSelector.toggle`: it started nothing while the page's `filtering` was set, and the page also sets `filtering` ("the new selection") in `FilesPage.showSelected` while it reads the list again for a selection it was given, as it does as it opens and after a chip is pressed on the chat bar.
- **Severity:** wrong result (the Person's press is lost; the chip stays as it was and nothing says why).
- **Steps:**
  1. Open the Files app on a session whose only chosen format is code, from a chat (`story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app`, `opened_from_chat`).
  2. Press the markdown chip as soon as it shows.
  3. Read the chip's `aria-pressed` for 12 seconds.
- **Expected:** markdown chosen and its chip selected, as a press made later does.
- **Actual:** in 2 of 3 runs the chip stayed unselected, with no notice and no call to `session.toggle_guidance`; the review-graph-violations e2e spec failed 6 of 8 examples on it.
- **Tier that should catch it:** unit, `files-page.spec.ts`: a press made while the page says it is filtering by a selection it was given.

## Triage

- **Status:** confirmed. Reproduced on its own by pressing the chip the moment it shows (2 of 3 runs dropped), and in a unit example that sets the page filtering by "the new selection" and presses.
- **Severity:** wrong result.
- **Triaged by:** Bolt, from the regression run's e2e failure; reporter and fixer are the same robot here, since the regression run found it after the testers had closed.
- **Why:** commit 48b156f34 kept a second press from starting a second toggle by checking the page's `filtering`, which a list read for a selection given from elsewhere sets too.

## Fix

- **Scenario:** A format press made while the list is read again is still made (`story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md`).
- **Test (unit):** `harness/files_app/app/files/files-page.spec.ts`, Select Guidance In Files App › that has the diagram format selected › should toggle a press made while the page reads the list for a selection changed elsewhere. Seen failing (no toggle posted), then passing.
- **Fix:** `GuidanceSelector.toggle` holds the next press back only while a press of its own is filtering (`isPressing`), not while the page reads the list for a selection it was given.
- **e2e:** the review-graph-violations spec presses the markdown chip on beside code (pressing off the only chosen format is refused since pip-4's fix) and passes 8 of 8.
- **Commit:** see git log for this file.
