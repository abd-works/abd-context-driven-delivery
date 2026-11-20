"""Specs for the edges of the session's graph operations the Files app's graph view calls (session.graph_trees,
graph_branch, graph_node_ranges): what they answer for no file, an unknown node, and every listed file. What the graph view
needs from them, scenario by scenario, is proved by the story tests in
story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/ and
explore-graph-in-files-app/."""
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.graph.explorer import ExplorerEntry
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session import Sessions
from space.session.session_file import VIEWER_SHOWS_LINES, FileTooLongToShowError
from space.session.session_files import NamedPathNotFoundError
from space.session.throwaway_project import ExampleHome

PRACTICE_CATALOGUE.create_all()

# Seed: two files the session's root holds, each one class with one operation, as the Files app lists them from the
# project: the ticket code the branch changed and the board code it did not.
TICKET_FILE = "work/kanban/ticket.py"
TICKET_TEXT = "class Ticket:\n    def activate(self) -> None:\n        return None\n\n    def close(self) -> None:\n        return None\n"
BOARD_FILE = "work/kanban/board.py"
BOARD_TEXT = "class Board:\n    def reread(self) -> None:\n        return None\n"
# Seconds past now a changed file is stamped, so its change is later than the graph's read on any clock.
A_MOMENT_LATER = 5
# The node the graph reads for the folder both files sit in: a package, read from no file's lines.
KANBAN_PACKAGE = "clean_engineering:Package:work/kanban"


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

    with context("asked for the trees of both code files with every practice turned off"):
        with before.each:
            self.session.own_practices["clean_engineering"].enable(False)

        with it("should answer no tree, since no practice reads the files"):
            expect(self.session.graph_trees([TICKET_FILE, BOARD_FILE])).to(equal([]))

    with context("asked for the lines of a node it no longer holds"):
        with it("should answer none"):
            expect(self.session.graph_node_ranges("no-such-node", [TICKET_FILE])).to(equal([]))

    with context("asked for the lines of the folder both code files sit in"):
        with before.each:
            self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            ranges = self.session.graph_node_ranges(KANBAN_PACKAGE, [TICKET_FILE, BOARD_FILE])
            self.lines = {each.path: (each.start_line, each.end_line) for each in ranges}

        with it("should answer each listed file below the folder, at the lines of the classes it holds"):
            expect(self.lines).to(equal({TICKET_FILE: (1, 6), BOARD_FILE: (1, 3)}))

    with context("asked for the lines of that folder once it has gone since the graph read it"):
        with before.each:
            self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            shutil.rmtree(Path(self.session.repo_path) / "work" / "kanban")

        with it("should refuse, naming the folder that is not there"):
            ranges = lambda: self.session.graph_node_ranges(KANBAN_PACKAGE, [TICKET_FILE, BOARD_FILE])
            expect(ranges).to(raise_error(NamedPathNotFoundError, contain("work/kanban")))

    with context("asked for the lines of an operation whose file gained two lines above it since the graph read it"):
        with before.each:
            self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            self.close = next(member.node_id for member in self.session.graph_members() if member.name == "close")
            ticket = Path(self.session.repo_path) / TICKET_FILE
            ticket.write_text("# one\n# two\n" + TICKET_TEXT, encoding="utf-8")
            os.utime(ticket, (time.time() + A_MOMENT_LATER, time.time() + A_MOMENT_LATER))
            ranges = self.session.graph_node_ranges(self.close, [TICKET_FILE, BOARD_FILE])
            self.lines = [(each.path, each.start_line, each.end_line) for each in ranges]

        with it("should answer the operation's lines as the file is now, two lines lower"):
            expect(self.lines).to(equal([(TICKET_FILE, 7, 8)]))

    with context("asked for the lines of a class whose file has gone since the graph read it"):
        with before.each:
            trees = self.session.graph_trees([TICKET_FILE, BOARD_FILE])
            _opened_down_to(self.session, trees, [TICKET_FILE, BOARD_FILE])
            self.ticket_class = next(member.node_id for member in self.session.graph_members() if member.name == "Ticket")
            (Path(self.session.repo_path) / TICKET_FILE).unlink()

        with it("should refuse, naming the file that is not there"):
            ranges = lambda: self.session.graph_node_ranges(self.ticket_class, [TICKET_FILE, BOARD_FILE])
            expect(ranges).to(raise_error(NamedPathNotFoundError, contain("kanban/ticket.py")))

    with context("asked, as the viewer asks, for a file that has gone since a page listed it"):
        with before.each:
            (Path(self.session.repo_path) / TICKET_FILE).unlink()

        with it("should refuse, naming the file that is not there"):
            expect(lambda: self.session.file(TICKET_FILE)).to(raise_error(NamedPathNotFoundError, contain(TICKET_FILE)))

    with context("asked, as the viewer asks, for a file one line longer than the viewer shows"):
        with before.each:
            (Path(self.session.repo_path) / BOARD_FILE).write_text("pass" + chr(10) * VIEWER_SHOWS_LINES + "pass", encoding="utf-8")

        with it("should refuse it, naming the file, its lines and the most the viewer shows"):
            expect(lambda: self.session.file(BOARD_FILE)).to(raise_error(FileTooLongToShowError, contain(BOARD_FILE, f"{VIEWER_SHOWS_LINES + 1:,} lines", f"{VIEWER_SHOWS_LINES:,}")))

    with context("asked, as the viewer asks, for a file as long as the viewer shows"):
        with before.each:
            (Path(self.session.repo_path) / BOARD_FILE).write_text("pass" + chr(10) * (VIEWER_SHOWS_LINES - 1) + "pass", encoding="utf-8")

        with it("should answer its text"):
            expect(self.session.file(BOARD_FILE).text.count(chr(10))).to(equal(VIEWER_SHOWS_LINES - 1))
