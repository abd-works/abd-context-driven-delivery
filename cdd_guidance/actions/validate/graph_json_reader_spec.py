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

from expects import contain, equal, expect
from mamba import before, context, description, it

from validate.graph_json_reader import (
    refresh_stale_limit_operation_parameter_messages,
    violations_from_graph_json_files,
)

_SAVED_GRAPH = Path(__file__).with_name("fixtures") / "saved-graph" / ".context" / "graph.json"


with description("graph JSON reader"):
    with context("refresh_stale_limit_operation_parameter_messages"):
        with before.each:
            self.temp = tempfile.TemporaryDirectory()
            self.root = Path(self.temp.name)
            source_dir = self.root / "src"
            source_dir.mkdir(parents=True)
            (source_dir / "widget.ts").write_text(
                "export class Widget {\n"
                "  private failure(a: string, b: string, c: string, d: string): void {\n"
                "    return;\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            self.violations = [
                {
                    "rule_slug": "limit-operation-parameters",
                    "location": "src/widget.ts",
                    "node_name": "failure",
                    "node_type": "Operation",
                    "line_number": 2,
                    "violation_message": (
                        "Operation `failure`: Operation 'failure' takes more than two parameters."
                    ),
                    "severity": "error",
                    "graph_rule": True,
                }
            ]

        with it("should replace legacy messages with parameter counts from source"):
            refreshed = refresh_stale_limit_operation_parameter_messages(
                self.violations,
                self.root,
            )
            expect(refreshed[0]["violation_message"]).to(
                contain("takes 4 parameters (maximum 3, excluding self)")
            )

    with context("a saved graph document"):
        with it("should read every practice's violating rule rows"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect([item["rule_slug"] for item in violations]).to(
                equal(["limit-operation-parameters", "load-with-identity-in-hand"])
            )
            expect(violations[1]["location"]).to(equal("src/orders/order.ts"))
            expect(violations[1]["practice"]).to(equal("ddd"))

        with it("should keep only the practices asked for"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH], practices=["ddd"])
            expect([item["rule_slug"] for item in violations]).to(equal(["load-with-identity-in-hand"]))
