"""The record an IDE folder keeps of what the install into it wrote, read by the next install and by clean; and the
folder a checkout last installed into."""
import json
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_record import InstallRecord, InstallRecordUnreadable, LastInstall
from harness.installation.install_target import InstallTarget

_SKILL = "skills/generate/SKILL.md"


def _written_skill(folder: Path) -> Path:
    written = folder / _SKILL
    written.parent.mkdir(parents=True)
    written.write_text("skill\n", encoding="utf-8")
    return written


def _record_of(folder: Path, ide: str = "Cursor") -> InstallRecord:
    return InstallRecord(InstallTarget(IdeLayout(ide), folder))


with description("an install record") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="install-record-"))
        self.folder = self.project / ".cursor"
        self.written = _written_skill(self.folder)
        self.record = _record_of(self.folder)

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    with context("of an install that has written one file and not yet finished"):
        with before.each:
            self.record.track(self.written)
            self.saved = json.loads((self.folder / InstallRecord.NAME).read_text(encoding="utf-8"))

        with it("should already list the file in the folder's own record, so a stopped install's files stay known"):
            expect(self.saved["installed_files"]).to(equal([_SKILL]))

        with it("should name the folder by its whole path"):
            expect(self.saved["path"]).to(equal(str(self.folder.absolute())))

        with it("should name the IDE the install is for"):
            expect(self.saved["ide"]).to(equal("Cursor"))

    with context("that lists a file the last install wrote"):
        with before.each:
            self.record.track(self.written)
            self.removed = _record_of(self.folder).remove_installed()

        with it("should remove the file on clean"):
            expect(self.written.is_file()).to(equal(False))

        with it("should answer the file it removed"):
            expect(self.removed).to(equal([_SKILL]))

        with it("should remove the folder the file leaves empty"):
            expect(self.written.parent.is_dir()).to(equal(False))

        with it("should list nothing afterwards"):
            expect(_record_of(self.folder).saved["installed_files"]).to(equal([]))

    with context("with another folder installed into after it"):
        with before.each:
            self.record.track(self.written)
            self.other = self.project / ".claude"
            _record_of(self.other, "Claude").track(_written_skill(self.other))

        with it("should still remove its own file on clean"):
            expect(_record_of(self.folder).remove_installed()).to(equal([_SKILL]))

        with it("should leave the other folder's file"):
            _record_of(self.folder).remove_installed()
            expect((self.other / _SKILL).is_file()).to(equal(True))

    with context("of a folder nothing was installed into"):
        with it("should remove nothing"):
            expect(self.record.remove_installed()).to(equal([]))

        with it("should write no record into the folder"):
            self.record.remove_installed()
            expect((self.folder / InstallRecord.NAME).exists()).to(equal(False))

    with context("of an install that adds to the last one"):
        with before.each:
            self.record.track(self.written)
            self.added = _record_of(self.folder)
            self.added.keep_existing()

        with it("should start from the files the last install wrote that are still there"):
            expect(self.added.installed_files).to(equal([_SKILL]))

        with it("should drop a file it is told to forget"):
            self.added.forget(_SKILL)
            expect(_record_of(self.folder).saved["installed_files"]).to(equal([]))

    with context("that is not JSON"):
        with before.each:
            self.record.path.write_text('{"installed_files": ["skills/generate/SKILL.md"', encoding="utf-8")

        with it("should refuse to clean"):
            expect(lambda: self.record.remove_installed()).to(raise_error(InstallRecordUnreadable))

        with it("should keep the file it lists"):
            try:
                self.record.remove_installed()
            except InstallRecordUnreadable:
                pass
            expect(self.written.is_file()).to(equal(True))

        with it("should name the record in its failure"):
            try:
                self.record.remove_installed()
            except InstallRecordUnreadable as failure:
                expect(str(failure)).to(contain(InstallRecord.NAME))

        with it("should refuse to start an install that adds to it"):
            expect(lambda: self.record.keep_existing()).to(raise_error(InstallRecordUnreadable))


with description("the folder a checkout last installed into") as self:
    with before.each:
        self.kept = Path(tempfile.mkdtemp(prefix="last-install-"))
        self.last = LastInstall(self.kept / InstallRecord.NAME)
        # A project's own folder, outside the temporary folder; nothing is written into it.
        self.project_folder = Path.home() / ".claude-of-no-such-project"

    with after.each:
        shutil.rmtree(self.kept, ignore_errors=True)

    with context("before any install"):
        with it("should be none"):
            expect(self.last.saved).to(equal({}))

    with context("after an install into a project's own folder"):
        with before.each:
            self.last.remember(InstallTarget(IdeLayout("Claude"), self.project_folder))

        with it("should be that folder, for that IDE"):
            expect(self.last.saved).to(equal({"ide": "Claude", "path": str(self.project_folder)}))

    with context("after an install into a temporary folder, as a spec's is"):
        with before.each:
            self.last.remember(InstallTarget(IdeLayout("Claude"), self.kept / ".claude"))

        with it("should stay as it was, so a spec's install never replaces the person's"):
            expect(self.last.saved).to(equal({}))

    with context("written by a CDD that listed the last install's files here, not in the folder"):
        with before.each:
            self.folder = self.kept / ".cursor"
            _written_skill(self.folder)
            earlier = {"ide": "Cursor", "path": str(self.folder), "installed_files": [_SKILL]}
            (self.kept / InstallRecord.NAME).write_text(json.dumps(earlier), encoding="utf-8")

        with it("should hand that folder's record the files, so its next clean removes them"):
            record = _record_of(self.folder)
            self.last.hand_over_to(record)
            expect(record.remove_installed()).to(equal([_SKILL]))

        with it("should hand nothing to the record of another folder"):
            other = _record_of(self.kept / ".claude", "Claude")
            self.last.hand_over_to(other)
            expect(other.saved).to(equal({}))

        with it("should hand nothing to a folder that keeps a record of its own already"):
            record = _record_of(self.folder)
            record.save()
            self.last.hand_over_to(record)
            expect(record.saved["installed_files"]).to(equal([]))
