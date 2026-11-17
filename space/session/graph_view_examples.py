"""Examples for the Files app's graph view: checkout-flow's code and story maps as the session's graph reads them, and the
session's answers a scenario reads its nodes through. Shared by the story tests of Switch Files App Between Files And
Graph and Explore Graph In Files App."""

from __future__ import annotations

from space.kanban.session_board_examples import SessionSeed

# Seed: checkout-flow working in the whole project with Stories and Clean Engineering on, its Stories root the project's
# .context, where the story map is kept, its scenarios and story tests in story_tests beside it.
CHECKOUT_FLOW = SessionSeed(
    "checkout-flow",
    "Checkout flow",
    fields={
        "practices": {key: {"enabled": False} for key in ("ux", "ddd", "bdd")},
        "outputs": {"stories": {"root": ".context"}},
    },
)
# Seed: checkout-flow as above, working in the folder space, so its story tests under story_tests sit outside the
# session's folder, as a ticket working in harness keeps its story tests in the project's story_tests.
CHECKOUT_FLOW_IN_SPACE = SessionSeed(
    "checkout-flow",
    "Checkout flow",
    workpath="space",
    fields={
        "practices": {key: {"enabled": False} for key in ("ux", "ddd", "bdd")},
        "outputs": {"stories": {"root": "../.context"}},
    },
)
# Seed: checkout-flow as above with Clean Engineering off as well, so its graph reads Stories alone and holds no
# operation a step can invoke, as the main session reads it.
CHECKOUT_FLOW_READING_NO_CODE = SessionSeed(
    CHECKOUT_FLOW.name,
    CHECKOUT_FLOW.title,
    fields={**CHECKOUT_FLOW.fields, "practices": {key: {"enabled": False} for key in ("ux", "ddd", "bdd", "clean_engineering")}},
)
# Seed: the ticket code the branch changed, Ticket with its operations, delete invoking Board.reread.
TICKET_CODE = "space/kanban/ticket.py"
TICKET_TEXT = (
    "class Ticket:\n"
    "    def activate(self) -> None:\n"
    "        return None\n"
    "\n"
    "    def close(self) -> None:\n"
    "        return None\n"
    "\n"
    "    def delete(self, board: Board) -> None:\n"
    "        board.reread()\n"
)
# Seed: the board code the branch did not change, Board with its operation.
BOARD_CODE = "space/kanban/board.py"
BOARD_TEXT = "class Board:\n    def reread(self) -> None:\n        return None\n"
# Seed: checkout-flow's story map, in the project's .context.
STORY_MAP = ".context/story-map.md"
# Its Delete Ticket, on line 5, links to the Story: Delete Ticket heading of its scenarios, as the project's own map does.
STORY_MAP_TEXT = (
    "# Story Map\n\n(E) Manage Tickets\n    (E) Remove Tickets\n"
    "        (S) Person --> [Delete Ticket](../story_tests/manage-tickets/remove-tickets/remove_tickets_story.test.md#story-delete-ticket)\n"
)
STORY_MAP_DELETE_LINE = 5
# Seed: a story map left in a folder's .context from before maps moved to the project's .context.
OLD_MAP = "harness/.context/stories/story-map.md"
OLD_MAP_TEXT = "# Story Map\n\n(E) Run Old Layout\n    (S) Person --> Open Old Map\n"
# Seed: Delete Ticket's story test, in code, in story_tests under its epic and sub-epic.
STORY_TEST = "story_tests/manage-tickets/remove-tickets/delete-ticket/delete_ticket_story.test.py"
STORY_TEST_TEXT = (
    "from story_test import given, scenario, story\n"
    "\n"
    'with story("Delete Ticket"):\n'
    '    with scenario("a ticket is deleted"):\n'
    '        with given("a ticket"):\n'
    "            pass\n"
)
# Seed: Delete Ticket's scenarios, in markdown, in story_tests under its epic and sub-epic: its story's heading on line
# 3, its scenario on lines 5 to 9, its Given on line 7, and its Then on line 9 naming the board, linked to the model.
SCENARIOS = "story_tests/manage-tickets/remove-tickets/remove_tickets_story.test.md"
SCENARIOS_TEXT = (
    "# Sub-epic: Remove Tickets\n"
    "\n"
    "## Story: Delete Ticket\n"
    "\n"
    "#### Scenario: a ticket is deleted\n"
    "\n"
    "*Given* a [ticket](../../../space/kanban/ticket.py) on the board  \n"
    "*When* the Person deletes the ticket's card  \n"
    "*Then* the ticket's card leaves the [board](../../../space/kanban/.context/kanban-model.md#board)\n"
)
SCENARIOS_GIVEN_LINE = 7
# Its When, on line 8, holds an apostrophe, as prose does, which code's quotes would read as a string left open.
SCENARIOS_WHEN_LINE = 8
SCENARIOS_STORY_LINE = 3
SCENARIOS_SCENARIO_LINE = 5
SCENARIOS_THEN_LINE = 9
# Seed: the kanban's class model, in markdown, its Board section on lines 3 to 5.
KANBAN_MODEL = "space/kanban/.context/kanban-model.md"
KANBAN_MODEL_TEXT = "# Kanban Model\n\n### Board\n\n- The board shows every ticket not yet deleted.\n\n### Ticket\n\n- A ticket moves through the stages.\n"
# Seed: Restore Ticket's story test, in code, for a story the markdown map does not have yet.
RESTORE_TEST = "story_tests/manage-tickets/remove-tickets/restore-ticket/restore_ticket_story.test.py"
RESTORE_TEST_TEXT = STORY_TEST_TEXT.replace("Delete Ticket", "Restore Ticket").replace("deleted", "restored")
# Seed: Remove Tickets' shared story test, in Python, its scenarios and steps decorated functions: Delete Ticket's
# first scenario on lines 7 to 15, its Given on lines 9 to 11, its second scenario on lines 18 to 22.
SHARED_STORY = "story_tests/manage-tickets/remove-tickets/remove-tickets.story.shared.py"
SHARED_STORY_TEXT = (
    '"""Remove Tickets: the shared scenarios."""\n'
    'from space.kanban.story_test import SharedStories\n'
    '\n'
    'shared_stories = SharedStories("Remove Tickets")\n'
    '\n'
    '\n'
    '@shared_stories.scenario("Delete Ticket", "a ticket is deleted")\n'
    'def _(s):\n'
    '    @s.given("a ticket on the board")\n'
    '    def _(world):\n'
    '        world.ticket = "checkout"\n'
    '\n'
    '    @s.when("the Person deletes it")\n'
    '    def _(world):\n'
    '        world.deleted = True\n'
    '\n'
    '\n'
    '@shared_stories.scenario("Delete Ticket", "a deleted ticket leaves the board")\n'
    'def _(s):\n'
    '    @s.then("the board no longer shows it")\n'
    '    def _(world):\n'
    '        world.shown = False\n'
)
LISTED = [STORY_MAP, TICKET_CODE, BOARD_CODE]
# Seed: the examples the story test below takes its ticket from, a function of its module, not a class's operation,
# and the constant its Then observes, CHECKOUT_TICKET on line 5.
TICKET_EXAMPLES = "space/kanban/ticket_story_examples.py"
TICKET_EXAMPLES_TEXT = 'def ticket_on_board(world) -> str:\n    return "checkout"\n\n\nCHECKOUT_TICKET = "checkout"\n'
TICKET_EXAMPLES_CONSTANT_LINE = 5
# Seed: Delete Ticket's Python shared story test, its docstring naming the class Ticket on line 1, its Given on line 9
# calling the seed ticket_on_board, its When on line 13 calling Ticket.delete, its Then on line 17 observing the example
# CHECKOUT_TICKET through the file's own helper ticket_left; neither the seed nor the helper is code a step invokes.
STEP_STORY = "story_tests/manage-tickets/remove-tickets/delete-ticket.story.shared.py"
STEP_STORY_TEXT = (
    '"""Delete Ticket: a Ticket leaves the board."""\n'
    "from space.kanban.story_test import SharedStories\n"
    "from space.kanban.ticket_story_examples import CHECKOUT_TICKET, ticket_on_board\n"
    "\n"
    'shared_stories = SharedStories("Remove Tickets")\n'
    "\n"
    '@shared_stories.scenario("Delete Ticket", "a ticket on the board is deleted")\n'
    "def _(s):\n"
    '    @s.given("a ticket on the board")\n'
    "    def _(world):\n"
    "        world.ticket = ticket_on_board(world)\n"
    "\n"
    '    @s.when("the Person deletes it")\n'
    "    def _(world):\n"
    "        world.ticket.delete(world.board)\n"
    "\n"
    '    @s.then("the checkout ticket is gone")\n'
    "    def _(world):\n"
    "        assert ticket_left(world) == CHECKOUT_TICKET\n"
    "\n"
    "\n"
    "def ticket_left(world) -> str:\n"
    "    return world.ticket\n"
    "\n"
    "\n"
    '@shared_stories.scenario("Delete Ticket", "a deleted ticket is looked up")\n'
    "def _(s):\n"
    '    @s.when("the Person looks up the deleted ticket")\n'
    "    def _(world):\n"
    "        world.found = ticket_left(world)\n"
)
# Seed: that story test's second scenario, its When on line 28 calling only the file's own helper ticket_left, so it
# invokes no code it tests.
STEP_STORY_HELPER_WHEN = "when the Person looks up the deleted ticket"
STEP_STORY_DOCSTRING_LINE = 1
STEP_STORY_GIVEN_LINE = 9
STEP_STORY_WHEN_LINE = 13
STEP_LISTED = [STEP_STORY, TICKET_CODE, BOARD_CODE, TICKET_EXAMPLES]
# Seed: Archive Ticket's Python story test, its steps `with` blocks, its When calling Ticket.delete on the ticket its
# Given holds, as the serve-cdd-code-in-lanes story tests call `self.lanes.for_project(...)`.
WITH_STORY = "story_tests/manage-tickets/remove-tickets/archive-ticket/archive_ticket_story.test.py"
WITH_STORY_TEXT = (
    "from story_test import given, scenario, story, when\n"
    "\n"
    'with story("Archive Ticket"):\n'
    '    with scenario("a ticket on the board is archived"):\n'
    '        with given("a ticket on the board"):\n'
    '            self.ticket = "checkout"\n'
    '        with when("the Person archives it"):\n'
    "            # Person -> Ticket.delete(board)\n"
    "            self.ticket.delete(self.board)\n"
)
WITH_LISTED = [WITH_STORY, TICKET_CODE, BOARD_CODE]


def seed_checkout_flow_with_graph_files(world, seed: SessionSeed = CHECKOUT_FLOW) -> None:
    world.project.seed_session(seed)
    for path, text in ((TICKET_CODE, TICKET_TEXT), (BOARD_CODE, BOARD_TEXT), (STORY_MAP, STORY_MAP_TEXT), (OLD_MAP, OLD_MAP_TEXT), (STORY_TEST, STORY_TEST_TEXT), (RESTORE_TEST, RESTORE_TEST_TEXT), (SCENARIOS, SCENARIOS_TEXT), (SHARED_STORY, SHARED_STORY_TEXT), (KANBAN_MODEL, KANBAN_MODEL_TEXT), (TICKET_EXAMPLES, TICKET_EXAMPLES_TEXT), (STEP_STORY, STEP_STORY_TEXT), (WITH_STORY, WITH_STORY_TEXT)):
        world.project.seed_file(path, text)


def session_of(world):
    return world.Ticket.load(CHECKOUT_FLOW.name).session


def node_id_of(world, name: str, paths: list[str]) -> str:
    """The id of the node named name in the trees answered for paths, opening each branch as the page opens it."""
    session = session_of(world)
    found = list(world.data_of(session.graph_trees(paths=paths)))
    while found:
        entry = found.pop()
        if entry["name"] == name:
            return entry["node_id"]
        if entry["children_left_out"]:
            entry = world.data_of(session.graph_branch(node_id=entry["node_id"], paths=paths)) or entry
        found.extend(child for child in entry["children"] if "children_left_out" in child)
    raise AssertionError(f"no node named {name} in the trees of {paths}")
