"""BDD spec for a JSON file its owner reads and writes whole."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from expects import be_a, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.json_file import HeldJsonFile, JsonFile, JsonFileUnreadable

os_replace = os.replace


class _OwnersError(JsonFileUnreadable):
    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} needs repair"


with description("a JSON file"):
    with before.each:
        self.path = Path(tempfile.mkdtemp(prefix="json-file-")) / "nested" / "settings.json"
        self.file = JsonFile(self.path, _OwnersError)

    with context("that is not there"):
        with it("should read as empty"):
            expect(self.file.read()).to(equal({}))

    with context("that its owner wrote"):
        with before.each:
            self.file.write({"name": "alpha"})

        with it("should read back what was written"):
            expect(self.file.read()).to(equal({"name": "alpha"}))

        with it("should be indented with a closing newline, for a person to read"):
            expect(self.path.read_text(encoding="utf-8")).to(equal('{\n  "name": "alpha"\n}\n'))

        # Several chats' calls write some files at once; each write is swapped in whole, so no reader sees half of one.
        with it("should leave nothing but the file in its folder"):
            expect([path.name for path in self.path.parent.iterdir()]).to(equal(["settings.json"]))

    with context("that its owner writes compact"):
        with it("should be written on one line, for programs to read"):
            JsonFile(self.path, compact=True).write({"name": "alpha", "tags": [1, 2]})
            expect(self.path.read_text(encoding="utf-8")).to(equal('{"name":"alpha","tags":[1,2]}\n'))

    with context("that its owner wrote over"):
        with it("should hold only the last object written"):
            self.file.write({"name": "alpha", "kept": True})
            self.file.write({"name": "beta"})
            expect(self.file.read()).to(equal({"name": "beta"}))

    # A reinstall writes every plugin's manifest again; a file whose text is the same is not touched, so nothing that
    # watches it, such as Claude Code reading a plugin's manifest, has it open while the install swaps it.
    with context("that its owner writes again with the same object"):
        with it("should leave the file as it was"):
            self.file.write({"name": "alpha"})
            written = self.path.stat().st_mtime_ns
            os.utime(self.path, ns=(written - 10**9, written - 10**9))
            self.file.write({"name": "alpha"})
            expect(self.path.stat().st_mtime_ns).to(equal(written - 10**9))

    # Windows refuses the swap while another process reads the file for a moment, as a watcher does after each write.
    with context("that another process holds open for a moment"):
        with it("should still be written"):
            self.file.write({"name": "alpha"})
            swaps = iter([PermissionError(5, "Access is denied")])

            def refused_once(staged, target):
                failure = next(swaps, None)
                if failure is not None:
                    raise failure
                os_replace(staged, target)

            with patch("harness.installation.json_file.os.replace", side_effect=refused_once):
                self.file.write({"name": "beta"})
            expect(self.file.read()).to(equal({"name": "beta"}))

    with context("that holds something other than an object"):
        with before.each:
            self.path.parent.mkdir(parents=True)
            self.path.write_text("[1, 2]", encoding="utf-8")

        with it("should raise its owner's kind of unreadable error"):
            expect(lambda: self.file.read()).to(raise_error(_OwnersError, contain("needs repair")))

        with it("should be an unreadable JSON file"):
            try:
                self.file.read()
            except JsonFileUnreadable as failure:
                expect(failure).to(be_a(_OwnersError))


with description("a JSON file held between reads"):
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-held-json-"))
        self.path = self.folder / "session.json"
        JsonFile(self.path).write({"stage": "Discovery"})
        self.held = HeldJsonFile(JsonFile(self.path))
        self.held.read()

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that another process writes over"):
        with it("should read what the other process wrote"):
            JsonFile(self.path).write({"stage": "Specification", "stage_mark": "done"})
            expect(self.held.read()).to(equal({"stage": "Specification", "stage_mark": "done"}))

    with context("that a reader changes what it was given"):
        with it("should keep what the file holds"):
            self.held.read()["stage"] = "Implementation"
            expect(self.held.read()).to(equal({"stage": "Discovery"}))

    with context("that its owner writes"):
        with it("should read back what was written"):
            self.held.write({"stage": "Implementation"})
            expect(self.held.read()).to(equal({"stage": "Implementation"}))

    with context("that is deleted"):
        with it("should read as empty"):
            self.path.unlink()
            expect(self.held.read()).to(equal({}))
