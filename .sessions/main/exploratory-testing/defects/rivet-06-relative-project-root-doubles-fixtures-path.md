# rivet-06 - A relative project root makes the LERN fixtures build look for its script at a doubled path

- **Title:** `ProjectStoryCanvas` with a relative `project_root` (such as `work/lern`) stops with *FixturesNotBuilt* because node is started in the workspace with the build script's path relative to the old directory: `Cannot find module '...\work\lern\work\lern\.temp\canvas-fixtures\build-canvas-fixtures.mjs'`.
- **Charter:** 6. **Tester:** Rivet
- **Story:** no scenario covers this. The mockup template (`cdd_guidance/practices/ux/templates/claude_design/mockup.py`) writes `project_root = Path("{{project root}}")`, which invites a relative path.
- **Module and class:** `cdd_guidance/patterns/lern_domain_driven/practices/stories/model/claude_design/fixtures.py`, `LernCanvasFixtures.build` (`subprocess.run(["node", str(script), str(entry), str(out)], cwd=self.workspace)` with `script` and `entry` relative to the caller's directory).
- **Severity:** misleading message (the error blames the fixtures bundle; the real cause is the relative root). Low: an absolute root works.

## Steps

1. Build the project: `python C:\dev\_et\after-1-2-1\rivet\scripts\make_lern.py C:\dev\_et\after-1-2-1\rivet\work\lern`.
2. From `C:\dev\_et\after-1-2-1\rivet`, with `PYTHONUTF8=1`: `python scripts\render_lern.py work/lern` (`ProjectStoryCanvas(project_root=Path("work/lern"), ..., fixtures=LernDomainDriven().canvas_fixtures(Path("work/lern")))`).

## Expected

The canvas renders as it does with `C:/dev/_et/after-1-2-1/rivet/work/lern` (46 files), or the root is refused up front as not absolute.

## Actual

```
FixturesNotBuilt: The canvas fixtures bundle (work\lern\ux\design-canvas\version-1\project\fixtures\canvas-fixtures.js) could not be built, so the story canvas is not rendered:
CalledProcessError: ... Error: Cannot find module 'C:\dev\_et\after-1-2-1\rivet\work\lern\work\lern\.temp\canvas-fixtures\build-canvas-fixtures.mjs'
```

An empty `version-1/project/fixtures/` folder is left behind.

## Tier that should catch it

Unit (`fixtures_spec.py`) or the heavy `project_story_canvas_heavy_spec.py`: both pass absolute temp folders only.

## Also seen by
