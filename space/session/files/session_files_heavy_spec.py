"""session.all_files and session.write_file on a real git checkout. session.all_files: the twin of
``session_files_spec.py``'s stubbed examples, where a plain folder is walked; here git lists the folder the session works
in, so what .gitignore leaves out is left out. session.write_file from a chat working in a ticket's worktree, on a real git main checkout and a real worktree of it:
the twin of ``session_files_spec.py``'s stubbed ``session.write_file`` examples, where the session's folder and its
checkout are given. Here git lists the worktree, so the session's checkout is found as a chat meets it. Heavy: each
example starts git on a throwaway repository of its own."""

import json
import os
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


# Seed: a session working in board, whose node_modules git ignores, and a folder outside board a person adds to two
# practices from the Files app's file menu.
WORK_FOLDER = "board"
NOTES = "board/notes.txt"
IGNORED_PACKAGE = "board/node_modules/left-pad/index.js"
# Seed: a folder of drafts under the session's folder, and one outside every root, each reached through a link too.
DRAFTS = "board/drafts"
DRAFT = "board/drafts/a.md"
OUTSIDE_NOTE = "outside/keep.md"


def _link(link: Path, target: Path) -> None:
    """A link to the folder target, as a person or a tool makes one: a junction on Windows, where making a symbolic link
    needs a privilege a person seldom has, and a symbolic link elsewhere."""
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)
ADDED_ROOT = "story_tests/checkout"
ADDED_SCENARIOS = "story_tests/checkout/checkout_story.test.md"


with description("session.all_files") as self:
    with before.each:
        self.home = ExampleHome()
        self.top = _REPOSITORIES.copy()
        self.main = self.top / "main"
        for path, text in {".gitignore": "node_modules/" + chr(10), NOTES: "notes" + chr(10), IGNORED_PACKAGE: "module.exports = 1" + chr(10), ADDED_SCENARIOS: "# checkout" + chr(10)}.items():
            (self.main / path).parent.mkdir(parents=True, exist_ok=True)
            (self.main / path).write_text(text, encoding="utf-8")
        _git(self.main, "add", "-A")
        _git(self.main, "commit", "-m", "board and its packages")
        self.session = Sessions(self.main).named("main")
        self.session.workpath = self.main / WORK_FOLDER
        self.listed = lambda: [entry.path for entry in self.session.all_files()]

    with after.each:
        self.home.close()
        shutil.rmtree(self.top, ignore_errors=True)

    with context("of a session working in a folder of a git checkout whose node_modules git ignores"):
        with it("should list the files git tracks there, leaving out every file under node_modules"):
            expect(self.listed()).to(equal([NOTES]))

    with context("with a folder outside it added to two practices"):
        with before.each:
            self.session.practice("stories").add_root(ADDED_ROOT)
            self.session.practice("ddd").add_root(ADDED_ROOT)

        with it("should list each file in that folder once"):
            expect([path for path in self.listed() if path == ADDED_SCENARIOS]).to(equal([ADDED_SCENARIOS]))


    # Defect gizmo-2: git lists the files under an untracked link as files of its own, so All files listed a file twice
    # and listed a file outside every root that the file menu then refused to delete.
    with context("with a link under its folder to a folder in it, and one to a folder outside every root"):
        with before.each:
            for path in (DRAFT, OUTSIDE_NOTE):
                (self.main / path).parent.mkdir(parents=True, exist_ok=True)
                (self.main / path).write_text("x" + chr(10), encoding="utf-8")
            _link(self.main / "board" / "link-in", self.main / DRAFTS)
            _link(self.main / "board" / "link-out", self.main / "outside")

        with it("should list each file once, under its own path"):
            expect([path for path in self.listed() if path.endswith("a.md")]).to(equal([DRAFT]))

        with it("should list nothing reached through the link to the folder outside"):
            expect([path for path in self.listed() if path.endswith("keep.md")]).to(equal([]))

    # Defect gizmo-4: a .git folder kept as a root made git's listing fail, and All files with it.
    with context("with git's own .git folder kept as a root of a practice, as an older version let a person add it"):
        with it("should still list the files of its other roots"):
            self.session.practice("stories").fidelity_outputs[0].keep_roots([self.main / ".git"])
            expect(self.listed()).to(contain(NOTES))


# Defect gizmo-1: a delete of a link followed it and deleted the folder it points to, with every file in it.
with description("session.delete_file of a link") as self:
    with before.each:
        self.home = ExampleHome()
        self.top = _REPOSITORIES.copy()
        self.main = self.top / "main"
        for path in (DRAFT, OUTSIDE_NOTE):
            (self.main / path).parent.mkdir(parents=True, exist_ok=True)
            (self.main / path).write_text("x" + chr(10), encoding="utf-8")
        self.session = Sessions(self.main).named("main")
        self.session.workpath = self.main / WORK_FOLDER

    with after.each:
        self.home.close()
        shutil.rmtree(self.top, ignore_errors=True)

    with context("that is a link under the session's folder to a folder in it"):
        with before.each:
            self.link = self.main / "board" / "link-in"
            _link(self.link, self.main / DRAFTS)
            self.answer = self.session.delete_file("board/link-in")

        with it("should answer the link's own path"):
            expect(self.answer).to(equal("board/link-in"))

        with it("should remove the link"):
            expect(os.path.lexists(self.link)).to(be_false)

        with it("should keep the folder it points to and every file in it"):
            expect((self.main / DRAFT).is_file()).to(equal(True))

    with context("that is held in a folder deleted, pointing outside every root"):
        with it("should keep every file in the folder it points to"):
            _link(self.main / DRAFTS / "link-out", self.main / "outside")
            self.session.delete_file(DRAFTS)
            expect([(self.main / DRAFTS).exists(), (self.main / OUTSIDE_NOTE).is_file()]).to(equal([False, True]))
