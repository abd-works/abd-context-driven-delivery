"""Walk desktop story tests in the real Claude desktop app by computer control.

A desktop story test (`{story_snake}_story.desktop.md`, beside its story's scenarios under `story_tests/`) holds the
story's scenarios word for word, and under each step what an agent does on the screen (`- Do:`) and what it must see
(`- See:`). No test tier runs one: computer control is a tool only an agent in a Claude chat has, so a walk is run by
an agent, from the walk command, and only when a person asks for it. Each step's screenshot and verdict are recorded
through the end-to-end review's walk (`e2e-review.walk`, `record_verdict`), so a desktop walk is reported and compared
as a browser walk is."""
from __future__ import annotations

import itertools
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownScenario
from cdd_guidance.practices.stories.model.markdown.scenario_file import ScenarioFileReading
from cdd_guidance.practices.stories.model.story_file import flat_steps
from cdd_guidance.practices.stories.model.story_map_files import STORY_TESTS_FOLDER, StoryMapFiles
from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.annotations.name import Name
from harness.chat.chat import ChatLinks, links_of_run
from harness.installation.data_class import data_field
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp
from space.repo.new_repository import NewRepository

# What a desktop story test writes under a step: what the agent does on the screen, and what it must see there.
_DIRECTION = re.compile(r"^\s*[-*]\s+\**(Do|See)\**\s*:\**\s*(.+?)\s*$", re.IGNORECASE)
# A line that ends the lines below a step: the next step, or a heading.
_ENDS_STEP = re.compile(r"^\s*(\*(Given|When|Then|And|But)\*\s|#)", re.IGNORECASE)
# The folder under the system's temporary folder that holds each walk's throwaway repository.
TEST_CHATS_FOLDER = "cdd-desktop-walk"
# How a walk's test chat is told apart from the person's own chats: this word and when the chat was opened.
TEST_CHAT_MARK = "desktop-walk-test-chat"


class NoDesktopStoryTest(LookupError):
    """Raised when a walk is asked for a target no desktop story test is under."""

    def __init__(self, target: str, stories: list[str]) -> None:
        held = ", ".join(stories) if stories else "none"
        super().__init__(f"no desktop story test is under {target!r}: name an epic's or sub-epic's folder under "
                         f"{STORY_TESTS_FOLDER}/, or one of the stories that has one ({held})")
        self.target = target


class DesktopStep:
    """One step of a desktop story test: its words as the scenario writes them, what the agent does on the screen for
    it, and what the agent must see before the step meets its intent."""

    def __init__(self, scenario: DesktopScenario, number: int, keyword: str, text: str, directions: list[tuple[str, str]]) -> None:
        self._scenario = scenario
        self._number = number
        self._keyword = keyword
        self._text = text
        self._directions = directions

    @property
    @data_field
    def key(self) -> str:
        """What the walk records the step under: its story, its scenario, then its number, keyword and words."""
        return f"{self._scenario.story} › {self._scenario.name} › {self._number} {self._keyword} {self._text}"

    @property
    @data_field
    def keyword(self) -> str:
        return self._keyword

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field
    def do(self) -> list[str]:
        """What the agent does on the screen, in order; nothing for a step the screen already shows."""
        return [words for kind, words in self._directions if kind == "do"]

    @property
    @data_field
    def see(self) -> list[str]:
        """Each thing the agent must see on the step's screenshot."""
        return [words for kind, words in self._directions if kind == "see"]


class DesktopScenario:
    """One scenario of a desktop story test, with the story and file it was read from and its steps."""

    def __init__(self, story: str, name: str, file: str) -> None:
        self._story = story
        self._name = name
        self._file = file
        self._steps: list[DesktopStep] = []

    @property
    @data_field
    def story(self) -> str:
        return self._story

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def file(self) -> str:
        """The desktop story test, as a path from the project."""
        return self._file

    @property
    @data_field
    def sub_epic(self) -> str:
        """`<epic>/<sub-epic>`, the folders the file sits in under story_tests: what e2e-review.walk takes."""
        return "/".join(Path(self._file).parts[1:-1])

    @property
    @data_field
    def steps(self) -> list[DesktopStep]:
        return list(self._steps)

    def read_steps(self, steps: list, lines: list[str]) -> None:
        """Take each of steps, its chained steps after it, with the Do and See lines the file holds below it, up to the
        next step or heading."""
        for number, step in enumerate(flat_steps(steps), start=1):
            below = itertools.takewhile(lambda line: not _ENDS_STEP.match(line), lines[step.source.start_line:])
            found = [_DIRECTION.match(line) for line in below]
            directions = [(match.group(1).lower(), match.group(2)) for match in found if match]
            self._steps.append(DesktopStep(self, number, step.keyword, step.text, directions))

    def is_under(self, target: str) -> bool:
        """Whether target names this scenario's story, or a folder under story_tests its file sits in."""
        folders = "/".join(Path(self._file).parts[1:-1])
        named = target.replace("\\", "/").strip("/")
        if named.startswith(f"{STORY_TESTS_FOLDER}/"):
            named = named[len(STORY_TESTS_FOLDER) + 1:]
        return folders == named or folders.startswith(f"{named}/") or Name(target).title_slug == Name(self._story).title_slug


class TestChat:
    """The chat a walk drives: a new chat in the Claude app on a throwaway repository, found by its mark."""

    __test__ = False

    def __init__(self, folder: Path, mark: str, link: str) -> None:
        self._folder = folder
        self._mark = mark
        self._link = link

    @property
    @data_field
    def folder(self) -> str:
        return str(self._folder)

    @property
    @data_field
    def mark(self) -> str:
        """The words the chat's first prompt holds, which the agent finds the chat by on the screen."""
        return self._mark

    @property
    @data_field
    def link(self) -> str:
        return self._link


@agent_toolset
class DesktopWalk:
    """Walk a project's desktop story tests in the real Claude desktop app by computer control, recording each step's
    screenshot and verdict through the end-to-end review's walk. Run only when a person asks."""

    def __init__(self, project: Path | str, opener: ChatLinks | None = None, test_chats_folder: Path | None = None,
                 make_repository: Callable[[Path], object] | None = None) -> None:
        self.project = Path(project).resolve()
        self._opener = opener
        # The boundary to git: makes a folder a repository on main with a first commit.
        self._make_repository = make_repository or (lambda folder: NewRepository(folder).create())
        self._test_chats_folder = test_chats_folder or Path(tempfile.gettempdir()) / TEST_CHATS_FOLDER

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> DesktopWalk:
        """The desktop story tests of project, the folder the call names."""
        return cls(project)

    @mcp
    @agent_tool
    def scenarios(self, target: str = "") -> list[DesktopScenario]:
        """The scenarios of the project's desktop story tests under target, each step with its key, its words, what to
        do on the screen and what must be seen. target is an epic's or a sub-epic's folder under story_tests
        (`<epic>` or `<epic>/<sub-epic>`) or a story's name; with none, every desktop story test."""
        held = [scenario for file in StoryMapFiles(self.project / STORY_TESTS_FOLDER).desktop_story_tests_below() for scenario in self._scenarios_in(file)]
        found = [scenario for scenario in held if not target or scenario.is_under(target)]
        if target and not found:
            raise NoDesktopStoryTest(target, sorted({scenario.story for scenario in held}))
        return found

    @mcp
    @agent_tool
    def open_test_chat(self) -> TestChat:
        """Make a throwaway git repository in the system's temporary folder and open a new chat on it in the Claude app,
        its prompt holding the mark the walk finds the chat by. The app asks for the folder to be confirmed and the
        prompt sent, which the walking agent does on the screen."""
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        folder = self._test_chats_folder / f"walk-{stamp}"
        self._make_repository(folder)
        mark = f"{TEST_CHAT_MARK} {stamp}"
        prompt = f"{mark}: this chat is driven by a desktop walk of the CDD chat bar. Reply with the one word ready and do nothing else."
        return TestChat(folder, mark, (self._opener or links_of_run()).open_new(str(folder), prompt))

    @mcp
    @skill
    @agent_instructions
    def desktop_walk(self, target: str = "") -> str:
        """Walk the desktop story tests under {{target}} (an epic's or sub-epic's folder under story_tests, or a story's name; every desktop story test when empty) in the real Claude desktop app by computer control, and record each step's screenshot and verdict. A walk takes the person's screen and keyboard, so run it only when the person asked for it in this chat, or answered yes to the timed run's question on the chat bar, which sends this command. You are the walking agent: this chat runs the walk, and a second chat, the test chat, is the one you click and type in."""
        """Step 1 - Read what to walk. Call scenarios with {{target}} and keep its answer: each scenario's story, sub_epic and file, and each step's key, keyword, text, do and see. Tell the person which stories you will walk and how many steps, and that their screen and keyboard are taken until you say the walk has ended. A target with no desktop story test is refused: pass the refusal on and stop."""
        tools(self.scenarios)
        """Step 2 - Get computer control. Load every computer control tool with one ToolSearch call (query "computer-use", max_results 30). When none is found, stop and tell the person this chat has no computer control, so the walk did not run: it needs a chat in the Claude desktop app with computer use turned on. Then call request_access for the app named Claude (the Claude desktop app), with the reason "Walk the CDD chat bar's desktop story tests in a test chat". When access is refused, or the app cannot be granted, stop and say so. Never fall back to a browser tool, a script or a stubbed page: a walk that did not drive the real app is not a walk."""
        """Step 3 - Open the test chat. Call open_test_chat: it makes a throwaway git repository and asks the Claude app to open a new chat on it, with a prompt that holds its mark. Take a screenshot, confirm the folder the app asks about when it is the test chat's folder, and send the prompt. Wait until the chat answers ready and the CDD chat bar is drawn above its prompt box; a first start in a new folder installs CDD there, which can take a few minutes, so screenshot every 20 seconds for up to 5 minutes. From here on, every click and keystroke goes to the test chat. Before each one, check on the latest screenshot that the chat in front shows the mark in its first prompt; never type in the chat that runs the walk, and never in any other chat of the person's. When the test chat cannot be found or opened, stop and say what the screen showed."""
        tools(self.open_test_chat)
        """Step 4 - Open one walk for each sub-epic. For each distinct sub_epic among the scenarios call e2e-review.walk with target set to that sub_epic, and keep the run_folder it answers. Its screens/ folder is where that sub-epic's screenshots go."""
        """Step 5 - Walk each scenario, one step at a time, in the file's order. For each step: (a) do what its do lines say, on the screen of the test chat, with computer control: click, type, press a key, scroll, or wait. A do line that names a cdd tool, such as server-health.report, is a call you make yourself with project set to the test chat's folder. A step with no do line changes nothing: go straight to (b). (b) Take a screenshot with save_to_disk true once the screen has settled, and zoom on the chat bar when its marks are too small to read. (c) Copy the saved image into the walk's screens/ folder as <number>-<scenario-slug>.png, numbering the steps of the whole walk from 1. (d) Judge the screenshot against the step's words and its see lines, as Stories acceptance tests says: would a person looking at this screen agree the step happened? A Given's state is visible, a When took effect, a Then shows the right values, labels and messages. The scenario's example values, such as the session name checkout-flow or 116 tools, stand for the test chat's own live values unless a see line says the exact words must show. (e) Call e2e-review.record_verdict with run set to the sub-epic's run_folder, step set to the step's key, step_text set to its keyword and text, screenshot set to screens/<file name>, verdict "meets the intent" or "misses the intent", and the reason in one sentence naming what the screenshot shows."""
        """Step 6 - When a step cannot be done. A do line you cannot carry out, a control that is not on the screen, or a state the Given needs that the test chat cannot be put in: record that step as "misses the intent" with the reason saying what blocked it, skip the rest of that scenario, and go on to the next scenario. Do not invent another way to reach the state, and change no file of the project to make a step pass. Each scenario starts from the test chat as the scenario before left it unless its Given's do lines say otherwise; close any panel or list you opened before the next scenario."""
        """Step 7 - End the walk. Close what the walk opened on the screen, and leave the test chat and its throwaway folder for the person to look at; name both. For each sub-epic walked, name its run folder and count the steps that meet and miss their intent. List every missed step with its reason, and add each one that is a defect of the chat bar, rather than of the test's own do or see lines, to .sessions/_backlog/chat-ui-defects.md. Tell the person the walk has ended and their screen is theirs again. Accept nothing: only the person accepts a walk as the reference, with e2e-review.accept."""
        return "Desktop walk recorded; the person reviews its report."

    def _scenarios_in(self, file: Path) -> list[DesktopScenario]:
        """The scenarios the desktop story test at file holds, each with its steps and their Do and See lines."""
        text = file.read_text(encoding="utf-8")
        named = file.relative_to(self.project).as_posix()
        found: list[DesktopScenario] = []
        for section in ScenarioFileReading(text, named, MarkdownScenario).read():
            for read in section.scenarios:
                scenario = DesktopScenario(section.name.strip(), read.name, named)
                scenario.read_steps(read.steps, text.splitlines())
                found.append(scenario)
        return found
