# A story test in Python or TypeScript shows no callout for its domain-term links, its Map and Model links, or its steps, with Rules and Cross-file on

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed, with a callout for each link (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / Open Calls And Classes In Place; `harness/files_app/.context/module-context.md`, Callouts: "a markdown link's section (`session.file` callouts) ... and in a story test the functions, operations and examples each step invokes and observes, on the step's first line (`session.file` steps, read with Rules or Cross-file, from the session's graph)". No scenario covers a link inside a step's string in code.

**Module and class:** `space/session/session_file.py` (`callouts`, and the steps of the `session.file` answer). Not in the other chat's Rendered / Source files. The missing steps may be the display side of r3-sparky-08 and r3-cog-03 (story tests in code lose their invokes edges, or are left out of the load).

**Severity:** wrong result: the same scenario written in markdown shows its domain terms as callouts; written in Python or TypeScript it shows none.

**Steps**
1. Stack `C:\dev\_et\round3\pixel\drv\stack.py` (cdd 8911, Files 8912) on the sandbox `C:\dev\_et\round3\pixel\work`; page `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen fidelities>&project=C:\dev\_et\round3\pixel\work`, All session files pressed.
2. Press Rules, then Cross-file. Press `submit_order_story.test.py` (`story_tests/check-out/place-order/submit-order/`) and wait for the read; then `view_order_confirmation_story.test.ts`. (Scripts `C:\dev\_et\round3\pixel\drv\p4.py`, `p5.py`.)

**Expected:** a callout on each step that links a domain term, such as line 14 `given("the Customer has [Cart](../../../../.context/domain-model.md#cart-aggregate-root-entity) cart with Tiny Tales")`, opening the model's Cart section as the markdown scenario does; a callout for the header's `Map: ../../../../.context/story-map.md#s-customer----submit-order` and `Model:` lines; and the operations each step invokes (TypeScript line 27, `orders.load(...).confirmation()`).

**Actual:** `session.file` answers `"callouts": [], "steps": []` for both, asked with `rules: true, cross_file: true` (violations are answered: 6 and 4).
- The Python test shows no callout mark at all: 0 of 8 linked terms, 0 of 2 header links (`C:\dev\_et\round3\pixel\shots\p5-code-story_tests_check-out_place-order_submit-order_submit_order_story.test.py.png`).
- The TypeScript test shows 0 of 1 linked term and 0 of 2 header links. Once the Graph view has been read it gets four marks for an import and calls (lines 10, 23, 27), which the module card says a story test does not open ("A story test opens no call or class of its own"), and still no step (`p5-code-story_tests_check-out_confirm-order_view-order-confirmation_view_order_confirmation_story.test.ts.png`).
- The markdown scenario beside them, `add_book_to_cart_story.test.md`, answers 10 callouts and 6 steps.

**Tier that should catch it:** heavy, on `session.file` with a real graph of a project holding a story test in each language; the server spec's story test is markdown.
