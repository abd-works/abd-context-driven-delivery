"""What Fix this one, Fix rule and Fix all on a broken rule send the chat, in the Graph app and the Files app: the words
are Python's, written word for word as the pages wrote them before they moved here (2026-11-22). Each names the
guidance that states the rule broken, the fidelity whose rules hold it, else its practice, so a story map's rule is not
fixed by Clean Engineering's guidelines (found 2026-11-23)."""

import shutil
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.graph.graph import Graph, Node, Source
from harness.graph.graph_rules_collection import GraphRule
from harness.graph.location import Location
from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.saved_graph import NodeIdentity
from harness.graph.violation import Finding
from harness.graph.violation_correction import CorrectedPlace, ViolationCorrection, ViolationCorrections
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_SLUG = "limit-operation-parameters"
_NODE_ID = "clean_engineering:Operation:place"
_MESSAGE = "Operation 'place' takes 4 parameters (maximum 2)."
# Interaction: limit-operation-parameters is a rule of Clean Engineering's model fidelity.
_GUIDANCE = "clean-engineering-model"
# Interaction: vocabulary-traces-to-source is one of Clean Engineering's shared rules, which no fidelity states.
_SHARED_SLUG = "vocabulary-traces-to-source"
_HOW_TO_FIX = (
    f"Fix this violation using the {_GUIDANCE} guidelines and a test-driven approach.\n"
    "Run or add tests that express the intended behavior before or alongside the fix.\n"
)
_ORDER = "class Order:\n    def place(self, cart, user, store, day):\n        return self\n"


class _CountedRule(PracticeGraphRule):
    slug = _SLUG
    node_types = ("Operation",)


class _SharedRule(PracticeGraphRule):
    slug = _SHARED_SLUG
    node_types = ("Operation",)


def _graph_holding_place(root: Path) -> tuple[Graph, Node]:
    """A graph holding the operation place, lines 2 to 3 of order.py under root, which its rule is run on."""
    (root / "order.py").write_text(_ORDER, encoding="utf-8")
    graph = Graph()
    graph.reads.open(root)
    practice = graph.practices.named("clean_engineering")
    place = Node(practice, NodeIdentity(type="Operation", node_id=_NODE_ID, name="place"), Source.from_root(str(root), Location("order.py", 2, 3)))
    place.rules.entries[_SLUG] = GraphRule(place, _SLUG, _CountedRule())
    place.rules.entries[_SHARED_SLUG] = GraphRule(place, _SHARED_SLUG, _SharedRule())
    practice.reading.in_graph.hold(place)
    return graph, place


with description("a correction of a broken rule"):
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        self.graph, self.place = _graph_holding_place(self.root)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("asked of the graph for a rule broken on its node"):
        with before.each:
            self.place.rules[_SLUG].record(Finding(self.place, _MESSAGE))

        with it("should ask the chat to fix it test first, naming the node, its file and lines, the rule, the code, and what is wrong"):
            expect(self.graph.correction_prompt(_NODE_ID, _SLUG)).to(equal(
                f"{_HOW_TO_FIX}\nNode: place (Operation)\nFile: order.py:2-3\nRule: {_SLUG}\n\nErroneous code:\n```\n"
                f"    def place(self, cart, user, store, day):\n        return self\n```\n\nViolation: {_MESSAGE}"
            ))

        with context("that gives two messages there"):
            with before.each:
                self.place.rules[_SLUG].record(Finding(self.place, "Second."))

            with it("should say every message, one to a line"):
                expect(self.graph.correction_prompt(_NODE_ID, _SLUG).split("Violation: ")[1]).to(equal(f"{_MESSAGE}\nSecond."))

    with context("asked of the graph for a rule its practice states for every fidelity"):
        with before.each:
            self.place.rules[_SHARED_SLUG].record(Finding(self.place, "Order names no term of the source."))

        with it("should ask the chat to fix it by its practice's guidelines"):
            expect(self.graph.correction_prompt(_NODE_ID, _SHARED_SLUG).splitlines()[0]).to(equal(
                "Fix this violation using the clean-engineering guidelines and a test-driven approach."
            ))

    with context("asked of the graph for a rule that passes on its node"):
        with it("should have nothing to correct"):
            expect(self.graph.correction_prompt(_NODE_ID, _SLUG)).to(equal(""))

    with context("asked of the graph for a node it does not hold"):
        with it("should have nothing to correct"):
            expect(self.graph.correction_prompt("no-such-node", _SLUG)).to(equal(""))

    with context("as a comment on the rule's lines"):
        with it("should ask the chat to fix it test first, naming the rule and what is wrong, and leave out the lines a sent comment quotes"):
            expect(ViolationCorrection(_SLUG, _MESSAGE, guidance=_GUIDANCE).comment).to(equal(f"{_HOW_TO_FIX}\nRule: {_SLUG}\nViolation: {_MESSAGE}"))

    with context("of a rule whose guidance is not known"):
        with it("should ask the chat to fix it by its own practice's guidelines"):
            expect(ViolationCorrection(_SLUG, _MESSAGE).comment.splitlines()[0]).to(equal(
                "Fix this violation using its practice's guidelines and a test-driven approach."
            ))


with description("the corrections Fix rule and Fix all send together"):
    with before.all:
        self.place = ViolationCorrection(_SLUG, _MESSAGE, CorrectedPlace("place", "Operation", "order.py", (2, 3), "def place"), _GUIDANCE)
        self.archive = ViolationCorrection("story-name-captures-system-mechanic", "Process opens the story name.", CorrectedPlace("Process Ticket Archive", "Story", "story-map.md", (5, 5), ""), "stories-story-map")

    with context("of several broken rules"):
        with it("should ask once to fix them all test first, then name each one, numbered, with the guidance that states its rule"):
            expect(ViolationCorrections([self.place, self.archive]).prompt).to(equal(
                "Fix these 2 violations, each using the guidelines it names, and a test-driven approach.\n"
                "Run or add tests that express the intended behavior before or alongside the fix.\n"
                f"\nViolation 1, by the {_GUIDANCE} guidelines:\n{self.place.described}"
                f"\n\nViolation 2, by the stories-story-map guidelines:\n{self.archive.described}"
            ))

    with context("of one broken rule"):
        with it("should be that rule's own correction"):
            expect(ViolationCorrections([self.place]).prompt).to(equal(self.place.prompt))

    with context("of no broken rule"):
        with it("should have nothing to send"):
            expect(ViolationCorrections([]).prompt).to(equal(""))
