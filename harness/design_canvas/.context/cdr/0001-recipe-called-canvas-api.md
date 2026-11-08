# CanvasVersions, FixtureScreen, and ScenarioSource are the API the Claude Design recipe calls

`CanvasVersions` (`versions.py`), `FixtureScreen`, and `ScenarioSource` (`fixture_bar.py`) are called by the agent while it follows the UX practice's Claude Design recipe, `cdd_guidance/practices/ux/model/claude_design/story_canvas.md`. No Python in the repository calls them. Round 6 (R6-L3, round 5's L5) flagged them as reached only through that recipe and asked to call them from the Claude Design render or to move the rule into code.

## Decision

Keep them, as the recipe's API, and keep the rule that uses them in the recipe.

- **The recipe is their caller.** The recipe's steps tell the agent to render into `CanvasVersions.working()`, to write screens into `CanvasVersions.unpublished()`, to release a version with `CanvasVersions.release(N, name)`, and to build each prototype screen as a `FixtureScreen` with its `ScenarioSource`. A markdown recipe is one of the ways the repository uses code, alongside imports and registrations, so these classes are in use.
- **The render cannot decide versions on its own.** `ClaudeDesignStoryModel.render` returns the canvas's files; which version they go into depends on whether the latest version is already published, which only the person and the published canvas's link (`versions.json`) know. The agent asks the person before overwriting a published version (`never-overwrite-a-published-canvas`), so the choice stays a recipe step rather than a silent rule inside the render.
- **Prototype screens are written by the agent.** Each screen is a real product screen ported by the agent, so `FixtureScreen` is the helper the agent builds it with, not something a generator can call for it.

## Consequences

Renaming or reshaping any of the three classes means updating `story_canvas.md` in the same change, as with any other caller. If the render later takes over choosing the version (for example by reading `versions.json` and refusing a published one), it should call `CanvasVersions` and the recipe step should go.
