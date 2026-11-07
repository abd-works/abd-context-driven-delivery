"""BDD spec — graph JSON violation reader."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.actions.validate.graph_json_reader import save_checked_graph, violations_from_graph_json_files

_SAVED_GRAPH = Path(__file__).with_name("fixtures") / "saved-graph" / ".context" / "graph.json"


with description("graph JSON reader"):
    with context("a saved graph document"):
        with it("should read every practice's violations"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect([violation.rule for violation in violations]).to(
                equal(["limit-operation-parameters", "load-with-identity-in-hand"])
            )

        with it("should place each violation at its node's file"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect(violations[1].location).to(equal("src/orders/order.ts"))

        with it("should name the practice that found each violation"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect(violations[1].practice).to(equal("ddd"))

        with it("should keep only the practices asked for"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH], practices=["ddd"])
            expect([violation.rule for violation in violations]).to(equal(["load-with-identity-in-hand"]))

        with it("should keep every hit when several checked graphs are saved as one"):
            with tempfile.TemporaryDirectory() as folder:
                saved = Path(folder) / "report.json"
                save_checked_graph([_SAVED_GRAPH, _SAVED_GRAPH], saved)
                expect(len(violations_from_graph_json_files([saved]))).to(equal(4))

        with it("should keep the same message when several checked graphs are saved as one"):
            with tempfile.TemporaryDirectory() as folder:
                saved = Path(folder) / "report.json"
                save_checked_graph([_SAVED_GRAPH, _SAVED_GRAPH], saved)
                messages = [violation.described for violation in violations_from_graph_json_files([saved])]
                expect(messages[:2]).to(equal([violation.described for violation in violations_from_graph_json_files([_SAVED_GRAPH])]))
