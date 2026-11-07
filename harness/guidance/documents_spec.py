"""The document a call names, read from the files at the paths it names."""
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, description, it

from harness.guidance.documents import load_document


with description("a document named by a folder") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "story.md").write_bytes(b"# Story\n")
        (self.folder / "map.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

    with it("should hold the text of each document in the folder"):
        expect(load_document(paths=[str(self.folder)])).to(contain("# Story"))

    with it("should leave out an image the folder holds beside them"):
        expect(load_document(paths=[str(self.folder)])).to(equal("# Story\n"))
