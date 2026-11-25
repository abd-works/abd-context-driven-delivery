"""Build the story canvas of {{Product}}: one prototype screen per story, drawn from each scenario's fixture through the
real domain, then the story map and the story explorer, into the working version of the UX root's design canvas.

Write the screen's markup from scratch, or take it from a page of an existing app the project can reach; porting
another Claude Design canvas is an option. Keep the product's stylesheets and components; never use a
screenshot as a screen. Every value the screen shows comes from the fixture through the domain objects; a screen keeps
only its position per step group (the page, an open sheet or dialog).

Run from the CDD checkout: PYTHONPATH=".;cdd_guidance;cdd_guidance/practices" python <this file>
"""
import json
from pathlib import Path

from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap
from cdd_guidance.practices.ux.model.claude_design.screen_walk import StoryCanvasWalk
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen, WrittenMarkup
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from harness.design_canvas.versions import CanvasVersions

project_root = Path("{{project root}}")
ux_root = project_root / "{{ux root}}"
version = CanvasVersions.in_practice_root(ux_root).working()
screens = version.folder / "project" / "screens"
screens.mkdir(parents=True, exist_ok=True)

story_map = MarkdownStoryMap().read_file(project_root / "{{story map file}}", project_root)
stories = [story.name for story in story_map.descendants.stories()]

# The scenarios' fixtures, run through the real domain. When this fails, say what failed and stop: never write states by
# hand into the screens in its place.
LernCanvasFixtures(project_root).build(stories, version.folder / "project" / "fixtures" / "canvas-fixtures.js")

# One screen for each story. The bar has already run the scenario's Whens up to the step group on show; the markup
# reads the domain objects the steps bound under the named input ({{ order.… }}) and keeps only its position per step
# group. The markup is written from scratch here; AppPageMarkup takes a page of an existing app instead, and
# PortedCanvasMarkup draws another Claude Design canvas's component.
screen = StoryScreen(
    title="{{Screen title}}",
    story="{{Story}}",
    markup=WrittenMarkup(
        head='<link rel="stylesheet" href="../styles/{{product stylesheet}}.css">',
        body="""<main>
<h1>{{ order.name }}</h1>
<sc-for list="{{ order.lines }}" as="line"><p>{{ line.name }} {{ line.price }}</p></sc-for>
<sc-if value="{{ position.page === 'review' }}"><button>{{Action label}}</button></sc-if>
</main>""",
    ),
    domain_input="order",
    # One position per step group the explorer lists for each scenario; an outline's rows take the outline's.
    positions={"{{first scenario}}": [{"page": "{{page before the action}}"}, {"page": "{{page after it}}"}]},
    root_class="{{screen root class}}",
    path="{{screen path}}",
    artboard="/screens/{{screen slug}}.dc.html",
)
(screens / "{{screen slug}}.dc.html").write_text(screen.html, encoding="utf-8")

# The UX map names each screen's prototype artboard and its shownOn edges; the canvas draws the story map and the
# explorer from it and the story map.
ux_map = JsonUxMap().parse((ux_root / "ux.json").read_text(encoding="utf-8"))
# sources: each story's and scenario's path:line in its scenario file, which the explorer copies as an open request.
setup = StoryCanvasSetup(workspace=str(version.folder), ux_map=ux_map, sources={"{{Story}}": "{{scenario file}}:{{line}}"})
for path, text in json.loads(ClaudeDesignStoryMap(setup=setup).render(story_map)).items():
    (version.folder / path).parent.mkdir(parents=True, exist_ok=True)
    (version.folder / path).write_text(text, encoding="utf-8")

# Walk every screen at every step group before publishing, and fix each value a step names that a screen leaves out.
report = StoryCanvasWalk(version).walk(story_map)
report.write(version.folder / "walk.md")
