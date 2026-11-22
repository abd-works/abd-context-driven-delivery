"""session.write_file from a chat working in a ticket's worktree, on a real git main checkout and a real worktree of it:
the twin of ``session_files_spec.py``'s stubbed ``session.write_file`` examples, where the session's folder and its
checkout are given. Here git lists the worktree, so the session's checkout is found as a chat meets it. Heavy: each
example starts git on a throwaway repository of its own."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_false, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentToolSet, ToolsetReference
from space.repo.built_once import BuiltOnce
from space.session import Session, Sessions
from space.session.session import SessionNotFoundError
from space.session.spec_support.throwaway_project import ExampleHome
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

# Seed: the report the debug skill writes in a session's folder, named as it names it.
DEBUG_REPORT = "debug/debug-20261116T225500.md"
DEBUG_TEXT = "# debug" + chr(10)
TICKET = "checkout-flow"
# Seed: a file whose name git writes in quotes with octal escapes unless it is asked for NUL-ended entries.
QUOTED_BY_GIT = "src/ünïcödé_日本.py"


def _git(folder: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


def _main_checkout_with_ticket_worktree(top: Path) -> None:
    """A main checkout with one commit and the ticket's session in its .sessions, and the ticket's worktree on a branch
    of the ticket's name beside it, as ticket.activate opens one."""
    main = top / "main"
    _git(top, "init", "-b", "main", str(main))
    _git(main, "config", "user.email", "board@example.com")
    _git(main, "config", "user.name", "Board")
    (main / "README.md").write_text("project\n", encoding="utf-8")
    _git(main, "add", "README.md")
    _git(main, "commit", "-m", "start")
    folder = main / ".sessions" / TICKET
    folder.mkdir(parents=True)
    (folder / "session.json").write_text(json.dumps({"name": TICKET}), encoding="utf-8")
    _git(main, "worktree", "add", "-b", TICKET, str(top / "worktree"))


_REPOSITORIES = BuiltOnce("cdd-session-files-", _main_checkout_with_ticket_worktree)


with description("SessionFiles") as self:
    with before.each:
        self.home = ExampleHome()
        self.top = _REPOSITORIES.copy()
        self.main = self.top / "main"

    with after.each:
        self.home.close()
        shutil.rmtree(self.top, ignore_errors=True)

    with context("of a session working in a git checkout that holds a file with letters outside ASCII in its name"):
        with before.each:
            (self.main / "src").mkdir()
            (self.main / QUOTED_BY_GIT).write_text("uni = 1" + chr(10), encoding="utf-8")
            _git(self.main, "add", "-A")
            _git(self.main, "commit", "-m", "a file git quotes")
            self.listed = Sessions(self.main).named("main").session_files.under_root()

        with it("should list that file among the files under the session's root"):
            expect([entry.path for entry in self.listed]).to(contain(QUOTED_BY_GIT))


with description("session.write_file") as self:
    with before.each:
        self.home = ExampleHome()
        self.top = _REPOSITORIES.copy()
        # A copied checkout keeps the worktree's links to the folder it was built in: git names them again here.
        _git(self.top / "main", "worktree", "repair", str(self.top / "worktree"))
        self.main, self.worktree = self.top / "main", self.top / "worktree"
        self.folder = self.main / ".sessions" / TICKET
        self.tool = ToolsetReference.of(Session).made().tools["write_file"]

    with after.each:
        self.home.close()
        shutil.rmtree(self.top, ignore_errors=True)

    with context("that names the session by its name, as sessions.switch names it, from a chat in the ticket's worktree"):
        with before.each:
            self.tool.invoke({"session": TICKET, "path": str(self.folder / DEBUG_REPORT), "text": DEBUG_TEXT}, project=self.worktree)

        with it("should save the file in that session's folder in the main checkout"):
            expect((self.folder / DEBUG_REPORT).read_text(encoding="utf-8")).to(equal(DEBUG_TEXT))

        with it("should write nothing into the worktree's own .sessions"):
            expect((self.worktree / ".sessions" / TICKET / DEBUG_REPORT).exists()).to(be_false)

    with context("that names a session the project does not have, from a chat in the ticket's worktree"):
        with it("should refuse rather than write into another session"):
            write = lambda: self.tool.invoke({"session": "no-such-ticket", "path": DEBUG_REPORT, "text": DEBUG_TEXT}, project=self.worktree)
            expect(write).to(raise_error(SessionNotFoundError))
