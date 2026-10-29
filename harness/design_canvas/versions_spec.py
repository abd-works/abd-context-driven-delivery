"""Mamba spec for canvas versions: a regeneration starts the next version and never touches the ones before."""

import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import equal, expect, be_none, raise_error

from harness.design_canvas.versions import CanvasVersions, PublishedVersion


with description("Canvas versions") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name) / "design-canvas"
        self.versions = CanvasVersions(self.root)

    with after.each:
        self.folder.cleanup()

    with context("with no versions yet"):
        with it("starts at version-1"):
            expect(self.versions.start_next()).to(equal(1))
            expect(self.versions.folder(1).is_dir()).to(equal(True))

    with context("with a version people have edited"):
        with before.each:
            edited = self.root / "version-1" / "project"
            edited.mkdir(parents=True)
            (edited / "Main.dc.html").write_text("edited on the canvas", encoding="utf-8")

        with it("starts the next version as a copy, leaving the edited one as it was"):
            number = self.versions.start_next()
            (self.versions.folder(number) / "project" / "Main.dc.html").write_text("regenerated", encoding="utf-8")
            expect(number).to(equal(2))
            expect((self.root / "version-1" / "project" / "Main.dc.html").read_text(encoding="utf-8")).to(equal("edited on the canvas"))

        with it("names the published canvas after its version"):
            expect(self.versions.title(2, "PML Story Map")).to(equal("PML Story Map \u2014 version-2"))

    with context("recording published links"):
        with it("remembers each version's link"):
            self.root.mkdir(parents=True)
            self.versions.record_link(1, "https://claude.ai/artifact/one")
            self.versions.record_link(2, "https://claude.ai/artifact/two")
            expect(self.versions.link(1)).to(equal("https://claude.ai/artifact/one"))
            expect(self.versions.link(3)).to(be_none)

    with context("choosing the version a generator writes into"):
        with before.each:
            (self.root / "version-1" / "project").mkdir(parents=True)

        with it("keeps writing into a version that is not published yet"):
            expect(self.versions.working()).to(equal(1))

        with it("starts the next version once the latest is published"):
            self.versions.record_link(1, "https://claude.ai/artifact/one")
            expect(self.versions.working()).to(equal(2))

        with it("refuses to add to a published version"):
            self.versions.record_link(1, "https://claude.ai/artifact/one")
            expect(lambda: self.versions.unpublished()).to(raise_error(PublishedVersion))
