# rivet-07 - Double braces in a story, scenario or step name are run as a template expression and vanish from the story map and Stories panels

- **Title:** Text written `{{...}}` in a story name (and in scenario and step text on the Stories panel) is HTML-escaped but not template-escaped, so the canvas's x-dc template evaluates it and the card shows the name with that part missing.
- **Charter:** 6. **Tester:** Rivet
- **Story:** no scenario covers this; it breaks `map-mirrors-drawio` (the card should read as the map names the story).
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/story_canvas.py` (story cards in `Main.dc.html`, `_context_panel` / `_context_story_lines` for `context/<screen>.dc.html`), via `harness/design_canvas/canvas.py` `Place.card`, which escape HTML only. The explorer is not affected: it carries names as JSON data.
- **Severity:** cosmetic (wrong text on the card; rare in practice, but scenarios about templates, such as `the page shows {{Product}}`, are plausible in this very repository's domain).

## Steps

1. `python C:\dev\_et\after-1-2-1\rivet\scripts\make_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern-odd`, then rename Story Number 06 to `Pay & "Ship" <Fast> {{x}}` in `tests/.context/story-map.md`, its scenario file, its shared story and `ux/ux.json`.
2. `python scripts\render_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern-odd`.
3. Render the map and the panel with the repository's own artboard renderer: `{"jobs":[{"artboard":"<project>/Main.dc.html","props":{}},{"artboard":"<project>/context/story-number-06.dc.html","props":{}}]}` into `node cdd_guidance/practices/ux/model/claude_design/screen_render.cjs`.

## Expected

The card and the panel read `Pay & "Ship" <Fast> {{x}}`.

## Actual

Both read `Pay & "Ship" <Fast>`; the file holds `<span>Pay &amp; &quot;Ship&quot; &lt;Fast&gt; {{x}}</span>` inside the `<x-dc>` template. `&`, quotes and `<` are escaped correctly; a `›` inside a scenario name (`Customer's order › with arrow`) also survives and plays in the explorer.

## Tier that should catch it

Unit (`story_canvas_spec.py`): names in the specs hold no braces.

## Also seen by
