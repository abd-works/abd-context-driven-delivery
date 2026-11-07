"""Specs for the session's file manager: listing and reading files under a session's roots."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentToolSet
from space.session import Session, Sessions
from space.session.file_manager import FileManager, PathOutsideRootsError

ORDER = b"export class Order {}\n"


with description("a session's file manager"):

    with before.each:
        self.workpath = Path(tempfile.mkdtemp()).resolve()
        (self.workpath / "src").mkdir()
        (self.workpath / "src" / "order.ts").write_bytes(ORDER)
        (self.workpath / "README.md").write_bytes(b"# Orders\n")
        self.files = FileManager(self.workpath, (self.workpath,))

    with after.each:
        shutil.rmtree(self.workpath, ignore_errors=True)

    with context("that a session owns"):

        with before.each:
            folder = self.workpath / ".sessions" / "orders"
            folder.mkdir(parents=True)
            (folder / "session.json").write_text(json.dumps({"name": "orders", "outputs": {"stories": {"root": "src"}}}), encoding="utf-8")
            self.session = Session(self.workpath)
            self.session.workpath = self.workpath
            self.session.session_path = folder

        with it("should read under the root session.json records for a practice"):
            expect(self.session.session_files.file_manager.roots).to(contain(self.workpath / "src"))

        with it("should be the same file manager each time the session is asked"):
            expect(self.session.session_files.file_manager).to(be(self.session.session_files.file_manager))

    with context("that a tool call on a project loads"):

        with before.each:
            sessions = Sessions(self.workpath)
            sessions.open(sessions.create("orders", self.workpath / "src"))
            self.other = Path(tempfile.mkdtemp()).resolve()
            (self.other / "notes.md").write_bytes(b"# Notes\n")

        with after.each:
            shutil.rmtree(self.other, ignore_errors=True)

        with it("should read under the session open in that project"):
            expect(FileManager.load(project=self.workpath).workpath).to(equal(self.workpath / "src"))

        with it("should list the files of the project its call names"):
            listing = AgentToolSet.instantiate(FileManager).tools["list"].invoke({}, project=self.other)
            expect([entry.name for entry in listing.entries]).to(contain("notes.md"))

        with it("should list each project's own files when calls name different projects"):
            tool = AgentToolSet.instantiate(FileManager).tools["list"]
            tool.invoke({}, project=self.other)
            expect([entry.name for entry in tool.invoke({}, project=self.workpath).entries]).to(equal(["order.ts"]))

    with context("that lists a folder"):

        with it("should list folders before files"):
            expect([entry.name for entry in self.files.list().entries]).to(equal(["src", "README.md"]))

        with it("should give each entry its path from the workpath"):
            expect(self.files.list("src").entries[0].path).to(equal("src/order.ts"))

        with it("should give each file its size"):
            expect(self.files.list("src").entries[0].size).to(equal(len(ORDER)))

    with context("that reads a file"):

        with it("should return the file's text"):
            expect(self.files.read("src/order.ts").text).to(equal(ORDER.decode()))

    with context("with roots narrower than the workpath"):

        with before.each:
            self.files = FileManager(self.workpath, (self.workpath / "src",))

        with it("should read a file under a root"):
            expect(self.files.read("src/order.ts").path).to(equal("src/order.ts"))

        with it("should refuse a file in the workpath outside every root"):
            expect(lambda: self.files.read("README.md")).to(raise_error(PathOutsideRootsError))

    with context("that is asked for a path outside its roots"):

        with it("should refuse to read it"):
            expect(lambda: self.files.read("../secrets.txt")).to(raise_error(PathOutsideRootsError))

        with it("should refuse to list it"):
            expect(lambda: self.files.list("..")).to(raise_error(PathOutsideRootsError))

    with context("that is asked for a file that is not there"):

        with it("should give no text, such as for a file deleted since a page listed it"):
            expect(self.files.read("src/missing.ts").text).to(equal(""))

    with context("that is asked for a folder that is not there"):

        with it("should list no entries, such as for a folder deleted since a page listed it"):
            expect(self.files.list("src/gone").entries).to(equal([]))
