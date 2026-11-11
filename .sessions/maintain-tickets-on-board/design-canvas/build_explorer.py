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
    'Add Child Ticket': {'selected': 'checkout-flow', 'openCard': 'checkout-flow'},
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


# How the board plays each scenario of this ticket: `given` sets up what the Givens say (from the board's seed), `act`
# does what the When does; both take the tickets and backlog and return the changes. The board shows the Given state
# up to the When step, and the result from the When on.
PLAYS = r'''
const IDS = { flow: 'checkout-flow', card: 'enter-card-details', order: 'confirm-order', pets: 'pet-visits', signUp: 'sign-up', billing: 'billing-report' };
const GIFT = '.sessions/_backlog/gift-cards.md', RETURNS = '.sessions/_backlog/returns-and-refunds.md';
const change = (tickets, id, fields) => tickets.map(t => (t.id === id ? Object.assign({}, t, fields) : t));
const stacked = tickets => change(change(tickets, IDS.card, { column: 'Discovery', done: false, pulledOut: false, parent: IDS.flow }), IDS.order, { column: 'Discovery', done: false, parent: IDS.flow });
const before = (list, key, moving, anchor) => {
  const item = list.find(x => x[key] === moving);
  const rest = list.filter(x => x[key] !== moving);
  const at = rest.findIndex(x => x[key] === anchor);
  return [...rest.slice(0, at), item, ...rest.slice(at)];
};
const PLAYS = {
  'Expand Ticket From Empty Area': {
    'Expand a card from an empty area': { act: () => ({ openCard: IDS.flow }) },
    "Leave a card's controls to do their own work": { act: () => ({ message: "The stories tile opens; checkout-flow's card stays collapsed." }) },
  },
  'Edit Ticket Text': {
    "Show a ticket's text from its session file": { act: () => ({ selected: IDS.flow }) },
    "Edit a ticket's text": { act: s => ({ tickets: change(s.tickets, IDS.flow, { text: 'Pay for the basket by card.' }), message: 'Saved to .sessions/checkout-flow/checkout-flow.md' }) },
    'Write the text file for a ticket that has none': { act: s => ({ tickets: change(s.tickets, IDS.pets, { text: 'Book a visit for a pet.' }), message: 'Wrote .sessions/pet-visits/pet-visits.md' }) },
    "Edit a backlog item's text": { act: s => ({ backlog: s.backlog.map(b => (b.path === GIFT ? Object.assign({}, b, { body: 'Sell gift cards at the till.' }) : b)), message: 'Saved to .sessions/_backlog/gift-cards.md' }) },
  },
  'Reorder Tickets In Column': {
    'Keep a ticket where it was moved in its column': { act: s => ({ tickets: before(s.tickets, 'id', IDS.signUp, IDS.pets), selected: IDS.signUp, openCard: IDS.signUp, message: 'sign-up now sits above pet-visits in Discovery' }) },
    'Keep a backlog item where it was moved': { act: s => ({ backlog: before(s.backlog, 'path', RETURNS, GIFT), selected: RETURNS, message: 'Returns and refunds now sits above Gift cards' }) },
  },
  'Delete Ticket': {
    'Delete a ticket and its session folder': { act: s => ({ tickets: s.tickets.filter(t => t.id !== IDS.pets), selected: null, openCard: null, message: 'Deleted pet-visits; .sessions/pet-visits is gone' }) },
    'Refuse to delete a ticket the board does not have': { act: () => ({ message: "No ticket named 'no-such-ticket' on the board; no session folder is removed" }) },
  },
  'Tag Ticket Session': {
    "Tag a ticket's session": { given: s => ({ tickets: change(s.tickets, IDS.pets, { tags: [] }) }), act: s => ({ tickets: change(s.tickets, IDS.pets, { tags: ['billing'] }) }) },
    'Add a second tag': { given: s => ({ tickets: change(s.tickets, IDS.pets, { tags: ['billing'] }) }), act: s => ({ tickets: change(s.tickets, IDS.pets, { tags: ['billing', 'urgent'] }) }) },
  },
  'Add Child Ticket': {
    'Add a child ticket by hand': {
      given: s => ({ tickets: s.tickets.filter(t => t.parent !== IDS.flow), selected: IDS.flow, openCard: IDS.flow }),
      act: s => ({ tickets: [...s.tickets, { id: IDS.card, title: 'Enter card details', column: 'Discovery', age: 'just now', progress: [IDLE, IDLE, IDLE], handoff: '', text: '', tags: [], parent: IDS.flow }], message: 'Opened enter-card-details in Discovery as a child of checkout-flow' }),
    },
  },
  'Display Child Tickets In Parent': {
    "Stack a parent's children inside its card": { given: s => ({ tickets: stacked(s.tickets), openCard: null }), act: () => ({ selected: IDS.flow, openCard: IDS.flow }) },
    'Keep a dashed row for a child pulled out of its parent': { given: () => ({ openCard: null }), act: () => ({ selected: IDS.flow, openCard: IDS.flow }) },
  },
  'Expand Parent Ticket': {
    'Expand a parent to show its children': { given: s => ({ tickets: stacked(s.tickets), selected: IDS.flow, openCard: null }), act: () => ({ openCard: IDS.flow }) },
    'Collapse a parent to its own card': { given: s => ({ tickets: stacked(s.tickets), selected: IDS.flow, openCard: IDS.flow }), act: () => ({ openCard: null }) },
  },
  'Detach Child Ticket': {
    'Pull a child out of its parent': { given: s => ({ tickets: stacked(s.tickets), selected: IDS.flow, openCard: IDS.flow }), act: s => ({ tickets: change(s.tickets, IDS.card, { pulledOut: true }), selected: IDS.card, message: 'enter-card-details is a card of its own; checkout-flow keeps a dashed row' }) },
    'Move a pulled-out child like any ticket': { given: s => ({ tickets: change(s.tickets, IDS.card, { column: 'Discovery', done: true, pulledOut: true }), selected: IDS.card }), act: s => ({ tickets: change(s.tickets, IDS.card, { column: 'Specification', done: false }), message: 'enter-card-details moved to Specification; its parent is still checkout-flow' }) },
  },
  'Reassign Ticket Parent': {
    'Move a child to another parent': { given: s => ({ tickets: stacked(s.tickets), selected: IDS.flow, openCard: IDS.flow }), act: s => ({ tickets: change(s.tickets, IDS.card, { parent: IDS.billing }), selected: IDS.billing, openCard: IDS.billing, message: 'enter-card-details is now a child of billing-report' }) },
    'Take a child off its parent': { given: s => ({ tickets: stacked(s.tickets), selected: IDS.flow, openCard: IDS.flow }), act: s => ({ tickets: change(s.tickets, IDS.card, { parent: undefined, pulledOut: false }), message: 'enter-card-details has no parent' }) },
  },
  'Place Parent At Leftmost Child Stage': {
    "Show a parent in its earliest child's stage": { act: () => ({ selected: IDS.flow }) },
    'Move a parent on when its last child moves on': { act: s => ({ tickets: change(s.tickets, IDS.order, { column: 'Specification', done: false }), selected: IDS.flow, message: 'Checkout flow moves with it to Specification' }) },
    'Refuse to move a parent by hand': { act: () => ({ selected: IDS.flow, openCard: IDS.flow, message: 'a parent moves with its children; checkout-flow stays in Discovery' }) },
  },
  'Nest Child Branch And Session': {
    "Nest a child's session and branch under its parent's": { act: () => ({ selected: IDS.card, openCard: IDS.card, message: 'enter-card-details: session .sessions/checkout-flow/enter-card-details, branch checkout-flow.enter-card-details' }) },
  },
};
'''


def steps_of(model: StoryModel) -> dict:
    """Each scenario's steps as the explorer shows them, by story then scenario: the When's place in them decides
    whether the board shows the Given state or the result."""
    found: dict = {}
    for epic in model.epics:
        for sub in [epic, *epic.epics, *[n for e in epic.epics for n in e.epics]]:
            for story in sub.stories:
                for scenario in story.scenarios:
                    found.setdefault(story.name, {})[scenario.name] = [f'{step.keyword} {step.text}' for step in scenario.steps]
    return found


def board_screen(project: Path, model: StoryModel) -> None:
    """The Session Board mockup as the explorer's screen: it takes the explorer's story, scenario and step, opens the
    ticket the story is about, and plays the scenario up to that step."""
    board = (WORKTREE / 'harness/.context/ux/Main.dc.html').read_text(encoding='utf-8')
    board = board.replace('<title>CDD Session Board</title>', '<title>Session Board</title>', 1)
    board = board.replace("data-props='{", "data-props='{\"story\":{\"editor\":null},\"scenario\":{\"editor\":null},\"step\":{\"editor\":null},\"go\":{\"editor\":null},", 1)
    follow = ('const STORY_FOCUS = ' + json.dumps(FOCUS, ensure_ascii=False) + ';\n'
              'const SCENARIO_STEPS = ' + json.dumps(steps_of(model), ensure_ascii=False) + ';\n'
              + PLAYS +
              'function storyFocus(story, scenario) {\n'
              '  const focus = STORY_FOCUS[story];\n'
              '  if (!focus) return null;\n'
              '  const own = focus[scenario];\n'
              '  return own || { selected: focus.selected, openCard: focus.openCard };\n'
              '}\n'
              'function stepPlace(story, scenario, step) {\n'
              '  const steps = (SCENARIO_STEPS[story] || {})[scenario] || [];\n'
              '  const shown = String(step || "").split("\\n").map(line => line.trim()).filter(Boolean).pop() || "";\n'
              '  const at = steps.findIndex(line => line === shown);\n'
              '  const when = steps.findIndex(line => line.startsWith("When "));\n'
              '  return { at, when };\n'
              '}\n')
    board = board.replace('class Component extends DCLogic {', follow + 'class Component extends DCLogic {', 1)
    hooks = ('  pinnedPlace = null;\n\n'
             '  componentDidMount() { this.seed = { tickets: this.state.tickets, backlog: this.state.backlog }; this.followStory(); }\n'
             '  componentDidUpdate(previous) {\n'
             '    const { story, scenario, step } = this.props;\n'
             '    if (previous.story !== story || previous.scenario !== scenario || previous.step !== step) this.followStory();\n'
             '  }\n'
             '  followStory() {\n'
             '    const { story, scenario, step } = this.props;\n'
             '    const focus = storyFocus(story, scenario);\n'
             '    if (!focus) return;\n'
             '    let s = { tickets: (this.seed || this.state).tickets, backlog: (this.seed || this.state).backlog, selected: focus.selected, openCard: focus.openCard, message: "" };\n'
             '    const play = (PLAYS[story] || {})[scenario];\n'
             '    if (play && play.given) s = Object.assign(s, play.given(s));\n'
             '    const { at, when } = stepPlace(story, scenario, step);\n'
             '    if (play && play.act && when >= 0 && at >= when) s = Object.assign(s, play.act(s));\n'
             '    this.setState(Object.assign({}, s, { tickets: settleParents(s.tickets), cardClosing: false, expansion: null, editingText: null }));\n'
             '  }\n')
    assert board.count('  pinnedPlace = null;\n') == 1
    board = board.replace('  pinnedPlace = null;\n', hooks, 1)
    target = project / 'screens/session-board.dc.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(board, encoding='utf-8', newline='\n')


def ux_map(model: StoryModel) -> UxMap:
    """The board screen shows every Session Board story, each of its steps on its own so the explorer can step
    through it."""
    screen = Screen('Session board', 1)
    screen.prototype = 'session-board.dc.html'
    for epic in model.epics:
        if epic.name != BOARD_EPIC:
            continue
        for sub in [epic, *epic.epics, *[n for e in epic.epics for n in e.epics]]:
            for story in sub.stories:
                screen.show_story(story.name)
                for scenario in story.scenarios:
                    for step in scenario.steps:
                        screen.show_step(f'{story.name} › {scenario.name} › {step.text}')
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
board_screen(project, model)
files = json.loads(ClaudeDesignStoryModel().render(model, workspace=str(VERSION), ux_map=ux_map(model)))
for path, text in files.items():
    target = VERSION / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8', newline='\n')
stories = sum(len(sub.stories) for epic in model.epics for sub in [epic, *epic.epics])
print(json.dumps({'files': sorted(str(p.relative_to(VERSION)).replace('\\', '/') for p in project.rglob('*') if p.is_file()),
                  'epics': len(model.epics)}, indent=1))
