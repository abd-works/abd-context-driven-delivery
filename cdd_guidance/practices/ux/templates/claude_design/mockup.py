"""Build the story canvas of {{Product}}: one prototype screen per story, drawn from each scenario's fixture through the
real domain, then the story map and the story explorer, into the working version of the UX root's design canvas.

Write the screen's markup from scratch, or port it from the product's own app or prototype source when the project can
reach one (another Claude Design canvas is one such source). Keep the product's stylesheets and components; never use a
screenshot as a screen. Every value the screen shows comes from the fixture through the domain objects; a screen keeps
only its position per step group (the page, an open sheet or dialog).

Run from the CDD checkout: PYTHONPATH=".;cdd_guidance;cdd_guidance/practices" python <this file>
"""
import json
from pathlib import Path

from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap
from cdd_guidance.practices.ux.model.claude_design.fixture_screen import FixtureScreen, ScenarioSource
from cdd_guidance.practices.ux.model.claude_design.screen_walk import StoryCanvasWalk
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
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

# One screen for each story. fromFixture reads the repositories the Givens filled and what the steps bound by name, and
# returns the state the step group on show leaves; the bar has already run the scenario's Whens up to that group.
screen = FixtureScreen(
    title="{{Screen title}}",
    head='<link rel="stylesheet" href="../styles/{{product stylesheet}}.css">\n<script src="../fixtures/canvas-fixtures.js"></script>',
    root_class="{{screen root class}}",
    body="""<main>
<h1>{{ heading }}</h1>
<sc-for list="{{ items }}" as="item"><p>{{ item.name }} {{ item.price }}</p></sc-for>
<button onClick="{{ next }}">{{Action label}}</button>
</main>""",
    source=ScenarioSource(story="{{Story}}", scenario="{{first scenario}}", path="{{screen path}}"),
    own_methods="""fromFixture(repositories, scenario, examples, step, bindings) {
const order = repositories.{{orders}}.{{find the aggregate the Givens stored}};
return { heading: order.{{name}}, items: order.{{lines}} };
}
paste(field) {
return {};
}
next(event) {
if (this.props.go) this.props.go(this.storyName(), this.scenarioName(), 'Then');
}
""",
    vals="heading: st.heading || '',\nitems: st.items || [],\nnext: (event) => this.next(event)",
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
