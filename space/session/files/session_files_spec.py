"""SessionFiles - the files a session's calls name, read from its project and refused when they are not there."""

import json
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error

import cdd_guidance.practices  # noqa: F401 - registers the practices a session's file manager reads its roots from
from harness.agent_tools.agent_tools import AgentToolSet, ToolsetReference
from space.session import Session, Sessions
from space.session.session import SessionNotFoundError
from space.session.files.file_manager import FileChangedSinceReadError, PathOutsideRootsError, SessionRecordWriteRefused, VersionControlPathRefused
from space.session.files.session_files import NamedPathNotFoundError, RootDeleteRefused
from space.session.spec_support.throwaway_project import OPEN_PROJECTS, ThrowawayProject

# Seed: the report the debug skill writes in a session's folder, named as it names it.
DEBUG_REPORT = "debug/debug-20261116T225500.md"
DEBUG_TEXT = "# debug" + chr(10)
# Seed: an examples module a story test imports its fixtures from.
EXAMPLES_TEXT = "LISTED = []" + chr(10)
# Seed: a cart module as read, as someone else changed it on disk, and as an agent saves it.
CART_TEXT = "class Cart:" + chr(10) + "    items = []" + chr(10)
CHANGED_CART_TEXT = "class Cart:" + chr(10) + "    CHANGED_ON_DISK = True" + chr(10)
SAVED_CART_TEXT = "class Cart:" + chr(10) + "    pass" + chr(10)


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


# The person's answer (2026-11-23, pixel-05): the repository's .git folder holds git's own record, its config and the
# hooks git runs on the next commit, so no file call reads or writes inside it.
with description("session.read_file and session.write_file, on a path inside the repository's .git folder") as self:
    with before.each:
        self.project = ThrowawayProject()
        (self.project.root / ".sessions" / "checkout-flow").mkdir(parents=True)
        (self.project.root / ".sessions" / "checkout-flow" / "session.json").write_text(json.dumps({"name": "checkout-flow"}), encoding="utf-8")
        (self.project.root / ".git").mkdir(exist_ok=True)
        (self.project.root / ".git" / "config").write_text("[core]" + chr(10), encoding="utf-8")
        tools = ToolsetReference.of(Session).made().tools
        self.read = lambda path: tools["read_file"].invoke({"session": "checkout-flow", "path": path}, project=self.project.root)
        self.write = lambda path: tools["write_file"].invoke({"session": "checkout-flow", "path": path, "text": "x"}, project=self.project.root)

    with after.each:
        OPEN_PROJECTS.close_all()

    with it("should refuse to read .git/config, naming the path"):
        expect(lambda: self.read(".git/config")).to(raise_error(VersionControlPathRefused, contain(".git/config", "git's own")))

    with it("should refuse to write a hook git would run on the next commit"):
        expect(lambda: self.write(".git/hooks/pre-commit")).to(raise_error(VersionControlPathRefused, contain(".git/hooks/pre-commit")))

    with it("should write nothing there"):
        try:
            self.write(".git/hooks/pre-commit")
        except VersionControlPathRefused:
            pass
        expect((self.project.root / ".git" / "hooks" / "pre-commit").exists()).to(equal(False))

    with it("should refuse the path written with a .git folder deeper down, such as a nested repository's"):
        expect(lambda: self.write("vendor/lib/.git/config")).to(raise_error(VersionControlPathRefused))

    with it("should refuse the path in another case, which Windows reads as the same folder"):
        expect(lambda: self.read(".GIT/config")).to(raise_error(VersionControlPathRefused))

    with it("should still save a file whose name only starts with .git, such as .gitignore"):
        self.write(".gitignore")
        expect((self.project.root / ".gitignore").read_text(encoding="utf-8")).to(equal("x"))


# The person's answer (2026-11-23, pixel-06): read_file answers the version of the file it read, and write_file takes it
# back; a file changed on disk since then is refused, so a change someone else made is never written over unseen.
with description("session.write_file, on a file that read_file read") as self:
    with before.each:
        self.project = ThrowawayProject()
        (self.project.root / ".sessions" / "checkout-flow").mkdir(parents=True)
        (self.project.root / ".sessions" / "checkout-flow" / "session.json").write_text(json.dumps({"name": "checkout-flow"}), encoding="utf-8")
        self.cart = self.project.root / "src" / "cart.py"
        self.cart.parent.mkdir(parents=True)
        self.cart.write_text(CART_TEXT, encoding="utf-8")
        tools = ToolsetReference.of(Session).made().tools
        self.read = lambda: tools["read_file"].invoke({"session": "checkout-flow", "path": "src/cart.py"}, project=self.project.root)
        self.write = lambda path, version: tools["write_file"].invoke({"session": "checkout-flow", "path": path, "text": SAVED_CART_TEXT, "version": version}, project=self.project.root)

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("that is as it was read"):
        with before.each:
            self.saved = self.write("src/cart.py", self.read().version)

        with it("should save the text"):
            expect(self.cart.read_text(encoding="utf-8")).to(equal(SAVED_CART_TEXT))

        with it("should answer the version of the file as saved, which a read now answers too"):
            expect(self.saved.version).to(equal(self.read().version))

    with context("that changed on disk since it was read"):
        with before.each:
            self.version = self.read().version
            self.cart.write_text(CHANGED_CART_TEXT, encoding="utf-8")

        with it("should refuse the write, saying the file changed since it was read"):
            expect(lambda: self.write("src/cart.py", self.version)).to(raise_error(FileChangedSinceReadError, contain("src/cart.py", "changed on disk since it was read")))

        with it("should keep the change made on disk"):
            try:
                self.write("src/cart.py", self.version)
            except FileChangedSinceReadError:
                pass
            expect(self.cart.read_text(encoding="utf-8")).to(equal(CHANGED_CART_TEXT))

    with context("that is on disk, written with no version, as by a caller that never read it"):
        with it("should refuse the write"):
            expect(lambda: self.write("src/cart.py", "")).to(raise_error(FileChangedSinceReadError))

    with context("that was deleted since it was read"):
        with it("should refuse the write"):
            version = self.read().version
            self.cart.unlink()
            expect(lambda: self.write("src/cart.py", version)).to(raise_error(FileChangedSinceReadError))

    with context("that is not there yet, written with no version"):
        with it("should save the new file"):
            self.write("src/checkout.py", "")
            expect((self.project.root / "src" / "checkout.py").read_text(encoding="utf-8")).to(equal(SAVED_CART_TEXT))

    with context("that a read answered as not there, written with that read's version"):
        with it("should save the new file"):
            read = ToolsetReference.of(Session).made().tools["read_file"]
            missing = read.invoke({"session": "checkout-flow", "path": "src/checkout.py"}, project=self.project.root)
            self.write("src/checkout.py", missing.version)
            expect((self.project.root / "src" / "checkout.py").is_file()).to(equal(True))


# The person's answer (2026-11-26): the Files app's file menu deletes a file or a folder, after a confirmation the page
# asks; what may be deleted is the session's rule: only what lies under its roots, never a root itself, never its own
# session.json or a folder holding it, and nothing inside a .git folder.
with description("session.delete_file") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".sessions" / "checkout-flow"
        self.folder.mkdir(parents=True)
        (self.folder / "session.json").write_text(json.dumps({"name": "checkout-flow"}), encoding="utf-8")
        self.cart = self.project.root / "src" / "cart.py"
        self.cart.parent.mkdir(parents=True)
        self.cart.write_text(CART_TEXT, encoding="utf-8")
        self.drafts = self.project.root / "src" / "drafts"
        self.drafts.mkdir()
        (self.drafts / "one.md").write_text("one", encoding="utf-8")
        (self.drafts / "two.md").write_text("two", encoding="utf-8")
        tool = ToolsetReference.of(Session).made().tools["delete_file"]
        self.delete = lambda path: tool.invoke({"session": "checkout-flow", "path": path}, project=self.project.root)

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("that names a file under the session's roots"):
        with it("should delete the file"):
            self.delete("src/cart.py")
            expect(self.cart.exists()).to(equal(False))

        with it("should answer the path deleted, from the project"):
            expect(self.delete("src/cart.py")).to(equal("src/cart.py"))

    with context("that names a folder"):
        with it("should delete the folder and every file in it"):
            self.delete("src/drafts")
            expect(self.drafts.exists()).to(equal(False))

    with context("that names a file that is not there"):
        with it("should refuse it, naming the path"):
            expect(lambda: self.delete("src/missing.py")).to(raise_error(NamedPathNotFoundError, contain("src/missing.py")))

    with context("that names the folder the session works in"):
        with it("should refuse to delete a root"):
            expect(lambda: self.delete(str(self.project.root))).to(raise_error(RootDeleteRefused))

    with context("that names the session's own session.json"):
        with it("should refuse it and keep the record"):
            expect(lambda: self.delete(".sessions/checkout-flow/session.json")).to(raise_error(SessionRecordWriteRefused))
            expect((self.folder / "session.json").is_file()).to(equal(True))

    with context("that names the folder holding the session's session.json"):
        with it("should refuse it and keep the folder"):
            expect(lambda: self.delete(".sessions/checkout-flow")).to(raise_error(SessionRecordWriteRefused))
            expect((self.folder / "session.json").is_file()).to(equal(True))

    with context("that names a file inside a .git folder"):
        with it("should refuse it"):
            (self.project.root / ".git").mkdir(exist_ok=True)
            (self.project.root / ".git" / "config").write_text("[core]" + chr(10), encoding="utf-8")
            expect(lambda: self.delete(".git/config")).to(raise_error(VersionControlPathRefused))

    with context("that names a file outside the session's roots"):
        with it("should refuse it, keeping the file"):
            outside = tempfile.TemporaryDirectory()
            kept = Path(outside.name) / "kept.md"
            kept.write_text("kept", encoding="utf-8")
            expect(lambda: self.delete(str(kept))).to(raise_error((PathOutsideRootsError, NamedPathNotFoundError)))
            expect(kept.is_file()).to(equal(True))
            outside.cleanup()


# The person's answer (2026-11-26): the Files app's All files button lists every file in the session's folders, the
# folder it works in and each root a person added to its practices, whatever the stages, practices and formats selected.
with description("session.all_files") as self:
    with before.each:
        self.project = ThrowawayProject()
        root = self.project.root
        for path, text in {"board/notes.txt": "notes", "board/.context/story-map.md": "# map", "story_tests/checkout/checkout_story.test.md": "# checkout", "story_tests/other/other_story.test.md": "# other", "README.md": "# shop"}.items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")
        self.session = _working_in(root, root / "board")
        self.listed = lambda: [entry.path for entry in self.session.all_files()]

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("of a session working in one folder"):
        with it("should list every file in that folder, a file no fidelity declares among them"):
            expect(self.listed()).to(equal(["board/.context/story-map.md", "board/notes.txt"]))

    with context("with a folder outside it added to a practice"):
        with it("should list every file in that folder as well, and nothing beside it"):
            self.session.practice("stories").add_root("story_tests/checkout")
            expect(self.listed()).to(equal(["board/.context/story-map.md", "board/notes.txt", "story_tests/checkout/checkout_story.test.md"]))

    with context("with a file outside it added to a practice"):
        with it("should list that file as well"):
            self.session.practice("stories").add_root("README.md")
            expect(self.listed()).to(contain("README.md"))

    with context("with a folder inside it added to a practice"):
        with it("should list each file in it once"):
            self.session.practice("stories").add_root("board/.context")
            expect(self.listed()).to(equal(["board/.context/story-map.md", "board/notes.txt"]))
