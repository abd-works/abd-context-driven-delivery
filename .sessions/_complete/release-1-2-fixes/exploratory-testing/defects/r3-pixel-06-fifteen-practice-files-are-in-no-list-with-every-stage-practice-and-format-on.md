# Fifteen of the project's 102 practice files are in no list of the Files app with every stage, practice and format on, while their siblings are

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed (check 3: open each file "from the practice and fidelity lists and from the file tree").
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / Filter Files In Files App / List This Session Or All Session Files / "List all session files, then this session's" (the button's own words: "All session files: every file of the stages, practices and formats selected, older work included").

**Module and class:** the listing the page asks the cdd server for (`space/session`, each fidelity's declared outputs; the page draws it in `harness/files_app/app/files/files-page-view.tsx`). Not in the other chat's Rendered / Source files. Possibly the listing side of r3-gizmo-05 and r3-cog-03.

**Severity:** wrong result: a person reviewing the work never sees these files unless they know the path and add `&file=<path>` to the address, which does open each of them.

**Steps**
1. Stack `C:\dev\_et\round3\pixel\drv\stack.py` (cdd 8911, Files 8912) on the sandbox `C:\dev\_et\round3\pixel\work`; page `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen fidelities>&project=C:\dev\_et\round3\pixel\work`, session `main`, nothing chosen beforehand. Press All session files. List and Folders both show 88 entries (87 files and `thin-slice.drawio`, "not generated yet").
2. Compare with `git ls-files` in the sandbox (102 files). (Script `C:\dev\_et\round3\pixel\drv\a3.py`.)

**Expected:** each file a fidelity wrote is listed under its fidelity.

**Actual:** not listed:
- DDD bounded_context: `catalogue/.context/bounded-context.md`, `fulfilment/.context/bounded-context.md`, `ordering/.context/bounded-context.md` (the root `bounded-context-map.md` is listed)
- UX: `bookshop/buy-a-book.drawio` (the mockup's drawing; `buy-a-book.html` is listed), `bookshop/ux-map.json`, `ux/ux.json` (so no JSON file of the project is in the list)
- Stories acceptance tests: `story_tests/browse-books/search-books/search_books_story.test.ts`, `story_tests/fulfil-order/pack-order/pack_order_story.test.py`, `story_tests/fulfil-order/fulfil-order.story.domain.spec.py`, `fulfil-order.story.server.spec.py`, `fulfil-order.story.shared.py`, `story_tests/fulfil-order/examples/order_examples.py`, `story_tests/check-out/confirm-order/examples/order.examples.ts`, `story_tests/story_test.py`, `story_tests/story-test.ts`

Listed beside them: `story_tests/check-out/place-order/submit-order/submit_order_story.test.py`, `story_tests/check-out/confirm-order/confirm-order.story.domain.spec.ts`, `story_tests/shared_stories.py`. A story test in Python or TypeScript two folders deep (`<epic>/<story>/`) is left out, one three folders deep is listed, and a markdown one two folders deep is listed.

Screenshots: `C:\dev\_et\round3\pixel\shots\a3-list.png`, `a2-all-folders.png`; the same files opened by address: `p3-deep-*.png`.

**Tier that should catch it:** heavy, a listing of a project holding every fidelity's files against the files on disk.
