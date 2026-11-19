# render of a .whiteboard file with `source` left out reads it as markdown and answers with the worker's Python traceback

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/actions/render/render.py` `Render._render_files` (`Format(source)` with no source), `render_worker.py`, `harness/guidance/practice_formats.py` `parse`.
- **Severity:** misleading message

## Steps
Sandbox `repo`, session `main`, after story-map.md was rendered to whiteboard (`drv\c8.json`, `drv\c9.json`):

    render.render {"guidance": "stories-story-map", "format": "drawio", "paths": [".context/story-map.whiteboard"]}

With `"source": "whiteboard"` the same file renders (to markdown, tried).

## Expected
The file's format is read from its name (.whiteboard, .drawio, .py), or the call is refused in one sentence saying to name `source`. Render's description says "Omit source when content is already the current format", which a caller reads as "the file knows its format".

## Actual
`isError=True`, 1,815 characters:

    RenderFailed: the render's worker process exited with 1:
    Traceback (most recent call last):
      File "<frozen runpy>", line 198, in _run_module_as_main
      ...
      File "...\cdd_guidance\practices\stories\model\markdown\nodes.py", line 535, in parse
        raise MarkdownParseError("Not a valid Markdown story map: no recognised structure found")

The file and the missing `source` are not named. Beside it: an empty markdown file and a file of stray bytes are both taken as a story map with nothing in it and saved (widget-06), and `"source": "python"` on a markdown file is accepted and ignored, so what `source` is checked against is not steady.

## Tier that should catch it
Heavy (`render_worker_heavy_spec.py`): no example sends a file whose format differs from the default with source left out.

## Also seen by
- Widget: the same with a drawing, `render.render {"guidance": "stories-story-map", "format": "markdown", "paths": [".context/story-map.drawio"]}` -> `MarkdownParseError: Not a valid Markdown story map: no recognised structure found` (one line, no traceback, still no word about `source`).

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). `render.render` to drawio of `.context/story-map.whiteboard` with no `source`: an error of 1,815 characters, `RenderFailed: the render's worker process exited with 1:` and a traceback ending `MarkdownParseError: Not a valid Markdown story map: no recognised structure found`; it does not name the file. With `source: "whiteboard"` the file renders to markdown. `source: "python"` on the markdown file is accepted and the drawing is saved.
- Cause, if you found it: `cdd_guidance/actions/render/render.py`: a path with no `source` is read as markdown whatever its extension, and the worker's failure is passed on as its traceback.
- Shares its cause with: widget-06 (what a source is taken to be is not checked against the file)
