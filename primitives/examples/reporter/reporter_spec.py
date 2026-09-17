"""BDD spec for reporter.py - Reporter toolset example covering all public members."""
import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.examples.reporter.reporter import Reporter


def make_reporter(beat: str = "technology") -> Reporter:
    """Minimal Reporter instance for tests."""
    return Reporter(beat=beat)


with description("a Reporter"):
    with context("that has been created"):
        with before.each:
            self.reporter = make_reporter("science")

        with it("should expose the beat it was given"):
            # Act / Assert
            expect(self.reporter.beat).to(equal("science"))

        with it("should start with a note count of zero"):
            # Act / Assert
            expect(self.reporter.note_count).to(equal(0))

    with context("that has a note added"):
        with before.each:
            self.reporter = make_reporter()

        with it("should confirm the note was recorded"):
            # Act
            result = self.reporter.add_note("AI beats chess record")
            # Assert
            expect(result).to(equal("Note added: AI beats chess record"))

        with it("should increment the note count"):
            # Act
            self.reporter.add_note("first fact")
            # Assert
            expect(self.reporter.note_count).to(equal(1))

    with context("that reads notes"):
        with context("with no notes collected"):
            with it("should report no notes yet"):
                # Arrange
                reporter = make_reporter()
                # Act / Assert
                expect(reporter.read_notes()).to(equal("No notes yet."))

        with context("with notes collected"):
            with before.each:
                self.reporter = make_reporter()
                self.reporter.add_note("alpha")
                self.reporter.add_note("beta")

            with it("should list them as a numbered sequence"):
                # Act
                result = self.reporter.read_notes()
                # Assert
                expect(result).to(equal("1. alpha\n2. beta"))

    with context("that clears notes"):
        with context("with notes present"):
            with before.each:
                self.reporter = make_reporter()
                self.reporter.add_note("stale note")

            with it("should reset the note count to zero"):
                # Act
                self.reporter.clear_notes()
                # Assert
                expect(self.reporter.note_count).to(equal(0))

    with context("that exposes style guidance"):
        with before.each:
            self.reporter = make_reporter()

        with it("should return the Style section from reporter.md"):
            expect(self.reporter.style).to(contain("inverted-pyramid"))

    with context("that exposes house guidelines"):
        with before.each:
            self.reporter = make_reporter()

        with it("should return house-guidelines.md"):
            expect(self.reporter.guidelines).to(contain("attribute"))

    with context("that has its toolset manifest read"):
        with it("should register add_note, read_notes, and clear_notes as tools"):
            reporter = make_reporter()
            expect(set(reporter.operations)).to(
                equal({"add_note", "read_notes", "clear_notes"})
            )

        with it("should register gather and file_report as agent instructions"):
            reporter = make_reporter()
            expect(set(reporter.instructions)).to(equal({"gather", "file_report"}))
