# Rendered scenarios show the underline marks of domain terms and examples as plus signs: "++Book++ ++Tiny Tales++"

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / "Render a markdown file as the page it describes" ("scenarios, story maps and domain models are read as pages"). The scenario files in the sandbox, and this repository's own under `story_tests/`, mark a domain term and an example with `++...++`.

**Module and class:** `harness/files_app/app/files/file-rendering.ts`, `renderingOf` (the other chat's Rendered / Source work, committed as aa23b0968).

**Severity:** cosmetic.

**Steps**
1. Stack `C:\dev\_et\round3\pixel\drv\stack.py` (cdd 8911, Files 8912) on the sandbox `C:\dev\_et\round3\pixel\work`; page `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen fidelities>&project=C:\dev\_et\round3\pixel\work`, All session files pressed.
2. Press `add_book_to_cart_story.test.md`.

**Expected:** Book and Tiny Tales underlined, as the marks mean.

**Actual:** (`C:\dev\_et\round3\pixel\shots\w05-story_tests_fill-cart_add-books_add_book_to_cart_story.test.md.png`) "Given the Bookshop sells ++Book++ ++Tiny Tales++", "++Cart Line++ - one Book in the Cart with its quantity": the plus signs are printed around every term and example. Tables, headings, the fenced call graph and the italic Given / When / Then render well.

**Tier that should catch it:** unit, `files/file-rendering.spec.ts`, with a scenario step as an example.
