"""Story map edits through the story map's tools: what the Story UI editor and an agent do to a story map, each edit saved
in the map's own file and rendered to the formats chosen for its fidelity in the session.

Story: Refactor Story UI App To Web Domain Access
(harness/.context/stories/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/
integrate_practice_content_editor_apps_in_chat_bar_story.test.md)."""

import json
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
    "space.session.practice_session_output:FidelitySessionOutput",
    "space.session.sessions:Sessions",
)
MAP_FILE = ".context/story-map.md"
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

    def call(self, tool: str, **arguments):
        return json.loads(json.dumps(self.server.invoke_tool(tool, arguments), default=data_of))

    def choose(self, format: str, is_chosen: bool) -> dict:
        return self.call("fidelity-session-output.choose_format", session=SESSION_FILE, practice="stories", fidelity="story_map", format=format, is_chosen=is_chosen)

    def story_names(self, story_map: dict) -> list[str]:
        return [story["name"] for epic in story_map["epics"] for sub in epic["epics"] for story in sub["stories"]]


with description("a story map edited through its tools") as self:
    with before.each:
        self.project = StoryMapProject()

    # (S) Deploy Story UI App With Board State: the editor follows the session open in the project.
    with context("opened on the session open in the project"):
        with it("should show that session's story map"):
            expect(self.project.call("story-model.open_in_session")["file"]).to(equal(MAP_FILE))

    with context("opened on story-map.md"):
        with before.each:
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
        with before.each:
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
        with before.each:
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
        with before.each:
            self.project.call("story.rename", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), name="Trace Story Across Artifacts")
            self.read = self.project.call("story-model.show", file=MAP_FILE)

        with it("should show the renamed story on the next read"):
            expect(self.project.story_names(self.read)).to(contain("Trace Story Across Artifacts"))

    with context("with each edit"):
        with it("should add an epic after the map's epics"):
            story_map = self.project.call("story-model.new_epic", file=MAP_FILE, name="Deploy Story UI App")
            expect([epic["name"] for epic in story_map["epics"]]).to(equal(["Move Work Forward From Chat Bar", "Deploy Story UI App"]))

        with it("should move a story before another under the same sub-epic"):
            story_map = self.project.call("story.move_before", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), other=_node(f"{SUB_EPIC}.open-story-ui-side-panel-from-chat-bar"))
            expect(self.project.story_names(story_map)[0]).to(equal("Trace Story Through Artifacts"))

        with it("should remove a story"):
            story_map = self.project.call("story.remove", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"))
            expect(self.project.story_names(story_map)).not_to(contain("Trace Story Through Artifacts"))

        with it("should refuse to move a story before an epic"):
            moving = lambda: self.project.call("story.move_before", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), other=_node(SUB_EPIC))
            expect(moving).to(raise_error(Exception, contain("not a Story")))

        # A story map keeps its stories; their scenarios are kept in each story's scenario file.
        with it("should refuse a scenario on a story map, which does not read one back"):
            adding = lambda: self.project.call("story.new_scenario", node=_node(f"{SUB_EPIC}.open-story-ui-side-panel-from-chat-bar"), name="Press opens the editor")
            expect(adding).to(raise_error(Exception, contain("would not keep the edit")))

        with it("should name each node by its file and its path"):
            story_map = self.project.call("story-model.new_epic", file=MAP_FILE, name="Deploy Story UI App")
            expect(story_map["epics"][0]["epics"][0]["node"]).to(equal(_node(SUB_EPIC)))

    with context("opened on a story map laid out by hand"):
        with before.each:
            self.project = StoryMapProject("# Checkout notes\n\nWritten by hand above the map.\n\n" + HAND_WRITTEN_MAP)

        with it("should say why an edit is not saved"):
            renaming = lambda: self.project.call("story.rename", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), name="Trace Story Across Artifacts")
            expect(renaming).to(raise_error(Exception, contain("beyond the edit")))

        with it("should leave its file as it was"):
            before_edit = self.project.map.read_text(encoding="utf-8")
            try:
                self.project.call("story.rename", node=_node(f"{SUB_EPIC}.trace-story-through-artifacts"), name="Trace Story Across Artifacts")
            except Exception:  # noqa: BLE001 - the refusal is the subject of the spec above
                pass
            expect(self.project.map.read_text(encoding="utf-8")).to(equal(before_edit))

    with it("should refuse a format the story map does not write"):
        expect(lambda: self.project.choose("python", True)).to(raise_error(Exception, contain("does not write python")))
