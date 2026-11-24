"""A rule broken on a range of a file, as the Files app shows it: Fix this one on its banner comments on the range with the
words Python writes, word for word as the page wrote them before they moved here (2026-11-22)."""

from expects import equal, expect
from mamba import description, it

from harness.graph.location import Location
from harness.graph.violation import FoundBy, Violation
from harness.installation.data_class import data_of
from space.session.files.file_range import LineSpan, Range
from space.session.files.session_file import FileViolation

_SLUG = "limit-operation-parameters"
_MESSAGE = "Operation 'place' takes 4 parameters (maximum 2)."
_BROKEN = FileViolation(
    Violation(FoundBy(_SLUG, "clean_engineering"), _MESSAGE, Location("src/order.py", 2, 3)),
    Range("src/order.py", LineSpan(2, 3), "    def place(self, cart, user, store, day):\n        return self"),
    "clean-engineering-model",
)


with description("a rule broken on a range of a file"):
    with it("should give the comment Fix this one sends: fix it test first, the rule, and what is wrong, without the lines a sent comment quotes"):
        expect(data_of(_BROKEN)["correction_comment"]).to(equal(
            "Fix this violation using the clean-engineering-model guidelines and a test-driven approach.\n"
            "Run or add tests that express the intended behavior before or alongside the fix.\n"
            f"\nRule: {_SLUG}\nViolation: {_MESSAGE}"
        ))
