# Rendering another markdown file of the folder to drawio (an empty one, a broken one) replaces story-map.drawio, so the story map's drawing and the layout a person gave it are gone

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this. Render's description: the render "is saved beside the first path, under the name the fidelity writes that format to, keeping the layout people gave a drawing already there".
- **Module and class:** `cdd_guidance/actions/render/rendered_file.py`, `RenderedFile.from_sources` / `save`.
- **Severity:** wrong result (a drawing a person laid out is overwritten with an empty one, and the call reports success)

## Steps
Sandbox `repo`, session `main` (`drv\c7.json`). `.context` holds story-map.md, an empty file empty.md, and story-map.drawio rendered from story-map.md with one card moved by hand (11 cells).

    render.render {"guidance": "stories-story-map", "format": "drawio", "paths": [".context/empty.md"], "source": "markdown"}

## Expected
Either the render of empty.md is saved under a name of its own (empty.drawio) or it is refused because empty.md is not the story map and holds no story map; story-map.drawio is left as it was.

## Actual
`[{"format": "drawio", "path": "...\.context\story-map.drawio"}]`, `isError=False`. story-map.drawio is now 218 characters with no cell; "Place Order" and the hand-given position are gone. The same happens with `.context/broken.md` (bytes that are no story map). The saved name comes from the fidelity, not from the file rendered, so any markdown file in a folder that also holds the story map's drawing overwrites it.

## Tier that should catch it
Unit (`render_spec.py`): every example renders the file named story-map.md; none renders a second markdown file beside an existing drawing.
