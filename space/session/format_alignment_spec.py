"""Specs for the rules one object of a format alignment decides: what one graph reading lacks from another, how a gap
says it, which gaps a render closes, and which edge a callout shows. The diagnosis and the alignment on a real project
are in format_alignment_heavy_spec.py."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_false, be_true, contain, equal, expect
from mamba import context, description, it

from harness.graph.edge import Edge
from harness.graph.saved_graph import SavedNode, SavedPractice
from space.session.callout_alignment import PlacedNode
from space.session.format_alignment import FORMAT_LACKS, MISSING_FILE, AlignedFile, AlignmentDiagnosis, AlignmentGap, GraphDifference, GraphReading

STORY_MAP = ".context/story-map.md"
DRAWING = ".context/story-map.drawio"


def _node(node_id: str, type: str, name: str, line: int = 1, end_line: int = 1) -> SavedNode:
    return SavedNode({"node_id": node_id, "name": name, "type": type, "practice": "stories", "file": STORY_MAP, "line": line, "end_line": end_line, "stage": "", "facts": {}})


def _reading(stories: list[str], ids: str = "") -> GraphReading:
    """The reading of a story map holding the sub-epic Review Cart and stories, its node ids led by ids, as each format
    gives its nodes ids of its own."""
    nodes = [_node(f"{ids}review-cart", "SubEpic", "Review Cart")] + [_node(f"{ids}{name}", "Story", name) for name in stories]
    edges = [Edge.from_record({"parent": f"{ids}review-cart", "child": f"{ids}{name}", "kind": "decomposedInto", "order": 1, "display": "direct"}) for name in stories]
    return GraphReading(SavedPractice.from_fields("stories", "", {}, nodes, edges, []))


with description("the graph's reading of one document") as self:
    with context("compared with the reading of the same document in another format"):
        with it("should lack nothing when both hold the same nodes and edges under other ids"):
            expect(bool(_reading(["Remove Cart Line"], "drawio-").lacking_from(_reading(["Remove Cart Line"])))).to(be_false)

        with context("that holds a story more"):
            with it("should lack the story, named by its type and name"):
                lacks = _reading(["Change Quantity"]).lacking_from(_reading(["Change Quantity", "Remove Cart Line"]))
                expect(lacks.node_names).to(equal(["Story 'Remove Cart Line'"]))

            with it("should lack the edge to the story, named by its two nodes and its kind"):
                lacks = _reading(["Change Quantity"]).lacking_from(_reading(["Change Quantity", "Remove Cart Line"]))
                expect(lacks.edge_names).to(equal(["SubEpic 'Review Cart' decomposedInto Story 'Remove Cart Line'"]))

    with context("that holds no node"):
        with it("should be empty"):
            expect(GraphReading(SavedPractice("stories")).is_empty).to(be_true)


with description("what one reading holds and another lacks") as self:
    with context("with more nodes than a message names"):
        with it("should name the first five and count the rest"):
            lacks = GraphDifference({("Story", f"Story {number}") for number in range(1, 8)}, set())
            expect(lacks.described).to(equal("Story 'Story 1', Story 'Story 2', Story 'Story 3', Story 'Story 4', Story 'Story 5' and 2 more"))


with description("a gap between a session's formats") as self:
    with context("that names the file to align from"):
        with it("should be closed by a render when its format is a drawing"):
            expect(AlignmentGap(MISSING_FILE, "stories-story-map", DRAWING, "", "drawio", STORY_MAP).is_alignable).to(be_true)

        with it("should be closed by a render when its format is code, which a render saves at the declared paths"):
            expect(AlignmentGap(MISSING_FILE, "ddd-model", "{bounded_context}/{aggregate}/{aggregate}.py", "", "python", ".context/domain-model.md").is_alignable).to(be_true)

        with context("that is left to a person because another format of its document conflicts"):
            with it("should name no file to align from"):
                left = AlignmentGap(FORMAT_LACKS, "stories-story-map", DRAWING, "It lacks a story.", "drawio", STORY_MAP).left_to_a_person()
                expect((left.source, left.is_alignable)).to(equal(("", False)))

            with it("should say it waits for the person"):
                left = AlignmentGap(FORMAT_LACKS, "stories-story-map", DRAWING, "It lacks a story.", "drawio", STORY_MAP).left_to_a_person()
                expect(left.message).to(contain("It lacks a story.", "until a person settles"))

    with context("that names no file to align from"):
        with it("should not be closed by a render"):
            expect(AlignmentGap(FORMAT_LACKS, "stories-story-map", DRAWING, "", "drawio").is_alignable).to(be_false)


with description("a diagnosis of a session's formats") as self:
    with context("with no gap"):
        with it("should be aligned"):
            expect(AlignmentDiagnosis(["stories-story-map"], []).is_aligned).to(be_true)

    with context("with a gap"):
        with it("should not be aligned"):
            expect(AlignmentDiagnosis(["stories-story-map"], [AlignmentGap(MISSING_FILE, "stories-story-map", DRAWING, "")]).is_aligned).to(be_false)


with description("a file an alignment rendered") as self:
    with context("that is a whiteboard"):
        with it("should say it still goes on its board in Claude"):
            expect(AlignedFile(".context/story-map.whiteboard", "whiteboard", STORY_MAP).follow_up).to(contain("render.publish_board"))

    with context("that is code keeping a member its model no longer holds"):
        with it("should say which member waits to be migrated, and that it is deleted only after"):
            aligned = AlignedFile("src/ordering/ordering.py", "python", STORY_MAP, ["Cart.total"])
            expect(aligned.follow_up).to(contain("Migrate in src/ordering/ordering.py: Cart.total", "then delete it"))

    with context("that is a drawing"):
        with it("should leave nothing to do"):
            expect(AlignedFile(DRAWING, "drawio", STORY_MAP).follow_up).to(equal(""))


with description("a node of the graph placed in its file") as self:
    with context("that is a story spanning lines 9 to 30"):
        with it("should hold a scenario on lines 12 to 20, so a callout on the story shows the scenario's edges"):
            story = PlacedNode(_node("story", "Story", "Submit Order", 9, 30), STORY_MAP)
            expect(story.holds(PlacedNode(_node("scenario", "Scenario", "Submit a cart", 12, 20), STORY_MAP))).to(be_true)

        with it("should not hold a scenario that starts after it ends"):
            story = PlacedNode(_node("story", "Story", "Submit Order", 9, 30), STORY_MAP)
            expect(story.holds(PlacedNode(_node("scenario", "Scenario", "Pack an order", 40, 50), STORY_MAP))).to(be_false)
