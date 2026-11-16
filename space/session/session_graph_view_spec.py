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
TICKET_FILE = "work/kanban/ticket.py"
TICKET_TEXT = "class Ticket:\n    def activate(self) -> None:\n        return None\n\n    def close(self) -> None:\n        return None\n"
BOARD_FILE = "work/kanban/board.py"
# Seed: the session's story map, in the Stories root the session names, below its own root.
STORY_MAP_FILE = "work/.context/stories/story-map.md"
STORY_MAP_TEXT = "# Story Map\n\n(E) Manage Customer Orders\n    (E) Place New Order\n        (S) Customer --> Submit Order\n"
# Seed: the project's own story map, in the repository's .context, above the session's root.
PROJECT_MAP_FILE = ".context/story-map.md"
PROJECT_MAP_TEXT = "# Story Map\n\n(E) Run Whole Project\n    (S) Person --> Open Project\n"
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


def _node_named(session, name: str) -> str:
    return next(node for node in session.graph.explorer.return_nodes({"name": name}) if node.name == name).node_id


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
            ranges = self.session.graph_node_ranges(_node_named(self.session, "activate"), [TICKET_FILE])
            expect([(found.path, found.start_line, found.end_line) for found in ranges]).to(equal([(TICKET_FILE, 2, 3)]))

        with it("should answer nothing for a node the graph no longer holds"):
            expect(self.session.graph_node_ranges("no-such-node", [TICKET_FILE])).to(equal([]))

    with context("whose package, a folder, a person selects"):
        with it("should answer each file the folder holds among those listed"):
            self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            module = next(node for node in self.session.graph.explorer.return_nodes({"name": "kanban"}) if node.name == "kanban")
            ranges = self.session.graph_node_ranges(module.node_id, [TICKET_FILE, BOARD_FILE])
            expect(sorted(found.path for found in ranges)).to(equal([BOARD_FILE, TICKET_FILE]))

    with context("whose calls a viewer opens in place"):
        with it("should answer every class and operation the graph holds, across files"):
            self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            names = {member.name for member in self.session.graph_members()}
            expect(names).to(contain("Ticket", "activate", "Board", "reread"))


def _session_with_stories():
    """A session working in work/, whose Stories root, .context/stories, holds a story map, with only Stories on, in a
    project whose own .context holds the project's story map, above the session's root."""
    repo = Path(tempfile.mkdtemp())
    (repo / ".git").mkdir()
    (repo / "work" / ".context" / "stories").mkdir(parents=True)
    (repo / STORY_MAP_FILE).write_text(STORY_MAP_TEXT, encoding="utf-8")
    (repo / ".context").mkdir()
    (repo / PROJECT_MAP_FILE).write_text(PROJECT_MAP_TEXT, encoding="utf-8")
    Sessions(repo).switch("checkout-flow", repo / "work")
    session = Sessions(repo).current()
    for key, practice in session.own_practices.items():
        if key != "stories":
            practice.enable(False)
    session.own_practices["stories"].choose_root("work/.context/stories")
    return session


with description("a session's story map answered to the Files app's graph view"):
    with before.each:
        self.home = ExampleHome()
        self.session = _session_with_stories()

    with after.each:
        self.home.close()

    with context("that lists the story map, read from the Stories root below the session's root"):
        with it("should answer the Stories tree holding its epic and stories"):
            trees = self.session.graph_trees([STORY_MAP_FILE])
            names = _flattened(_opened_down_to(self.session, trees, [STORY_MAP_FILE]))
            expect(names).to(contain("Manage Customer Orders", "Submit Order"))

        with it("should not answer the project's story map, above the session's root"):
            trees = self.session.graph_trees([STORY_MAP_FILE])
            names = _flattened(_opened_down_to(self.session, trees, [STORY_MAP_FILE]))
            expect("Run Whole Project" in names).to(equal(False))
