"""BDD spec — a validation report links each graph hit to its file."""

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

from harness.graph.violation import Violation
from space.session import Session, Sessions
from cdd_guidance.actions.validate.validation_report import ValidationReport


with description("a validation report"):
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
                Violation(
                    "limit-operation-parameters",
                    "takes 4 parameters.",
                    subject="Operation `credentialsFailure`",
                    location="src/customer/account/account.ts",
                    line=287,
                )
            ]

        with it("should link each finding to its file by absolute path and line"):
            session = Session(Sessions(self.root))
            session.workpath = self.root
            session.session_path = self.session_dir
            report_md = ValidationReport(session, []).of_graph(self.violations)
            report_path = self.session_dir / "validate-clean-engineering-code-src.md"
            report_path.write_text(report_md, encoding="utf-8")
            account = (self.root / "src/customer/account/account.ts").resolve()
            expect(report_md).to(
                contain(f"[src/customer/account/account.ts]({account}#L287)")
            )
            expect(report_md).not_to(contain("vscode://"))
            expect(report_md).not_to(contain("file://"))
