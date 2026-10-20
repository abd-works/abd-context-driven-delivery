"""BDD spec — validation report file links."""

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

from validate.validation_report import build_graph_json_report
from validate.verify_report_links import verify_report


with description("validation report formatter links"):
    with context("with a session report folder under the workspace"):
        with before.each:
            self.temp = tempfile.TemporaryDirectory()
            self.root = Path(self.temp.name)
            self.session_dir = self.root / ".sessions" / "LERN alignment"
            self.session_dir.mkdir(parents=True)
            source = self.root / "src" / "customer" / "account" / "account.ts"
            source.parent.mkdir(parents=True)
            source.write_text("\n" * 286 + "export function credentialsFailure() {}\n", encoding="utf-8")
            self.violations = [
                {
                    "rule_slug": "limit-operation-parameters",
                    "location": "src/customer/account/account.ts",
                    "line_number": 287,
                    "violation_message": "Operation `credentialsFailure`: takes 4 parameters.",
                    "severity": "error",
                    "graph_rule": True,
                }
            ]

        with it("should emit absolute path #L links that verify_report_links accepts"):
            report_md = build_graph_json_report(
                self.violations,
                workspace_directory=self.root,
                link_from_directory=self.session_dir,
            )
            report_path = self.session_dir / "validate-clean-engineering-code-src.md"
            report_path.write_text(report_md, encoding="utf-8")
            account = (self.root / "src/customer/account/account.ts").resolve()
            expect(report_md).to(
                contain(f"[src/customer/account/account.ts]({account}#L287)")
            )
            expect(report_md).not_to(contain("vscode://"))
            expect(report_md).not_to(contain("file://"))
            expect(verify_report(report_path)).to(equal([]))
