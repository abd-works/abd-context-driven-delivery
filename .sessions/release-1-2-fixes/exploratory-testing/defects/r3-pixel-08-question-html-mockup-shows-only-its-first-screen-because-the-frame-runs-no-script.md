# Question: a UX mockup's HTML page shows only its first screen in the Files app, its Site Map Explorer empty and its buttons dead, because the frame runs no script

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / "Render each format the page can draw" (`notes/page.html`: "the page in a frame that runs no script"). The UX mockup fidelity writes "runnable greybox - typed controls and key interactions". The two promises meet on `bookshop/buy-a-book.html`.

**Module and class:** `harness/files_app/app/files/file-view.tsx`, `RenderedFileView` (`<iframe sandbox="" srcDoc>`); the other chat's Rendered / Source work, committed as aa23b0968.

**Severity:** question. Is the Files app meant to show a mockup a person can walk, or only its still first screen? If still, the page could say the mockup's scripts are off and where to open it running.

**Steps**
1. Stack `C:\dev\_et\round3\pixel\drv\stack.py` (cdd 8911, Files 8912) on the sandbox `C:\dev\_et\round3\pixel\work`; page `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen fidelities>&project=C:\dev\_et\round3\pixel\work`, All session files pressed.
2. Press `buy-a-book.html`.

**Expected (if a mockup is to be reviewed here):** its six screens reachable, Play next and the zoom buttons working; or a note saying its scripts are off.

**Actual:** (`C:\dev\_et\round3\pixel\shots\w31-bookshop_buy-a-book.html.png`) the Book List screen only; the other five screens stay `hidden`; "Site Map Explorer" is an empty box; Reset, Play next, - and + do nothing; no note. The browser console holds errors for the page's own scripts (`bookshop/domain/cart.js`, `/practices/ux/story-demo/mount-generated-mockup.js`), asked of the Files server at 8912, which does not serve them, so they would not load without the sandbox either.

**Tier that should catch it:** e2e, a generated mockup opened in the Files app.
