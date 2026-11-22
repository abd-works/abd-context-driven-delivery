"""The addresses in Claude that files in one folder were published to, kept beside them."""
import tempfile
from pathlib import Path

from expects import be_none, equal, expect
from mamba import before, description, it

from harness.installation.json_file import JsonFile
from harness.installation.published_links import PublishedLinks


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

    with it("should keep none when the record holds something that is no record of them"):
        self.file.write_text("not json", encoding="utf-8")
        expect(self.links.all()).to(equal({}))
