# rivet-05 - Rendering the story canvas for a project with no UX folder stops with a raw FileNotFoundError on ux.json

- **Title:** `ProjectStoryCanvas.render` (and so the UX practice's `render_story_canvas`) crashes with `FileNotFoundError: ...\ux\ux.json` when the project has no UX folder, while the same project with an empty `{}` ux.json renders the story map fine.
- **Charter:** 6. **Tester:** Rivet
- **Story:** no scenario covers this. The module has a named error for the Stories side (`StoryMapNotFound`) but none for the UX map.
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/project_story_canvas.py`, `ProjectStoryCanvas._ux_document` (reads `<ux root>/ux.json` unguarded); also a non-JSON (empty) ux.json gives a bare `JSONDecodeError` with no file name.
- **Severity:** misleading message (severity `question` on whether a project with no UX map should get the story map alone, as `{}` already does).

## Steps

1. `python C:\dev\_et\after-1-2-1\rivet\scripts\make_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern-noux`, then delete `work/lern-noux/ux`.
2. With `PYTHONUTF8=1` and the sandbox `CDD_HOME`: `python C:\dev\_et\after-1-2-1\rivet\scripts\render_bare.py C:/dev/_et/after-1-2-1/rivet/work/lern-noux` (a plain `ProjectStoryCanvas(...).render()`, as `render_story_canvas` calls it).
3. Repeat with `ux/ux.json` holding `{}`, then holding nothing (0 bytes).

## Expected

A named error saying the UX root holds no `ux.json` and what to do (generate the UX map, or link stories to screens first), as `StoryMapNotFound` does for the story map; or the story map rendered without screens, as with `{}`.

## Actual

- No UX folder: `FileNotFoundError: [Errno 2] No such file or directory: 'C:\\dev\\_et\\after-1-2-1\\rivet\\work\\lern-noux\\ux\\ux.json'` (traceback from `pathlib.read_text`).
- `{}`: renders 45 stories with no screens; summary "0 value(s) the screens leave out ... Publish it as a new canvas", with no word that no story has a screen (`thumbnails-need-screenshots` asks to say so when publishing).
- Empty file: `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, naming no file.

## Tier that should catch it

Unit (`project_story_canvas_spec.py`): every example writes a ux.json first.

## Also seen by
