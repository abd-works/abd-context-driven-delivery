import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.graph.file_lines import FileLines
from harness.graph.graph import Source


with description("the lines a graph build reads of a file") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        self.file = self.root / "story.ts"
        self.file.write_text("story('one', () => {\n  scenario('a');\n});\n", encoding="utf-8")

    with it("should be the file's lines"):
        expect(FileLines.of(self.file)).to(equal(["story('one', () => {", "  scenario('a');", "});"]))

    with context("that the file changes under"):
        with before.each:
            self.during = []
            with FileLines.during_build():
                self.during.append(FileLines.of(self.file))
                self.file.write_text("story('two');\n", encoding="utf-8")
                self.during.append(FileLines.of(self.file))

        with it("should be read from disk once while the build runs"):
            expect(self.during[1]).to(equal(self.during[0]))

        with it("should be read again by the next build"):
            with FileLines.during_build():
                expect(FileLines.of(self.file)).to(equal(["story('two');"]))

        with it("should be read again outside a build"):
            expect(FileLines.of(self.file)).to(equal(["story('two');"]))

    with context("that a node's source widens to its call's close in"):
        with before.each:
            with FileLines.during_build():
                self.first = Source("story.ts", 1, 1, str(self.root))
                self.first.widen_to_call_close()
            self.file.write_text("story('one', () => {\n  scenario('a');\n  scenario('b');\n});\n", encoding="utf-8")
            with FileLines.during_build():
                self.second = Source("story.ts", 1, 1, str(self.root))
                self.second.widen_to_call_close()

        with it("should close where the file closed the call in the build that read it"):
            expect(self.first.end_line).to(equal(3))

        with it("should close where the file closes it now in a later build"):
            expect(self.second.end_line).to(equal(4))
