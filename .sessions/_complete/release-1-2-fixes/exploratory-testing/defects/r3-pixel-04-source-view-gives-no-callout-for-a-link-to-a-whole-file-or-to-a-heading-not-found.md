# The source view gives no callout for a link to a whole file, or to a heading it does not find, and says nothing about either: a story's link to its scenario file cannot be followed anywhere in the Files app

**Charter:** Round 3 second pass, Pixel: a callout for each link to another file and to another practice (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View; `harness/files_app/.context/module-context.md`, Callouts: "What opens in place under a line is a callout: a markdown link's section (`session.file` callouts)". No scenario covers a link without `#section`, or one whose section is not found.

**Module and class:** `space/session/session_file.py`, `callouts` and `_callouts_on` (the `callouts` of the `session.file` answer); the page only draws what it is given (`harness/files_app/app/files/source-of-file.ts` `calloutsOf`). Not in the other chat's Rendered / Source files.

**Severity:** wrong result (links a person cannot follow), with a misleading silence for the broken ones.

**Steps**
1. Stack and page as in r3-pixel-03. Press a markdown file, press Source. Callouts are the marks in the margin; `session.file`'s `callouts` in the answer holds the same (walk: `C:\dev\_et\round3\pixel\drv\walk.json`).
2. Compare the links in each file with its callouts.

**Expected:** each link to another file shows something to follow: a callout of the file's start for a link to a whole file, and for a link whose `#section` matches no heading a mark saying the section is not there.

**Actual:** 14 callouts for 28 links.

| File | Links | Callouts | Without one |
|---|---|---|---|
| `.context/story-map.md` | 2 | 0 | both story links to their scenario files, `[Add Book To Cart](../story_tests/fill-cart/add-books/add_book_to_cart_story.test.md)` (no `#section`) |
| `story_tests/fill-cart/add-books/add_book_to_cart_story.test.md` | 14 | 10 | `[story map](../../../.context/story-map.md#s-customer----add-book-to-cart)`: the heading is there, `### (S) Customer --> [Add Book To Cart](...)`, but holds a link; and 3 x `[Cart Line](...domain-model.md#cartline-entity)`, where the model's heading is `CartLine <<Value Object>>` (the file's own wrong anchor) |
| `story_tests/fill-cart/add-books/change_cart_line_quantity_story.test.md` | 8 | 4 | 4 x `#cartline-entity` |
| `.context/bounded-context-map.md` | 2 | 0 | `[story-map.md](story-map.md)`, `[domain-model.md](domain-model.md)` |
| `.context/domain-model.md` | 2 | 0 | `[bounded-context-map.md](bounded-context-map.md)`, `[story-map.md](story-map.md)` |

The callouts that do show open the right section in place (Book opens `.context/domain-model.md` lines 129 to 142; screenshot `C:\dev\_et\round3\pixel\shots\p2-scenario-callout-open.png`). The lines without one look like any other line: nothing tells a wrong anchor from a line with no link (`p2-scenario-source.png`, lines 11 and 17). With r3-pixel-03, the link from a story to its scenario file, the main link between the story map and the scenarios, can be followed nowhere in the Files app.

**Tier that should catch it:** unit, on the reader of link sections in `space/session`: examples of a link with no section, a section not found, and a heading that holds a link.

**Edge case, same failure:** a file made for it, `.context/edge/edge-links.md` in the sandbox, opened by `&file=.context/edge/edge-links.md`: `[gone](../gone-file.md#section)` (the file is not there) and `[no section](../domain-model.md#no-such-heading)` get no mark and no word in Source, exactly like a line with no link; `[Cart](../domain-model.md#cart-aggregate-root-entity)` gets its callout (`C:\dev\_et\round3\pixel\shots\p3-deep-.context_edge_edge-links.md-source.png`).
