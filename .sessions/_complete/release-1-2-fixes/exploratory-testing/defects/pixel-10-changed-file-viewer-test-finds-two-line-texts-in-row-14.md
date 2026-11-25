# The board's file viewer test "Show the agent's change to the open file" fails on a strict locator: row 14 holds the old line struck through and the new line

- **Charter:** Closing the gaps - the e2e tier run on the finished code (HEAD 8762cff7a)
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > Show Changed File In Viewer, Scenario "Show the agent's change to the open file".
- **Module and class:** the test, `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review-files-in-viewer.story.ui.spec.ts` line 343 (`row(page, 14).locator('.line-text')`), against `space/kanban/app/src/kanban/ticket/file-viewer-view.tsx` `CodeRowView`, which draws `RemovedLinesView` inside the row.
- **Severity:** test fails by timing (the viewer shows what the scenario asks: the new line 14, with the line it replaced struck through above it)

## Steps

1. Run the Playwright story-ui project on `review-files-in-viewer.story.ui.spec.ts`.

## Expected

"Then the viewer shows line 14 as raise EmptyCartError(cart.id, "a cart needs one item to be placed")" passes.

## Actual

Strict mode violation: `.code-row[data-line="14"] .line-text` resolved to 2 elements, the old line and the new one. Seen in the coordinator's e2e run on 8762cff7a; I read the cause from the code and history and did not run the spec again.

## Cause

Not caused by this session's fixes: neither the spec, `file-viewer-view.tsx`, `space/session/file_comments.py`, `harness/chat` nor the story-ui support changed between 302efe378 and HEAD, and `space/session/session_file.py` changed only by two refusals placed before `changes` is read.

`CodeRowView` puts the removed lines inside `div.code-row[data-line]`, each with its own `span.line-text`, and has since the change view was written (4b8219966, 2026-11-12). `SessionFile.changes` answers a change only once the comment is processed. So the locator finds one `.line-text` while the comment is still sent and two once it is processed: the assertion passes when it reads the row before the processed state reaches the page and fails when it reads it after. The second test of the scenario waits for "processed", which shows the page does reach that state.

## Tier that should catch it

e2e, which did, on a run where the processed state arrived first.

## Suggested correction, for whoever takes it

Name the line itself in the test, not every `.line-text` in the row: the row's own line is the `.line-text` outside `.removed-lines`, and the struck-through line is the one inside it. Asserting both (the new text on the line, the old text among the removed lines) would also make the test wait for the processed state instead of racing it.
