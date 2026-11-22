"""SessionFiles - the files a session's calls name, read from its project and refused when they are not there."""

import json
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error

import cdd_guidance.practices  # noqa: F401 - registers the practices a session's file manager reads its roots from
from harness.agent_tools.agent_tools import AgentToolSet, ToolsetReference
from space.session import Session, Sessions
from space.session.session import SessionNotFoundError
from space.session.files.file_manager import PathOutsideRootsError, SessionRecordWriteRefused
from space.session.files.session_files import NamedPathNotFoundError
from space.session.spec_support.throwaway_project import OPEN_PROJECTS, ThrowawayProject

# Seed: the report the debug skill writes in a session's folder, named as it names it.
DEBUG_REPORT = "debug/debug-20261116T225500.md"
DEBUG_TEXT = "# debug" + chr(10)
# Seed: an examples module a story test imports its fixtures from.
EXAMPLES_TEXT = "LISTED = []" + chr(10)


def _working_in(project: Path, root: Path) -> Session:
    """A session of project that works in root, a folder of the project."""
    session = Sessions(project).named("main")
    session.workpath = root
    return session


with description("SessionFiles") as self:
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name).resolve()
        (self.project / "board" / ".context").mkdir(parents=True)
        (self.project / "board" / ".context" / "story-map.md").write_text("# map\n", encoding="utf-8")
        (self.project / "notes.md").write_text("notes\n", encoding="utf-8")
        self.files = _working_in(self.project, self.project / "board").session_files

    with after.each:
        self.tmp.cleanup()

    with context("that is named a path from the project's root"):
        with it("should answer the path in the project"):
            expect(self.files.existing("notes.md")).to(equal(self.project / "notes.md"))

    with context("that is named an absolute path"):
        with it("should answer that path"):
            expect(self.files.existing(str(self.project / "notes.md"))).to(equal(self.project / "notes.md"))

    with context("that is named a path that is not there"):
        with it("should refuse it, naming the path and the project it was read from"):
            expect(lambda: self.files.existing("missing.md")).to(raise_error(NamedPathNotFoundError, f"nothing at missing.md, read from {self.project}; name paths from the project's root, or absolute"))

    with context("that is asked for a path from the session's root"):
        with it("should write a path under the root from that root"):
            expect(self.files.from_root("board/.context/story-map.md")).to(equal(".context/story-map.md"))

        with it("should refuse a path in the project outside the root, naming the root"):
            expect(lambda: self.files.from_root("notes.md")).to(
                raise_error(NamedPathNotFoundError, f"nothing under the session's root {self.project / 'board'} at notes.md, read from {self.project}; name paths from the project's root, or absolute")
            )

        with it("should refuse a path that is not there"):
            expect(lambda: self.files.from_root("board/missing.md")).to(raise_error(NamedPathNotFoundError))

    with context("that writes into the session's record folder, kept outside the folder it works in"):
        # A ticket's session works in its worktree, while its record folder is in the main checkout's .sessions.
        with before.each:
            self.main_checkout = tempfile.TemporaryDirectory()
            self.session_folder = Path(self.main_checkout.name).resolve() / ".sessions" / "checkout-flow"
            session = _working_in(self.project, self.project / "board")
            session.record_folder = self.session_folder
            self.files = session.session_files

        with after.each:
            self.main_checkout.cleanup()

        with it("should save the file in the session's record folder"):
            self.files.write(str(self.session_folder / DEBUG_REPORT), DEBUG_TEXT)
            expect((self.session_folder / DEBUG_REPORT).read_text(encoding="utf-8")).to(equal(DEBUG_TEXT))

        with it("should still refuse a file outside the session's folders and its roots"):
            outside = self.session_folder.parent / "other-session" / DEBUG_REPORT
            expect(lambda: self.files.write(str(outside), DEBUG_TEXT)).to(raise_error(PathOutsideRootsError))


    with context("of a ticket that works in a worktree beside the main checkout, which holds the session"):
        # Seen live 2026-11-17: the Files app opened a scenario whose example is declared in an examples module of the
        # worktree, outside the session's roots, and its range was refused.
        with before.each:
            self.worktree_folder = tempfile.TemporaryDirectory()
            self.worktree = Path(self.worktree_folder.name).resolve()
            (self.worktree / "board").mkdir()
            (self.worktree / "space").mkdir()
            (self.worktree / "space" / "examples.py").write_text(EXAMPLES_TEXT, encoding="utf-8")
            session = Sessions(self.project).create("board-ticket")
            session.record.update(lambda fields: setattr(fields, "worktree", str(self.worktree)), "worktree")
            session.placed().workpath = self.worktree / "board"
            self.files = session.session_files

        with after.each:
            self.worktree_folder.cleanup()

        with it("should read a file anywhere in the worktree, such as an examples module outside its roots"):
            expect(self.files.read(str(self.worktree / "space" / "examples.py")).text).to(equal(EXAMPLES_TEXT))


with description("session.write_file") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".sessions" / "checkout-flow"
        self.folder.mkdir(parents=True)
        (self.folder / "session.json").write_text(json.dumps({"name": "checkout-flow"}), encoding="utf-8")
        self.tool = ToolsetReference.of(Session).made().tools["write_file"]

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("that names the session by its name, as sessions.switch names it"):
        with it("should save the file in that session's folder"):
            self.tool.invoke({"session": "checkout-flow", "path": str(self.folder / DEBUG_REPORT), "text": DEBUG_TEXT}, project=self.project.root)
            expect((self.folder / DEBUG_REPORT).read_text(encoding="utf-8")).to(equal(DEBUG_TEXT))

    with context("that names its session.json"):
        with it("should save the file in that session's folder"):
            self.tool.invoke({"session": ".sessions/checkout-flow/session.json", "path": str(self.folder / DEBUG_REPORT), "text": DEBUG_TEXT}, project=self.project.root)
            expect((self.folder / DEBUG_REPORT).read_text(encoding="utf-8")).to(equal(DEBUG_TEXT))

    with context("that names a session the project does not have"):
        with it("should refuse rather than write into another session"):
            write = lambda: self.tool.invoke({"session": "no-such-ticket", "path": DEBUG_REPORT, "text": DEBUG_TEXT}, project=self.project.root)
            expect(write).to(raise_error(SessionNotFoundError))

    # The person's answer (2026-11-22): the session's record has one writer, the held update, so a write aimed at the
    # session's own session.json is refused whatever way its path is spelt.
    with context("that is aimed at the session's own session.json"):
        with before.each:
            self.record = self.folder / "session.json"
            self.before = self.record.read_text(encoding="utf-8")
            self.write = lambda path: self.tool.invoke({"session": "checkout-flow", "path": path, "text": "{}"}, project=self.project.root)

        with it("should refuse its path from the project, saying to change the record with the session's tools"):
            expect(lambda: self.write(".sessions/checkout-flow/session.json")).to(
                raise_error(SessionRecordWriteRefused, contain("session.json", "the session's tools"))
            )

        with it("should refuse its absolute path"):
            expect(lambda: self.write(str(self.record))).to(raise_error(SessionRecordWriteRefused))

        with it("should refuse its path in another case, where the file system reads that as the same file"):
            # On a file system that tells case apart, such as a cloud session's, that path is another file and is saved.
            same_file = (self.folder.parent / "Checkout-Flow" / "SESSION.JSON").is_file()
            write = lambda: self.write(".sessions/Checkout-Flow/SESSION.JSON")
            expect(write).to(raise_error(SessionRecordWriteRefused)) if same_file else write()
            expect(self.record.read_text(encoding="utf-8")).to(equal(self.before))

        with it("should refuse its path opened with ./"):
            expect(lambda: self.write("./.sessions/checkout-flow/session.json")).to(raise_error(SessionRecordWriteRefused))

        with it("should refuse its path through a parent folder and back"):
            expect(lambda: self.write(".sessions/checkout-flow/debug/../session.json")).to(raise_error(SessionRecordWriteRefused))

        with it("should refuse its path written with backslashes"):
            expect(lambda: self.write(chr(92).join((".sessions", "checkout-flow", "session.json")))).to(raise_error(SessionRecordWriteRefused))

        with it("should leave the record as it was"):
            try:
                self.write(".sessions/checkout-flow/session.json")
            except SessionRecordWriteRefused:
                pass
            expect(self.record.read_text(encoding="utf-8")).to(equal(self.before))

        with it("should still read the record"):
            read = ToolsetReference.of(Session).made().tools["read_file"]
            answered = read.invoke({"session": "checkout-flow", "path": ".sessions/checkout-flow/session.json"}, project=self.project.root)
            expect(answered.text).to(equal(self.before))

    with context("that is aimed at another file named session.json, which is not the session's record"):
        with it("should save it"):
            self.tool.invoke({"session": "checkout-flow", "path": ".sessions/checkout-flow/debug/session.json", "text": "{}"}, project=self.project.root)
            expect((self.folder / "debug" / "session.json").read_text(encoding="utf-8")).to(equal("{}"))


with description("the files of a session's folder, as the Files app lists them") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".sessions" / "checkout-flow"
        self.folder.mkdir(parents=True)
        (self.folder / "session.json").write_text(json.dumps({"name": "checkout-flow"}), encoding="utf-8")
        (self.folder / "session.log").write_text("", encoding="utf-8")
        self.session = Sessions(self.project.root).named("checkout-flow")
        self.listed = lambda: [Path(entry.path).name for entry in self.session.folder_files()]

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("after a change held its session.json"):
        with before.each:
            self.session.add_tag("urgent")

        with it("should leave a lock file beside the record"):
            expect((self.folder / "session.json.lock").is_file()).to(equal(True))

        with it("should list the record and the log, and not the lock file"):
            expect(self.listed()).to(equal(["session.json", "session.log"]))

    with context("with the text a killed writer staged beside its session.json"):
        with it("should not list the staged text"):
            (self.folder / "session.json.4242.1.tmp").write_text("{", encoding="utf-8")
            expect(self.listed()).to(equal(["session.json", "session.log"]))

    with context("with a person's own file whose name ends as a lock file's does"):
        with it("should list it"):
            (self.folder / "notes.lock").write_text("", encoding="utf-8")
            expect(self.listed()).to(equal(["notes.lock", "session.json", "session.log"]))
