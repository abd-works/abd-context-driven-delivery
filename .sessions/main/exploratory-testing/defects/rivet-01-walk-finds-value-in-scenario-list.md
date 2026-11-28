# rivet-01 - The screen walk counts a step's value as shown when it appears only in the fixture bar's scenario list

- **Title:** The walk reports a quoted step value as "Found" on a screen that never draws it, because the value is part of a scenario's name in the fixture bar's scenario list.
- **Charter:** 6 - story canvas and story explorer, on a real project. **Tester:** Rivet
- **Story:** no scenario covers this directly; it breaks the rule `walk-before-publish` in `cdd_guidance/practices/ux/model/claude_design/story_canvas.md` ("reports for each step the values it names ... that the screen shows or leaves out"; `publish_at` refuses while a value is missing).
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/screen_walk.py`, `_checked` / `ShownText`, over the text `screen_render.cjs` returns, which includes the fixture bar (`fixture_screen.py`) and its `<option>` list of scenario names.
- **Severity:** wrong result - the publish gate passes a screen that leaves a value out.

## Steps

1. `python C:\dev\_et\after-1-2-1\rivet\scripts\make_lern.py C:\dev\_et\after-1-2-1\rivet\work\lern` (a LERN project; Story 02 has no `*.story.shared.ts`, so no fixture data; its scenario is named `Customer orders the Plan01 plan` and its steps quote `"Plan01"`).
2. With `PYTHONUTF8=1`, `CDD_HOME` set to the sandbox: `python C:\dev\_et\after-1-2-1\rivet\scripts\render_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern` (ProjectStoryCanvas with one WrittenMarkup screen per story, body `<h1>story</h1><p>Plan {{ order.plan }}</p>`).
3. Read `work\lern\ux\design-canvas\version-1\walk.md`, Story Number 02 lines.
4. Render the screen yourself: pipe `{"jobs":[{"artboard":"<abs>/screens/story-number-02.dc.html","props":{"story":"Story Number 02","scenario":"Customer orders the Plan01 plan","step":"x","stepIndex":1,"stepKind":"then"}}]}` into `node cdd_guidance/practices/ux/model/claude_design/screen_render.cjs`.

## Expected

The screen draws `Plan` with no plan (no fixture loaded: `Story registry: unknown story "Story Number 02"`), so every step of both Story 02 scenarios should list `"Plan01"` as Missing, and `publish_at` should refuse.

## Actual

walk.md:

```
| Story Number 02 › Customer orders the Plan01 plan | story-number-02 | Then the order holds the "Plan01" plan | "Plan01" |  |
| Story Number 02 › Customer views without a screen | story-number-02 | Then the catalog shows the "Plan01" plan |  | "Plan01" |
```

The rendered text is `Back to the story map\n← Story map\nScenario\nLoad a scenario…\nCustomer orders the Plan01 plan\nStory Number 02\nPlan` - the only `Plan01` is the scenario's own name in the bar's list. The second scenario, whose name holds no value, is correctly reported missing. Any scenario named after the value it quotes (common: `Customer orders the Ace plan`) passes the walk whatever the screen draws; in Story 05 the list holds both scenario names, so both pass on the list alone.

## Tier that should catch it

Unit (`screen_walk_spec.py`): a walk over a screen whose markup omits the value but whose scenario name contains it. The specs use scenario names that do not repeat the quoted value, or screens that draw it, so the leak through the bar never shows.

## Also seen by
