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

from expects import contain, expect
from mamba import before, context, description, it

from validate.graph_json_reader import refresh_stale_limit_operation_parameter_messages


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
