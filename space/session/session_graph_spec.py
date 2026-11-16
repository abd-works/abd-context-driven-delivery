"""Specs for the edges of the session's graph operations the Files app's graph view calls (session.graph_trees,
graph_branch, graph_node_ranges): what they answer for no file, an unknown node, and every listed file. What the graph view
needs from them, scenario by scenario, is proved by the story tests in
story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/ and
explore-graph-in-files-app/."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.graph.explorer import ExplorerEntry
from harness.guidance.practice_catalogue import PracticeCatalogue
from space.session import Sessions
from space.session.throwaway_project import ExampleHome

PracticeCatalogue.create_all()

# Seed: two files the session's root holds, each one class with one operation, as the Files app lists them from the
# project: the ticket code the branch changed and the board code it did not.
TICKET_FILE = "work/kanban/ticket.py"
TICKET_TEXT = "class Ticket:\n    def activate(self) -> None:\n        return None\n\n    def close(self) -> None:\n        return None\n"
BOARD_FILE = "work/kanban/board.py"
BOARD_TEXT = "class Board:\n    def reread(self) -> None:\n        return None\n"


def _session_with_code():
    """A session working in work/, whose kanban folder holds the ticket and board code, with only Clean Engineering on."""
    repo = Path(tempfile.mkdtemp())
    (repo / ".git").mkdir()
    (repo / "work" / "kanban").mkdir(parents=True)
    (repo / TICKET_FILE).write_text(TICKET_TEXT, encoding="utf-8")
    (repo / BOARD_FILE).write_text(BOARD_TEXT, encoding="utf-8")
    Sessions(repo).switch("checkout-flow", repo / "work")
    session = Sessions(repo).current()
    for key, practice in session.own_practices.items():
        if key != "clean_engineering":
            practice.enable(False)
    return session


def _opened_down_to(session, entries: list, paths: list[str]) -> list:
    """entries with every entry below them read, each branch opened through the session as a person opens it."""
    opened = []
    for entry in entries:
        branch = session.graph_branch(entry.node_id, paths) if entry.children_left_out or not entry.children else entry
        children = [child for child in (branch.children if branch else []) if isinstance(child, ExplorerEntry)]
        opened.append((entry.name, _opened_down_to(session, children, paths)))
    return opened


def _flattened(opened: list) -> list[str]:
    return [name for name, below in opened for name in [name, *_flattened(below)]]


with description("a session's graph"):
    with before.each:
        self.home = ExampleHome()
        self.session = _session_with_code()

    with after.each:
        self.home.close()

    with context("asked for the trees of both code files"):
        with it("should answer the Clean Engineering tree holding both classes"):
            trees = self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            names = _flattened(_opened_down_to(self.session, trees, [TICKET_FILE, BOARD_FILE]))
            expect(names).to(contain("Ticket", "Board"))

    with context("asked for the trees of no file"):
        with it("should answer no tree"):
            expect(self.session.graph_trees([])).to(equal([]))

    with context("asked for the lines of a node it no longer holds"):
        with it("should answer none"):
            expect(self.session.graph_node_ranges("no-such-node", [TICKET_FILE])).to(equal([]))
