# A file deleted from disk while the Files app lists it opens as an empty editor, with no word that it is gone

- **Charter:** Round 1 - explore the Files app and the board's pages in a real browser as a person whose files change under the page
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > Open Files In Files App. No scenario covers a file that goes while the page lists it.
- **Module and class:** `harness/files_app/app/files/files-page.ts` (`open`) and `files-page-view.tsx` (the open file's view); `space/session/file_manager.py` `FileText` ("no text for a file that is not there") and `Session.read_file` ("no text when the file is gone") answer an empty text with no sign the file is missing, so the page cannot tell a gone file from an empty one.
- **Severity:** misleading message (a person reads a deleted file as an empty one; the editor is live, so the next step is a save that brings the file back empty)

## Steps

Sandbox: git repository `C:\dev\_et\pixel\work\repo`, branch `pixel-files`, session `pixel-files`, with `src/order.py` (6 lines) and `src/cart.py` committed. Files server on 8902 over a cdd server of its own (`C:\dev\_et\pixel\work\scripts\stack.py`); script `C:\dev\_et\pixel\work\scripts\t2.py`.

1. Open `http://127.0.0.1:8902/?files=pixel-files&fidelity=stories-story-map,clean-engineering-code,stories-acceptance-tests&project=C:\dev\_et\pixel\work\repo`.
2. Press **All session files** and turn the code format filter off, so `src/order.py` and `src/cart.py` are listed.
3. On disk, move `src/order.py` out of the repository (or delete it).
4. Press `order.py` in the list.

The same happens for a renamed file: rename `src/cart.py` to `src/basket.py` and press `cart.py`.

## Expected

The page says the file is gone. `files-page-view.tsx` line 22 promises it for the list: "a file it cannot open says why, not generated yet or deleted on this branch", and a listed file that does not exist is drawn disabled with its reason.

## Actual

The file opens as `src/order.py` with one empty line in a live editor, exactly as an empty file opens. No request fails (no response of 400 or above), the console is silent, and the list keeps the entry enabled with no note. Screenshot: `C:\dev\_et\pixel\work\shots\t2-deleted-open.png`. Putting the file back and pressing it again shows its text, so nothing was cached.

Pressing **This session** and **All session files** again after the rename does not list the files again: `cart.py` stays, `basket.py` never appears, until the page is reloaded.

## Tier that should catch it

e2e (`open-files-in-files-app.story.ui_e2e_spec.py`): only a real page over a real folder has a file that goes between the list and the press. The unit specs stub the session's answers and never answer a read for a file that is gone; the domain tier asserts `read_file` answers no text, which is the very answer the page cannot tell from an empty file.

## Also seen by
