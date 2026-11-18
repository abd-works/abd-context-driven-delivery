"""Specs for a log file kept under a size, so a log that is written to all day cannot fill the disk."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from harness.process.capped_log_file import CappedLogFile

_LIMIT = 100

with description("a log file kept under a size"):
    with before.each:
        self.path = Path(tempfile.mkdtemp()) / "server.log"
        self.log = CappedLogFile(self.path, _LIMIT)

    with context("that is under its size"):
        with before.each:
            self.path.write_text("first line\n", encoding="utf-8")
            self.rolled = self.log.roll_when_full()

        with it("should keep its lines where they are"):
            expect(self.path.read_text(encoding="utf-8")).to(equal("first line\n"))

        with it("should say it did not roll"):
            expect(self.rolled).to(equal(False))

    with context("that reached its size"):
        with before.each:
            self.path.write_text("x" * _LIMIT, encoding="utf-8")
            self.rolled = self.log.roll_when_full()

        with it("should move its lines to the previous file beside it"):
            expect(self.log.previous.read_text(encoding="utf-8")).to(equal("x" * _LIMIT))

        with it("should leave no file in its place, so the next line starts a new one"):
            expect(self.path.exists()).to(equal(False))

        with it("should say it rolled"):
            expect(self.rolled).to(equal(True))

        with context("with a previous file from an earlier roll"):
            with before.each:
                self.path.write_text("y" * _LIMIT, encoding="utf-8")
                self.log.roll_when_full()

            with it("should replace it, so the log never takes more than twice its size"):
                expect(self.log.previous.read_text(encoding="utf-8")).to(equal("y" * _LIMIT))

    with context("that is not there yet"):
        with it("should say it did not roll"):
            expect(self.log.roll_when_full()).to(equal(False))
