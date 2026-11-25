"""The addresses in Claude that a design canvas's versions were published to, kept beside them."""
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.installation.json_file import JsonFile
from harness.installation.published_links import PublishedLinks, PublishedLinksUnreadable


with description("the addresses a folder's design canvas versions were published to") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp())
        self.file = self.folder / "versions.json"
        self.links = PublishedLinks(JsonFile(self.file))
        self.links.record("version-1", "https://claude.ai/artifact/first")
        self.links.record("version-2", "https://claude.ai/artifact/second")

    with it("should keep each address under its version's name"):
        expect(self.links.of("version-1")).to(equal("https://claude.ai/artifact/first"))

    with it("should keep an address under a new name in the same place in the order"):
        self.links.rename("version-1", "release-1")
        expect(list(self.links.all())).to(equal(["release-1", "version-2"]))

    with context("with what else is kept beside an address"):
        with before.each:
            self.links.record("version-3", "https://claude.ai/artifact/third", beside={"accepted_misses": ["Pay › Pay by card › \"Visa\""]})

        with it("should still read the address back"):
            expect(self.links.of("version-3")).to(equal("https://claude.ai/artifact/third"))

        with it("should keep what was recorded beside it"):
            expect(self.links.beside("version-3")).to(equal({"accepted_misses": ["Pay › Pay by card › \"Visa\""]}))

        with it("should keep nothing beside an address recorded alone"):
            expect(self.links.beside("version-1")).to(equal({}))

        with it("should keep what is beside it under a new name"):
            self.links.rename("version-3", "release-3")
            expect(self.links.beside("release-3")).to(equal({"accepted_misses": ["Pay › Pay by card › \"Visa\""]}))

    with context("with a record that cannot be read"):
        with before.each:
            self.file.write_text("not json", encoding="utf-8")

        with it("should refuse to read it, naming the file"):
            expect(lambda: self.links.all()).to(raise_error(PublishedLinksUnreadable, contain(str(self.file))))

        with it("should refuse to record another address over it"):
            expect(lambda: self.links.record("version-3", "https://claude.ai/artifact/third")).to(
                raise_error(PublishedLinksUnreadable))

        with it("should leave what the file holds for a person to repair"):
            try:
                self.links.record("version-3", "https://claude.ai/artifact/third")
            except PublishedLinksUnreadable:
                pass
            expect(self.file.read_text(encoding="utf-8")).to(equal("not json"))

    with context("with no record kept yet"):
        with it("should keep no address"):
            expect(PublishedLinks(JsonFile(Path(tempfile.mkdtemp()) / "versions.json")).all()).to(equal({}))
