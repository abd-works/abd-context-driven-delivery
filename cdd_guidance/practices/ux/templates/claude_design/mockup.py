"""Build the story canvas of {{Product}}: one prototype screen per story, drawn from each scenario's fixture through the
real domain, then the story map and the story explorer, into the working version of the UX root's design canvas.

Write the screen's markup from scratch, or take it from a page of an existing app the project can reach; porting
another Claude Design canvas is an option. Keep the product's stylesheets and components; never use a
screenshot as a screen. Every value the screen shows comes from the fixture through the domain objects; a screen keeps
only its position per step group (the page, an open sheet or dialog).

Run from the CDD checkout: PYTHONPATH=".;cdd_guidance;cdd_guidance/practices" python <this file>. Without screens to
add, the UX practice's render_story_canvas operation does the same render with the session's roots.
"""
from pathlib import Path

from cdd_guidance.patterns.lern_domain_driven.lern_domain_driven import LernDomainDriven
from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import ProjectStoryCanvas
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen, WrittenMarkup

project_root = Path("{{project root}}")

# One screen for each story. The fixture bar has already run the scenario's Whens up to the step group on show; the
# markup reads the domain objects the steps bound under the named input ({{ order.… }}) and keeps only its position per
# step group. The markup is written from scratch here; AppPageMarkup takes a page of an existing app instead, and
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
    # One position per step group the explorer lists for each scenario; an outline's example takes the outline's.
    positions={"{{first scenario}}": [{"page": "{{page before the action}}"}, {"page": "{{page after it}}"}]},
    root_class="{{screen root class}}",
    path="{{screen path}}",
    artboard="/screens/{{screen slug}}.dc.html",
)

# One call: the story map below the Stories root and ux.json in the UX root, the scenarios' fixtures run through the real
# domain (it stops with FixturesNotBuilt, rendering nothing, when they cannot be built: say what failed and stop, never
# write states by hand into the screens in its place), each screen written and named on the UX map, the story map and
# the explorer rendered into the working version, and the walk of every screen at every step group written to walk.md.
canvas = ProjectStoryCanvas(
    project_root=project_root,
    ux_root=project_root / "{{ux root}}",
    stories_root=project_root / "{{stories root}}",
    fixtures=LernDomainDriven().canvas_fixtures(project_root),
)
rendered = canvas.render({"{{screen slug}}": screen})
# Fix each value a step names that a screen leaves out (rendered.walk.misses), and render again until nothing is
# missing but what the person accepts.
print(rendered.summary("{{Product}} Story Map"))
