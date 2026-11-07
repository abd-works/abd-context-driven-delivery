"""The record of what the last install wrote, read by the next install and by clean."""
import json
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installer.install_record import InstallRecord, InstallRecordUnreadable


with description("an install record") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="install-record-"))
        self.written = self.folder / "skills" / "generate" / "SKILL.md"
        self.written.parent.mkdir(parents=True)
        self.written.write_text("skill\n", encoding="utf-8")
        self.record = InstallRecord(self.folder / InstallRecord.NAME)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that lists a file the last install wrote"):
        with before.each:
            self.record.track(self.written, self.folder)
            self.record.save("Cursor", self.folder)
            self.removed = InstallRecord(self.record.path).remove_installed(self.folder)

        with it("should remove the file on clean"):
            expect(self.written.is_file()).to(equal(False))

        with it("should answer the file it removed"):
            expect(self.removed).to(equal(["skills/generate/SKILL.md"]))

        with it("should remove the folder the file leaves empty"):
            expect(self.written.parent.is_dir()).to(equal(False))

    with context("that is not JSON"):
        with before.each:
            self.record.path.write_text('{"installed_files": ["skills/generate/SKILL.md"', encoding="utf-8")

        with it("should refuse to clean"):
            expect(lambda: self.record.remove_installed(self.folder)).to(raise_error(InstallRecordUnreadable))

        with it("should keep the file it lists"):
            try:
                self.record.remove_installed(self.folder)
            except InstallRecordUnreadable:
                pass
            expect(self.written.is_file()).to(equal(True))

        with it("should name the record in its failure"):
            try:
                self.record.remove_installed(self.folder)
            except InstallRecordUnreadable as failure:
                expect(str(failure)).to(contain(InstallRecord.NAME))

        with it("should refuse to start an install that adds to it"):
            expect(lambda: self.record.keep_existing(self.folder)).to(raise_error(InstallRecordUnreadable))

    with context("of another folder"):
        with before.each:
            self.record.track(self.written, self.folder)
            self.record.save("Cursor", self.folder / "elsewhere")

        with it("should remove nothing from this folder"):
            expect(self.record.remove_installed(self.folder)).to(equal([]))

        with it("should keep the record's own list"):
            expect(json.loads(self.record.path.read_text(encoding="utf-8"))["installed_files"]).to(
                equal(["skills/generate/SKILL.md"])
            )
