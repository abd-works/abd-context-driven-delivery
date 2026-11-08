"""BDD spec for a JSON file its owner reads and writes whole."""

import tempfile
from pathlib import Path

from expects import be_a, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.installation.json_file import JsonFile, JsonFileUnreadable


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

    with context("that its owner wrote over"):
        with it("should hold only the last object written"):
            self.file.write({"name": "alpha", "kept": True})
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
