"""The addresses in Claude that files in one folder were published to, kept beside them."""
import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.installation.json_file import JsonFile
from harness.installation.published_links import PublishedLinks, PublishedLinksUnreadable


with description("the addresses a folder's files were published to") as self:
    with before.each:
        self.file = Path(tempfile.mkdtemp()) / "whiteboards.json"
        self.links = PublishedLinks(JsonFile(self.file))
        self.links.record("story-map.whiteboard", "https://claude.ai/artifact/map")
        self.links.record("modules.whiteboard", "https://claude.ai/artifact/modules")

    with it("should keep each address under its file's name"):
        expect(self.links.of("story-map.whiteboard")).to(equal("https://claude.ai/artifact/map"))

    with it("should name the file published at an address"):
        expect(self.links.named_at("https://claude.ai/artifact/modules")).to(equal("modules.whiteboard"))

    with it("should name nothing for an address no file was published at"):
        expect(self.links.named_at("https://claude.ai/artifact/other")).to(be_none)

    with it("should keep an address under a new name in the same place in the order"):
        self.links.rename("story-map.whiteboard", "release-1")
        expect(list(self.links.all())).to(equal(["release-1", "modules.whiteboard"]))

    with context("with a record that cannot be read"):
        with before.each:
            self.file.write_text("not json", encoding="utf-8")

        with it("should refuse to read it, naming the file"):
            expect(lambda: self.links.all()).to(raise_error(PublishedLinksUnreadable, contain(str(self.file))))

        with it("should refuse to record another address over it"):
            expect(lambda: self.links.record("ux.whiteboard", "https://claude.ai/artifact/ux")).to(
                raise_error(PublishedLinksUnreadable))

        with it("should leave what the file holds for a person to repair"):
            try:
                self.links.record("ux.whiteboard", "https://claude.ai/artifact/ux")
            except PublishedLinksUnreadable:
                pass
            expect(self.file.read_text(encoding="utf-8")).to(equal("not json"))

    with context("with no record kept yet"):
        with it("should keep no address"):
            expect(PublishedLinks(JsonFile(self.file.with_name("versions.json"))).all()).to(equal({}))
