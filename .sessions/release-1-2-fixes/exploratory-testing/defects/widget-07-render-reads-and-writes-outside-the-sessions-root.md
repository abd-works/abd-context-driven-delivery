# render takes a path outside the session's root and writes its drawing outside the project, where validate refuses the same path

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this. Validate's description promises "A path that is not there, or not under the session's root, is refused"; render's says nothing either way.
- **Module and class:** `cdd_guidance/actions/render/render.py`, `Render._render_files` (`self.files.path_named`), `rendered_file.py` `RenderedFile.save`.
- **Severity:** wrong result (a file written outside the project the session works on); question whether render is meant to be bounded as validate is

## Steps
Sandbox project `C:\dev\_et\widget\work\repo`, session `main`. A story map copied to `C:\dev\_et\widget\work\outside.md`, one folder above the project (`drv\c7.json`, `drv\c8.json`).

    render.render {"guidance": "stories-story-map", "format": "drawio", "paths": ["../outside.md"], "source": "markdown"}
    validate.validate {"guidance": "stories-story-map", "paths": ["../outside.md"]}

## Expected
Both actions treat the path alike: refused by name as outside the session's root.

## Actual
validate: `NamedPathNotFoundError: nothing under the session's root C:\dev\_et\widget\work\repo at ../outside.md ...` (refused, good).
render: the first call answered "render.render is still running after 10 seconds; it was not started again. Call render.render again ..."; afterwards `C:\dev\_et\widget\work\story-map.drawio` exists, outside the project. Renders of files inside the project answered in under a second, so the long first call is unexplained.

## Tier that should catch it
Heavy (`render_saves_beside_source_heavy_spec.py`): no example names a path outside the project.
