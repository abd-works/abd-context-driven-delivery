"""The explorer names the practice, file, and rule while a working copy loads."""

from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph

_SAMPLE = Path(__file__).resolve().parent / "examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]


with description("a working copy load"):
    with context("that the explorer is watching"):
        with before.all:
            self.graph = Graph()
            self.messages = []
            self.graph.watch_progress(lambda event: self.messages.append(event["message"]))
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            self.graph.load_working_copy(str(_SAMPLE), roots, database=str(_SAMPLE))

        with it("should name each source file as it is read"):
            named = [message for message in self.messages if ".ts" in message and "/" in message]
            expect(bool(named)).to(equal(True))

        with it("should name each rule as it runs"):
            named = [message for message in self.messages if " rule " in message]
            expect(bool(named)).to(equal(True))
