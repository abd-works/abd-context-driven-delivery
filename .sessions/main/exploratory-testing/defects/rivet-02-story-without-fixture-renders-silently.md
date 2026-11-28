# rivet-02 - A story with no example data renders an empty screen, and the render never says the story has no fixture

- **Title:** When a story has no shared story (no example data), the fixtures bundle builds without it and the canvas renders its screen empty; the render summary and walk.md never name the missing fixture, only symptoms.
- **Charter:** 6. **Tester:** Rivet
- **Story:** no scenario covers this. Nearest promise: `stop-when-fixtures-fail` in `cdd_guidance/practices/ux/model/claude_design/story_canvas.md` ("Never fall back silently to states ... the reader cannot tell").
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/project_story_canvas.py`, `ProjectStoryCanvas._build_fixtures` / `RenderedStoryCanvas.summary`; the bundle side is `cdd_guidance/patterns/lern_domain_driven/practices/stories/model/claude_design/canvas-fixtures.ts` (`console.warn('Canvas fixtures: story ... not loaded')`).
- **Severity:** misleading message (severity `question` on whether the render should stop instead).

## Steps

1. Build `work/lern` as in rivet-01 (`scripts/make_lern.py`): Story Number 02 has its scenario file but no `*.story.shared.ts`.
2. `python C:\dev\_et\after-1-2-1\rivet\scripts\render_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern`

## Expected

The render names Story Number 02 as having no fixture ("no shared story found for Story Number 02; its screen draws no data"), or stops as for an unbuilt bundle, so the person knows the screen's emptiness comes from missing example data, not from the screen.

## Actual

```
Rendered 46 canvas files into ...\version-1.
Walk: ...walk.md (3 value(s) the screens leave out or action(s) that leave the screen as it was).
  - Story Number 02 › Customer views without a screen › "Plan01"
  - Story Number 02 › Customer orders the Plan01 plan › (screen stays as it was after): When ...
  - Story Number 02 › Customer views without a screen › (screen stays as it was after): When ...
```

The cause shows only on the screen renderer's stderr, which the walk discards: `Canvas fixtures: story "Story Number 02" not loaded Error: Story registry: unknown story "Story Number 02"`. A person reading the summary is pointed at fixing the screen. In the explorer, the screen's scenario list for that story holds no scenarios from the fixture.

## Tier that should catch it

Heavy (`project_story_canvas_heavy_spec.py`): its project has one story, always with a shared story, so a story map with a story the bundle cannot load is never rendered.

## Also seen by
