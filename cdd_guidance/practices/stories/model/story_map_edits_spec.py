"""Story map edits through the story map's tools: what the Story UI editor and an agent do to a story map, each edit saved
in the map's own file and rendered to the formats chosen for its fidelity in the session.

Story: Refactor Story UI App To Web Domain Access
(harness/.context/stories/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/
integrate_practice_content_editor_apps_in_chat_bar_story.test.md)."""

import difflib
import json
import shutil
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[4]).ensure_import_path()

import cdd_guidance.practices  # noqa: E402,F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.stories.stories import Stories  # noqa: E402
from harness.guidance.practice_formats import RenderRequest  # noqa: E402
from harness.installation.data_class import data_of  # noqa: E402
from harness.markdown.format import Format  # noqa: E402
from harness.mcp.mcp_server import McpServer  # noqa: E402
from space.session.throwaway_project import ThrowawayProject  # noqa: E402

TOOLSETS = (
    "cdd_guidance.practices.stories.model.story_model:StoryModel",
    "cdd_guidance.practices.stories.model.story_model:Epic",
    "cdd_guidance.practices.stories.model.story_model:Story",
    "cdd_guidance.practices.stories.model.story_model:Scenario",
    "cdd_guidance.practices.stories.model.story_model:Step",
    "cdd_guidance.practices.stories.model.story_model:Example",
    "cdd_guidance.practices.stories.model.story_model:Increment",
    "space.session.practice_session_output:FidelitySessionOutput",
    "space.session.sessions:Sessions",
)
# A snapshot of this repository's story map, its thin slice, and the chat bar's scenario file, taken before its stories
# were regrouped, so the edits below run on fixed text rather than on a story map that keeps changing.
STORIES = Path(__file__).resolve().parent / "fixtures" / "repository-story-map"
MAP_FILE = ".context/story-map.md"
THIN_SLICE_FILE = ".context/thin-slice.md"
CHAT_BAR_FOLDER = "move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar"
SCENARIO_FILE = f".context/{CHAT_BAR_FOLDER}/open-story-ui-side-panel-from-chat-bar/integrate_practice_content_editor_apps_in_chat_bar_story.test.md"
STORY_TEST_FILE = f"{CHAT_BAR_FOLDER}/open-story-ui-side-panel-from-chat-bar/open_story_ui_side_panel_from_chat_bar_story.test.py"
STORY_TEST = """from story_test import given, scenario, story

# Story: Open Story UI Side Panel From Chat Bar
with story("Open Story UI Side Panel From Chat Bar"):
    with scenario("the editor opens beside the chat"):
        with given("a story map"):
            pass
"""
NAMED_EXAMPLES_FILE = f".context/{CHAT_BAR_FOLDER}/open-story-ui-side-panel-from-chat-bar/press_story_ui_story.test.md"
# A scenario whose example rows are named by their example column.
NAMED_EXAMPLES = """# Sub-epic: Integrate Practice Content Editor Apps In Chat Bar

## Story: Open Story UI Side Panel From Chat Bar

#### Scenario Outline: A press on the Story UI editor readies it by its status

*Given* the app status row reads Story UI ${status row reads}
*When* the Person opens the Story UI editor from the app status row
*Then* the side panel shows the Story UI editor

##### Examples

| example | status row reads |
| --- | --- |
| not installed | not installed |
| not running | not running |
| running | running :8778 |
"""
# The chat bar's Story UI story on the snapshot of this repository's story map.
CHAT_BAR_SUB_EPIC = "move-work-forward-from-chat-bar.work-fidelity-outputs-in-chat-bar.integrate-practice-content-editor-apps-in-chat-bar"
CHAT_BAR_STORY = f"{CHAT_BAR_SUB_EPIC}.open-story-ui-side-panel-from-chat-bar"
DRAWIO_FILE = ".context/story-map.drawio"
SESSION_FILE = ".sessions/checkout-flow/session.json"
SUB_EPIC = "move-work-forward-from-chat-bar.integrate-practice-content-editor-apps-in-chat-bar"
# The checkout-flow story map, as the chat bar scenarios name its stories.
HAND_WRITTEN_MAP = """# (E) Move Work Forward From Chat Bar
## (E) Integrate Practice Content Editor Apps In Chat Bar
### (S) Person --> Open Story UI Side Panel From Chat Bar
### (S) Person --> Open Kanban Side Panel From Chat Bar
### (S) Person --> Trace Story Through Artifacts
"""


def _laid_out(text: str) -> str:
    """text as the markdown format writes a story map, so saving it changes nothing but an edit."""
    stories = Stories()
    model = stories.formats.parse(Format("markdown"), text)
    return stories.formats.render(RenderRequest(Format("markdown"), model))["content"]


def _changed(before: str, after: str) -> tuple[list[str], list[str]]:
    """The lines before had that after has not, and the lines after has that before had not."""
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="", n=0))
    removed = [line[1:] for line in diff if line.startswith("-") and not line.startswith("---")]
    added = [line[1:] for line in diff if line.startswith("+") and not line.startswith("+++")]
    return removed, added


def _node(path: str) -> str:
    return f"{MAP_FILE}#{path}"


class StoryMapProject:
    """A throwaway project holding the checkout-flow session and its story map, whose story map tools run on an
    McpServer, as the Story UI's server reaches them."""

    def __init__(self, map_text: str = "") -> None:
        self.root = ThrowawayProject().root
        (self.root / ".git").mkdir()
        session = self.root / ".sessions" / "checkout-flow"
        session.mkdir(parents=True)
        (session / "session.json").write_text(json.dumps({"name": "checkout-flow"}), encoding="utf-8")
        (self.root / ".context").mkdir()
        self.map.write_text(map_text or _laid_out(HAND_WRITTEN_MAP), encoding="utf-8")
        self.server = McpServer(project=self.root)
        self.server.start(TOOLSETS)
        # The Story UI works in the session open in the project, as the board's server reaches the cdd server.
        self.call("sessions.switch", name="checkout-flow")

    @property
    def map(self) -> Path:
        return self.root / MAP_FILE

    @property
    def drawio(self) -> Path:
        return self.root / DRAWIO_FILE

    def copy(self, source: Path, file: str) -> str:
        """source copied into the project at file; answers its text."""
        target = self.root / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return target.read_text(encoding="utf-8")

    def write(self, file: str, text: str) -> None:
        target = self.root / file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def text(self, file: str) -> str:
        return (self.root / file).read_text(encoding="utf-8")

    def call(self, tool: str, **arguments):
        return json.loads(json.dumps(self.server.invoke_tool(tool, arguments), default=data_of))

    def choose(self, format: str, is_chosen: bool) -> dict:
        return self.call("fidelity-session-output.choose_format", session=SESSION_FILE, practice="stories", fidelity="story_map", format=format, is_chosen=is_chosen)

    def story_at(self, story_map: dict, name: str) -> dict:
        """The story called name, wherever it sits on story_map."""
        epics = list(story_map["epics"])
        while epics:
            epic = epics.pop()
            found = next((story for story in epic["stories"] if story["name"] == name), None)
            if found is not None:
                return found
            epics.extend(epic["epics"])
        raise LookupError(name)

    def story_names(self, story_map: dict) -> list[str]:
        return [story["name"] for epic in story_map["epics"] for sub in epic["epics"] for story in sub["stories"]]




def _snapshot_project() -> StoryMapProject:
    """A project holding the snapshot of this repository's story map and its thin slice."""
    project = StoryMapProject()
    project.copy(STORIES / "story-map.md", MAP_FILE)
    project.copy(STORIES / "thin-slice.md", THIN_SLICE_FILE)
    return project


def _scenario_project() -> tuple[StoryMapProject, str, dict, dict]:
    """A project holding the chat bar's scenario file: the project, the file as written, the map shown from it, and its
    Refactor Story UI App To Web Domain Access story."""
    project = StoryMapProject()
    written = project.copy(STORIES / CHAT_BAR_FOLDER / "integrate_practice_content_editor_apps_in_chat_bar_story.test.md", SCENARIO_FILE)
    shown = project.call("story-model.show", file=SCENARIO_FILE)
    return project, written, shown, project.story_at(shown, "Refactor Story UI App To Web Domain Access")


def _named_examples_project() -> tuple[StoryMapProject, dict]:
    """A project holding a scenario file whose examples are named: the project and its scenario as shown."""
    project = StoryMapProject()
    project.write(NAMED_EXAMPLES_FILE, NAMED_EXAMPLES)
    shown = project.call("story-model.show", file=NAMED_EXAMPLES_FILE)
    return project, project.story_at(shown, "Open Story UI Side Panel From Chat Bar")["scenarios"][0]


def _failure(call) -> Exception | None:
    """What call raised; none when it raised nothing."""
    try:
        call()
    except Exception as failure:  # noqa: BLE001 - the examples check what was raised
        return failure
    return None


def _again(failure: Exception | None) -> None:
    """Raise failure again, so an example checks what a call raised; nothing when it raised nothing."""
    if failure is not None:
        raise failure


# Each context makes its project and runs its tool calls once, in before.all; its examples read what came of them.
with description("a story map edited through its tools") as self:
    # (S) Deploy Story UI App With Board State: the editor follows the session open in the project.
    with context("opened on the session open in the project"):
        with before.all:
            self.opened = StoryMapProject().call("story-model.open_in_session")

        with it("should show that session's story map"):
            expect(self.opened["file"]).to(equal(MAP_FILE))

    with context("opened on story-map.md"):
        with before.all:
            self.project = StoryMapProject()
            self.shown = self.project.call("story-model.show", file=MAP_FILE)

        with it("should show the stories story-map.md holds"):
            expect(self.project.story_names(self.shown)).to(equal(["Open Story UI Side Panel From Chat Bar", "Open Kanban Side Panel From Chat Bar", "Trace Story Through Artifacts"]))

        with it("should name the file it was opened from"):
            expect(self.shown["file"]).to(equal(MAP_FILE))

        with it("should show the formats its fidelity offers and the ones chosen"):
            expect((self.shown["formats"]["offered_formats"], self.shown["formats"]["chosen_formats"])).to(equal((["markdown", "drawio"], ["markdown"])))

        with it("should take edits"):
            expect(self.shown["refusal"]).to(equal(""))

    # (S) Person --> Refactor Story UI App To Web Domain Access: an edit is saved and rendered to the chosen formats.
    with context("whose story-map fidelity has markdown and drawio chosen"):
        with before.all:
            self.project = StoryMapProject()
            self.project.choose("drawio", True)
            self.renamed = self.project.call("story.rename", node=_node(f"{SUB_EPIC}.open-kanban-side-panel-from-chat-bar"), name="Open Board Side Panel From Chat Bar")

        with it("should name the story in story-map.md"):
            expect(self.project.map.read_text(encoding="utf-8")).to(contain("Open Board Side Panel From Chat Bar"))

        with it("should name the story in story-map.drawio"):
            expect(self.project.drawio.read_text(encoding="utf-8")).to(contain("Open Board Side Panel From Chat Bar"))

        with it("should write no JSON story map"):
            expect(sorted(path.name for path in (self.project.root / ".context").iterdir())).to(equal(["story-map.drawio", "story-map.md"]))

        with it("should answer the story map as its file now holds it"):
            expect(self.project.story_names(self.renamed)).to(contain("Open Board Side Panel From Chat Bar"))

    # A format turned off in the Story UI is left out of the next save.
    with context("whose drawio is turned off"):
        with before.all:
            self.project = StoryMapProject()
            self.project.choose("drawio", True)
            self.project.call("story.rename", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), name="Trace Story Across Artifacts")
            self.drawn = self.project.drawio.read_text(encoding="utf-8")
            self.chosen = self.project.choose("drawio", False)
            self.project.call("epic.new_story", node=_node(SUB_EPIC), name="Open Graph Side Panel From Board")

        with it("should keep only markdown chosen for the story map"):
            expect(self.chosen["chosen_formats"]).to(equal(["markdown"]))

        with it("should add the new story to story-map.md"):
            expect(self.project.map.read_text(encoding="utf-8")).to(contain("Open Graph Side Panel From Board"))

        with it("should leave story-map.drawio as it was"):
            expect(self.project.drawio.read_text(encoding="utf-8")).to(equal(self.drawn))

    # The Story UI shows an edit the agent made through the tools: the next read takes the file as it is.
    with context("renamed by the agent through the story map's tools"):
        with before.all:
            self.project = StoryMapProject()
            self.project.call("story.rename", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), name="Trace Story Across Artifacts")
            self.read = self.project.call("story-model.show", file=MAP_FILE)

        with it("should show the renamed story on the next read"):
            expect(self.project.story_names(self.read)).to(contain("Trace Story Across Artifacts"))

    with context("with each edit"):
        with context("that adds an epic"):
            with before.all:
                self.story_map = StoryMapProject().call("story-model.new_epic", file=MAP_FILE, name="Deploy Story UI App")

            with it("should add an epic after the map's epics"):
                expect([epic["name"] for epic in self.story_map["epics"]]).to(equal(["Move Work Forward From Chat Bar", "Deploy Story UI App"]))

            with it("should name each node by its file and its path"):
                expect(self.story_map["epics"][0]["epics"][0]["node"]).to(equal(_node(SUB_EPIC)))

        with context("that moves a story"):
            with before.all:
                self.project = StoryMapProject()
                self.story_map = self.project.call("story.move_before", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), other=_node(f"{SUB_EPIC}.open-story-ui-side-panel-from-chat-bar"))

            with it("should move a story before another under the same sub-epic"):
                expect(self.project.story_names(self.story_map)[0]).to(equal("Trace Story Through Artifacts"))

        with context("that removes a story"):
            with before.all:
                self.project = StoryMapProject()
                self.story_map = self.project.call("story.remove", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"))

            with it("should remove a story"):
                expect(self.project.story_names(self.story_map)).not_to(contain("Trace Story Through Artifacts"))

        with context("that moves a story before an epic"):
            with before.all:
                project = StoryMapProject()
                self.moving = _failure(lambda: project.call("story.move_before", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), other=_node(SUB_EPIC)))

            with it("should refuse to move a story before an epic"):
                expect(lambda: _again(self.moving)).to(raise_error(Exception, contain("not a Story")))

        # A story map keeps its stories; their scenarios are kept in each story's scenario file.
        with context("that adds a scenario to a story"):
            with before.all:
                project = StoryMapProject()
                self.adding = _failure(lambda: project.call("story.new_scenario", node=_node(f"{SUB_EPIC}.open-story-ui-side-panel-from-chat-bar"), name="Press opens the editor"))

            with it("should refuse a scenario on a story map, which does not read one back"):
                expect(lambda: _again(self.adding)).to(raise_error(Exception, contain("would not keep the edit")))

    # (S) Refactor Story UI App To Web Domain Access: a story map laid out by hand is edited, not read only.
    with context("opened on a story map laid out by hand"):
        with before.all:
            self.project = StoryMapProject("# Checkout notes\n\nWritten by hand above the map.\n\n" + HAND_WRITTEN_MAP)
            self.project.call("story.rename", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), name="Trace Story Across Artifacts")

        with it("should save the rename"):
            expect(self.project.text(MAP_FILE)).to(contain("### (S) Person --> Trace Story Across Artifacts"))

        with it("should keep the lines written by hand above the map"):
            expect(self.project.text(MAP_FILE)).to(contain("# Checkout notes\n\nWritten by hand above the map.\n\n# (E) Move Work Forward From Chat Bar"))

    # This repository's own story map, laid out by hand, read and saved through the tools.
    with context("opened on a snapshot of this repository's story map"):
        with before.all:
            self.written = (STORIES / "story-map.md").read_text(encoding="utf-8")
            self.sliced = (STORIES / "thin-slice.md").read_text(encoding="utf-8")

        with context("saved with no change"):
            with before.all:
                self.project = _snapshot_project()
                self.shown = self.project.call("story.rename", node=_node(CHAT_BAR_STORY), name="Open Story UI Side Panel From Chat Bar")

            with it("should write story-map.md as it was written"):
                expect(self.project.text(MAP_FILE)).to(equal(self.written))

            with it("should leave thin-slice.md as it was written"):
                expect(self.project.text(THIN_SLICE_FILE)).to(equal(self.sliced))

            with it("should show each story's description, the paragraph under its heading"):
                story = self.project.story_at(self.shown, "Open Story UI Side Panel From Chat Bar")
                expect(story["description"]).to(contain('Requested (2026-11-06, "chat band -> story UI side panel")'))

        with context("with a story renamed"):
            with before.all:
                self.project = _snapshot_project()
                self.project.call("story.rename", node=_node(CHAT_BAR_STORY), name="Open Story UI Beside The Chat")

            with it("should change only that story's heading"):
                expect(_changed(self.written, self.project.text(MAP_FILE))).to(equal((
                    ["#### (S) Person --> Open Story UI Side Panel From Chat Bar"],
                    ["#### (S) Person --> Open Story UI Beside The Chat"],
                )))

        with context("with a story's description edited"):
            with before.all:
                self.project = _snapshot_project()
                self.project.call("story.edit_description", node=_node(CHAT_BAR_STORY), description="Requested (2026-11-12): the chat bar opens the Story UI editor beside the chat.")

            with it("should change only the paragraph under that story's heading"):
                removed, added = _changed(self.written, self.project.text(MAP_FILE))
                expect((len(removed), added)).to(equal((1, ["Requested (2026-11-12): the chat bar opens the Story UI editor beside the chat."])))

        # (S) Refactor Story UI App To Web Domain Access: an epic's and a sub-epic's descriptions are edited on screen and
        # saved the way a story's is.
        with context("with an epic's description edited"):
            with before.all:
                self.project = _snapshot_project()
                self.shown = self.project.call("epic.edit_description", node=_node("move-work-forward-from-chat-bar"), description="The Chat Bar is the line above the chat prompt.")

            with it("should change only the paragraph under that epic's heading"):
                removed, added = _changed(self.written, self.project.text(MAP_FILE))
                expect((len(removed), added)).to(equal((1, ["The Chat Bar is the line above the chat prompt."])))

            with it("should show the epic's new description"):
                epic = next(epic for epic in self.shown["epics"] if epic["node"] == _node("move-work-forward-from-chat-bar"))
                expect(epic["description"]).to(equal("The Chat Bar is the line above the chat prompt."))

        with context("with a sub-epic given a description"):
            with before.all:
                self.project = _snapshot_project()
                self.project.call("epic.edit_description", node=_node(CHAT_BAR_SUB_EPIC), description="Requested (2026-11-12): the chat bar opens the editor apps.")

            with it("should add only the paragraph under that sub-epic's heading"):
                removed, added = _changed(self.written, self.project.text(MAP_FILE))
                expect((removed, [line for line in added if line])).to(equal(([], ["Requested (2026-11-12): the chat bar opens the editor apps."])))

    # (S) Refactor Story UI App To Web Domain Access: increments are edited through the story map and kept in its thin
    # slice.
    with context("sliced into increments by the thin slice beside it"):
        with before.all:
            self.sliced = (STORIES / "thin-slice.md").read_text(encoding="utf-8")
            self.shown = _snapshot_project().call("story-model.show", file=MAP_FILE)

        with it("should show its increments in order"):
            expect([increment["name"] for increment in self.shown["increments"]][:3]).to(equal(["Built Today", "Maintain Tickets On Board", "Integrate Practice Content Editor Apps"]))

        with it("should show each increment's description, its outcome and slicing notes"):
            expect(self.shown["increments"][2]["description"]).to(contain("**Outcome:** the board and the chat bar open the Story UI editor"))

        with it("should show the stories each increment delivers"):
            expect(self.shown["increments"][2]["stories"]).to(contain(_node(CHAT_BAR_STORY)))

        with context("with an increment added and given a story"):
            with before.all:
                self.project = _snapshot_project()
                self.project.call("story-model.new_increment", file=MAP_FILE, name="Edit Story Maps In Story UI")
                self.added = self.project.call("increment.add_story", node=_node("increment:edit-story-maps-in-story-ui"), story=_node(CHAT_BAR_STORY))

            with it("should write the increment after the last one in thin-slice.md"):
                expect(self.project.text(THIN_SLICE_FILE)).to(contain("### Increment 18: Edit Story Maps In Story UI\n\n**Stories in this increment:**\n\n- *Open Story UI Side Panel From Chat Bar*\n"))

            with it("should take the story off the increment that delivered it"):
                expect(self.added["increments"][2]["stories"]).not_to(contain(_node(CHAT_BAR_STORY)))

            with it("should take only that story's line out of the rest of thin-slice.md"):
                removed, _ = _changed(self.sliced, self.project.text(THIN_SLICE_FILE))
                expect(removed).to(equal(["- *Open Story UI Side Panel From Chat Bar*"]))

        with context("with an increment renamed"):
            with before.all:
                self.project = _snapshot_project()
                self.project.call("increment.rename", node=_node("increment:maybe-later"), name="Later")

            with it("should change only its heading in thin-slice.md"):
                expect(_changed(self.sliced, self.project.text(THIN_SLICE_FILE))).to(equal((
                    ["### Increment 17: Maybe Later"],
                    ["### Increment 17: Later"],
                )))

    # (S) Refactor Story UI App To Web Domain Access: a scenario file is edited through the story model too.
    with context("opened on a scenario file"):
        with before.all:
            self.project, self.written, self.shown, self.story = _scenario_project()
            self.trace = self.project.story_at(self.shown, "Trace Story Through Artifacts")["scenarios"][0]

        with it("should take edits"):
            expect(self.shown["refusal"]).to(equal(""))

        with it("should show the story's scenarios"):
            expect([scenario["name"] for scenario in self.story["scenarios"]]).to(contain("An edit is saved in the story map file and rendered to the chosen formats"))

        with context("with a step added to a scenario"):
            with before.all:
                self.project, self.written, _, story = _scenario_project()
                self.project.call("scenario.new_step", node=story["scenarios"][0]["node"], step_type="then", text="the story map file keeps its other lines")

            with it("should write the step under that scenario and change nothing else"):
                removed, added = _changed(self.written, self.project.text(SCENARIO_FILE))
                expect((removed, [line.strip() for line in added])).to(equal(([], ["*Then* the story map file keeps its other lines"])))

        # (S) Refactor Story UI App To Web Domain Access: a scenario's example rows are edited through each example.
        with it("should show each example row by the node its own tools take"):
            expect(self.trace["examples"][0]["node"]).to(equal(f"{self.trace['node']}.example:example-1"))

        with it("should show each example row's fields as its table holds them"):
            expect(self.trace["examples"][0]["fields"]).to(equal({"example": "example-1", "violation": "Ticket Archive name", "file": "harness/.context/stories/story-map.md", "lines": "86 to 88", "story": "Ticket Archive"}))

        with context("with an example's field edited"):
            with before.all:
                self.project, self.written, shown, _ = _scenario_project()
                trace = self.project.story_at(shown, "Trace Story Through Artifacts")["scenarios"][0]
                self.edited = self.project.call("example.edit_field", node=trace["examples"][0]["node"], field="lines", text="86 to 90")

            with it("should change only that example's row"):
                expect(_changed(self.written, self.project.text(SCENARIO_FILE))).to(equal((
                    ["| Ticket Archive name | harness/.context/stories/story-map.md | 86 to 88 | Ticket Archive |"],
                    ["| Ticket Archive name | harness/.context/stories/story-map.md | 86 to 90 | Ticket Archive |"],
                )))

            with it("should answer the example as its file now holds it"):
                trace = self.project.story_at(self.edited, "Trace Story Through Artifacts")["scenarios"][0]
                expect(trace["examples"][0]["fields"]["lines"]).to(equal("86 to 90"))

        with context("with a field its example's row does not have edited"):
            with before.all:
                self.editing = _failure(lambda: self.project.call("example.edit_field", node=self.trace["examples"][0]["node"], field="owner", text="Person"))

            with it("should refuse a column the example's row does not have"):
                expect(lambda: _again(self.editing)).to(raise_error(Exception, contain("has no owner column")))

        with context("with an example moved before another"):
            with before.all:
                self.moving = _failure(lambda: self.project.call("example.move_before", node=self.trace["examples"][1]["node"], other=self.trace["examples"][0]["node"]))

            with it("should refuse to move an example, which keeps the place its table gives it"):
                expect(lambda: _again(self.moving)).to(raise_error(Exception, contain("keeps the place its table gives it")))

    # (S) Refactor Story UI App To Web Domain Access: an example named by its example column is renamed in that cell.
    with context("opened on a scenario file whose examples are named"):
        with context("with an example renamed through its example column"):
            with before.all:
                self.project, scenario = _named_examples_project()
                self.renamed = self.project.call("example.edit_field", node=scenario["examples"][1]["node"], field="example", text="stopped")

            with it("should change only that cell of its row"):
                expect(_changed(NAMED_EXAMPLES, self.project.text(NAMED_EXAMPLES_FILE))).to(equal((["| not running | not running |"], ["| stopped | not running |"])))

            with it("should name the example by its new name"):
                scenario = self.project.story_at(self.renamed, "Open Story UI Side Panel From Chat Bar")["scenarios"][0]
                expect([example["name"] for example in scenario["examples"]]).to(equal(["not installed", "stopped", "running"]))

        with context("with an example removed"):
            with before.all:
                self.project, scenario = _named_examples_project()
                self.project.call("example.remove", node=scenario["examples"][1]["node"])

            with it("should take only that example's row out of the file"):
                expect(_changed(NAMED_EXAMPLES, self.project.text(NAMED_EXAMPLES_FILE))).to(equal((["| not running | not running |"], [])))

    # (S) Refactor Story UI App To Web Domain Access: acceptance-test files are linked, not edited.
    with context("whose story has an acceptance-test file in the session"):
        with before.all:
            self.project = StoryMapProject()
            self.project.write(STORY_TEST_FILE, STORY_TEST)
            self.shown = self.project.call("story-model.show", file=MAP_FILE)

        with it("should link the story to that file"):
            expect(self.project.story_at(self.shown, "Open Story UI Side Panel From Chat Bar")["acceptance_tests"]).to(equal([STORY_TEST_FILE]))

        with it("should link no other story to it"):
            expect(self.project.story_at(self.shown, "Trace Story Through Artifacts")["acceptance_tests"]).to(equal([]))

    # (S) Open Story UI On Ticket Scope: the story map says which part of it the ticket's session covers.
    with context("opened in a session whose ticket names its stories"):
        with before.all:
            project = StoryMapProject()
            project.write(".sessions/checkout-flow/checkout-flow.md", "# Checkout flow\n\n## Story: Open Story UI Side Panel From Chat Bar\n\n## Story: Open Kanban Side Panel From Chat Bar\n")
            self.shown = project.call("story-model.open_in_session")

        with it("should scope the map to the stories the session names"):
            expect(self.shown["scope"]).to(equal([_node(f"{SUB_EPIC}.open-story-ui-side-panel-from-chat-bar"), _node(f"{SUB_EPIC}.open-kanban-side-panel-from-chat-bar")]))

    with context("opened in a session that names no story"):
        with before.all:
            self.shown = StoryMapProject().call("story-model.show", file=MAP_FILE)

        with it("should scope the map to none of its stories, so the whole map shows"):
            expect(self.shown["scope"]).to(equal([]))

    with context("asked to write a format it does not write"):
        with before.all:
            project = StoryMapProject()
            self.choosing = _failure(lambda: project.choose("python", True))

        with it("should refuse a format the story map does not write"):
            expect(lambda: _again(self.choosing)).to(raise_error(Exception, contain("does not write python")))
