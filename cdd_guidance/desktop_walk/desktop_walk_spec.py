"""A desktop walk: the desktop story tests of a project, what each of their steps asks an agent to do and see in the
real desktop app, the test chat a walk drives, and the instructions the walk command gives."""
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, have_len, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from cdd_guidance.desktop_walk.desktop_walk import DesktopWalk, NoDesktopStoryTest

SUB_EPIC = "move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar"
MARK_FILE = f"story_tests/{SUB_EPIC}/display_server_health_mark_story.desktop.md"
QUEUE_FILE = "story_tests/queue-prompts-for-later/build-prompt-queue/open_prompt_queue_story.desktop.md"

MARK_TEST = """\
## Story: Display Server Health Mark

#### Scenario: Show the connected mark

*Given* cdd answers server-health.report with 116 tools loaded

- Do: nothing; the test chat starts with cdd running.
- See: the chat bar is drawn above the prompt box.

*When* the Chat Bar draws the active session checkout-flow

- Do: wait until the chat bar shows a session name.

*Then* a green ✓ sits left of checkout-flow

- See: a green ✓ is the first mark on the chat bar's line.
- See: the session's name is to its right.

  *And* no failure line shows

- See: no red line above the chat bar.
"""

QUEUE_TEST = """\
## Story: Open Prompt Queue

#### Scenario: Open an empty queue

*Given* the prompt queue holds no prompt

*When* the Person presses the stack image

- Do: press the stack image above the chat bar.

*Then* the queue opens upward showing Add

#### Scenario: Close the open queue

*Given* the prompt queue is open

- See: the queue's box above the chat bar.

*When* the Person presses the stack image

*Then* only the stack shows
"""


class OpenedChats:
    """The chats as the walk sees them: each folder and prompt a new chat was opened with."""

    def __init__(self) -> None:
        self.opened: list[tuple[str, str]] = []

    def open(self, folder: str, prompt: str) -> str:
        self.opened.append((folder, prompt))
        return f"claude://code/new?folder={folder}"


with description("a desktop walk of a project") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="desktop-walk-"))
        for file, text in ((MARK_FILE, MARK_TEST), (QUEUE_FILE, QUEUE_TEST)):
            (self.project / file).parent.mkdir(parents=True, exist_ok=True)
            (self.project / file).write_text(text, encoding="utf-8")
        self.test_chats = Path(tempfile.mkdtemp(prefix="desktop-walk-chats-"))
        self.chats = OpenedChats()
        self.made: list[Path] = []
        self.walk = DesktopWalk(self.project, chats=self.chats, test_chats_folder=self.test_chats, make_repository=self.made.append)

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)
        shutil.rmtree(self.test_chats, ignore_errors=True)

    with context("that lists the scenarios of its desktop story tests"):
        with it("should hold every scenario of every desktop story test when no target is named"):
            expect([scenario.name for scenario in self.walk.scenarios()]).to(equal(["Show the connected mark", "Open an empty queue", "Close the open queue"]))

        with it("should hold only the scenarios under an epic's folder when the target is the epic"):
            expect({scenario.story for scenario in self.walk.scenarios("queue-prompts-for-later")}).to(equal({"Open Prompt Queue"}))

        with it("should hold only the scenarios of a sub-epic when the target is its folder"):
            expect([scenario.story for scenario in self.walk.scenarios(SUB_EPIC)]).to(equal(["Display Server Health Mark"]))

        with it("should hold only a story's scenarios when the target is the story's name"):
            expect([scenario.name for scenario in self.walk.scenarios("Open Prompt Queue")]).to(equal(["Open an empty queue", "Close the open queue"]))

        with it("should name the sub-epic a scenario's walk is recorded under"):
            expect(self.walk.scenarios(SUB_EPIC)[0].sub_epic).to(equal(SUB_EPIC))

        with it("should name the file a scenario was read from, as a path from the project"):
            expect(self.walk.scenarios(SUB_EPIC)[0].file).to(equal(MARK_FILE))

        with it("should refuse a target no desktop story test is under, naming it"):
            expect(lambda: self.walk.scenarios("author-story-maps")).to(raise_error(NoDesktopStoryTest, contain("author-story-maps")))

    with context("that reads a scenario's steps"):
        with before.each:
            self.steps = self.walk.scenarios(SUB_EPIC)[0].steps

        with it("should hold each Given, When, Then and And in the file's order"):
            expect([step.keyword for step in self.steps]).to(equal(["Given", "When", "Then", "And"]))

        with it("should key a step by its story, its scenario, its number and its words, as the walk report names it"):
            expect(self.steps[2].key).to(equal("Display Server Health Mark › Show the connected mark › 3 Then a green ✓ sits left of checkout-flow"))

        with it("should hold what the agent does on the screen for the step"):
            expect(self.steps[1].do).to(equal(["wait until the chat bar shows a session name."]))

        with it("should hold each thing the agent must see for the step"):
            expect(self.steps[2].see).to(equal(["a green ✓ is the first mark on the chat bar's line.", "the session's name is to its right."]))

        with it("should give a chained step its own number and what it must see"):
            expect((self.steps[3].key.split(" › ")[-1], self.steps[3].see)).to(equal(("4 And no failure line shows", ["no red line above the chat bar."])))

        with it("should end a scenario's last step where the next scenario starts"):
            expect(self.walk.scenarios("Open Prompt Queue")[0].steps[-1].see).to(equal([]))

        with it("should hold nothing to do or see for a step that names neither"):
            given = self.walk.scenarios("Open Prompt Queue")[0].steps[0]
            expect((given.do, given.see)).to(equal(([], [])))

    with context("that opens the test chat a walk drives"):
        with before.each:
            self.test_chat = self.walk.open_test_chat()

        with it("should make a throwaway git repository for the chat to work in"):
            expect([str(folder) for folder in self.made]).to(equal([self.test_chat.folder]))

        with it("should keep the throwaway repository out of the project the walk tests"):
            expect(self.project in Path(self.test_chat.folder).resolve().parents).to(equal(False))

        with it("should open one new chat in the Claude app on that folder"):
            expect([folder for folder, _ in self.chats.opened]).to(equal([self.test_chat.folder]))

        with it("should fill the new chat's prompt with the mark the agent finds the chat by"):
            expect(self.chats.opened[0][1]).to(contain(self.test_chat.mark))

    with context("whose walk command gives its instructions"):
        with before.each:
            self.prompt = "\n".join(AgentInstructions.for_callable(DesktopWalk.desktop_walk, self.walk).prompt)

        with it("should ask for access to the Claude app before any step"):
            expect(self.prompt).to(contain("request_access"))

        with it("should keep the agent from typing in the chat that runs the walk"):
            expect(self.prompt).to(contain("never type in the chat that runs the walk"))

        with it("should record each step through the end-to-end review's walk"):
            expect(self.prompt).to(contain("record_walked_step"))
