# Rendering a story map's drawing back to markdown overwrites story-map.md with the template's placeholder title and boilerplate, losing the map's own title

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a trip from markdown to drawio and back.
- **Module and class:** `cdd_guidance/actions/render/render.py` `Render._render_files` and `rendered_file.py` `RenderedFile.save`; the Stories markdown format adapter under `cdd_guidance/practices/stories/model/`.
- **Severity:** wrong result (a person's file is rewritten with text they did not write)

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`drv\run.py`, `drv\c6.json`). `.context/story-map.md` starts as:

    # Story Map — Bookshop

    # (E) Sell Books

    ## (E) Take Orders

    ### (S) Customer --> Place Order
    ### (S) Customer --> Cancel Order

1. `render.render {"guidance": "stories-story-map", "format": "drawio", "paths": [".context/story-map.md"], "source": "markdown"}`
2. `render.render {"guidance": "stories-story-map", "format": "markdown", "paths": [".context/story-map.drawio"], "source": "drawio"}`
3. `git diff .context/story-map.md`

## Expected
The markdown that comes back names the same map: the title "Story Map — Bookshop" and the four nodes. Render's own description promises a markdown render is saved beside its source "keeping" what people gave; a trip through the drawing changes nothing a person wrote unless the drawing changed it.

## Actual
Step 2 answers `[{"format": "markdown", "path": "...\.context\story-map.md"}]` and the file is now:

    ---
    fidelity: [discovery]
    artifact: [story-map]
    format: md
    ---

    # Story Map — Product / Feature Name

    **Sources / context:** see engagement sketch

    ---

    # (E) Sell Books
    ## (E) Take Orders
    ### (S) Customer --> Place Order
    ### (S) Customer --> Cancel Order

    ---

    ## Scope boundary

    **In scope:** see sketch increments and detailed themes
    **Out of scope:** themes not yet moved to specification

The title "Bookshop" is gone, replaced by the template's placeholder "Product / Feature Name", and placeholder Sources and Scope sections were added. The nodes survive. Any Sources or Scope text a real map holds would be replaced the same way (not tried on a map that has them).

## Tier that should catch it
Heavy (`render_saves_beside_source_heavy_spec.py`): it renders markdown to drawio and whiteboard, never drawio back to markdown over an existing story-map.md. A unit example on the Stories markdown adapter comparing a map before and after the trip would also catch it.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). After markdown to drawio to markdown, `story-map.md` is the report's text word for word: front matter, `# Story Map — Product / Feature Name`, the placeholder Sources line and Scope boundary section, and the four nodes. Where the loss is: the drawing never held the title (the word `Bookshop` is not in `story-map.drawio`), so the adapter that reads the drawing has nothing to read and fills the template's placeholders; the title is then lost in the save, which writes the whole of that text over the person's file.
- Cause, if you found it: `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save` writes the rendered text over the file the fidelity names, whole, keeping nothing of the file already there; the Stories markdown writer fills what the drawing does not hold from the template.
- Shares its cause with: widget-05, widget-08 (the save writes over the person's markdown whole); widget-06 (the saved name comes from the fidelity)
