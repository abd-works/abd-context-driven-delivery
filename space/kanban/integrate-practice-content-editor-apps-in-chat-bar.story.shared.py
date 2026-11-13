"""Integrate Practice Content Editor Apps In Chat Bar: the shared scenarios the Python tiers replay for the apps the
chat bar's status row lists and opens.

Scenarios: harness/.context/stories/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/
integrate_practice_content_editor_apps_in_chat_bar_story.test.md (Open Story UI Side Panel From Chat Bar, Open Knowledge
Graph Side Panel From Chat Bar, Open Kanban Side Panel From Chat Bar).
Model: harness/.context/editor-apps/.context/editor-apps-model.md#app.

The status row reads each app from the server health report and a press calls `app.open`, so a step reads the row from
`report()` and presses through `open_app(label)`, which the tier hands it. Left to other increments: the story map, the
graph's practice roots, and the outlined ticket the opened page shows, and the side panel itself, which is the chat
bar's TypeScript.

The file viewer's editor tile is the Python's decision: a Stories file's tab carries its practice's editor, the Story UI
app (`BoardPractice.editor`, which the chat bar reads from the board overview), and the editor opens the file through
`StoryModel.load`. The file viewer's design view link is the one the session's UX practice answers
(`PracticeSessionOutput.design_view`), which the chat bar reads from the active ticket's session. The Story UI editor follows the session open in the project through `StoryModel.open_in_session`.
Left to other increments: the story-map.drawio and chat bar scenarios rows of the editor tile outline, which need a
rendered diagram and a scenario file seeded beside the story map. So is "A board that does not come up says so instead of opening an
empty panel": the chat bar starts the server and says when nothing answers, so no Python tier replays it.
"""

from __future__ import annotations

from expects import be_a, be_none, contain, equal, expect

from cdd_guidance.practices.stories.model.story_model import StoryModel
from harness.design_canvas.versions import CanvasVersions
from harness.diagnostics.app import AppNotStarted, AppStatus
from space.kanban.board import BoardPractice
from space.kanban.board_app import STORY_UI_APP
from space.kanban.ticket import FidelityProgress
from space.kanban.editor_apps_examples import CDD_KANBAN, CHECKOUT_FLOW_DESIGN, GRAPH_APP, MISSING_DEPENDENCY, SERVE, STORY_UI_EDITOR, AppExample, ThrowawayApp, app_in
from space.kanban.knowledge_graph_examples import BILLING_REPORT, CHECKOUT_FLOW, STORIES, STORY_MAP, UX, files_read, roots_loaded
from space.kanban.story_test import SharedStories, refusal_of

shared_stories = SharedStories("Integrate Practice Content Editor Apps In Chat Bar")

OPEN_STORY_UI = "Open Story UI Side Panel From Chat Bar"
OPEN_GRAPH = "Open Knowledge Graph Side Panel From Chat Bar"
OPEN_KANBAN = "Open Kanban Side Panel From Chat Bar"
OPEN_DESIGN = "Invoke Claude Design Story Explorer From Chat Bar"
DEPLOY_STORY_UI = "Deploy Story UI App With Board State"

# Interaction: what a press does to an app of each status, as the app statuses table has it.
PRESS_DOES = {
    AppStatus.NOT_INSTALLED: "is installed, launched and opened in the side panel",
    AppStatus.DOWN: "is launched and opened in the side panel",
    AppStatus.RUNNING: "is opened in the side panel",
}


def press_readies_by_status(story: str, example: AppExample, name: str, status: AppStatus) -> None:
    """One row of a press-readies-by-status outline: the app reads status in the row, and a press opens it."""

    @shared_stories.scenario(story, f"{name}: {status.value}")
    def _(s):
        @s.given(f"the app status row reads {example.label} {status.value}")
        def _(world):
            world.app = ThrowawayApp(example)
            world.apps.append(world.app)
            world.app.seed(status)

        @s.when(f"the Person opens the {example.label} from the app status row")
        def _(world):
            world.opened = world.open_app(example.label)

        @s.then(f"the {example.label} {PRESS_DOES[status]}")
        def _(world):
            expect(world.app.app.status).to(equal(AppStatus.RUNNING))

        @s.and_(f"the side panel shows it at its url, on its page {example.page}")
        def _(world):
            expect(world.opened["url"]).to(equal(world.app.url))

        @s.and_(f"the app status row reads {example.label} running on its port")
        def _(world):
            row = app_in(world.report(), example.label)
            expect((row["status"], row["port"])).to(equal((AppStatus.RUNNING.value, world.app.port)))


for app_status in PRESS_DOES:
    press_readies_by_status(OPEN_STORY_UI, STORY_UI_EDITOR, "A press on the Story UI editor readies it by its status and opens it beside the chat", app_status)


@shared_stories.scenario(OPEN_STORY_UI, "An install that fails says what failed and how to fix it")
def _(s):
    @s.given("the app status row reads Story UI not installed")
    def _(world):
        world.app = ThrowawayApp(STORY_UI_EDITOR)
        world.apps.append(world.app)

    @s.but_("npm install fails in the Story UI editor's folder with npm's ENOENT")
    def _(world):
        world.app.write_code(MISSING_DEPENDENCY, SERVE)

    @s.when("the Person opens the Story UI editor from the app status row")
    def _(world):
        world.refusal = refusal_of(lambda: world.open_app(STORY_UI_EDITOR.label))

    @s.then("the side panel stays closed")
    def _(world):
        expect(world.refusal).to(be_a(AppNotStarted))

    @s.and_("the server health panel says the Story UI install failed, with npm's ENOENT")
    def _(world):
        expect(str(world.refusal)).to(contain("The Story UI install failed:", "ENOENT"))

    @s.and_("it says to run npm install in the Story UI editor's folder")
    def _(world):
        expect(str(world.refusal)).to(contain(f"Run npm install in {world.app.folder}"))

    @s.and_("the app status row still reads Story UI not installed")
    def _(world):
        expect(app_in(world.report(), STORY_UI_EDITOR.label)["status"]).to(equal(AppStatus.NOT_INSTALLED.value))


for app_status in PRESS_DOES:
    press_readies_by_status(OPEN_GRAPH, GRAPH_APP, "A press on the Graph app readies it by its status and opens it beside the chat", app_status)


@shared_stories.scenario(OPEN_GRAPH, "The graph loads the folders the session's practice roots name")
def _(s):
    @s.given("checkout-flow is the session open in the project")
    def _(world):
        BILLING_REPORT.seed_into(world.sessions_project)
        world.sessions_project.seed_active(CHECKOUT_FLOW.seed)

    @s.and_("its practice roots are harness/.context/stories, harness/.context/ux and harness/.context")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.sessions_project)

    @s.when("the Person opens the Graph app from the app status row")
    def _(world):
        world.graph = world.app_call().session.graph
        world.graph.load_practice_roots(world.app_call())

    @s.then("the knowledge graph shows the Stories tree read from harness/.context/stories, the UX tree from harness/.context/ux and the Clean Engineering tree from harness/.context")
    def _(world):
        expect(roots_loaded(world.graph, world.project)).to(equal(CHECKOUT_FLOW.roots))

    @s.and_("it shows no folder of billing-report")
    def _(world):
        expect(files_read(world.graph, world.project)).to(equal([f"{CHECKOUT_FLOW.roots[STORIES]}/{STORY_MAP}"]))


@shared_stories.scenario(OPEN_GRAPH, "The open graph follows the session open in the project")
def _(s):
    @s.given("the knowledge graph is open in the side panel on checkout-flow's practice roots")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.sessions_project)
        BILLING_REPORT.seed_into(world.sessions_project)
        world.sessions_project.seed_active(CHECKOUT_FLOW.seed)
        world.app_call().session.graph.load_practice_roots(world.app_call())

    @s.when("billing-report's session is opened in the project")
    def _(world):
        world.sessions.switch(BILLING_REPORT.name)
        world.graph = world.app_call().session.graph
        world.graph.load_practice_roots(world.app_call())

    @s.then("the knowledge graph shows the Stories tree read from billing/.context/stories and the DDD tree from billing/.context")
    def _(world):
        expect(roots_loaded(world.graph, world.project)).to(equal(BILLING_REPORT.roots))

    @s.and_("it shows no folder of checkout-flow")
    def _(world):
        expect(files_read(world.graph, world.project)).to(equal([f"{BILLING_REPORT.roots[STORIES]}/{STORY_MAP}"]))

for app_status in PRESS_DOES:
    press_readies_by_status(OPEN_KANBAN, CDD_KANBAN, "A press on the CDD Kanban readies it by its status and opens it beside the chat", app_status)


@shared_stories.scenario(OPEN_STORY_UI, "A Stories file's editor tile opens that file in the Story UI editor: story-map.md")
def _(s):
    @s.given("checkout-flow's file viewer shows story-map.md")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.sessions_project)
        world.sessions_project.seed_active(CHECKOUT_FLOW.seed)
        world.row = FidelityProgress.load(CHECKOUT_FLOW.name, "stories-story-map", project=world.project)

    @s.and_("the Story UI editor is running")
    def _(world):
        world.file = f"{CHECKOUT_FLOW.roots[STORIES]}/{STORY_MAP}"

    @s.when("the Person opens story-map.md from its story-map editor tile")
    def _(world):
        world.editor = BoardPractice(world.row.practice).editor
        world.opened = StoryModel.load(world.file, call=world.app_call())

    @s.then("the side panel shows the Story UI editor on story-map.md")
    def _(world):
        expect((world.editor, world.opened.file)).to(equal((STORY_UI_APP, world.file)))

    @s.and_("it shows the epics, sub-epics and stories story-map.md holds")
    def _(world):
        epic = world.opened.epics[0]
        shown = [epic.name, [sub_epic.name for sub_epic in epic.epics], [story.name for sub_epic in epic.epics for story in sub_epic.stories]]
        expect(shown).to(equal(["Move Work Forward From Chat Bar", ["Integrate Practice Content Editor Apps In Chat Bar"], ["Open Story UI Side Panel From Chat Bar", "Open Kanban Side Panel From Chat Bar"]]))


@shared_stories.scenario(OPEN_STORY_UI, "A file of another practice has no story-map editor tile")
def _(s):
    @s.given("checkout-flow's file viewer shows canvas.json, a UX file")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.sessions_project)
        world.sessions_project.seed_active(CHECKOUT_FLOW.seed)
        world.row = FidelityProgress.load(CHECKOUT_FLOW.name, "ux-mockup", project=world.project)

    @s.when("the Person looks at canvas.json in the file viewer")
    def _(world):
        world.editor = BoardPractice(world.row.practice).editor

    @s.then("the file viewer shows no story-map editor tile for canvas.json")
    def _(world):
        expect(world.editor).to(be_none)


@shared_stories.scenario(OPEN_DESIGN, "The file viewer opens the session's design view")
def _(s):
    @s.given("checkout-flow's UX practice has design canvas version-2 with the design view https://claude.ai/design/checkout-flow-v2")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.sessions_project)
        versions = CanvasVersions.in_practice_root(world.project / CHECKOUT_FLOW_DESIGN.ux_root)
        for _version in range(CHECKOUT_FLOW_DESIGN.version):
            versions.start_next()
        versions.record_link(CHECKOUT_FLOW_DESIGN.version, CHECKOUT_FLOW_DESIGN.link)

    @s.and_("the file viewer is open on checkout-flow")
    def _(world):
        world.session = world.sessions.named(CHECKOUT_FLOW.name)

    @s.when("the Person opens the design view from the file viewer")
    def _(world):
        world.design_view = world.session.practice(UX).design_view

    @s.then("https://claude.ai/design/checkout-flow-v2 opens in Claude Design")
    def _(world):
        expect(world.design_view).to(equal(CHECKOUT_FLOW_DESIGN.link))


@shared_stories.scenario(OPEN_DESIGN, "A session with no design view offers no link")
def _(s):
    @s.given("billing-report has Stories and DDD enabled")
    def _(world):
        BILLING_REPORT.seed_into(world.sessions_project)

    @s.but_("no design view is recorded for billing-report")
    def _(world):
        world.session = world.sessions.named(BILLING_REPORT.name)

    @s.when("the Person opens billing-report's file viewer")
    def _(world):
        world.design_view = world.session.practice(UX).design_view

    @s.then("the file viewer shows no design view link")
    def _(world):
        expect(world.design_view).to(equal(""))


@shared_stories.scenario(DEPLOY_STORY_UI, "A ticket activated on the board is the one the Story UI editor shows")
def _(s):
    @s.given("the Story UI editor is open on checkout-flow's story-map.md")
    def _(world):
        CHECKOUT_FLOW.seed_into(world.sessions_project)
        BILLING_REPORT.seed_into(world.sessions_project)
        world.sessions_project.seed_active(CHECKOUT_FLOW.seed)
        world.opened = StoryModel.open_in_session(call=world.app_call())

    @s.when("the Person activates billing-report's ticket on the board")
    def _(world):
        world.sessions.switch(BILLING_REPORT.name)

    @s.then("the Story UI editor shows billing-report's story map, without a reload")
    def _(world):
        expect(StoryModel.open_in_session(call=world.app_call()).file).to(equal(f"{BILLING_REPORT.roots[STORIES]}/{STORY_MAP}"))
