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
STORY_MAP_TEXT = "# Story Map\n\n(E) Manage Tickets\n    (E) Remove Tickets\n        (S) Person --> Delete Ticket\n"
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
# Seed: Restore Ticket's story test, in code, for a story the markdown map does not have yet.
RESTORE_TEST = "story_tests/manage-tickets/remove-tickets/restore-ticket/restore_ticket_story.test.py"
RESTORE_TEST_TEXT = STORY_TEST_TEXT.replace("Delete Ticket", "Restore Ticket").replace("deleted", "restored")
LISTED = [STORY_MAP, TICKET_CODE, BOARD_CODE]


def seed_checkout_flow_with_graph_files(world) -> None:
    world.project.seed_session(CHECKOUT_FLOW)
    for path, text in ((TICKET_CODE, TICKET_TEXT), (BOARD_CODE, BOARD_TEXT), (STORY_MAP, STORY_MAP_TEXT), (OLD_MAP, OLD_MAP_TEXT), (STORY_TEST, STORY_TEST_TEXT), (RESTORE_TEST, RESTORE_TEST_TEXT)):
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
