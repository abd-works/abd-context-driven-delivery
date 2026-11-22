"""Mamba spec for canvas versions: a regeneration starts the next version and never touches the ones before."""

import shutil
import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import contain, equal, expect, be_none, raise_error

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
            started = self.versions.start_next()
            expect((started.number, started.folder.is_dir())).to(equal((1, True)))

        with it("has no latest version"):
            expect(self.versions.latest).to(be_none)

    with context("with a version people have edited"):
        with before.each:
            edited = self.root / "version-1" / "project"
            edited.mkdir(parents=True)
            (edited / "Main.dc.html").write_text("edited on the canvas", encoding="utf-8")

        with it("starts the next version as a copy, leaving the edited one as it was"):
            started = self.versions.start_next()
            (started.folder / "project" / "Main.dc.html").write_text("regenerated", encoding="utf-8")
            expect(started.number).to(equal(2))
            expect((self.root / "version-1" / "project" / "Main.dc.html").read_text(encoding="utf-8")).to(equal("edited on the canvas"))

        with it("names the published canvas after its version"):
            expect(self.versions.start_next().title("PML Story Map")).to(equal("PML Story Map — version-2"))

    with context("recording published links"):
        with it("remembers each version's link"):
            (self.root / "version-1").mkdir(parents=True)
            first = self.versions.latest
            first.publish_at("https://claude.ai/artifact/one")
            second = self.versions.start_next()
            expect((first.link, second.link)).to(equal(("https://claude.ai/artifact/one", None)))

    with context("choosing the version a generator writes into"):
        with before.each:
            (self.root / "version-1" / "project").mkdir(parents=True)

        with it("keeps writing into a version that is not published yet"):
            expect(self.versions.working().number).to(equal(1))

        with it("starts the next version once the latest is published"):
            self.versions.latest.publish_at("https://claude.ai/artifact/one")
            expect(self.versions.working().number).to(equal(2))

        with it("refuses to add to a published version"):
            self.versions.latest.publish_at("https://claude.ai/artifact/one")
            expect(lambda: self.versions.unpublished()).to(raise_error(PublishedVersion))

    with context("keeping a published version as a release"):
        with before.each:
            for number in (1, 2):
                (self.root / f"version-{number}" / "project").mkdir(parents=True)
                (self.root / f"version-{number}" / "project" / "Main.dc.html").write_text(f"version {number}", encoding="utf-8")
                self.versions.latest.publish_at(f"https://claude.ai/artifact/{number}")
            self.released = self.versions.latest.release("design-system-setup")

        with it("renames the version's folder and its link to the release"):
            expect((self.root / "design-system-setup" / "project" / "Main.dc.html").is_file()).to(equal(True))
            expect(self.released.link).to(equal("https://claude.ai/artifact/2"))
            expect(list(self.versions.published.all())).to(equal(["version-1", "design-system-setup"]))

        with it("starts the next version from the release once no numbered version is left"):
            shutil.rmtree(self.root / "version-1")
            started = self.versions.start_next()
            expect(started.number).to(equal(1))
            expect((started.folder / "project" / "Main.dc.html").read_text(encoding="utf-8")).to(equal("version 2"))


with description("the UX practice's canvas") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.repo = Path(self.folder.name)

    with after.each:
        self.folder.cleanup()

    with it("should keep its versions in the UX practice's root"):
        expect(CanvasVersions.in_practice_root(self.repo / "harness" / ".context" / "ux").root).to(equal(self.repo / "harness" / ".context" / "ux" / "design-canvas"))

    with it("should keep them out of the session's own folder"):
        expect(str(CanvasVersions.in_practice_root(self.repo / "harness" / ".context" / "ux").root)).not_to(contain(".sessions"))
