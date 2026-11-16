"""Examples for the Files app's graph view: checkout-flow's code and story maps as the session's graph reads them, and the
session's answers a scenario reads its nodes through. Shared by the story tests of Switch Files App Between Files And
Graph and Explore Graph In Files App."""

from __future__ import annotations

from space.kanban.session_board_examples import SessionSeed

# Seed: checkout-flow working in the whole project with Stories and Clean Engineering on, its Stories root holding its
# story map below the project's own .context, which holds the project's story map.
CHECKOUT_FLOW = SessionSeed(
    "checkout-flow",
    "Checkout flow",
    fields={
        "practices": {key: {"enabled": False} for key in ("ux", "ddd", "bdd")},
        "outputs": {"stories": {"root": "harness/.context/stories"}},
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
# Seed: checkout-flow's story map, in its Stories root.
STORY_MAP = "harness/.context/stories/story-map.md"
STORY_MAP_TEXT = "# Story Map\n\n(E) Manage Tickets\n    (E) Remove Tickets\n        (S) Person --> Delete Ticket\n"
# Seed: the project's own story map, above the session's Stories root.
PROJECT_MAP = ".context/story-map.md"
PROJECT_MAP_TEXT = "# Story Map\n\n(E) Run Whole Project\n    (S) Person --> Open Project\n"
LISTED = [STORY_MAP, TICKET_CODE, BOARD_CODE]


def seed_checkout_flow_with_graph_files(world) -> None:
    world.project.seed_session(CHECKOUT_FLOW)
    for path, text in ((TICKET_CODE, TICKET_TEXT), (BOARD_CODE, BOARD_TEXT), (STORY_MAP, STORY_MAP_TEXT), (PROJECT_MAP, PROJECT_MAP_TEXT)):
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
