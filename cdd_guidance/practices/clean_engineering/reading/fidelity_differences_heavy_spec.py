"""The repository's report of where its fidelities disagree. A load reads each format and joins nothing across them, and a
class written in a model document and in code is one node, so a difference between the model and the code is not a
failure of the load: either may be ahead, since people edit a model first as often as they edit the code first. This
spec loads the whole repository for Clean Engineering and reports, without failing, each class the model describes
that no code declares, each member only the model declares, and each public operation the code has that its class's
model leaves out; it fails only when the comparison itself cannot be made. Heavy: it reads every file of the
repository."""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_above, contain, equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.clean_engineering.measures.read_facts import DESCRIBED_FACT
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

MODEL_ONLY_CLASSES = "Classes the model describes that no code declares"
MODEL_ONLY_MEMBERS = "Members the model declares that the code lacks"
CODE_ONLY_OPERATIONS = "Public operations the code has that the model leaves out"


class FidelityDifferences:
    """Where the model fidelity and the code fidelity of one Clean Engineering graph disagree, read from the places each
    node is written in."""

    def __init__(self, in_graph) -> None:
        self._in_graph = in_graph
        self._edges = in_graph.practice.reading.graph.edges
        self._test_code = in_graph.practice.reading.test_code

    def by_kind(self) -> dict[str, list[str]]:
        return {
            MODEL_ONLY_CLASSES: sorted(f"{node.name} ({node.source.file})" for node in self._in_graph.nodes("OoadClass") if node.has_fact(DESCRIBED_FACT)),
            MODEL_ONLY_MEMBERS: sorted(f"{cls.name}.{member.name} ({member.source.file})" for cls, member in self._members() if member.source.file.endswith(".md")),
            CODE_ONLY_OPERATIONS: sorted(f"{cls.name}.{member.name} ({member.source.file})" for cls, member in self._members() if self._missing_from_model(cls, member)),
        }

    def report(self) -> str:
        lines = ["# Where the model and the code disagree", ""]
        for kind, found in self.by_kind().items():
            lines += [f"## {kind}: {len(found)}", "", *(f"- {item}" for item in found), ""]
        return "\n".join(lines)

    def _members(self):
        """Each member of each class of code a model document describes too, with its class."""
        for cls in self._in_graph.nodes("OoadClass"):
            if "markdown" in cls.places and not cls.has_fact(DESCRIBED_FACT) and not self._test_code.is_test_code(cls.source.file):
                for kind in ("owns", "properties"):
                    yield from ((cls, edge.child) for edge in self._edges.from_parent(kind, cls))

    def _missing_from_model(self, cls, member) -> bool:
        public = member.type == "Operation" and not member.name.startswith("_") and member.name not in CONSTRUCTOR_NAMES
        return public and not member.source.file.endswith(".md") and "markdown" not in member.places


_MODEL = "# shop\n\n## Ledger\n\n------\n+ balance: int\n----\n+ record(entry: str): str\n+ close(): None\n\n## Till\n\n----\n+ open(): None\n"
_CODE = "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n\n    def audit(self) -> None:\n        return None\n"


with description("the repository's report of where its model and its code disagree") as self:
    with context("with a module whose model and code each hold what the other lacks"):
        with before.all:
            fixture = practice_from_files({"shop/.context/shop-model.md": _MODEL, "shop/ledger.py": _CODE})
            self.found = FidelityDifferences(fixture.practice.reading.in_graph).by_kind()

        with it("should report the class the model describes that no code declares"):
            expect(self.found[MODEL_ONLY_CLASSES]).to(equal(["Till (shop/.context/shop-model.md)"]))

        with it("should report the members only the model declares"):
            expect(self.found[MODEL_ONLY_MEMBERS]).to(equal(["Ledger.balance (shop/.context/shop-model.md)", "Ledger.close (shop/.context/shop-model.md)"]))

        with it("should report the public operation the code has that the model leaves out"):
            expect(self.found[CODE_ONLY_OPERATIONS]).to(equal(["Ledger.audit (shop/ledger.py)"]))

    with context("with this repository loaded whole"):
        with before.all:
            graph = Graph()
            graph.load_working_copy(str(_REPO), {"clean_engineering": "."}, database=tempfile.mkdtemp(prefix="cdd-fidelity-"), force=True)
            in_graph = graph.practices.named("clean_engineering").reading.in_graph
            self.classes = list(in_graph.nodes("OoadClass"))
            differences = FidelityDifferences(in_graph)
            self.found = differences.by_kind()
            self.report = Path(tempfile.gettempdir()) / "cdd-fidelity-differences.md"
            self.report.write_text(differences.report(), encoding="utf-8")
            print(f"\nWhere the model and the code disagree: {self.report}\n" + "\n".join(f"  {kind}: {len(found)}" for kind, found in self.found.items()))

        with it("should compare classes the model and the code both hold"):
            written_in_both = [node for node in self.classes if "markdown" in node.places and "python" in node.places]
            expect(len(written_in_both)).to(be_above(0))

        with it("should write the report of each kind of difference, however many it finds"):
            expect(self.report.read_text(encoding="utf-8")).to(contain(MODEL_ONLY_CLASSES, MODEL_ONLY_MEMBERS, CODE_ONLY_OPERATIONS))

