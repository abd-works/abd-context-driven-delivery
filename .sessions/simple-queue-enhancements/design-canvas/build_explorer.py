"""Build the story explorer canvas for ticket simple-queue-enhancements: the epic Queue Prompts For Later, its stories and
their scenarios, played on the chat's prompt queue ported from tools/prompt_queue/hooks/queue/.

    python build_explorer.py

The stories are the epic's in the story map (.context/story-map.md, the same twenty the story map drawio shows), with
the scenarios their story_tests files hold. Each scenario's Givens are replayed on the cdd server's real PromptQueue with
the stories' examples (tools/prompt_queue/examples/prompt_queue_examples.py); the queue they leave, and what the mod's
view starts with, become the fixtures the screen loads. The screen runs the mod's own TypeScript, bundled by
queue_domain.mjs, so every button does what the real queue does.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
sys.path.insert(0, str(WORKTREE))

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel  # noqa: E402
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel  # noqa: E402
from cdd_guidance.practices.stories.model.story_model import Epic, StoryModel  # noqa: E402
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryModel, StoryCanvasSetup  # noqa: E402
from cdd_guidance.practices.ux.model.nodes import Screen  # noqa: E402
from cdd_guidance.practices.ux.model.story_link import key_of  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map import UxMap  # noqa: E402
from harness.design_canvas.fixture_bar import FixtureScreen, ScenarioSource  # noqa: E402
from harness.design_canvas.versions import CanvasVersions  # noqa: E402
from tools.prompt_queue import prompt_queue as queue_module  # noqa: E402
from tools.prompt_queue.examples import prompt_queue_examples as examples  # noqa: E402
from tools.prompt_queue.examples.prompt_queue_examples import (  # noqa: E402
    READ_THE_EPIC, RUN_THE_UNIT_TIER, VALIDATE_THE_SCENARIOS, WRITE_THE_SCENARIOS, WRITE_THE_STORIES,
    id_of, seed_queue, steps, three_steps_pending,
)

EPIC = 'Queue Prompts For Later'
MAP = WORKTREE / '.context/story-map.md'
STORY_TESTS = WORKTREE / 'story_tests/queue-prompts-for-later'
SCREEN_FILE = 'prompt-queue.dc.html'
FIXTURES_FILE = 'fixtures/canvas-fixtures.js'
SCREEN_PARTS = HERE / 'prompt_queue_screen'
# What the screen offers when opened on its own: ticking off a card's steps. The fixture bar writes the scenario's name
# into the screen's script unescaped, so it is one whose name holds no quote.
STANDALONE = ScenarioSource('Tick Off Prompt Step', 'Mark one step done', '/')
# The handoff Queue Handoff Steps On Session Start names: session alpha's, with two steps under Approach for Next Agent.
ALPHA_HANDOFF = '# Handoff\n\n## Approach for Next Agent\n\n1. Read the handoff\n2. Run the unit tier\n'


@dataclass
class Givens:
    """What a scenario's Givens leave: the queue the cdd server holds, and what the mod's view starts with: the queue
    open or closed, playing or paused, the prompts whose steps are open, and the prompt the agent was asked to take."""

    queue: queue_module.PromptQueue
    is_expanded: bool = True
    is_playing: bool = False
    open_steps: List[str] = field(default_factory=list)
    asked_about: str = ''

    def fixture(self) -> dict:
        view = {'isExpanded': self.is_expanded, 'isPlaying': self.is_playing, 'openSteps': self.open_steps, 'askedAbout': self.asked_about}
        return {'queue': {'chat': self.queue.chat, 'prompts': self.queue.prompts}, 'view': view}


def _steps_set(queue: queue_module.PromptQueue, planned: list) -> queue_module.PromptQueue:
    """WRITE_THE_SCENARIOS given planned as its steps."""
    return queue.set_steps(id_of(queue, WRITE_THE_SCENARIOS), planned)


def _steps_open(queue: queue_module.PromptQueue, **view) -> Givens:
    """The queue with WRITE_THE_SCENARIOS's steps open under its card."""
    return Givens(queue, open_steps=[id_of(queue, WRITE_THE_SCENARIOS)], **view)


def _asked_to_take(queue: queue_module.PromptQueue, **view) -> Givens:
    """The queue playing, the agent asked to take WRITE_THE_SCENARIOS."""
    return Givens(queue, is_playing=True, asked_about=id_of(queue, WRITE_THE_SCENARIOS), **view)


def _handoff_queued() -> Givens:
    """A chat that switched to alpha once: its queue holds alpha's handoff steps."""
    queue = seed_queue()
    handoff = Path(tempfile.mkdtemp()) / 'alpha-handoff.md'
    handoff.write_text(ALPHA_HANDOFF, encoding='utf-8')
    queue.queue_handoff(handoff)
    return Givens(queue)


def _working_with_first_step(queue: queue_module.PromptQueue) -> Givens:
    """WRITE_THE_SCENARIOS the working prompt, Read the epic being worked and two steps pending, its steps open."""
    _steps_set(queue, steps((READ_THE_EPIC, 'in_progress'), (WRITE_THE_STORIES, 'pending'), (VALIDATE_THE_SCENARIOS, 'pending')))
    return _asked_to_take(queue, open_steps=[id_of(queue, WRITE_THE_SCENARIOS)])


def _progress_shown(queue: queue_module.PromptQueue, **view) -> Givens:
    """WRITE_THE_SCENARIOS with Read the epic done, Write the stories being worked and Validate the scenarios pending."""
    _steps_set(queue, steps((READ_THE_EPIC, 'done'), (WRITE_THE_STORIES, 'in_progress'), (VALIDATE_THE_SCENARIOS, 'pending')))
    return Givens(queue, **view)


# Each scenario's Givens, by story and scenario as their files name them, replayed on the real queue.
GIVENS: Dict[str, Dict[str, Callable[[], Givens]]] = {
    'Queue Prompts Through The Cdd Server': {
        "Queue a list of work on the agent's own chat": lambda: Givens(seed_queue()),
        'Mark a prompt done once its work is done': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER)),
        "Keep each chat's queue apart": lambda: Givens(seed_queue(RUN_THE_UNIT_TIER)),
    },
    'Queue Handoff Steps On Session Start': {
        "Queue the handoff's steps when a chat switches to its session": lambda: Givens(seed_queue()),
        'Queue a handoff once': _handoff_queued,
    },
    'Show Prompt Queue To Agent': {
        'Carry the queue beside each prompt while it plays': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER), is_playing=True),
        'Carry no queue while paused': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS)),
        'Ask for the next prompt when a turn ends': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS), is_playing=True),
        'Pause when the agent left the prompt it was asked to take': lambda: _asked_to_take(seed_queue(WRITE_THE_SCENARIOS)),
    },
    'Set Steps Of Queued Prompt': {
        'Give a queued prompt its steps': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER)),
        "Keep each step's state as given": lambda: Givens(seed_queue(WRITE_THE_SCENARIOS)),
        'Replace the steps a prompt had': lambda: _steps_open(_steps_set(seed_queue(WRITE_THE_SCENARIOS), three_steps_pending())),
        'Refuse steps for a prompt the queue does not hold': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS)),
    },
    'Tick Off Prompt Step': {
        'Mark one step done': lambda: _steps_open(_steps_set(seed_queue(WRITE_THE_SCENARIOS), three_steps_pending())),
        'Leave the prompt on the queue once every step is done': lambda: _steps_open(_steps_set(seed_queue(WRITE_THE_SCENARIOS), steps(
            (READ_THE_EPIC, 'done'), (WRITE_THE_STORIES, 'done'), (VALIDATE_THE_SCENARIOS, 'pending')))),
        'Refuse a step the prompt does not have': lambda: _steps_open(_steps_set(seed_queue(WRITE_THE_SCENARIOS), three_steps_pending())),
    },
    'Copy Task List Onto Working Prompt': {
        'Copy the task list onto the working prompt': lambda: _asked_to_take(seed_queue(WRITE_THE_SCENARIOS)),
        'Follow the task list as the agent ticks it off': lambda: _working_with_first_step(seed_queue(WRITE_THE_SCENARIOS)),
        'Tell the agent to keep the steps itself when its task list cannot be seen': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS), is_playing=True),
    },
    'Queue Sent Prompt As Running': {
        'Put a prompt sent straight to the chat on the queue as running': lambda: Givens(seed_queue(RUN_THE_UNIT_TIER)),
        "Leave play's own request off the queue": lambda: Givens(seed_queue(WRITE_THE_SCENARIOS), is_playing=True),
    },
    'Show Prompt Steps In Queue': {
        "Show each card's progress": lambda: Givens(_steps_set(seed_queue(WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER), steps(
            (READ_THE_EPIC, 'done'), (WRITE_THE_STORIES, 'pending'), (VALIDATE_THE_SCENARIOS, 'pending'))), is_expanded=False),
        "Show a prompt's steps under its card": lambda: _progress_shown(seed_queue(WRITE_THE_SCENARIOS)),
        "Fold a prompt's steps away": lambda: _steps_open(_progress_shown(seed_queue(WRITE_THE_SCENARIOS)).queue),
    },
    'Attach Images To Queued Prompt': {
        "Keep a queued draft's image beside its prompt": lambda: Givens(seed_queue(WRITE_THE_SCENARIOS)),
        'Refuse an image for a prompt the queue does not hold': lambda: Givens(seed_queue(WRITE_THE_SCENARIOS)),
    },
}


def stories_of(epic: Epic) -> list:
    """The epic's stories in map order: its own, then each sub-epic's."""
    return [*epic.stories, *[story for sub in epic.epics for story in sub.stories]]


class QueueCanvas:
    """The canvas of the epic: its stories, the fixtures their scenarios load, and the prompt queue screen."""

    def __init__(self) -> None:
        self.versions = CanvasVersions(HERE)
        self.number = self.versions.working()
        self.folder = self.versions.folder(self.number)
        self.project = self.folder / 'project'
        epic = self._epic()
        self.sources = self._sources(epic)
        self.story_map = self._story_map(epic)

    def _epic(self) -> Epic:
        """The epic as the story map holds it, each story with its scenarios: from the sub-epic scenario files the map
        reads, and from a story's own Python story test where it has no markdown scenarios."""
        full = MarkdownStoryModel.from_workspace(MAP, project=WORKTREE)
        epic: Epic = next(epic for epic in full.epics if epic.name == EPIC)
        coded = {story.name: story for path in sorted(STORY_TESTS.rglob('*_story.test.py'))
                 for story in PythonStoryModel.story_type.load_file(path.read_text(encoding='utf-8'), WORKTREE)}
        for story in stories_of(epic):
            if not story.scenarios and story.name in coded:
                story.scenarios.extend(coded[story.name].scenarios)
        return epic

    def _story_map(self, epic: Epic) -> StoryModel:
        """The epic alone on a story map. The canvas draws only the stories of an epic's innermost sub-epics, so the
        stories that sit on the epic itself, beside its two sub-epics, go first in a column under the epic's own name."""
        own = type(epic)(EPIC, 1)
        own.stories.extend(list(epic.stories))
        epic.stories.refill([])
        epic.epics.insert(0, own)
        scoped = StoryModel()
        scoped.name = EPIC
        scoped.epics.append(epic.clone())
        return scoped

    def build(self) -> dict:
        self.project.mkdir(parents=True, exist_ok=True)
        self._write_fixtures()
        self._write_screen()
        return self._render()

    def _fixtures(self) -> dict:
        """Every scenario's Givens as the screen loads them, refusing a scenario with none so none plays empty."""
        scenarios: dict = {}
        for story in stories_of(self.story_map.epics[0]):
            for scenario in story.scenarios:
                scenarios.setdefault(story.name, {})[scenario.name] = GIVENS[story.name][scenario.name]().fixture()
        named = {name: value for name, value in vars(examples).items() if name.isupper() and isinstance(value, str)}
        return {'scenarios': scenarios, 'examples': named}

    def _write_fixtures(self) -> None:
        held = Path(tempfile.mkdtemp()) / 'fixtures.json'
        held.write_text(json.dumps(self._fixtures(), ensure_ascii=False, indent=1), encoding='utf-8')
        target = self.project / FIXTURES_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['node', str(HERE / 'queue_domain.mjs'), str(WORKTREE), str(target), str(held)], check=True,
                       stderr=subprocess.DEVNULL)

    def _write_screen(self) -> None:
        part = lambda name: (SCREEN_PARTS / name).read_text(encoding='utf-8')  # noqa: E731
        screen = FixtureScreen(
            title='Prompt queue',
            head=f'<script src="../{FIXTURES_FILE}"></script>\n{part("stand-ins.html")}',
            root_class='pq-root',
            body=part('body.html').replace('__STYLE__', part('style.css')),
            source=STANDALONE,
            own_methods=part('methods.js'),
            vals='...this.queueVals()',
            width=1280, height=900,
            artboard=f'/screens/{SCREEN_FILE}',
        )
        target = self.project / 'screens' / SCREEN_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(screen.html, encoding='utf-8', newline='\n')

    def _ux_map(self) -> UxMap:
        """One screen, the prompt queue, showing every story of the epic and each of their steps."""
        screen = Screen('Prompt queue', 1)
        screen.prototype = SCREEN_FILE
        for story in stories_of(self.story_map.epics[0]):
            screen.show_story(story)
            for scenario in story.scenarios:
                for step in scenario.steps:
                    screen.show_step(step)
        mapped = UxMap.create()
        mapped.append_screen(screen)
        return mapped

    def _sources(self, epic: Epic) -> Dict[str, str]:
        """Where each story and scenario sits, as path:line, for the explorer's open-in-file-viewer request; read from
        the epic as loaded, since a copy of the map names no file."""
        found: Dict[str, str] = {}
        for story in stories_of(epic):
            for node, key in [(story, story.name), *[(scenario, key_of(scenario)) for scenario in story.scenarios]]:
                source = getattr(node, 'source', None)
                if source is not None and source.file:
                    found[key] = f'{source.file}:{source.start_line}'
        return found

    def _render(self) -> dict:
        setup = StoryCanvasSetup(workspace=str(self.folder), ux_map=self._ux_map(), sources=self.sources)
        files = json.loads(ClaudeDesignStoryModel().render(self.story_map, setup=setup))
        for path, text in files.items():
            target = self.folder / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8', newline='\n')
        return {'version': self.folder.name, 'files': sorted(files)}


if __name__ == '__main__':
    print(json.dumps(QueueCanvas().build(), indent=1))
