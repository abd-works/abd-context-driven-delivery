# A link to another file in a rendered markdown page does nothing when pressed: no file opens, no callout, no word

**Charter:** Round 3 second pass, Pixel: display of each file, with a callout for each link to another file and practice (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / View File In Source View / "Render a markdown file as the page it describes". No scenario says what a link in a rendered page does. `harness/files_app/.context/module-context.md` (Rendered or source) says: "A link in a rendered page opens a web page in a tab of its own and leaves the Files app where it is for any other", so the dead link is written down as intended; charter check 3 asks for a callout for each link. Report it as a defect against the charter, or answer it as a question.

**Module and class:** `harness/files_app/app/files/file-view.tsx`, `keepPage` (prevents the press and opens only `http(s)` links). The other chat's Rendered / Source work, committed as aa23b0968.

**Severity:** wrong result. Markdown files open Rendered by default, so the page a person first reads a story map or a scenario file on shows every link underlined, as a link, and none can be followed: 28 of 28 links to other files in the sandbox's markdown.

**Steps**
1. Stack `C:\dev\_et\round3\pixel\drv\stack.py` (cdd 8911, Files 8912), sandbox `C:\dev\_et\round3\pixel\work`; open `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen>&project=C:\dev\_et\round3\pixel\work`, press All session files.
2. Press `story-map.md`. In the rendered page press the story link **Add Book To Cart** (`../story_tests/fill-cart/add-books/add_book_to_cart_story.test.md`).
3. Press `add_book_to_cart_story.test.md`. Press **story map** in "See the story map for where this story sits", then a domain term, **Book** (`../../../.context/domain-model.md#book-aggregate-root-entity`).
4. Press `domain-model.md`. Press **bounded-context-map.md**.
(Script: `C:\dev\_et\round3\pixel\drv\p2.py`, part b.)

**Expected:** the story's scenario file opens (or opens beside the map); a domain term opens the domain model at Book, or shows its section in place as the source view's callout does; at the least a hint saying where the link points and that Source follows it.

**Actual:** nothing: the open file stays, the address stays, no toast, no tooltip on the link (its `title` is empty), no callout mark. Screenshots `C:\dev\_et\round3\pixel\shots\p2-link-hover-.context_story-map.md.png`, `p2-link-hover-story_tests_fill-cart_add-books_add_book_to_cart_story.test.md.png`. Counts, shown of expected callouts in the rendered page: story-map.md 0 of 2, add_book_to_cart 0 of 14, change_cart_line_quantity 0 of 8, bounded-context-map.md 0 of 2, domain-model.md 0 of 2.

**Tier that should catch it:** e2e (`review-files-in-files-app.story.ui_e2e_spec.py`): the rendered examples check a heading and the toggle, none presses a link.
