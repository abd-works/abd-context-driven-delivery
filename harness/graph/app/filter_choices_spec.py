"""The filter answers the explorer's tests use: Python's own, recorded in filter-choices.json."""
from expects import equal, expect
from mamba import before, description, it

from harness.graph.app.filter_choices_record import read, recorded

with description("the filter answers the explorer is tested against"):
    with before.all:
        self.kept = read()

    # A change to Graph.filter_choices changes the answers; run filter_choices_record.py to record them again.
    with it("should be the answers Graph.filter_choices gives the explorer's requests now"):
        expect(self.kept["answers"]).to(equal(recorded(self.kept)["answers"]))
