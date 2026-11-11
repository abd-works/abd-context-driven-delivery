"""Build the story explorer canvas for ticket maintain-tickets-on-board: the stories and their scenarios, played on the
Session Board mockup (harness/.context/ux/Main.dc.html).

    python build_explorer.py <worktree> <version folder> ticket|all

``ticket`` takes this ticket's stories only; ``all`` takes the whole harness story map, every story with the scenarios
its sub-epic file holds. The board is shown for the Session Board stories; it opens the ticket each story is about.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

WORKTREE = Path(sys.argv[1]).resolve()
VERSION = Path(sys.argv[2]).resolve()
SCOPE = sys.argv[3]
sys.path.insert(0, str(WORKTREE))

from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel  # noqa: E402
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryModel  # noqa: E402
from cdd_guidance.practices.ux.model.nodes import Screen  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map import UxMap  # noqa: E402

STORIES = WORKTREE / 'harness/.context/stories'
BOARD_EPIC = 'Move Work Forward On Session Board'
TICKET = {
    'See Work On Session Board': ['Expand Ticket From Empty Area'],
    'Maintain Tickets': ['Edit Ticket Text', 'Reorder Tickets In Column', 'Delete Ticket', 'Tag Ticket Session'],
    'Organize Ticket Hierarchy': ['Add Child Ticket', 'Display Child Tickets In Parent', 'Expand Parent Ticket', 'Detach Child Ticket',
                                  'Reassign Ticket Parent', 'Place Parent At Leftmost Child Stage', 'Nest Child Branch And Session'],
}
KIND = {'Given': StepType.GIVEN, 'When': StepType.WHEN, 'Then': StepType.THEN}

# What the board opens for a story (and, where it differs, a scenario): the ticket it selects and whether its card is open.
FOCUS = {
    'Expand Ticket From Empty Area': {'selected': 'checkout-flow', 'openCard': None},
    'Edit Ticket Text': {'selected': 'checkout-flow', 'openCard': None,
                         'Write the text file for a ticket that has none': {'selected': 'pet-visits', 'openCard': None},
                         'Edit a backlog item\'s text': {'selected': '.sessions/_backlog/gift-cards.md', 'openCard': None}},
    'Reorder Tickets In Column': {'selected': 'pet-visits', 'openCard': 'pet-visits',
                                  'Keep a backlog item where it was moved': {'selected': '.sessions/_backlog/gift-cards.md', 'openCard': None}},
    'Delete Ticket': {'selected': 'pet-visits', 'openCard': 'pet-visits'},
    'Tag Ticket Session': {'selected': 'pet-visits', 'openCard': 'pet-visits'},
    'Add Child Ticket': {'selected': 'pet-visits', 'openCard': 'pet-visits'},
    'Display Child Tickets In Parent': {'selected': 'checkout-flow', 'openCard': 'checkout-flow'},
    'Expand Parent Ticket': {'selected': 'checkout-flow', 'openCard': None,
                             'Collapse a parent to its own card': {'selected': 'checkout-flow', 'openCard': 'checkout-flow'}},
    'Detach Child Ticket': {'selected': 'checkout-flow', 'openCard': 'checkout-flow',
                            'Move a pulled-out child like any ticket': {'selected': 'enter-card-details', 'openCard': 'enter-card-details'}},
    'Reassign Ticket Parent': {'selected': 'checkout-flow', 'openCard': 'checkout-flow'},
    'Place Parent At Leftmost Child Stage': {'selected': 'checkout-flow', 'openCard': None},
    'Nest Child Branch And Session': {'selected': 'checkout-flow', 'openCard': 'checkout-flow'},
}


def plain(text: str) -> str:
    return re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text).strip()


def scenarios_by_story() -> dict:
    """Every story's scenarios, from the sub-epic scenario files under the stories folder."""
    found: dict = {}
    for path in sorted(STORIES.rglob('*_story.test.md')):
        for section in re.split(r'(?m)^(?=#{1,2} Story: )', path.read_text(encoding='utf-8'))[1:]:
            story = plain(section.splitlines()[0].split('Story:', 1)[1])
            scenarios = []
            for order, block in enumerate(re.split(r'(?m)^(?=#### Scenario(?: Outline)?: )', section)[1:], start=1):
                scenario = Scenario(plain(block.splitlines()[0].split(':', 1)[1]), order)
                kind = StepType.GIVEN
                for number, m in enumerate(re.finditer(r'(?m)^\s*\*(Given|When|Then|And|But)\*\s+(.+?)\s*$', block), start=1):
                    word = m.group(1)
                    kind = KIND.get(word, kind)
                    scenario.steps.append(Step(plain(m.group(2)), kind, number, keyword=word))
                scenarios.append(scenario)
            found.setdefault(story, scenarios)
    return found


def story_map() -> StoryModel:
    """The epics, sub-epics and stories of the harness story map, in its order, each story with its scenarios."""
    scenarios = scenarios_by_story()
    model = StoryModel()
    stack: list = []
    for line in (STORIES / 'story-map.md').read_text(encoding='utf-8').splitlines():
        epic = re.match(r'^(#+) \(E\) (.+)$', line)
        story = re.match(r'^(#+) \(S[^)]*\) (.+?) --> (.+)$', line)
        if epic:
            depth = len(epic.group(1))
            node = Epic(plain(epic.group(2)), 1)
            stack = stack[:depth - 1]
            (stack[-1].append_epic(node) if stack else model.append_epic(node))
            stack.append(node)
        elif story and stack:
            node = Story(plain(story.group(3)), len(stack[-1].stories) + 1)
            node.actors.append(plain(story.group(2)))
            node.scenarios.extend(scenarios.get(node.name, []))
            stack[-1].append_story(node)
    return model


def ticket_only(model: StoryModel) -> StoryModel:
    """This ticket's stories under their sub-epics, in map order."""
    scoped = StoryModel()
    board = next(epic for epic in model.epics if epic.name == BOARD_EPIC)
    kept = Epic(board.name, 1)
    for sub in board.epics:
        if sub.name in TICKET:
            copy = Epic(sub.name, len(kept.epics) + 1)
            for story in sub.stories:
                if story.name in TICKET[sub.name]:
                    copy.append_story(story)
            kept.append_epic(copy)
    scoped.append_epic(kept)
    return scoped


def board_screen(project: Path) -> None:
    """The Session Board mockup as the explorer's screen: it takes the explorer's story and scenario and opens the
    ticket that story is about."""
    board = (WORKTREE / 'harness/.context/ux/Main.dc.html').read_text(encoding='utf-8')
    board = board.replace('<title>CDD Session Board</title>', '<title>Session Board</title>', 1)
    board = board.replace("data-props='{", "data-props='{\"story\":{\"editor\":null},\"scenario\":{\"editor\":null},\"go\":{\"editor\":null},", 1)
    follow = ('const STORY_FOCUS = ' + json.dumps(FOCUS, ensure_ascii=False) + ';\n'
              'function storyFocus(story, scenario) {\n'
              '  const focus = STORY_FOCUS[story];\n'
              '  if (!focus) return null;\n'
              '  const own = focus[scenario];\n'
              '  return own || { selected: focus.selected, openCard: focus.openCard };\n'
              '}\n')
    board = board.replace('class Component extends DCLogic {', follow + 'class Component extends DCLogic {', 1)
    hooks = ('  pinnedPlace = null;\n\n'
             '  componentDidMount() { this.followStory(); }\n'
             '  componentDidUpdate(previous) {\n'
             '    if (previous.story !== this.props.story || previous.scenario !== this.props.scenario) this.followStory();\n'
             '  }\n'
             '  followStory() {\n'
             '    const focus = storyFocus(this.props.story, this.props.scenario);\n'
             '    if (focus) this.setState({ selected: focus.selected, openCard: focus.openCard, cardClosing: false, expansion: null });\n'
             '  }\n')
    assert board.count('  pinnedPlace = null;\n') == 1
    board = board.replace('  pinnedPlace = null;\n', hooks, 1)
    target = project / 'screens/session-board.dc.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(board, encoding='utf-8', newline='\n')


def ux_map(model: StoryModel) -> UxMap:
    screen = Screen('Session board', 1)
    screen.prototype = 'session-board.dc.html'
    for epic in model.epics:
        if epic.name != BOARD_EPIC:
            continue
        for sub in [epic, *epic.all_epics()] if hasattr(epic, 'all_epics') else [epic, *epic.epics]:
            for story in sub.stories:
                screen.show_story(story.name)
            for nested in getattr(sub, 'epics', []):
                for story in nested.stories:
                    screen.show_story(story.name)
    mapped = UxMap.create()
    mapped.append_screen(screen)
    return mapped


full = story_map()
model = ticket_only(full) if SCOPE == 'ticket' else full
model.name = 'Maintain Tickets On Board' if SCOPE == 'ticket' else 'CDD Harness Story Map'
project = VERSION / 'project'
for stale in project.rglob('*') if project.exists() else []:
    if stale.is_file():
        stale.unlink()
project.mkdir(parents=True, exist_ok=True)
board_screen(project)
files = json.loads(ClaudeDesignStoryModel().render(model, workspace=str(VERSION), ux_map=ux_map(model)))
for path, text in files.items():
    target = VERSION / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8', newline='\n')
stories = sum(len(sub.stories) for epic in model.epics for sub in [epic, *epic.epics])
print(json.dumps({'files': sorted(str(p.relative_to(VERSION)).replace('\\', '/') for p in project.rglob('*') if p.is_file()),
                  'epics': len(model.epics)}, indent=1))
