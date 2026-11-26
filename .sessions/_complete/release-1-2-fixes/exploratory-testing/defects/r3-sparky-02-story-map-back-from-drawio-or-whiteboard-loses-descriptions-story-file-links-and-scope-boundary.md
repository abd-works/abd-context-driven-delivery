# A story map rendered to drawio or whiteboard and back loses the descriptions under its epics and stories, the links from stories to their scenarios files, and the Scope boundary section

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a story map's trip through its formats.
- **Module and class:** the Stories adapters `cdd_guidance/practices/stories/model/drawio/nodes.py` and `model/whiteboard/nodes.py` (neither holds a node's description or a story's file link), and the save in `cdd_guidance/actions/render/rendered_file.py`.
- **Severity:** wrong result (what a person wrote is lost from their own file)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh b1.json`). `.context/story-map.md` (kept as `trip\orig\story-map.md`) holds a title, a Sources line, an opening sentence, 4 epics, 4 sub-epics, 16 stories, a sentence under epic Browse Books, under sub-epic Add Books and under story Submit Order, two stories linked to their scenarios files (`### (S) Customer --> [Add Book To Cart](../story_tests/fill-cart/add-books/add_book_to_cart_story.test.md)`), one `(S:system)` story, and a `## Scope boundary` section with In scope and Out of scope lines.

1. `render.render {"guidance": "stories-story-map", "format": "drawio", "paths": [".context/story-map.md"], "source": "markdown"}`
2. `render.render {"guidance": "stories-story-map", "format": "markdown", "paths": [".context/story-map.drawio"], "source": "drawio"}`
3. Compare `.context/story-map.md` with the copy kept before step 1. The same with `whiteboard` in place of `drawio`.

## Expected
Nothing a person wrote is changed by a trip nobody edited the drawing in. `story-map-links-to-markdown` asks for a Story to link to its own markdown file when one exists, so the trip must keep that link.

## Actual
The file that comes back (`trip\story-map.from-drawio.md`, and the same text in `trip\story-map.from-whiteboard.md`):

- kept: the front matter, the title "Story Map — Bookshop", the Sources line, the opening sentence, every epic, sub-epic and story in order, the actors, and `(S:system)`. So widget-04's lost title is fixed on this build.
- lost: the three sentences under Browse Books, Add Books and Submit Order; both story links, which come back as plain `### (S) Customer --> Add Book To Cart`; the whole `## Scope boundary` section with its two lines and the rule above it; every blank line between headings.

The drawing never held them: `story-map.drawio` has no cell text "finds a Book", and the story cell for Add Book To Cart carries `link="story-map.md#s-customer----add-book-to-cart"`, the map entry, not the scenarios file the template says a story with a file links to.

Drawio to whiteboard and whiteboard to drawio keep the tree; the whiteboard written from the drawing differs from the one written from markdown only in numbers written `20.0` for `20`.

## Tier that should catch it
Unit (`drawio_round_trip_spec.py`, `markdown_story_map_round_trip_spec.py`): no example carries a node description, a story's file link or a Scope boundary through a drawing and back onto the markdown it came from.
