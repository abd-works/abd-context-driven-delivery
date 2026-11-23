# A story added to a sub-epic after its drawing exists comes back from the drawing under the next sub-epic

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a trip from markdown to drawio and back.
- **Module and class:** `cdd_guidance/actions/render/rendered_file.py` (the kept layout, `saved.previous`) with the Stories drawio adapter under `cdd_guidance/practices/stories/model/`: the kept sub-epic is not made wide enough for its new story, and the drawio reader places a story by where it sits.
- **Severity:** wrong result (the story map's tree changes with nobody moving anything)

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`drv\run.py`, `drv\c8.json`). No hand edit of the drawing.

1. `.context/story-map.md`: epic Sell Books, sub-epic Take Orders with stories `Customer --> Place Order` and `Customer --> Cancel Order`. No story-map.drawio.
2. `render.render {"guidance": "stories-story-map", "format": "drawio", "paths": [".context/story-map.md"], "source": "markdown"}`
3. Add to the markdown, under Take Orders, `### (S) Customer --> Track Order`, then a second sub-epic `## (E) Ship Orders` with `### (S) Clerk --> Pack Order` (`drv\grow.py`).
4. The same render call again (the drawing is there, so its layout is kept).
5. `render.render {"guidance": "stories-story-map", "format": "markdown", "paths": [".context/story-map.drawio"], "source": "drawio"}`

## Expected
The markdown that comes back has the tree it was drawn from: Track Order under Take Orders.

## Actual
After step 4 the cells sit at: Take Orders x=20, Place Order x=25, Cancel Order x=85, Track Order x=145, Ship Orders x=200, Pack Order x=205. After step 5 story-map.md reads:

    # (E) Sell Books
    ## (E) Take Orders
    ### (S) Customer --> Place Order
    ### (S) Customer --> Cancel Order
    ## (E) Ship Orders
    ### (S) Customer --> Track Order
    ### (S) Clerk --> Pack Order

Track Order moved to Ship Orders. In an earlier run where Place Order had been moved by hand to x=777, y=555 before step 4, the trip back also wrote it last as `### (S) --> Place Order`, its actor Customer lost.

## Tier that should catch it
Heavy (`render_saves_beside_source_heavy_spec.py`) or a unit example on the Stories drawio adapter: the specs keep a moved card's position but never read the kept drawing back into a tree after the map grew.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). After the second render the cells sit as the report says: Take Orders x=20, Place Order 25, Cancel Order 85, Track Order 145, Ship Orders 200, Pack Order 205. The markdown that comes back has `Customer --> Track Order` under `Ship Orders`. Where the loss is: in the adapter that reads the drawing. The drawing still says whose story it is: its actor cell's id is `sell-books/take-orders/track-order/actor`. But the second render kept Take Orders at its first width (x=20, width 110, so it ends at 130) and put the new story at x=145, outside it, and the reader goes by position, not by the id. The save then writes that tree over the person's file. The hand-moved card of the report's last sentence was not run.
- Cause, if you found it: The Stories drawio adapter under `cdd_guidance/practices/stories/model/`: its writer keeps a sub-epic's old width when a story is added, and its reader finds a story's sub-epic from where the cells sit.
- Shares its cause with: widget-04, widget-08 (the save over the markdown)
