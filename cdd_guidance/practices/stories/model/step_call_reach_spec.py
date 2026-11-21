"""Which operation a step of a story test in code invokes, when its story file does not import the operation's class:
the class its seed's package holds, the class the file built the receiver as, and never a class the file cannot reach."""

import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph

_TICKET = "class Ticket:\n    def delete(self, board) -> None:\n        board.reread()\n"
_BOARD = "class Board:\n    def reread(self) -> None:\n        return None\n\n    def delete(self) -> None:\n        return None\n"
_EXAMPLES = 'def ticket_on_board(world) -> str:\n    return "checkout"\n'
# A class of another package, which no import of the story tests below leads to, with operations of the same names.
_ARCHIVE = "class Archive:\n    def delete(self) -> None:\n        return None\n\n    def reread(self) -> None:\n        return None\n"

# The shape of Delete Ticket's shared story test: it imports its seed from the package of the code it tests, and calls
# the operation on what the world holds, whose class no line of the file names.
_THROUGH_A_SEED = (
    "from space.kanban.story_test import SharedStories\n"
    "from space.kanban.ticket_story_examples import ticket_on_board\n"
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
    "        world.ticket.reread()\n"
)
# The same package holds two classes with a delete; the file builds the receiver as one of them.
_BUILT_IN_THE_FILE = (
    "from space.kanban.board import Board\n"
    "from space.kanban.ticket import Ticket\n"
    "from story_test import given, scenario, story, when\n"
    "\n"
    'with story("Clear Board"):\n'
    '    with scenario("a board is cleared"):\n'
    '        with given("a board"):\n'
    "            self.board = Board()\n"
    '        with when("the Person clears it"):\n'
    "            self.board.delete()\n"
)
# Two classes in reach declare delete, and no line of the file says which the receiver is.
_UNKNOWN_AMONG_TWO = (
    _BUILT_IN_THE_FILE.replace("self.board = Board()", "self.board = seeded()").replace("Clear Board", "Empty Board").replace("clears it", "empties it")
)
# No import of the file leads to any code that declares the operation.
_NOTHING_IN_REACH = (
    "from story_test import given, scenario, story, when\n"
    "\n"
    'with story("Drop Ticket"):\n'
    '    with scenario("a ticket is dropped"):\n'
    '        with when("the Person drops it"):\n'
    "            self.ticket.delete(self.board)\n"
)

_FILES = {
    "space/kanban/ticket.py": _TICKET,
    "space/kanban/board.py": _BOARD,
    "space/kanban/ticket_story_examples.py": _EXAMPLES,
    "space/archive/archive.py": _ARCHIVE,
    "story_tests/manage-tickets/remove-tickets/delete-ticket.story.shared.py": _THROUGH_A_SEED,
    "story_tests/manage-tickets/clear-board/clear_board_story.test.py": _BUILT_IN_THE_FILE,
    "story_tests/manage-tickets/empty-board/empty_board_story.test.py": _UNKNOWN_AMONG_TWO,
    "story_tests/manage-tickets/drop-ticket/drop_ticket_story.test.py": _NOTHING_IN_REACH,
}


def _invoked_by(graph: Graph, when: str) -> list[str]:
    """What the When called when invokes, each as its file and its class's operation."""
    stories = graph.practices.named("stories").reading.in_graph
    step = next(node for node in stories.nodes("When") if node.name == when)
    return sorted(f"{edge.child.source.file}:{edge.child.get_fact('owner')}.{edge.child.name}" for edge in graph.edges.from_parent("invokes", step))


with description("a step of a story test in code that calls an operation") as self:
    with before.all:
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name).resolve()
        for relative, text in _FILES.items():
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_files(str(root), ["stories", "clean_engineering"], ["space", "story_tests"])

    with context("on what its world holds, in a file that imports only a seed from the package of the code it tests"):
        with it("should invoke the one class of that package that declares the operation, not a class of a package it never imports"):
            expect(_invoked_by(self.graph, "when the Person deletes it")).to(equal(["space/kanban/board.py:Board.reread"]))

    with context("that two classes it imports declare, on a receiver the file builds as one of them"):
        with it("should invoke the operation of the class the file built the receiver as"):
            expect(_invoked_by(self.graph, "when the Person clears it")).to(equal(["space/kanban/board.py:Board.delete"]))

    with context("that two classes it imports declare, on a receiver no line of the file gives a class"):
        with it("should invoke neither"):
            expect(_invoked_by(self.graph, "when the Person empties it")).to(equal([]))

    with context("that no file its imports lead to declares"):
        with it("should invoke nothing"):
            expect(_invoked_by(self.graph, "when the Person drops it")).to(equal([]))
