"""Mamba spec for where a session says a file is published, which a page opens instead of the file. Reported
2026-11-26 from pml-web: the Files app named a design canvas by its version folder, "version-7 ↗ design canvas", while
it was published as "ux-mockup"; the session now sends the title the canvas is published under."""

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from space.session.files.file_manager import FileEntry
from space.session.practices.practice_session_output import publication_of

CANVAS_LINK = "https://claude.ai/artifact/canvas"


def _canvas_at(root: Path, version: str, record: dict) -> Path:
    """A design canvas version's canvas.json under root, with versions.json holding record."""
    canvas = root / "design-canvas" / version / "project" / "canvas.json"
    canvas.parent.mkdir(parents=True)
    canvas.write_text("{}", encoding="utf-8")
    (root / "design-canvas" / "versions.json").write_text(json.dumps(record), encoding="utf-8")
    return canvas


with description("a published file a session lists") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)

    with after.each:
        self.folder.cleanup()

    with context("that is a design canvas kept as one, updated in place"):
        with before.each:
            canvas = _canvas_at(self.root, "version-7", {"keep_one": True, "version-7": CANVAS_LINK})
            self.entry = FileEntry("ux/design-canvas/version-7/project/canvas.json", True).linked(publication_of(canvas))

        with it("should be named ux-mockup, the title it is published under, with no version"):
            expect(self.entry.published_name).to(equal("ux-mockup"))

        with it("should open at its link"):
            expect(self.entry.link).to(equal(CANVAS_LINK))

    with context("that is a design canvas kept in versions"):
        with before.each:
            canvas = _canvas_at(self.root, "version-7", {"version-7": CANVAS_LINK})
            self.entry = FileEntry("ux/design-canvas/version-7/project/canvas.json", True).linked(publication_of(canvas))

        with it("should be named ux-mockup.version-7, the title that version is published under"):
            expect(self.entry.published_name).to(equal("ux-mockup.version-7"))

    with context("that is a whiteboard"):
        with before.each:
            board = self.root / "story-map.whiteboard"
            board.write_text("{}", encoding="utf-8")
            self.entry = FileEntry("story-map.whiteboard", True).linked(publication_of(board))

        with it("should have no published name, so the page names it by its file"):
            expect(self.entry.published_name).to(equal(""))
