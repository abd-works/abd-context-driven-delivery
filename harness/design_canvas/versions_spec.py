"""Mamba spec for canvas versions: a regeneration starts the next version and never touches the ones before."""

import shutil
import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import contain, equal, expect, be_none, raise_error

from harness.design_canvas.versions import CanvasVersions, PublishedVersion, UnshownStepValues


class _Walk:
    """A walk of a version's screens, as the publish gate reads it: each step value a screen leaves out."""

    def __init__(self, *misses: str) -> None:
        self.misses = list(misses)


_CLEAN = _Walk()


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

        with it("titles the published canvas ux-mockup with its version, for the whole repository"):
            expect(self.versions.start_next().title).to(equal("ux-mockup.version-2"))

        with it("puts the scope's name in front of a scoped canvas's title"):
            expect(CanvasVersions(self.root, "ordering").start_next().title).to(equal("ordering-ux-mockup.version-2"))

        with it("keeps the scope's name in the title of a version kept as a release"):
            self.versions = CanvasVersions(self.root, "ordering")
            (self.root / "versions.json").write_text('{"version-1": "https://claude.ai/artifact/one"}', encoding="utf-8")
            expect(self.versions.latest.release("first-release").title).to(equal("ordering-ux-mockup.first-release"))

    with context("recording published links"):
        with it("remembers each version's link"):
            (self.root / "version-1").mkdir(parents=True)
            first = self.versions.latest
            first.publish_at("https://claude.ai/artifact/one", _CLEAN)
            second = self.versions.start_next()
            expect((first.link, second.link)).to(equal(("https://claude.ai/artifact/one", None)))

    with context("publishing a version whose screens leave out values their steps name"):
        with before.each:
            (self.root / "version-1" / "project").mkdir(parents=True)
            self.version = self.versions.latest
            self.walk = _Walk('Apply Voucher › Apply a voucher › "ALL10"', "Sign In › Wrong password › \"Invalid password\"")

        with it("should refuse to record the link, naming each value left out"):
            expect(lambda: self.version.publish_at("https://claude.ai/artifact/one", self.walk)).to(
                raise_error(UnshownStepValues, contain('Apply Voucher › Apply a voucher › "ALL10"')))

        with it("should leave the version unpublished"):
            try:
                self.version.publish_at("https://claude.ai/artifact/one", self.walk)
            except UnshownStepValues:
                pass
            expect(self.version.link).to(be_none)

        with it("should still refuse while only some of the values left out are accepted"):
            expect(lambda: self.version.publish_at("https://claude.ai/artifact/one", self.walk, accepted_misses=[self.walk.misses[0]])).to(
                raise_error(UnshownStepValues, contain("Invalid password")))

        with context("when the person accepts every value left out"):
            with before.each:
                self.version.publish_at("https://claude.ai/artifact/one", self.walk, accepted_misses=self.walk.misses)

            with it("should record the link"):
                expect(self.version.link).to(equal("https://claude.ai/artifact/one"))

            with it("should keep the accepted values beside the link, so the gap stays in view"):
                expect(self.version.accepted_misses).to(equal(self.walk.misses))

    with context("publishing a version whose screens show every value their steps name"):
        with it("should keep no accepted values beside the link"):
            (self.root / "version-1" / "project").mkdir(parents=True)
            self.versions.latest.publish_at("https://claude.ai/artifact/one", _CLEAN)
            expect(self.versions.latest.accepted_misses).to(equal([]))

    with context("choosing the version a generator writes into"):
        with before.each:
            (self.root / "version-1" / "project").mkdir(parents=True)

        with it("keeps writing into a version that is not published yet"):
            expect(self.versions.working().number).to(equal(1))

        with it("starts the next version once the latest is published"):
            self.versions.latest.publish_at("https://claude.ai/artifact/one", _CLEAN)
            expect(self.versions.working().number).to(equal(2))

        with it("refuses to add to a published version"):
            self.versions.latest.publish_at("https://claude.ai/artifact/one", _CLEAN)
            expect(lambda: self.versions.unpublished()).to(raise_error(PublishedVersion))

    with context("keeping one canvas that every render updates in place"):
        with before.each:
            self.root.mkdir(parents=True)
            (self.root / "versions.json").write_text('{"keep_one": true}', encoding="utf-8")

        with it("starts version-1 when there is no version yet"):
            expect(self.versions.working().number).to(equal(1))

        with context("once the version is published"):
            with before.each:
                (self.root / "version-1" / "project").mkdir(parents=True)
                self.versions.latest.publish_at("https://claude.ai/artifact/one", _CLEAN)

            with it("keeps writing into the published version"):
                expect(self.versions.working().number).to(equal(1))

            with it("starts no next version"):
                self.versions.working()
                expect((self.root / "version-2").exists()).to(equal(False))

            with it("lets generators add to the published version"):
                expect(self.versions.unpublished().number).to(equal(1))

            with it("records the same link again when it is published again"):
                self.versions.working().publish_at("https://claude.ai/artifact/one", _CLEAN)
                expect(self.versions.published.all()).to(equal({"version-1": "https://claude.ai/artifact/one"}))

            with it("keeps the setting when it is published again"):
                self.versions.working().publish_at("https://claude.ai/artifact/one", _CLEAN)
                expect(self.versions.keeps_one).to(equal(True))

            with it("still refuses to publish screens that leave out values their steps name"):
                expect(lambda: self.versions.working().publish_at("https://claude.ai/artifact/one", _Walk('Pay › Pay by card › "Visa"'))).to(
                    raise_error(UnshownStepValues, contain('"Visa"')))

    with context("without the setting"):
        with it("does not keep one canvas"):
            expect(self.versions.keeps_one).to(equal(False))

    with context("keeping a published version as a release"):
        with before.each:
            for number in (1, 2):
                (self.root / f"version-{number}" / "project").mkdir(parents=True)
                (self.root / f"version-{number}" / "project" / "Main.dc.html").write_text(f"version {number}", encoding="utf-8")
                self.versions.latest.publish_at(f"https://claude.ai/artifact/{number}", _CLEAN)
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
