"""SessionFiles - the files a session's calls name, read from its project and refused when they are not there."""

import tempfile
from pathlib import Path

from expects import equal, expect, raise_error

from space.session import Session, Sessions
from space.session.session_files import NamedPathNotFoundError


def _working_in(project: Path, root: Path) -> Session:
    """A session of project that works in root, a folder of the project."""
    session = Session(Sessions(project))
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
