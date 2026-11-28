# rivet-03 - A screen the UX map links to a scenario (not a story) gets no Stories panel beside it

- **Title:** A prototype screen whose UX-map screen names only `scenario_names` (or `step_names`) is placed on the Screens page with no read-only Stories board beside it.
- **Charter:** 6. **Tester:** Rivet
- **Story:** breaks the rule `story-panel-beside-the-screen` in `cdd_guidance/practices/ux/model/claude_design/story_canvas.md` ("Each screen's page also holds a separate, read-only Stories board to the right of the screen"). No story test scenario covers it.
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/story_canvas.py`, `ClaudeDesignStoryMap._stories_shown_on` (reads only `screen.story_links`) and `_add_context_panel` (returns when that is empty).
- **Severity:** wrong result (the screen's board shows no place in the story map; cosmetic for the reader, but the rule is broken silently).

## Steps

1. Build `work/lern` with `C:\dev\_et\after-1-2-1\rivet\scripts\make_lern.py`, then edit `work/lern/ux/ux.json` so screen `story-number-04` has `"story_names": []` and `"scenario_names": ["Story Number 04 › Customer orders the Plan03 plan"]`.
2. `python C:\dev\_et\after-1-2-1\rivet\scripts\render_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern`
3. List `work/lern/ux/design-canvas/version-1/project/context/` and the boards of `canvas.json`.

## Expected

`context/story-number-04.dc.html`, placed beside `screens/story-number-04.dc.html`, with Story Number 04 opened to the scenario the screen shows.

## Actual

`context/` holds a panel for every other screen (01, 02, 05 ... 45) but none for 04; `canvas.json` has 44 screen boards and 43 "Stories" boards. The explorer still plays Story 04's first scenario on that screen, so the screen does serve the story.

The same screen also gets no thumbnail under Story Number 04 on the story map (`Main.dc.html` links thumbnails for 01, 02, 05 ... but none for 04; opened through Playwright, the card has an empty space where the others read "No screenshot"), so the explorer cannot be reached from that story's card (`one-thumbnail-per-story`, `only-thumbnails-link`).

## Tier that should catch it

Unit (`story_canvas_spec.py`): every spec screen links its story through `show_story`; none links a scenario or step alone.

## Also seen by
