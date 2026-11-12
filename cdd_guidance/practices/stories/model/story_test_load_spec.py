"""A story test read alone, as a load of the files being edited reads it: the examples it imports are read with it, and
the domain code its steps call is not; its background is given by its Given steps."""

from pathlib import Path

from expects import be_empty, contain, equal, expect
from mamba import before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph

_SAMPLE = Path(__file__).resolve().parents[4] / "harness" / "graph" / "_examples" / "input"
_STORY = "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts"


with description("a TypeScript story test read alone"):
    with before.all:
        self.graph = Graph()
        self.graph.load_files(str(_SAMPLE), ["clean_engineering", "stories"], [_STORY])
        self.stories = self.graph.practice("stories").reading.in_graph

    with it("should read the examples the story test imports"):
        expect([node.name for node in self.stories.nodes("Example")]).to(contain("emailedValidationCode"))

    with it("should give each example the names its examples file declares it with"):
        example = next(node for node in self.stories.nodes("Example") if node.name == "unverifiedAccountCredentials")
        expect(example.get_fact("source_names")).to(contain("AccountCredentials"))

    with it("should read none of the domain code its steps call"):
        expect(self.graph.practice("clean_engineering").reading.in_graph.nodes("OoadClass")).to(be_empty)

    with it("should give its background the Given steps it holds"):
        background = self.stories.nodes("Background")[0]
        given = [edge.child.type for edge in self.graph.edges_from("given", background)]
        expect(given).to(equal(["Given"]))
