"""Specs for the session answering its graph to the Files app's graph view: the practice trees of the files the page
lists, one branch of them, and the lines a node covers in its file.

Scenarios: harness/.context/stories/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/
switch_files_app_between_files_and_graph_story.test.md. The page's own part, the toggle and the tree drawn, is proved by
harness/files_app/app/files/files-graph.spec.ts."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, contain, equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.graph.explorer import ExplorerEntry
from harness.guidance.practice_catalogue import PracticeCatalogue
from space.session import Sessions
from space.session.throwaway_project import ExampleHome

PracticeCatalogue.create_all()

# Seed: two files the session's root holds, each one class with one operation, as the Files app lists them from the
# project: the ticket code the branch changed and the board code it did not.
TICKET_FILE = "work/ticket.py"
TICKET_TEXT = "class Ticket:\n    def activate(self) -> None:\n        return None\n\n    def close(self) -> None:\n        return None\n"
BOARD_FILE = "work/board.py"
BOARD_TEXT = "class Board:\n    def reread(self) -> None:\n        return None\n"


def _session_with_code():
    """A session working in work/, which holds the ticket and board code, with only Clean Engineering on."""
    repo = Path(tempfile.mkdtemp())
    (repo / ".git").mkdir()
    (repo / "work").mkdir()
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


# (E) Switch Files App Between Files And Graph
with description("a session's graph answered to the Files app's graph view"):
    with before.each:
        self.home = ExampleHome()
        self.session = _session_with_code()

    with after.each:
        self.home.close()

    with context("that lists both files"):
        with it("should answer the Clean Engineering tree holding both classes"):
            trees = self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            names = _flattened(_opened_down_to(self.session, trees, [TICKET_FILE, BOARD_FILE]))
            expect(names).to(contain("Ticket", "Board"))

    with context("that lists only the changed ticket code"):
        with it("should keep Ticket and its operations but not Board"):
            trees = self.session.graph_trees([TICKET_FILE])
            names = _flattened(_opened_down_to(self.session, trees, [TICKET_FILE]))
            expect(("Ticket" in names, "activate" in names, "Board" in names)).to(equal((True, True, False)))

    with context("that lists no file"):
        with it("should answer no tree"):
            expect(self.session.graph_trees([])).to(equal([]))

    with context("whose node a person selects"):
        with it("should answer the lines the operation covers in its file, named from the project"):
            self.session.graph_trees([TICKET_FILE])
            activate = next(node for node in self.session.graph.explorer.return_nodes({"name": "activate"}) if node.name == "activate")
            lines = self.session.graph_node_range(activate.node_id)
            expect((lines.path, lines.start_line, lines.end_line)).to(equal((TICKET_FILE, 2, 3)))

        with it("should answer nothing for a node the graph no longer holds"):
            expect(self.session.graph_node_range("no-such-node")).to(be_none)
